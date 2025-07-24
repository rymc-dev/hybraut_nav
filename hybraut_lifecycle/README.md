# Hybrid Automaton Framework

## Overview

The **Hybrid Automaton Framework** is a **ROS2-based** implementation that provides a formal, configurable approach to autonomous system control using hybrid automaton theory. This framework enables seamless transitions between discrete modes while managing continuous dynamics, invariants, and guard conditions in real-time applications.

---

## Architecture

### Core Components

The framework is built around several key modules:

- **Automaton Node**: Central managed lifecycle node that orchestrates the entire system
- **Guard Module**: Evaluates transition conditions between modes
- **Dynamics Module**: Manages continuous control behavior within each mode
- **Invariants Module**: Monitors safety conditions and constraints
- **Resets Module**: Handles state resets during mode transitions
- **Configuration System**: YAML-based formal automaton model definitions

---

### Hybrid Automaton Lifecycle

The system follows a structured lifecycle management pattern:

<img src="./.github/assets/hybrid_automaton_lifecycle.png" alt="Hybrid Automaton Lifecycle" width="1000"/>

#### Lifecycle States

- **Unconfigured**: Initial state, no configuration loaded
- **Inactive**: Configuration loaded, waiting for activation parameters (goal waypoints)
- **Active**: Executing the hybrid automaton with real-time mode management
- **Finalized**: Clean shutdown and resource cleanup

---

### Implementation Details

#### `HybridAutomatonNode` Class

The main `HybridAutomatonNode` extends ROS2's `LifecycleNode` and provides:

##### Configuration Parameters

- `configuration_path`: Absolute path to the hybrid automaton YAML configuration
- `evaluation_frequency`: Frequency (Hz) for guard condition evaluation (max 100Hz)
- `control_frequency`: Frequency (Hz) for dynamics control feedback (max 100Hz)

##### Activation Parameters

- `waypoint_x`: Goal waypoint X position (meters)
- `waypoint_y`: Goal waypoint Y position (meters)
- `waypoint_acceptance_radius`: Waypoint acceptance radius (meters)

---

#### Multithreaded Architecture

The framework utilizes a multithreaded executor with `ReentrantCallbackGroup` to achieve near real-time performance:

```python
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
```

## Asynchronous Callbacks

Three main timer-based callbacks run concurrently:

- **Guard Evaluation Timer**: Evaluates transition conditions
- **Dynamics Timer**: Executes mode-specific control dynamics
- **Invariant Evaluation Timer**: Monitors safety constraints

---

## Thread Safety

The implementation includes comprehensive thread safety mechanisms:

- `transition_lock`: Protects mode transition operations
- `executing_mode_lock`: Guards active mode execution
- `mode_callback_lock`: Synchronizes mode change callbacks

Additional locks are used for evaluation timers and error handling.

---

## Configuration System

### YAML Configuration Structure

The hybrid automaton is defined through a structured YAML configuration file that specifies:

- **Modes**: Discrete control modes and their behaviors
- **States**: Continuous state variables and subscriptions
- **Transitions**: Conditions for switching between modes
- **Guards**: Boolean conditions that trigger transitions
- **Dynamics**: Control laws active within each mode
- **Invariants**: Safety conditions that must be maintained
- **Resets**: State resets that occur during transitions
- **Initial Mode**: The mode the hybrid automaton starts in

### Factory Pattern Implementation

The framework uses factory functions to create automaton components:

- `create_hybrid_automaton_config()`: Builds automaton structure from YAML
- `create_state_subscriptions()`: Sets up ROS2 state topic subscriptions
- `create_state_publishers()`: Configures state publishing mechanisms

---

# ROS2 Integration

## Topics

### Published Topics

- `/hybrid_automaton/mode`: Current active mode
- `/hybrid_automaton/status`: Automaton execution status
- `/hybrid_automaton/invariant`: Invariant evaluation results
- `/hybrid_automaton/dynamics`: Control dynamics output
- `/hybrid_automaton/guard_evaluations`: Guard condition evaluations
- `/hybrid_automaton/state/waypoints`: Current waypoint state

