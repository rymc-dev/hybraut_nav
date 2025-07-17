from abc import ABC, abstractmethod
from typing import Any, Dict, Type, List, Optional, ClassVar
from dataclasses import dataclass, field
from collections import namedtuple
from rclpy.logging import get_logger
from ..spec.io_spec import IOSpec
from collections import deque
from .hybrid_automaton_component_interface import HybridAutomatonComponentInterface

@dataclass
class DynamicsField:
    """
    Represents a single field in the dynamics specification.
    
    Args:
        name: Field name (e.g., 'yaw_rate', 'velocity')
        dtype: Python type (e.g., float, int)
        unit: Unit string (e.g., 'rad/s', 'm/s')
        description: Optional description of the field
        default: Optional default value
        bounds: Optional tuple of (min, max) values
    """
    name: str
    dtype: Type
    unit: str
    description: Optional[str] = None
    default: Optional[Any] = None
    bounds: Optional[tuple] = None

    def __post_init__(self):
        """Validate the field specification."""
        if not isinstance(self.name, str) or not self.name.isidentifier():
            raise ValueError(f"Field name '{self.name}' must be a valid Python identifier")
        
        if not isinstance(self.dtype, type):
            raise TypeError(f"dtype must be a type, got {type(self.dtype)}")
        
        if not isinstance(self.unit, str):
            raise TypeError(f"unit must be a string, got {type(self.unit)}")
        
        if self.bounds is not None:
            if not isinstance(self.bounds, tuple) or len(self.bounds) != 2:
                raise ValueError("bounds must be a tuple of (min, max)")
            if self.bounds[0] is not None and self.bounds[1] is not None:
                if self.bounds[0] >= self.bounds[1]:
                    raise ValueError("bounds minimum must be less than maximum")
    
    def validate_value(self, value: Any) -> bool:
        """Validate that a value conforms to this field specification."""
        if value is None and self.default is not None:
            return True
        
        if not isinstance(value, self.dtype):
            return False
        
        if self.bounds is not None:
            min_val, max_val = self.bounds
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
        
        return True
    
    def get_value_or_default(self, value: Any) -> Any:
        """Get the value or default if value is None."""
        return value if value is not None else self.default

