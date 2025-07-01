# Hybrid Automaton Guards

**Guards** are conditional functions that determine whether a transition from one mode to another should be executed in the hybrid automaton framework. Guard conditions evaluate to `True` if the transition should occur, or `False` if it should not.

---

## Overview

This module provides an abstract base class `Guard` that serves as the foundation for creating custom guard functions within the hybrid automaton framework. All guard implementations must inherit from this class and implement the required abstract methods.

---

## Architecture

The guard system follows a two-phase approach:

1. **Initialization Phase**: Static configuration and validation of parameters
2. **Execution Phase**: Runtime evaluation of guard conditions based on current system state

---

## Core Components

### Abstract Base Class: `Guard`

The `Guard` class defines the interface that all guard implementations must follow.

---

### Key Methods

#### `__init__(self, **init_kwargs)`

**Purpose**: Initialize the guard with static configuration parameters.

- **When Called**: Once during hybrid automaton configuration phase
- **Parameters**:
  - `**init_kwargs`: Keyword arguments for guard configuration (hyperparameters, thresholds, etc.)
- **Function**: Set up static parameters, constants, or pre-computed values that remain constant during execution
- **Validation**: Calls `_validate_initialization()` to ensure parameters are valid

---

#### `__call__(self, **state_kwargs) -> bool`

**Purpose**: Execute the guard condition evaluation.

- **When Called**: Every time the hybrid automaton evaluates this guard (typically on timer callbacks)
- **Parameters**:
  - `**state_kwargs`: Current system state inputs (e.g., `agent_state`, `waypoints_state`, `obstacles_state`)
- **Returns**:
  - `True`: Transition should be executed
  - `False`: Transition should not be executed
- **Validation**: Calls `_validate_states()` to ensure state inputs are valid

---

#### `_validate_initialization(self, **init_kwargs) -> None`

**Purpose**: Validate initialization parameters during setup.

- **Override**: Implement in subclasses for custom parameter validation
- **Responsibilities**:
  - Check if required parameters are provided
  - Validate parameter types and value ranges
  - Ensure parameter combinations are valid
- **Raises**: `ValueError`, `TypeError` for invalid parameters

---

#### `_validate_states(self, **state_kwargs) -> None`

**Purpose**: Validate state inputs before guard evaluation.

- **Override**: Implement in subclasses for custom state validation
- **Responsibilities**:
  - Verify required state objects are provided
  - Check state object types and validity
  - Ensure state compatibility for guard logic
- **Raises**: `ValueError`, `TypeError` for invalid states

---

## Helper Methods

### `get_guard_info(self) -> Dict[str, Any]`

Returns metadata about the guard including class name, module, initialization status, and description.

---

### `__repr__(self) -> str`

Returns a string representation showing the class name and initialization status.

---

### `__str__(self) -> str`

Returns a human-readable string with the guard function name.

---

## Implementation Example

```python
from .guard import Guard

class DistanceThresholdGuard(Guard):
    """Guard that activates when agent is within threshold distance of target."""

    def __init__(self, distance_threshold: float, **init_kwargs):
        self.distance_threshold = distance_threshold
        super().__init__(**init_kwargs)

    def _validate_initialization(self, **init_kwargs):
        if self.distance_threshold <= 0:
            raise ValueError("distance_threshold must be positive")
        if not isinstance(self.distance_threshold, (int, float)):
            raise TypeError("distance_threshold must be numeric")

    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)

        if 'agent_state' not in state_kwargs:
            raise KeyError("agent_state is required")
        if not isinstance(state_kwargs['agent_state'], AgentState):
            raise TypeError("agent_state must be AgentState type")

        if 'waypoints_state' not in state_kwargs:
            raise KeyError("waypoints_state is required")
        if not isinstance(state_kwargs['waypoints_state'], WaypointsState):
            raise TypeError("waypoints_state must be WaypointsState type")

    def __call__(self, **state_kwargs) -> bool:
        super().__call__(**state_kwargs)  # Validates initialization and states

        agent_pos = state_kwargs['agent_state'].position
        target_pos = state_kwargs['waypoints_state'].current_waypoint.position

        distance = calculate_distance(agent_pos, target_pos)
        return distance <= self.distance_threshold
```

## 4. Guard Logic

- Implement the core guard logic in `__call__()`
- Always return a boolean value
- Call `super().__call__(**state_kwargs)` first to ensure proper validation

---

## 5. Error Handling

Use appropriate exception types:

- `KeyError`: Missing required parameters or states
- `TypeError`: Wrong parameter or state types
- `ValueError`: Invalid parameter or state values
- `RuntimeError`: Execution errors (e.g., uninitialized guard)

---

## Integration with Hybrid Automaton

Guards are integrated into the hybrid automaton framework as follows:

1. **Configuration**: Guards are instantiated with their initialization parameters
2. **Registration**: Guards are registered with specific transitions
3. **Evaluation**: During execution, the automaton calls guards to evaluate transition conditions
4. **Decision**: Transitions occur only when their associated guards return `True`

---

## Best Practices

- **Stateless Design**: Guards should not maintain mutable state between calls
- **Fast Execution**: Guard evaluation should be computationally efficient
- **Clear Naming**: Use descriptive names that indicate the guard condition
- **Comprehensive Validation**: Validate both initialization and runtime inputs
- **Documentation**: Provide clear docstrings explaining the guard condition
- **Type Hints**: Use type annotations for better code clarity and IDE support
