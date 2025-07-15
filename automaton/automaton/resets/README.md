# Hybrid Automaton Resets

Resets are update functions that modify state variables when a transition from one mode to another occurs in the hybrid automaton framework. Reset functions compute new values for specified target objects based on the current system state during mode transitions.

---

## Overview

This module provides an abstract base class `Reset` that serves as the foundation for creating custom reset functions within the hybrid automaton framework. All reset implementations must inherit from this class and implement the required abstract methods.

---

## Architecture

The reset system follows a two-phase approach:

1. **Initialization Phase**

   - Static configuration and validation of parameters
   - Definition of target objects to be updated

2. **Execution Phase**
   - Runtime computation of new state values during mode transitions

---

## Core Components

### Abstract Base Class: `Reset`

The `Reset` class defines the interface that all reset implementations must follow.

---

### Key Methods

#### `__init__(self, reset_targets: List[Dict[str, Any]], **init_kwargs)`

- **Purpose:** Initialize the reset function with target objects and static configuration parameters.
- **When Called:** Once during hybrid automaton configuration phase

**Parameters:**

- `reset_targets`: List of dictionaries defining objects to be reset. Each dictionary must contain:

  - `'name'`: `str` — The name/key of the object to update
  - `'type'`: `type` — The expected type of the object
  - `'description'`: `str` _(optional)_ — Description of the object

- `**init_kwargs`: Additional keyword arguments for reset configuration (e.g., hyperparameters, constants)

**Function:**  
Sets up target objects and stores static configuration.

**Validation:**  
Calls `_validate_initialization()` to ensure targets and parameters are valid.

---

#### `__call__(self, **state_kwargs) -> Dict[str, Any]`

- **Purpose:** Execute the reset function to compute new state values
- **When Called:** During hybrid automaton mode transitions

**Parameters:**

- `**state_kwargs`: Current system state inputs (e.g., `agent_state`, `waypoints_state`, `obstacles_state`)

**Returns:**

- `Dict[str, Any]`: Dictionary mapping target object names to new values
  - Keys must match the `'name'` fields from `reset_targets`
  - Values must match the expected types from `reset_targets`

**Validation:**  
Calls `_validate_states()` before computation

---

#### `_validate_initialization(self, reset_targets: List[Dict[str, Any]], **init_kwargs) -> None`

- **Purpose:** Validate initialization parameters and reset targets
- **Override:** Subclasses must override to implement custom validation (call `super()` first)

**Responsibilities:**

- Check required parameters
- Validate parameter types and ranges
- Validate `reset_targets` structure and content

**Default Behavior:**

- Ensures `reset_targets` is a non-empty list
- Checks each target has `'name'` and `'type'`
- Validates `'name'` is a string

**Raises:** `ValueError`, `TypeError`, `KeyError` on invalid config

---

#### `_validate_states(self, **state_kwargs) -> None`

- **Purpose:** Validate state inputs before computing reset
- **Override:** Subclasses should call `super()` before custom logic

**Responsibilities:**

- Ensure required states are present
- Validate types and values
- Ensure compatibility of states for the reset

**Raises:** `ValueError`, `TypeError`, `KeyError` on invalid state inputs

---

#### `_validate_reset_output(self, reset_output: Dict[str, Any]) -> None`

- **Purpose:** Validate the computed output against reset target specs
- **When Called:** After reset function returns a result

**Responsibilities:**

- Ensures output is a dictionary
- Checks required keys match the target names
- Validates output types match declared target types
- Warns if unexpected keys are present

**Raises:** `ValueError`, `TypeError`, `KeyError` for invalid outputs

---

## Helper Methods

### `get_reset_info(self) -> Dict[str, Any]`

Returns metadata about the reset function:

- Class name
- Module name
- Initialization status
- Target object definitions
- Optional description

---

### `__repr__(self) -> str`

Returns a string representation showing:

- Class name
- Initialization status
- Target names

---

### `__str__(self) -> str`

Returns a human-readable description of:

- Reset function name
- Target count

---

## Implementation Example

