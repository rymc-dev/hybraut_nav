# TurtleBot3 + Dynamic Obstacles Demo

Extends the [base TurtleBot3 demo](turtlebot3_demo.md) with 2-3 independently
moving "mover" obstacles in Gazebo, bridged into real
`colav_interfaces/AgentState`/`ObstaclesState` messages, so the **real**
`risk_envelope_node` (not `fake_riskenv_publisher`'s synthetic polygon) drives
`tactical_node`'s discrete-mode transitions off `riskenv.create_unsafe_set()`
computed from genuine obstacle motion.

## What's involved

- `worlds/models/simple_mover/model.sdf` - a template SDF for a plain box
  body driven by gz-sim's `VelocityControl`/`OdometryPublisher` systems (no
  wheel joints needed - direct velocity actuation). Rendered per-instance
  with a unique name and absolute gz topics (`/model/<name>/cmd_vel`,
  `/model/<name>/odometry`) - relative topic names do **not** auto-namespace
  by model in gz-sim, verified empirically; every mover would otherwise
  collide on one global `/cmd_vel`/`/odometry`.
- `mover_random_walk` - one instance per mover, picks a new random forward
  speed + turn rate every few seconds and publishes it once (gz-sim's
  `VelocityControl` holds the last command indefinitely, no watchdog).
- `agent_state_bridge` - republishes the ego robot's `/odom` as
  `colav_interfaces/AgentState` on `/agent_state`.
- `obstacles_state_bridge` - aggregates all movers' odometry into
  `colav_interfaces/ObstaclesState` on `/obstacles_state`
  (`static_obstacles` is left empty - only the dynamic movers are modelled).
- `launch/hybraut_nav_dynamic_obstacles.launch.py` - spawns the movers,
  bridges their gz topics, and brings up the two bridge nodes above plus the
  real `risk_envelope_node`.

## Running it

```bash
# terminal 1 - sim
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo empty_world.launch.py

# terminal 2 - movers + real risk pipeline
source ~/ros2_ws/install/setup.bash
ros2 launch hybraut_nav hybraut_nav_dynamic_obstacles.launch.py
# override obstacle count: HYBRAUT_NAV_NUM_MOVERS=2 ros2 launch ...

# terminal 3 - tactical + immediate layers (note use_sim_time - see Gotchas)
source ~/ros2_ws/install/setup.bash
ros2 launch hybraut_nav hybraut_nav_tactical_immediate.launch.py \
    use_sim_time:=true safety_radius:=1.5 acceptance_radius:=0.3 \
    los_distance_threshold:=5.0
ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
    hybraut_interfaces/action/ExecuteMission \
    "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback
```

`hybraut_nav_tactical_immediate.launch.py` is one of several run
configurations under `launch/` - `hybraut_nav_tactical.launch.py` (tactical
alone), `hybraut_nav_strategic_tactical_immediate.launch.py` (adds
`strategy_node`, still no `risk_envelope_node`), and `hybraut_nav.launch.py`
(the full stack, `risk_envelope_node` included - the "risk assessment"
configuration). Don't use the full-stack `hybraut_nav.launch.py` here
though: `hybraut_nav_dynamic_obstacles.launch.py` above already starts its
own `risk_envelope_node`, and a second one would collide (duplicate node
name, both publishing `/hybraut_nav/riskenv`) - same reason not to also run
`fake_riskenv_publisher` alongside this demo.

`safety_radius` is larger here (`1.5`) than in the base demo (`0.5`) since
movers spawn ~2.5m out on a random walk - tune `SPAWN_RADIUS` in the launch
file or `safety_radius` to taste.

## Watching it work

```bash
ros2 topic echo /hybraut_nav/riskenv          # real unsafe-region hull, from riskenv.create_unsafe_set()
ros2 topic echo /hybraut_nav/tactical_node/automaton_state
tail -f ~/log_hybrid_automaton/temporal_automaton.log
```

## Gotchas

- **`use_sim_time` is not optional here.** `risk_envelope_node`'s
  `ApproximateTimeSynchronizer` matches `/agent_state` <-> `/obstacles_state`
  by `header.stamp`. If any node in the chain stamps off the wall clock
  instead of `/clock` (sim time), its stream drifts arbitrarily far from the
  others' and never synchronises - `risk_envelope_node` will sit there
  warning "No synchronised agent/obstacles update received" forever, with
  `/hybraut_nav/riskenv` never actually publishing. `mover_random_walk`,
  `agent_state_bridge`, `obstacles_state_bridge`, and `risk_envelope_node`
  are all launched with `use_sim_time:=true` already in
  `hybraut_nav_dynamic_obstacles.launch.py` - remember to pass
  `use_sim_time:=true` to `hybraut_nav_tactical_immediate.launch.py` too (as
  above), it doesn't default to true.
- **Even with matching clocks, expect a real gap between streams.**
  `agent_state_bridge` stamps from the ego `/odom` sample time;
  `obstacles_state_bridge` stamps at its own publish tick - two
  independently-timed pipelines rarely land within
  `risk_envelope_node`'s default `dt_global_update_tolerance` (`0.5`s). The
  launch file overrides it to `2.0`; tighten it once you've confirmed your
  machine's actual gap is smaller (`ros2 topic echo ... --field header.stamp`
  on both topics side by side).
- **Gazebo may run well below real-time** with three extra physics bodies in
  play, especially with the GUI client open - if `/clock` is advancing
  noticeably slower than wall time, all the `use_sim_time` watchdog/timeout
  thresholds above effectively take proportionally longer in real time to
  fire. Not a bug, just slower to observe.