@dataclass
class DynamicsSpec:
    """
    Specification for dynamics function inputs/outputs.
    
    This class allows you to define the structure of your dynamics data
    including field names, types, units, and validation rules.
    """
    name: str
    fields: List[DynamicsField] = field(default_factory=list)
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate the specification."""
        if not isinstance(self.name, str) or not self.name.isidentifier():
            raise ValueError(f"Spec name '{self.name}' must be a valid Python identifier")
        
        # Check for duplicate field names
        field_names = [f.name for f in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Duplicate field names are not allowed")
    
    def add_field(self, name: str, dtype: Type, unit: str, **kwargs) -> 'DynamicsSpec':
        """
        Add a field to the specification.
        
        Args:
            name: Field name
            dtype: Python type
            unit: Unit string
            **kwargs: Additional field properties (description, default, bounds)
        
        Returns:
            Self for method chaining
        """
        field_obj = DynamicsField(name=name, dtype=dtype, unit=unit, **kwargs)
        self.fields.append(field_obj)
        return self
    
    def create_namedtuple(self) -> Type[namedtuple]:
        """
        Create a namedtuple type from this specification.
        
        Returns:
            A namedtuple class with fields matching this specification
        """
        field_names = [f.name for f in self.fields]
        return namedtuple(self.name, field_names)
    
    def create_dataclass(self) -> Type:
        """
        Create a dataclass type from this specification.
        
        Returns:
            A dataclass with fields matching this specification
        """
        annotations = {}
        defaults = {}
        
        for field_obj in self.fields:
            annotations[field_obj.name] = field_obj.dtype
            if field_obj.default is not None:
                defaults[field_obj.name] = field_obj.default
        
        # Create the dataclass dynamically
        def __init__(self, **kwargs):
            for field_obj in self.fields:
                value = kwargs.get(field_obj.name)
                if value is None and field_obj.default is not None:
                    value = field_obj.default
                setattr(self, field_obj.name, value)
        
        def __repr__(self):
            field_strs = []
            for field_obj in self.fields:
                value = getattr(self, field_obj.name)
                field_strs.append(f"{field_obj.name}={value}")
            return f"{self.name}({', '.join(field_strs)})"
        
        # Create the class
        cls_dict = {
            '__init__': __init__,
            '__repr__': __repr__,
            '__annotations__': annotations,
            '_dynamics_spec': self,
        }
        
        # Add defaults as class attributes
        cls_dict.update(defaults)
        
        return type(self.name, (object,), cls_dict)
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate data against this specification.
        
        Args:
            data: Dictionary of field_name -> value
            
        Returns:
            Dictionary of field_name -> error_message for any validation errors
        """
        errors = {}
        
        for field_obj in self.fields:
            value = data.get(field_obj.name)
            
            # Check required fields
            if value is None and field_obj.default is None:
                errors[field_obj.name] = f"Required field '{field_obj.name}' is missing"
                continue
            
            # Skip validation if value is None and there's a default
            if value is None and field_obj.default is not None:
                continue
            
            # Validate the value
            if not field_obj.validate_value(value):
                type_name = field_obj.dtype.__name__
                bounds_str = f" (bounds: {field_obj.bounds})" if field_obj.bounds else ""
                errors[field_obj.name] = f"Invalid value for '{field_obj.name}': expected {type_name}{bounds_str}, got {type(value).__name__}"
        
        return errors
    
    def get_field_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all fields.
        
        Returns:
            Dictionary mapping field names to their specifications
        """
        return {
            field_obj.name: {
                'type': field_obj.dtype.__name__,
                'unit': field_obj.unit,
                'description': field_obj.description,
                'default': field_obj.default,
                'bounds': field_obj.bounds
            }
            for field_obj in self.fields
        }
    
    def __repr__(self) -> str:
        return f"DynamicsSpec(name='{self.name}', fields={len(self.fields)})"

# Example usage and factory functions
class DynamicsSpecBuilder:
    """Builder class for creating common dynamics specifications."""
    
    @staticmethod
    def create_vehicle_state() -> DynamicsSpec:
        """Create a typical vehicle state specification."""
        return (DynamicsSpec("VehicleState", description="Vehicle state variables")
                .add_field("position_x", float, "m", description="X position")
                .add_field("position_y", float, "m", description="Y position")
                .add_field("velocity", float, "m/s", description="Forward velocity", bounds=(0, None))
                .add_field("yaw_rate", float, "rad/s", description="Yaw rate", bounds=(-10, 10))
                .add_field("steering_angle", float, "rad", description="Steering angle", bounds=(-1.57, 1.57)))
    
    @staticmethod
    def create_control_inputs() -> DynamicsSpec:
        """Create a typical control input specification."""
        return (DynamicsSpec("ControlInputs", description="Control input variables")
                .add_field("throttle", float, "percent", description="Throttle percentage", bounds=(0, 100))
                .add_field("brake", float, "percent", description="Brake percentage", bounds=(0, 100))
                .add_field("steering_command", float, "rad", description="Steering command", bounds=(-1.57, 1.57)))
    
    @staticmethod
    def create_derivatives() -> DynamicsSpec:
        """Create a typical derivatives specification."""
        return (DynamicsSpec("StateDerivatives", description="State derivative variables")
                .add_field("velocity_dot", float, "m/s^2", description="Velocity derivative")
                .add_field("yaw_rate_dot", float, "rad/s^2", description="Yaw rate derivative")
                .add_field("x_dot", float, "m/s", description="X position derivative")
                .add_field("y_dot", float, "m/s", description="Y position derivative"))
    
    @staticmethod
    def create_automaton_control_outputs() -> DynamicsSpec:
        """Create a automaton control spec"""
        return (DynamicsSpec("AutomatonControlOutputs", description="outputs for automaton spec")
                .add_field("velocity", float, unit="m/s", description="Velocity in meters per second")
                .add_field("yaw_rate", float, unit="rad/s", description="Yaw rate in radians per second"))

class DynamicsInterface(HybridAutomatonComponentInterface):
    """
    Dynamics interface for hybrid automaton components.

    Defines a contract for components that evolve state over time.
    """

    _dynamic_output_spec: ClassVar['DynamicsSpec'] = None

    # Update init, dynamic_output_spec is a class varianble that is not optional it must be assigned on 
    # implenetation of this interface

    def __init__(self, **init_kwargs):
        """
        Initialize the dynamics interface.

        Args:
            output_spec (DynamicsSpec, optional): The output specification.
            **init_kwargs: Initialization keyword arguments.
        """
        # Set output spec before calling parent
        self._dt = 0.1
        self._avg_dt = self._dt  # initialize average dt
        self._output_spec = self._dynamic_output_spec.create_namedtuple()
        super().__init__(**init_kwargs)
    
    def _post_init_hook(self) -> None:
        """
        Hook for subclasses to create state buffers after init.
        """
        self._state_buffer: Dict[str, deque] = {}
        for state_input in self._state_input_spec:
            self._state_buffer[state_input.name] = deque(maxlen=state_input.buffer_size)

    def create_output(self, **kwargs) -> Any:
        """
        Create a validated dynamics output namedtuple.

        Returns:
            NamedTuple: Instance of output_type.
        """
        output_data = {}
        for field in self.output_spec.fields:
            value = kwargs.get(field.name)
            output_data[field.name] = field.get_value_or_default(value)

        errors = self.output_spec.validate_data(output_data)
        if errors:
            error_msgs = [f"{k}: {v}" for k, v in errors.items()]
            raise ValueError(f"Output creation failed: {'; '.join(error_msgs)}")

        output = self.output_type(**output_data)
        self._validate_output(output)
        return output

    def _validate_output(self, output: Any):
        if not isinstance(output, self.output_type):
            raise TypeError(f"Output must be of type {self.output_type.__name__}, got {type(output).__name__}")

        errors = self.output_spec.validate_data(output._asdict())
        if errors:
            error_msgs = [f"{k}: {v}" for k, v in errors.items()]
            raise ValueError(f"Output validation failed: {'; '.join(error_msgs)}")

    def _avg_dt_calc(self, current_dt: float, alpha: float = 0.1):
        """Exponential moving average for time delta smoothing."""
        self._avg_dt = alpha * current_dt + (1 - alpha) * self._avg_dt

    def __call__(self, **state_kwargs) -> Any:
        """call function for dynamics, this will
        generate the dynamics evaluation output for this inerface,
        must return the spec type defined in classes dynamics_output_spec

        Returns:
            Any: _description_
        """
        super().__call__(**state_kwargs)

    @classmethod
    def dynamic_output_spec_name(cls) -> str:
        return cls._dynamic_output_spec.name if cls._dynamic_output_spec else "Undefined"

    @classmethod
    def dynamic_output_spec_description(cls) -> str:
        return cls._dynamic_output_spec.description if cls._dynamic_output_spec else "No description"

    @classmethod
    def dynamic_output_spec_names(cls) -> List[str]:
        return [f.name for f in cls._dynamic_output_spec.fields] if cls._dynamic_output_spec else []

    @classmethod
    def dynamic_output_spec_types(cls) -> List[str]:
        return [f.dtype.__name__ for f in cls._dynamic_output_spec.fields] if cls._dynamic_output_spec else []

    @classmethod
    def dynamic_output_spec_units(cls) -> List[str]:
        return [f.unit for f in cls._dynamic_output_spec.fields] if cls._dynamic_output_spec else []

    def get_component_info(self) -> Dict[str, Any]:
        """Return introspection information about this dynamics component."""
        info: Dict[str, Any] = super().get_component_info()
        class_doc = self.__class__.__doc__
        info.update({
            'output_spec_name': self.dynamic_output_spec_name(),
            'output_spec_description': self.dynamic_output_spec_description(),
            'output_spec_param_names': self.dynamic_output_spec_names(),
            'output_spec_param_types': self.dynamic_output_spec_types(),
            'output_spec_param_units': self.dynamic_output_spec_units(),
        })

        return info

    def _get_component_type(self) -> str:
        return "Dynamics"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_type={self.output_type.__name__}, initialized={self.is_initialized})"

    def __str__(self) -> str:
        return f"Dynamics Function: {self.__class__.__name__} (Output: {self.output_type.__name__})"