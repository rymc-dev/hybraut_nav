from abc import ABC, abstractmethod
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.callback_groups import CallbackGroup
from typing import Optional, Dict, Any, Generic, TypeVar, List, Type
from dataclasses import dataclass, field
import logging

# Type variable for the managed component type
T = TypeVar('T')

class RegistryComponent(ABC):
    """
    Abstract base class for components that can be managed by a Registry.
    
    All components (States, Guards, Resets, Dynamics) should inherit from this
    to ensure they have the required lifecycle methods.
    """
    
    @abstractmethod
    def activate(self, node: Node, qos: Optional[QoSProfile] = None, 
                cb_group: Optional[CallbackGroup] = None) -> None:
        """Activate the component with ROS2 node."""
        pass
    
    @abstractmethod
    def deactivate(self, node: Node) -> None:
        """Deactivate the component and cleanup resources."""
        pass
    
    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Check if component is currently active."""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get component status and configuration info."""
        pass
    
    @property
    @abstractmethod
    def error_count(self) -> int:
        """Get the number of errors encountered."""
        pass


class Registry(Generic[T], ABC):
    """
    Abstract base class for component registries.
    
    This provides the interface that all specialized registries
    (StateRegistry, GuardRegistry, etc.) should implement.
    
    Type Parameters:
        T: The type of component this registry manages
    """
    
    @abstractmethod
    def add_component(self, name: str, component: T) -> None:
        """Add a component to the registry."""
        pass
    
    @abstractmethod
    def remove_component(self, name: str, node: Optional[Node] = None) -> None:
        """Remove a component from the registry."""
        pass
    
    @abstractmethod
    def get_component(self, name: str) -> T:
        """Get a specific component by name."""
        pass
    
    @abstractmethod
    def get_component_names(self) -> List[str]:
        """Get list of all component names."""
        pass
    
    @abstractmethod
    def activate_components(self, node: Node, qos: Optional[QoSProfile] = None,
                           cb_group: Optional[CallbackGroup] = None) -> None:
        """Activate all components in the registry."""
        pass
    
    @abstractmethod
    def deactivate_components(self, node: Node) -> None:
        """Deactivate all components in the registry."""
        pass
    
    @abstractmethod
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status."""
        pass
    
    @abstractmethod
    def validate_dependencies(self, required_components: List[str], 
                            required_types: Optional[List[Type]] = None) -> bool:
        """Validate that required components exist and match expected types."""
        pass


@dataclass
class ComponentRegistry(Registry[T]):
    """
    Generic implementation of Registry for managing components.
    
    This concrete implementation provides the core functionality that can be
    used directly or extended by specialized registries.
    
    Type Parameters:
        T: The type of component this registry manages (must inherit from RegistryComponent)
    
    Attributes:
        _components (Dict[str, T]): Dictionary of component instances keyed by name
        _are_components_active (bool): Whether all components are currently active
        _logger (logging.Logger): Dedicated logger for this registry instance
        _component_type_name (str): Human-readable name for the component type
    """
    _components: Dict[str, T] = field(default_factory=dict)
    _are_components_active: bool = False
    _logger: Optional[logging.Logger] = None
    _component_type_name: str = "Component"

    def __post_init__(self):
        """Initialize the logger after dataclass creation."""
        class_name = self.__class__.__name__
        self._logger = logging.getLogger(f"{__name__}.{class_name}")

    def add_component(self, name: str, component: T) -> None:
        """
        Add a component to the registry.
        
        Args:
            name (str): Name for the component
            component (T): Component instance to add
            
        Raises:
            ValueError: If component name already exists
            TypeError: If component doesn't inherit from RegistryComponent
        """
        if not isinstance(component, RegistryComponent):
            error_msg = f"Component must inherit from RegistryComponent"
            self._logger.error(error_msg)
            raise TypeError(error_msg)
            
        if name in self._components:
            error_msg = f"{self._component_type_name} '{name}' already exists in registry"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        
        self._components[name] = component
        self._logger.info(f"Added {self._component_type_name.lower()} '{name}' to registry")

    def remove_component(self, name: str, node: Optional[Node] = None) -> None:
        """
        Remove a component from the registry.
        
        Args:
            name (str): Name of the component to remove
            node (Optional[Node]): ROS2 node for deactivation if component is active
            
        Raises:
            KeyError: If component name not found
            RuntimeError: If component is active but no node provided
        """
        if name not in self._components:
            error_msg = f"{self._component_type_name} '{name}' not found in registry"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
        
        component = self._components[name]
        if component.is_active:
            if node is None:
                error_msg = f"Cannot remove active {self._component_type_name.lower()} '{name}' without providing node for deactivation"
                self._logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            try:
                component.deactivate(node)
                self._logger.debug(f"Deactivated {self._component_type_name.lower()} '{name}' before removal")
            except Exception as e:
                self._logger.warning(f"Failed to deactivate {self._component_type_name.lower()} '{name}' during removal: {e}")
        
        del self._components[name]
        self._logger.info(f"Removed {self._component_type_name.lower()} '{name}' from registry")

    def get_component(self, name: str) -> T:
        """
        Get a specific component by name.
        
        Args:
            name (str): Name of the component to retrieve
            
        Returns:
            T: The requested component instance
            
        Raises:
            KeyError: If component name is not found
        """
        if name not in self._components:
            error_msg = f"{self._component_type_name} '{name}' not found in registry"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
        return self._components[name]

    def get_component_names(self) -> List[str]:
        """
        Get a list of all registered component names.
        
        Returns:
            List[str]: List of component names
        """
        return list(self._components.keys())

    def get_components_by_names(self, component_names: List[str]) -> Dict[str, T]:
        """
        Retrieve specific components by their names.
        
        Args:
            component_names (List[str]): List of component names to retrieve
            
        Returns:
            Dict[str, T]: Mapping of component names to their instances
            
        Raises:
            KeyError: If any component name is not found in the registry
        """
        components = {}
        missing_components = []
        
        for name in component_names:
            if name in self._components:
                components[name] = self._components[name]
            else:
                missing_components.append(name)
        
        if missing_components:
            error_msg = f"{self._component_type_name}s not found in registry: {missing_components}"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
            
        self._logger.debug(f"Retrieved components for: {component_names}")
        return components

    def activate_components(self, node: Node, qos: Optional[QoSProfile] = None,
                           cb_group: Optional[CallbackGroup] = None) -> None:
        """
        Activate all registered components.
        
        Args:
            node (Node): ROS2 node to attach publishers/subscribers to
            qos (Optional[QoSProfile]): Quality of Service profile for all components
            cb_group (Optional[CallbackGroup]): Callback group for all components
            
        Raises:
            RuntimeError: If components are already active
        """
        if self._are_components_active:
            error_msg = f'{self._component_type_name}s are already active'
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._logger.info(f"Activating {len(self._components)} {self._component_type_name.lower()}s")
        
        activated_components = []
        try:
            for component_name, component in self._components.items():
                self._logger.debug(f"Activating {self._component_type_name.lower()}: {component_name}")
                component.activate()
                activated_components.append(component_name)
                
            self._are_components_active = True
            self._logger.info(f"Successfully activated all {self._component_type_name.lower()}s: {activated_components}")
            
        except Exception as e:
            # Rollback: deactivate any components that were successfully activated
            self._logger.error(f"Failed to activate {self._component_type_name.lower()}s, rolling back: {e}")
            for component_name in activated_components:
                try:
                    self._logger.debug(f"Rolling back activation for {self._component_type_name.lower()}: {component_name}")
                    self._components[component_name].deactivate(node)
                except Exception as rollback_error:
                    self._logger.error(f"Rollback failed for {self._component_type_name.lower()} '{component_name}': {rollback_error}")
            raise

    def deactivate_components(self, node: Node) -> None:
        """
        Deactivate all registered components.
        
        Args:
            node (Node): ROS2 node containing the publishers/subscribers
            
        Raises:
            RuntimeError: If components are not currently active
        """
        if not self._are_components_active:
            error_msg = f'{self._component_type_name}s are not currently active'
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self._logger.info(f"Deactivating {len(self._components)} {self._component_type_name.lower()}s")
        
        deactivation_errors = []
        for component_name, component in self._components.items():
            try:
                self._logger.debug(f"Deactivating {self._component_type_name.lower()}: {component_name}")
                component.deactivate()
            except Exception as e:
                error_msg = f"Failed to deactivate {self._component_type_name.lower()} '{component_name}': {e}"
                self._logger.error(error_msg)
                deactivation_errors.append(error_msg)
        
        self._are_components_active = False
        
        if deactivation_errors:
            self._logger.warning(f"Some {self._component_type_name.lower()}s failed to deactivate properly: {len(deactivation_errors)} errors")
        else:
            self._logger.info(f"Successfully deactivated all {self._component_type_name.lower()}s")

    def validate_dependencies(self, required_components: List[str], 
                            required_types: Optional[List[Type]] = None) -> bool:
        """
        Validate that required components exist and optionally match expected types.
        
        Args:
            required_components (List[str]): List of required component names
            required_types (Optional[List[Type]]): Expected component types (same order)
            
        Returns:
            bool: True if all dependencies are satisfied
            
        Raises:
            ValueError: If validation fails
        """
        missing_components = [name for name in required_components if name not in self._components]
        if missing_components:
            error_msg = f"Missing required {self._component_type_name.lower()}s: {missing_components}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        
        if required_types and len(required_types) == len(required_components):
            type_mismatches = []
            for component_name, expected_type in zip(required_components, required_types):
                actual_type = type(self._components[component_name])
                if not issubclass(actual_type, expected_type):
                    type_mismatches.append(f"{component_name}: expected {expected_type}, got {actual_type}")
            
            if type_mismatches:
                error_msg = f"{self._component_type_name} type mismatches: {type_mismatches}"
                self._logger.error(error_msg)
                raise ValueError(error_msg)
        
        self._logger.debug(f"{self._component_type_name} dependencies validated: {required_components}")
        return True

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status information about the registry.
        
        Returns:
            Dict[str, Any]: Status information including component count, 
                           activation status, and individual component info
        """
        status = {
            f"total_{self._component_type_name.lower()}s": len(self._components),
            f"{self._component_type_name.lower()}s_active": self._are_components_active,
            f"{self._component_type_name.lower()}_names": self.get_component_names(),
            f"{self._component_type_name.lower()}s_info": {
                name: component.get_info() 
                for name, component in self._components.items()
            },
            f"error_{self._component_type_name.lower()}s": [
                name for name, component in self._components.items() 
                if component._error_count > 0
            ]
        }
        
        self._logger.debug(
            f"Generated registry status: {len(self._components)} {self._component_type_name.lower()}s, "
            f"active: {self._are_components_active}"
        )
        return status

    def __len__(self) -> int:
        """Return the number of components in the registry."""
        return len(self._components)

    def __contains__(self, component_name: str) -> bool:
        """Check if a component exists in the registry."""
        return component_name in self._components

    def __iter__(self):
        """Iterate over component names."""
        return iter(self._components)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        active_status = "Active" if self._are_components_active else "Inactive"
        return f"<{self.__class__.__name__}: {len(self._components)} {self._component_type_name.lower()}s ({active_status})>"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(_components={list(self._components.keys())}, "
            f"_are_components_active={self._are_components_active})"
        )

