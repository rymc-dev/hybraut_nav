# !/usr/bin/env python
"""
and interface for hybraut_models.core wrapper classes for the
hybraut_aci ACI (Automaton Component Interface) type instances.
"""

from typing import Any, Type, Optional, Dict, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from builtin_interfaces.msg import Time
from hybraut_models.ctx.evaluation_context import EvaluationContext
from hybraut_aci.core.core_interface.hybrid_automaton_component_interface import (
    HybridComponentInterface,
)


@dataclass
class WrapperInterface(ABC):
    """
    wrapper interface for ACI (Automaton Component Interface) types instances.
    """

    name: str = field(init=True)
    component_class: Type[HybridComponentInterface]
    component_instance: Optional[HybridComponentInterface] = field(
        default=None, init=False
    )
    configuration: Optional[Dict[str, Any]] = field(init=True)

    cache_enabled: bool = field(default=True, init=True)
    cache_ttl: float = field(
        default=1.0, init=True
    )  # Time-to-live in seconds for caching evaluation results
    last_evaluation: Optional[Any] = field(default=None, init=False)
    last_evaluation_time: Optional[Time] = field(default=None, init=False)
    is_initialized: bool = field(default=False, init=False)

    def __post_init__(self):
        """
        Called automatically after dataclass initialization.
        Validates the component configuration against the expected constructor arguments.
        """

        expected_names: List[str] = self.component_class.get_init_input_spec_names()
        expected_types: List[Type] = self.component_class.get_init_input_spec_types()
        for config_name, expected_type in zip(expected_names, expected_types):
            if config_name not in self.configuration:
                raise ValueError(
                    f"Missing configuration for required argument '{config_name}' in component '{self.component_class.__name__}'."
                )
            if not isinstance(self.configuration[config_name], expected_type):
                raise TypeError(
                    f"Invalid type for configuration key '{config_name}': "
                    f"expected {expected_type.__name__}, got {type(self.configuration[config_name]).__name__}."
                )

        self.__post_init_hook__()

    def get_configuration_names(self) -> List[str]:
        return self.component_class.init_input_spec_names()

    def get_configuration_types(self) -> List[Type]:
        return self.component_class.init_input_spec_types()

    def get_state_input_names(self) -> List[str]:
        return self.component_class.state_input_spec_names()

    def get_state_input_types(self) -> List[Type]:
        return self.component_class.state_input_spec_types()

    def get_current_configuration(self) -> Dict[str, Any]:
        return self.configuration

    def update_configuration_value(
        self, configuration_name: str, configuration_value: Any
    ):
        if configuration_name not in self.configuration:
            return AttributeError("configuration_name is not in configuration")

        self.configuration[configuration_name] = configuration_value

    def __post_init_hook__(self):
        """
        Optional hook for subclasses to run additional validation or setup after post-init.
        """
        pass

    def __pre_evaluate_hook__(self, context: EvaluationContext):
        """
        Optional hook to validate the evaluation context before calling `evaluate`.
        Subclasses may override this to perform schema checks or consistency validation.
        """
        if not self.is_initialized:
            raise RuntimeError("Tried to evaluate but the component is not activated")

    def _is_cache_valid(self, context: EvaluationContext) -> bool:
        """
        Check if cached result is still valid based on TTL and context.
        """
        if not self.cache_enabled or self.last_evaluation_time is None:
            return False

        if context.stamp is None:
            return False

        # Simple TTL check - in real implementation you'd convert Time to seconds
        time_diff = context.stamp - self.last_evaluation_time
        return time_diff < self.cache_ttl

    @abstractmethod
    def _evaluate(self, context: EvaluationContext) -> Any:
        """
        Abstract method that must be implemented by subclasses to perform evaluation logic.
        """
        pass

    def __call__(self, context: EvaluationContext) -> Any:
        self.__pre_evaluate_hook__(context)

        # Check cache first
        if self._is_cache_valid(context):
            return self._last_evaluation

        # Perform evaluation
        result = self._evaluate(context)

        # Update cache
        if self.cache_enabled:
            self.last_evaluation = result
            self.last_evaluation_time = context.stamp

        return result

    def initialize(self):
        """
        Instantiates the component using the provided configuration dictionary.
        Sets the `` flag to True.
        """
        self.component_instance = self.component_class(**self.configuration)
        self.is_initialized = True

    def shutdown(self):
        """
        Deactivates the component and clears the instance.
        """
        self.component_instance = None
        self.is_initialized = False

    def clear_cache(self) -> None:
        """
        Clears the cached evaluation result.
        """
        self._last_evaluation = None
        self._last_evaluation_time = None
