# hybraut_nav

`hybraut_nav` is a ROS 2 (rclpy) navigation stack built around a **hybrid-automaton
tactical layer**. It is organised into four layered ROS packages plus a shared
support package, each mapping to one console script / node:

| Layer | Package | Node (`ros2 run hybraut_nav ...`) | Responsibility |
|---|---|---|---|
| 1 - Strategy | `hybraut_nav_strategy` | `strategy_node` | Global path planning (A*, Dijkstra, RRT, RRT*) over the static costmap. |
| 2 - Tactical | `hybraut_nav_tactical` | `tactical_node` | Runs a `colav_automaton.ColavAutomaton` (`hybrid_automaton.Automaton`) that reacts to odometry + the live risk envelope and republishes reference continuous dynamics. |
| 3 - Immediate | `hybraut_nav_immediate` | `immediate_node` | Guidance/control layer: tracks the tactical layer's desired heading and outputs `cmd_vel` (yaw rate + cruise velocity). |
| Risk | `hybraut_nav_risk` | `risk_envelope_node` | Fuses agent + obstacle state into a risk envelope (unsafe set) for the tactical layer's COLAV guards, via `riskenv`. |
| Shared | `hybraut_nav` | - | QoS profiles, node-state enum, and misc launch/CLI/demo scripts used across layers. |

`hybraut_nav_utils` provides small cross-package helpers (quaternion/heading
conversions, euclidean distance, dynamic class import, YAML loading).

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Topic contract](#topic-contract)
- [License](#license)

## Dependencies

Pre-requisites:
- Ubuntu with a ROS 2 distribution installed and sourced.
- Python 3 with `pip` available.

`hybraut_nav` depends on three sibling libraries published on PyPI:
- [`colav-automaton`](https://pypi.org/project/colav-automaton/) - the COLAV
  hybrid-automaton definition run by the tactical layer.
- [`hybrid-automaton`](https://pypi.org/project/hybrid-automaton/) - the
  generic hybrid-automaton runtime `colav-automaton` is built on.
- [`riskenv`](https://pypi.org/project/riskenv/) - risk-envelope (unsafe set)
  geometry used by the risk layer.

All three are pinned in [`requirements.txt`](./requirements.txt) alongside the
rest of the Python dependencies.

`hybraut_nav` also depends on two custom ROS 2 interface packages that are
**not** on PyPI/rosdep and must be built from source in the same workspace:
- `colav_interfaces`
- `hybraut_interfaces`

## Installation

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone <this repo> hybraut_nav

# custom interface packages (source dependencies, not on rosdep)
git clone https://github.com/Artemis-QUB-COLAV/colav-interfaces.git colav_interfaces
git clone <hybraut_interfaces repo> hybraut_interfaces

cd hybraut_nav && pip install -r requirements.txt

cd ~/ros2_ws && colcon build --packages-select \
    colav_interfaces hybraut_interfaces \
    hybraut_nav hybraut_nav_strategy hybraut_nav_tactical hybraut_nav_immediate hybraut_nav_risk

source install/setup.bash
```

## Usage

Launch the full stack:

```bash
ros2 launch hybraut_nav hybraut_nav.launch.py
```

This brings up `risk_envelope_node`, `strategy_node`, `immediate_node`, and
`tactical_node`. `tactical_node` is a lifecycle node and must be configured
and activated once its parameters are set:

```bash
ros2 lifecycle set /hybraut_nav/tactical_node configure
ros2 lifecycle set /hybraut_nav/tactical_node activate
```

Individual nodes can also be run standalone via `ros2 run hybraut_nav <node>`
(see the table above for the executable names).

## Topic contract

- `risk_envelope_node` subscribes to `/agent_state`
  (`colav_interfaces/AgentState`) and `/obstacles_state`
  (`colav_interfaces/ObstaclesState`), and publishes the computed risk
  envelope hull on `/hybraut_nav/riskenv` (`geometry_msgs/PolygonStamped`).
- `tactical_node` subscribes to `/odom` and `/hybraut_nav/riskenv`, and
  publishes the automaton's reference continuous state on
  `/hybraut_nav/continous_dynamics` (`std_msgs/Float64MultiArray`).
- `immediate_node` subscribes to `/odom` and
  `/hybraut_nav/continous_dynamics`, and publishes actuator commands on
  `/cmd_vel` (`geometry_msgs/TwistStamped`).

## License

`hybraut_nav` is distributed under the terms of the [MIT](./LICENSE) license.