### Subscribed Topics

- `/hybrid_automaton/mode`: Mode change requests
- `/hybrid_automaton/guards_evaluation`: Guard evaluation results

## Services

- `/hybrid_automaton/change_state`: Lifecycle state transitions

## Message Types

The framework defines custom message interfaces, found in the `hybrid_automaton_interfaces` package:

- **HybridAutomatonMode**: Mode information
- **HybridAutomatonStatus**: System status
- **HybridAutomatonDynamics**: Control dynamics
- **HybridAutomatonGuardEvaluations**: Guard condition results
- **HybridAutomatonInvariant**: Invariant evaluations

---

# Usage

## Basic Launch Sequence

1. **Configuration Phase**: Load YAML configuration file

```bash
    ros2 param set /hybrid_automaton configuration_path "./absolute/path/to/formal_automaton_config.yml"
    ros2 param set /hybrid_automaton evaluation_frequency 100
    ros2 param set /hybrid_automaton control_frequency 100
    ros2 lifecycle set /hybrid_automaton configure
```

2. **Activation Phase**: Set goal waypoint and activate

```bash
    ros2 param set /hybrid_automaton waypoint_x 10.0
    ros2 param set /hybrid_automaton waypoint_y 5.0
    ros2 param set /hybrid_automaton waypoint_acceptance_radius 2.0
    ros2 lifecycle set /hybrid_automaton activate
```

3. **Execution**: This automaton begins executing with the specified configuration. When it completes, it will automatonically mode to inactive lifecycle state

# Example Configuration

```yaml
# ============================================================================
# Simplified Hybrid Automaton Configuration Example
# ============================================================================
# A basic example showing the core structure of a hybrid automaton for
# autonomous navigation with obstacle avoidance.

# ============================================================================
# Continuous States - Data inputs from sensors/system
# ============================================================================
states:
  robot_pose:
    topic: "/robot/pose"
    type:
      pkg: "geometry_msgs.msg"
      msg: "PoseStamped"
    params:
      - update_hz: 10.0
      - timeout_sec: 0.5

  obstacles:
    topic: "/obstacles"
    type:
      pkg: "sensor_msgs.msg"
      msg: "LaserScan"
    params:
      - update_hz: 5.0
      - timeout_sec: 1.0

  goal_waypoint:
    topic: "/goal"
    type:
      pkg: "geometry_msgs.msg"
      msg: "PoseStamped"

# ============================================================================
# Guard Conditions - Boolean checks for transitions
# ============================================================================
guards:
  obstacle_detected:
    module: my_automaton.guards
    function: check_obstacle_distance
    state_inputs:
      - "robot_pose"
      - "obstacles"

  path_clear:
    module: my_automaton.guards
    function: check_path_clear
    state_inputs:
      - "robot_pose"
      - "obstacles"
      - "goal_waypoint"

  goal_reached:
    module: my_automaton.guards
    function: check_goal_reached
    state_inputs:
      - "robot_pose"
      - "goal_waypoint"

# ============================================================================
# Reset Functions - State modifications during transitions
# ============================================================================
resets:
  calculate_avoidance_path:
    module: my_automaton.resets
    function: compute_avoidance_waypoint
    state_inputs:
      - "robot_pose"
      - "obstacles"
    state_outputs:
      - "goal_waypoint"

# ============================================================================
# Invariants - Safety conditions that must be maintained
# ============================================================================
invariants:
  safety_check:
    module: my_automaton.invariants
    function: maintain_safe_distance
    state_inputs:
      - "robot_pose"
      - "obstacles"

  always_true:
    module: my_automaton.invariants
    function: trivial_invariant

# ============================================================================
# Dynamics - Control laws for each mode
# ============================================================================
dynamics:
  navigate_controller:
    module: my_automaton.controllers
    class: SimpleNavigationController
    init_args:
      max_speed: 1.0
      goal_tolerance: 0.5
    state_inputs:
      - "robot_pose"
      - "goal_waypoint"
    output:
      linear_velocity: "m/s"
      angular_velocity: "rad/s"

  avoidance_controller:
    module: my_automaton.controllers
    class: ObstacleAvoidanceController
    init_args:
      max_speed: 0.5
      safety_distance: 1.0
    state_inputs:
      - "robot_pose"
      - "obstacles"
      - "goal_waypoint"
    output:
      linear_velocity: "m/s"
      angular_velocity: "rad/s"

  stop_controller:
    module: my_automaton.controllers
    class: StopController
    output:
      linear_velocity: "m/s"
      angular_velocity: "rad/s"

# ============================================================================
# Transitions - How to move between modes
# ============================================================================
transitions:
  navigate_to_avoid:
    guard: "obstacle_detected"
    reset: "calculate_avoidance_path"

  avoid_to_navigate:
    guard: "path_clear"
    reset: null

  navigate_to_goal:
    guard: "goal_reached"
    reset: null

  avoid_to_goal:
    guard: "goal_reached"
    reset: null

# ============================================================================
# Modes - Discrete behavioral states
# ============================================================================
modes:
  navigate:
    index: 0
    dynamics: "navigate_controller"
    invariants: "safety_check"
    transitions:
      navigate_to_avoid:
        priority: 0
      navigate_to_goal:
        priority: 1

  obstacle_avoidance:
    index: 1
    dynamics: "avoidance_controller"
    invariants: "safety_check"
    transitions:
      avoid_to_navigate:
        priority: 0
      avoid_to_goal:
        priority: 1

  goal_reached:
    index: 2
    dynamics: "stop_controller"
    invariants: "always_true"
    transitions: []

# ============================================================================
# Initial Configuration
# ============================================================================
initial_mode: "navigate"

goal_modes:
  - "goal_reached"

# ============================================================================
# Runtime Parameters
# ============================================================================
parameters:
  target_goal:
    type:
      pkg: "geometry_msgs.msg"
      msg: "PoseStamped"

  evaluation_frequency:
    type: float
    default: 10.0

  control_frequency:
    type: float
    default: 20.0
```

