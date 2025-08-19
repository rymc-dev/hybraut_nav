from abc import abstractmethod
from typing import Any, Dict, Type
from collections import deque
from .core_interface import (
    HybridComponentInterface,
)


class DynamicsInterface(HybridComponentInterface):
    """
    Dynamics interface for hybrid automaton components.

    Defines a contract for components that evolve state over time.
    """

    _dynamic_output_type: Type = None
    _component_type = "Dynamics"

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
        if self._dynamic_output_type is None:
            raise ValueError(
                f"{self.__class__.__name__} must define `_dynamic_output_type`"
            )

        self._output_type = self._dynamic_output_type
        super().__init__(**init_kwargs)

    def _post_init_hook(self) -> None:
        """
        Hook for subclasses to create state buffers after init.
        """
        self._state_buffer: Dict[str, deque] = {}
        for state_input in self._state_input_spec:
            self._state_buffer[state_input.name] = deque(maxlen=100)

    def _validate_output(self, output: Any):
        if not isinstance(output, self._output_type):
            raise TypeError(
                f"Output must be of type {self._output_type}, got {type(output).__name__}"
            )

    def _avg_dt_calc(self, current_dt: float, alpha: float = 0.1):
        """Exponential moving average for time delta smoothing."""
        self._avg_dt = alpha * current_dt + (1 - alpha) * self._avg_dt

    @abstractmethod
    def _evaluate(self, **state_kwargs):
        """this contains the implementation of the runtime dynamics evaluation"""
        pass

    def __call__(self, **state_kwargs) -> Any:
        """call function for dynamics, this will
        generate the dynamics evaluation output for this inerface,
        must return the spec type defined in classes dynamics_output_spec

        Returns:
            Any: _description_
        """
        return super().__call__(**state_kwargs)

    def _validate_evaluation_output(self, output):
        self._validate_output(output)

    @classmethod
    def dynamic_output_type(cls) -> str:
        return cls._dynamic_output_type if cls._dynamic_output_type else "Undefined"

    def get_component_info(self) -> Dict[str, Any]:
        """Return introspection information about this dynamics component."""
        info: Dict[str, Any] = super().get_component_info()
        class_doc = self.__class__.__doc__
        info.update(
            {
                "output_type": self.dynamic_output_type(),
            }
        )

        return info

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_type={self._output_type}, initialized={self.is_initialized})"

    def __str__(self) -> str:
        return f"Hybrid Automaton Dynamics: {self.__class__.__name__} (Output: {self._output_type.__name__})"
