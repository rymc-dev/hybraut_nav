# TurtleBot3 Gazebo Demo

Runs the tactical + immediate layers against a TurtleBot3 in Gazebo, using
`fake_riskenv_publisher` to stand in for `risk_envelope_node` (no
`/agent_state`/`/obstacles_state` source exists in a bare TB3 sim), so you can
watch the COLAV automaton's discrete-mode transitions
(`Transit` -> `Fallback` -> `Transit`) happen live.

For the same demo driven by real moving obstacles instead of a synthetic
polygon, see
[turtlebot3_dynamic_obstacles_demo.md](turtlebot3_dynamic_obstacles_demo.md).
For scripted COLREG encounters (head-on, crossing, overtaking) driving the
*real* `riskenv.create_unsafe_set()` geometry instead of a fixed square, see
[turtlebot3_colreg_encounters_demo.md](turtlebot3_colreg_encounters_demo.md).

## Prerequisites

- `ros-<distro>-turtlebot3*` installed (Gazebo world/model packages).
- `hybraut_nav` built per the main [README](../README.md#installation).

## 1. Sim

```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

(`turtlebot3_world.launch.py` also works, but the room is small relative to
`colav_automaton`'s vessel-scale defaults - see the params below.)

## 2. Tactical + immediate layers

`colav_automaton`'s `safety_radius`/`acceptance_radius`/`los_distance_threshold`/
`lateral_offset_distance`/`longitudinal_offset_distance` all default to
values sized for a vessel (metres in the tens to low hundreds), which
trivially intersect (or land absurdly far outside) a small Gazebo room.
`launch/hybraut_nav_tactical_immediate.launch.py` brings up `tactical_node`
+ `immediate_node` together (no `strategy_node`) with these overridden for
TB3 scale by default:

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch hybraut_nav hybraut_nav_tactical_immediate.launch.py
```

(Override further via e.g. `safety_radius:=0.5 acceptance_radius:=0.3
los_distance_threshold:=3.0 lateral_offset_distance:=1.0` launch arguments if
your world needs different values than the defaults.)

**`lateral_offset_distance` matters even if you don't touch the others.**
It's how far off to the side of the unsafe region
`generate_new_virtual_waypoint` places each COLAV detour waypoint (see
`/hybraut_nav/tactical_node/virtual_waypoint_markers` in RViz). Left at its
vessel-scale default (100.0), every detour lands ~100m away - unreachable in
a TB3 room - so the automaton just keeps stacking new detours on top each
time it re-enters `Transit`, and you'll never see `Waypoint_Reached` clear
them. This launch file already overrides it to `1.0`; if you run
`tactical_node`/`hybraut_nav.launch.py` standalone instead, pass
`lateral_offset_distance:=1.0` (or similar) explicitly.

Other available run configurations, if you don't need both layers together:

- `hybraut_nav_tactical.launch.py` - `tactical_node` alone.
- `hybraut_nav_strategic_tactical_immediate.launch.py` - adds `strategy_node`
  on top (global path planning, still no `risk_envelope_node`).
- `hybraut_nav.launch.py` - the full stack, `risk_envelope_node` included
  (the "risk assessment" configuration - see
  [turtlebot3_dynamic_obstacles_demo.md](turtlebot3_dynamic_obstacles_demo.md)
  for when to use the real risk layer instead of `fake_riskenv_publisher`
  below).

`tactical_node` has no lifecycle to configure/activate - it comes up ready.
In another terminal, once it's up, send it a waypoint directly via its
action server (no `strategy_node` running, so there's nobody else to do it
for you):

```bash
ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
    hybraut_nav/action/ExecuteMission \
    "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback
```

This blocks and streams feedback (discrete automaton state, time since its
last transition, live reference position) until the leg finishes; send the
next leg the same way once it returns `success: true`, e.g. back to
`(0, 0)`. Each waypoint is run as its own leg of the automaton;
`Waypoint_Reached` is terminal, so the action resolves once that leg's
target is reached (or cancel it early with `ros2 action cancel` /
Ctrl-C while it's streaming feedback).

For a real strategic-driven demo instead of the fixed 2-point route - where
you set one long-range goal and `strategy_node` plans + dispatches the
intermediate waypoints itself - see
[Strategic-driven demo](#strategic-driven-demo) below.

`immediate_node` needs no manual activation - its control loop always runs,
but it only commands real motion while `/hybraut_nav/continous_dynamics` is
actively being published to, which is exactly while a leg is executing.

## 3. Fake risk envelope

```bash
source ~/ros2_ws/install/setup.bash
ros2 run hybraut_nav fake_riskenv_publisher
```

Cycles: `cooldown_period` seconds with no unsafe region (a clean window to
observe `Transit`) -> places a small square unsafe-region
polygon `obstacle_offset` metres ahead of the agent's current heading ->
clears it as soon as `/hybraut_nav/tactical_node/automaton_state` reports
`Fallback` (or after `max_active_duration` seconds as a safety net) -> repeat.
Tune via `--ros-args -p obstacle_offset:=... -p obstacle_halfwidth:=...` if
the room is too small/large for the defaults.

## Strategic-driven demo

Instead of sending each leg's goal by hand (section 2), `strategy_node`
accepts a single long-range goal via its own `navigate_to_goal` action,
plans a global A* route to it, and dispatches the resulting waypoints to
`tactical_node`'s `execute_mission` action one at a time itself - streaming
back feedback that covers both the currently-active leg (relayed from
`tactical_node`) and mission-level progress (the planned waypoint list,
elapsed time, an ETA, and overall completion fraction).

Two live inputs `strategy_node` needs that a bare TB3 sim doesn't produce on
its own:

- **`/agent_state`** - `agent_state_bridge` (built for the
  [dynamic obstacles demo](turtlebot3_dynamic_obstacles_demo.md) but
  standalone/reusable here) republishes `/odom` as
  `hybraut_nav/msg/AgentState`.
- **`/map`** (`nav_msgs/OccupancyGrid`, transient-local) - `fake_map_publisher`
  publishes a single static, entirely free 20m x 20m grid centred on `(0, 0)`
  (tune via `--ros-args -p width:=... -p resolution:=... -p origin_x:=...`
  etc.). It's a flat stand-in for "having a costmap at all", not real
  occupancy data - point `nav2_map_server` at a real saved map instead if you
  need actual obstacles reflected in the plan.

```bash
# terminal 1 - sim
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo empty_world.launch.py

# terminal 2 - strategic + tactical + immediate (no risk_envelope_node)
source ~/ros2_ws/install/setup.bash
ros2 launch hybraut_nav hybraut_nav_strategic_tactical_immediate.launch.py \
    safety_radius:=0.5 acceptance_radius:=0.3 los_distance_threshold:=3.0

# terminal 3 - agent state + map
source ~/ros2_ws/install/setup.bash
ros2 run hybraut_nav agent_state_bridge &
ros2 run hybraut_nav fake_map_publisher

# terminal 4 - goal (immediate_node needs no manual activation anymore)
ros2 action send_goal /hybraut_nav/strategy_node/navigate_to_goal \
    hybraut_nav/action/NavigateToGoal \
    "{goal_waypoint: {position: {x: 3.0, y: 2.0}}}" --feedback
```

`strategy_node` will dispatch each downsampled waypoint to `tactical_node`
in turn as the previous one is reached, replanning in place if the agent
drifts too far off the stored route, until the goal is reached. Cancel a
mission early with `ros2 action cancel` (or Ctrl-C the send_goal call
above).

## Watching it work

```bash
# discrete-mode transitions, live
ros2 topic echo /hybraut_nav/tactical_node/automaton_state

# the reference dynamics immediate_node is tracking (theta = data[2])
ros2 topic echo /hybraut_nav/continous_dynamics --field data

# full transition history for the run, with the guard/edge name that fired
tail -f ~/log_hybrid_automaton/temporal_automaton.log

# strategic-driven demo only: the downsampled route, and (from a separate
# terminal, without having to be the one that sent the goal) mission-level
# feedback - waypoint list, progress, ETA, and the relayed leg status -
# streaming for whichever navigate_to_goal mission is currently in flight
ros2 topic echo /hybraut_nav/planner/plan
ros2 topic echo /hybraut_nav/strategy_node/navigate_to_goal/_action/feedback
```

## Gotchas

- **Restarting doesn't kill the old process.** `ros2 launch`/`ros2 run` block
  in their own terminal; Ctrl-C before relaunching. Two instances of the same
  node (e.g. two `immediate_node`s both racing to publish `/cmd_vel`) causes
  exactly the kind of erratic behaviour that's hard to diagnose after the
  fact - `ros2 node list` will warn about duplicate names if this happens.
- **No in-place sim reset.** There's no `ros2 service` exposed to reset the
  Gazebo world/robot pose - restart the whole `ros2 launch
  turtlebot3_gazebo ...` process for a clean baseline.
- **rviz shows nothing on `/cmd_vel` (or other TF-relative topics) even
  though the topic is clearly publishing.** `ros2 topic echo`/`hz` will look
  completely normal - the silent culprit is `use_sim_time`. If
  `immediate_node` stamps messages off the wall clock while
  `robot_state_publisher`/`ros_gz_bridge` stamp `/tf` off `/clock` (sim
  time), the two clocks diverge by however long the wall clock has been
  running (seconds vs. a multi-billion-second epoch) - rviz's TF-synced
  displays wait forever for a transform that will never match and never
  render, with no error printed anywhere. Fix: launch with
  `use_sim_time:=true` (not the default) any time Gazebo is running, e.g.:
  `ros2 launch hybraut_nav hybraut_nav_tactical_immediate.launch.py use_sim_time:=true`.