# Performance Characteristics

## Real-Time Capabilities

- Configurable evaluation frequencies up to 100Hz
- Multithreaded execution for parallel processing
- Lock-based synchronization for thread safety
- Asynchronous callback architecture

## Resource Management

- Automatic cleanup during lifecycle transitions
- Memory-efficient state management
- CPU core utilization through multithreading

---

# Safety Features

## Invariant Monitoring

- Continuous safety condition evaluation
- Automatic violation detection and response
- Timeout-based safety guards

## Error Handling

- Comprehensive exception handling in lifecycle transitions
- Graceful degradation on configuration errors
- Safe shutdown procedures

---

# Dependencies

## ROS2 Dependencies

- `rclpy`: Python ROS2 client library
- `lifecycle_msgs`: Lifecycle management messages
- `std_msgs`: Standard ROS2 message types
- `geometry_msgs`: Geometric message types

## Custom Dependencies

- `hybrid_automaton_interfaces`: Custom message definitions
- `colav_interfaces`: Collision avoidance interfaces
- `colav_hybrid_automaton`: Framework core modules

---

# Development Notes

## Extension Points

The framework is designed for extensibility through:

- Custom guard condition implementations
- Pluggable dynamics controllers
- Configurable invariant monitors
- Custom state subscription handlers

## Known Limitations

- Maximum evaluation frequency limited to 100Hz
- Single goal waypoint support in current implementation
- Configuration requires system restart for major changes

## Future Enhancements

- Multi-waypoint trajectory support
- Dynamic reconfiguration capabilities
- Enhanced debugging and visualization tools
- Performance profiling and optimization
- Formal verification integration

---

# COLAV FAMD

in the current implementation we have implemented a famd for utilization for colav.

<img src="./_internal/.github/assets/diagrams/colav_hybrid_automaton.famd.png" alt="colav Hybrid automaton famd state diagram" width="1000"/>

# Contributing

When extending the framework, ensure:

- Thread safety for all shared resources
- Proper lifecycle management compliance
- Comprehensive error handling
- Configuration validation
- Documentation updates

---

# License

**TODO**: No License yet
