# Hybrid Automaton Dynamics

**Dynamics** are functions that define the continuous evolution of the system state within a given mode in a hybrid automaton. They compute outputs—typically state derivatives or control signals—based on the current state and input.

---

## Overview

This module provides an abstract base class `Dynamics` that serves as the foundation for creating custom dynamics functions in the hybrid automaton framework. All dynamics implementations must inherit from this class and implement the required abstract methods.

---

## Architecture

`Dynamics` follow a two-phase design pattern:

1. **Initialization Phase**  
   Configure static parameters and validate `output_type` and any hyperparameters.

2. **Execution Phase**  
   Validate runtime state inputs and compute the dynamics output.

This separation ensures configuration errors are caught early and runtime evaluation is efficient.

---

## Core Components

```python
# Abstract Base Class: Dynamics


from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from collections import namedtuple
from rclpy.logging import get_logger

class Dynamics(ABC):
def **init**(self, output_type: Type[namedtuple], \*\*init_kwargs):
"""
Initialize the dynamics with the required output structure.

        Args:
            output_type: A namedtuple class defining the expected output fields.
            **init_kwargs: Additional static configuration parameters.
        """
        self.logger = get_logger(self.__class__.__name__)

        # Validate output_type
        if not isinstance(output_type, type) or not hasattr(output_type, '_fields'):
            raise TypeError("output_type must be a namedtuple type")

        self.output_type = output_type
        self.is_initialized = False

        # Static configuration validation
        self._validate_initialization(**init_kwargs)
        self.is_initialized = True

    @abstractmethod
    def __call__(self, **state_kwargs) -> Any:
        """
        Compute the dynamics output based on current state inputs.

        Args:
            **state_kwargs: Keyword arguments for state inputs (e.g., sensor readings).

        Returns:
            An instance of `self.output_type` containing dynamics outputs.

        Raises:
            RuntimeError: If called before initialization.
            TypeError / ValueError: If state inputs are invalid.
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")

        self._validate_states(**state_kwargs)
        # Subclass implementation returns self.output_type(...)

    def _validate_initialization(self, **init_kwargs) -> None:
        """
        Validate static parameters during setup.

        Override in subclasses to enforce custom constraints.
        """
        pass

    def _validate_states(self, **state_kwargs) -> None:
        """
        Validate state inputs before computation.

        Override in subclasses to enforce required inputs and types.
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} is not initialized")

    def get_dynamics_info(self) -> Dict[str, Any]:
        """
        Return metadata about the dynamics function.

        Includes class name, module, init status, and output_type.
        """
```

## Key Methods

### `__init__(self, output_type: Type[namedtuple], **init_kwargs)`

- Validates `output_type` and static parameters.
- Sets `is_initialized = True` after successful validation.

---

### `__call__(self, **state_kwargs) -> Any`

- Checks initialization status.
- Validates runtime state inputs via `_validate_states`.
- Returns an instance of `output_type` representing computed dynamics.

---

### `_validate_initialization(self, **init_kwargs)`

- Hook for subclasses to enforce specific parameter checks.
- Should raise `TypeError` or `ValueError` on invalid input.

---

### `_validate_states(self, **state_kwargs)`

- Hook for subclasses to enforce required state inputs and types.
- Should raise `KeyError`, `TypeError`, or `ValueError` as appropriate.

---

### `get_dynamics_info(self) -> Dict[str, Any>`

- Returns introspection data (`class name`, `module`, `init status`, `output type`).

---

### `__repr__ / __str__`

- Provide consistent, informative string representations.

---

## Implementation Example

```python

    from collections import namedtuple
    from .dynamics import Dynamics

    # Define the expected output structure

    MotionOutput = namedtuple('MotionOutput', ['velocity', 'acceleration'])

    class SimpleLinearDynamics(Dynamics):
    """Linear dynamics: velocity = gain \* input_signal"""

        def __init__(self, gain: float, **init_kwargs):
            self.gain = gain
            super().__init__(output_type=MotionOutput, **init_kwargs)

        def _validate_initialization(self, **init_kwargs):
            if not isinstance(self.gain, (int, float)):
                raise TypeError("gain must be numeric")
            if self.gain < 0:
                raise ValueError("gain must be non-negative")

        def _validate_states(self, **state_kwargs):
            if 'input_signal' not in state_kwargs:
                raise KeyError("input_signal is required for dynamics computation")
            if not isinstance(state_kwargs['input_signal'], (int, float)):
                raise TypeError("input_signal must be numeric")

        def __call__(self, **state_kwargs):
            super().__call__(**state_kwargs)
            u = state_kwargs['input_signal']
            velocity = self.gain * u
            acceleration = 0.0
            return self.output_type(velocity=velocity, acceleration=acceleration)
```

## Dynamics Logic

- Implement core computation in `__call__`.
- Always invoke `super().__call__(**state_kwargs)` first for consistent validation.
- Return a fully populated instance of the provided `output_type`.

---

## Error Handling

Use clear exception types:

- **`TypeError`**: Invalid types for parameters or state inputs.
- **`ValueError`**: Invalid parameter values or configuration.
- **`KeyError`**: Missing required state inputs.
- **`RuntimeError`**: Invoking `__call__` before initialization.

---

## Integration with Hybrid Automaton

- **Configuration**: Instantiate dynamics with `output_type` and static parameters.
- **Registration**: Attach dynamics functions to specific modes.
- **Execution**: On each integration step, call dynamics with current state inputs to compute outputs.

---

## Best Practices

- **Stateless Functions**: Avoid side-effects and mutable state.
- **Efficient Execution**: Optimize for real-time performance.
- **Robust Validation**: Validate both initialization and runtime inputs rigorously.
- **Clear Naming**: Class and method names should reflect the dynamics behavior.
- **Comprehensive Documentation**: Provide docstrings and examples.
- **Type Annotations**: Use type hints for clarity and IDE support.