```python
from .reset import Reset

class WaypointProgressReset(Reset):
    """Reset that updates waypoint progress when transitioning to next waypoint."""

    def __init__(self, increment_step: int = 1, **init_kwargs):
        # Define what objects this reset will update
        reset_targets = [
            {'name': 'current_waypoint_index', 'type': int, 'description': 'Index of current waypoint'},
            {'name': 'waypoint_position', 'type': tuple, 'description': 'Position of current waypoint'},
            {'name': 'progress_percentage', 'type': float, 'description': 'Progress through waypoint sequence'}
        ]

        self.increment_step = increment_step
        super().__init__(reset_targets=reset_targets, **init_kwargs)

    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)

        if self.increment_step <= 0:
            raise ValueError("increment_step must be positive")
        if not isinstance(self.increment_step, int):
            raise TypeError("increment_step must be an integer")

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

    def __call__(self, **state_kwargs) -> Dict[str, Any]:
        super().__call__(**state_kwargs)  # Validates initialization and states

        waypoints_state = state_kwargs['waypoints_state']
        current_index = waypoints_state.current_waypoint_index
        waypoints_list = waypoints_state.waypoints

        # Calculate new values
        new_index = min(current_index + self.increment_step, len(waypoints_list) - 1)
        new_position = waypoints_list[new_index].position
        new_progress = (new_index / (len(waypoints_list) - 1)) * 100.0

        # Return updated values for target objects
        return {
            'current_waypoint_index': new_index,
            'waypoint_position': new_position,
            'progress_percentage': new_progress
        }
```

## Implementation Guidelines

### 1. Target Definition

Define clear reset targets in `__init__()`:

- Each target should specify:
  - `'name'`: Unique identifier for the state variable to reset
  - `'type'`: Expected Python type of the reset output
  - `'description'` _(optional)_: Explanation of the target’s role
- Example:

```python
reset_targets = [
    {"name": "agent_state", "type": AgentState, "description": "Updated agent state after reset"},
    {"name": "waypoints_state", "type": WaypointsState}
]
super().__init__(reset_targets=reset_targets)
```

## 2. Parameter Validation

Override `_validate_initialization()` for custom parameter validation:

- Check required parameters are provided
- Validate data types and ranges
- Ensure `reset_targets` list is well-formed
- Always call `super()._validate_initialization()` first

```python
def _validate_initialization(self, **init_kwargs):
    super()._validate_initialization(**init_kwargs)
    # Custom validation logic here
```

## 3. State Validation

Override `_validate_states()` for custom input validation:

- Ensure required state inputs are present
- Validate types and logical correctness
- Always call `super()._validate_states()` first

```python
def _validate_states(self, **state_kwargs):
    super()._validate_states(**state_kwargs)
    # Custom state validation logic here
```

## 4. Reset Logic

Implement the core reset logic in **`__call__()`**:

- Compute new state values based on inputs
- Always call `super().__call__(**state_kwargs)` first to trigger validation
- Return a dictionary mapping target names to new values
- Ensure all returned values match the types defined in `reset_targets`

## Example: Error Handling

Use appropriate exception types to ensure meaningful error reporting:

- `KeyError`: Missing required parameters, states, or output keys
- `TypeError`: Incorrect parameter, state, or output value types
- `ValueError`: Invalid values or configurations
- `RuntimeError`: Execution errors (e.g., if reset is called before initialization)

## Integration with Hybrid Automaton

Resets are integrated into the hybrid automaton workflow as follows:

- **Configuration**:  
  Resets are instantiated with their target definitions and any static configuration parameters.

- **Registration**:  
  Resets are linked to specific transitions between modes.

- **Execution**:  
  During a mode transition, the reset function is called to compute the new state values.

- **State Update**:  
  The output dictionary is used to update the system's state objects accordingly.

## Best Practices

- ✅ **Clear Target Definition**: Use descriptive names and explicit types
- ✅ **Stateless Design**: Do not retain mutable state across invocations
- ✅ **Deterministic Output**: Same input → same output
- ✅ **Fast Execution**: Minimize computation time to avoid blocking transitions
- ✅ **Complete Output**: Always return all defined targets
- ✅ **Type Safety**: Match returned values to declared types
- ✅ **Clear Naming**: Use meaningful names for classes and targets
- ✅ **Comprehensive Validation**: Validate parameters, states, and outputs
- ✅ **Documentation**: Use docstrings to explain purpose and behavior
- ✅ **Type Hints**: Use Python typing for clarity and IDE support

## Output Validation

The reset system includes built-in output validation via `_validate_reset_output()`:

- ✅ Ensures output is a dictionary
- ✅ Verifies all expected target names are present
- ✅ Validates that returned types match target specifications
- ⚠️ Warns if unexpected keys are returned

This method can be called explicitly during development or testing to ensure reset outputs conform to expectations.
