# Hybrid Automaton Invariants

Invariants are conditional functions that determine whether the system may remain in its current mode within the hybrid automaton framework. An invariant evaluates to `True` to permit staying in the mode, or `False` to indicate a violation requiring a transition.

---

## 1. Overview

This module provides an abstract base class `Invariant` that serves as the foundation for creating custom invariant functions in the hybrid automaton framework. All invariants must inherit from this class and implement the required abstract methods.

---

## 2. Architecture

The invariant system follows a two-phase approach:

- **Initialization Phase**: Static configuration and validation of parameters
- **Execution Phase**: Runtime evaluation of invariants against the current state

---

## 3. Core Components

### Abstract Base Class: `Invariant`

The `Invariant` class defines the interface and lifecycle for all invariant implementations.

---

## 4. Key Methods

### `__init__(self, **init_kwargs)`

- **Purpose**: Set up static parameters, constants, or pre-computed values that remain constant during execution.
- **When Called**: Once during hybrid automaton configuration.
- **Parameters**:  
  `**init_kwargs`: Keyword arguments for invariant configuration.
- **Behavior**:
  - Initializes a ROS2 logger instance.
  - Sets `is_initialized = False`.
  - Calls `_validate_initialization()` for parameter validation.
  - Sets `is_initialized = True` upon successful validation.
- **Exceptions**:
  - `ValueError` or `TypeError` for invalid parameters.

---

### `__call__(self, **state_kwargs) -> bool`

- **Purpose**: Evaluate the invariant based on the current system state.
- **When Called**: At each automaton evaluation cycle while in the mode.
- **Parameters**:  
  `**state_kwargs`: State inputs (e.g., `agent_state`, `waypoints_state`, `obstacles_state`).
- **Behavior**:
  - Raises `RuntimeError` if called before initialization.
  - Calls `_validate_states()` to verify inputs.
  - Executes subclass-specific logic and returns `True` or `False`.
- **Returns**:
  - `True` if the invariant holds (staying in mode permitted).
  - `False` if the invariant is violated (transition required).
- **Exceptions**:
  - `RuntimeError`, `ValueError`, `TypeError`, `KeyError` for invalid usage or inputs.

---

### `_validate_initialization(self, **init_kwargs) -> None`

- **Purpose**: Validate static parameters at setup.
- **Override** in subclasses to implement custom validation.
- **Responsibilities**:
  - Check required parameters.
  - Validate types and value ranges.
  - Raise `ValueError`, `TypeError`, or `KeyError` as needed.

---

### `_validate_states(self, **state_kwargs) -> None`

- **Purpose**: Validate runtime state inputs.
- **Behavior**:
  - Checks `is_initialized`, raising `RuntimeError` if not.
  - (Subclasses) Verify presence and types of required state objects.
  - **Override** in subclasses, calling `super()._validate_states()` first.
- **Exceptions**:
  - `RuntimeError` for uninitialized invariant.
  - `ValueError`, `TypeError`, `KeyError` for invalid states.

---

## 5. Helper Methods

### `get_invariant_info(self) -> Dict[str, Any]`

- **Returns**: Metadata including class name, module path, initialization status, and a brief description.

### `__repr__(self) -> str`

- **Purpose**: String representation showing the class name and initialization flag.

### `__str__(self) -> str`

- **Purpose**: Human-readable description of the invariant function.

---

## 6. Implementation Example

```python
from .invariant import Invariant

class DistanceLimitInvariant(Invariant):
    """Invariant that holds while the agent stays within a maximum distance."""

    def __init__(self, max_distance: float, **init_kwargs):
        self.max_distance = max_distance
        super().__init__(**init_kwargs)

    def _validate_initialization(self, **init_kwargs):
        if not isinstance(self.max_distance, (int, float)):
            raise TypeError("max_distance must be numeric")
        if self.max_distance <= 0:
            raise ValueError("max_distance must be positive")

    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)
        if 'agent_state' not in state_kwargs:
            raise KeyError("agent_state is required")
        if not hasattr(state_kwargs['agent_state'], 'position'):
            raise TypeError("agent_state must have a position attribute")

    def __call__(self, **state_kwargs) -> bool:
        super().__call__(**state_kwargs)
        agent_pos = state_kwargs['agent_state'].position
        origin = (0, 0)
        distance = calculate_distance(agent_pos, origin)
        return distance <= self.max_distance
```

## 7. Invariant Logic

- Implement core logic in `__call__()` after calling `super()`.
- Always return a boolean indicating if staying in mode is allowed.

---

## 8. Error Handling

Use appropriate exceptions:

- `KeyError`: Missing required state inputs.
- `TypeError`: Invalid state or parameter types.
- `ValueError`: Invalid parameter values.
- `RuntimeError`: Invocation before initialization.

---

## 9. Integration with Hybrid Automaton

- **Configuration**: Instantiate invariants with parameters.
- **Registration**: Attach invariants to modes in the automaton.
- **Evaluation**: At each cycle, the automaton calls invariants.
- **Decision**: Modes persist only while their invariants return `True`.

---

## 10. Best Practices

- **Stateless**: Avoid mutable state between calls.
- **Efficiency**: Keep evaluation lightweight.
- **Clear Naming**: Reflect the invariant condition.
- **Comprehensive Validation**: Check both init and runtime inputs.
- **Documentation**: Provide docstrings explaining behavior.
- **Type Hints**: Use annotations for clarity and tooling support.
