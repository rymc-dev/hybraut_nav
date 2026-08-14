# TurtleBot3 COLREG Encounters Demo

Extends the [base TurtleBot3 demo](turtlebot3_demo.md), swapping
`fake_riskenv_publisher`'s fixed square for `colreg_encounter_publisher` - a
demo node that cycles the live agent through the classic COLREG encounter
geometries (head-on, crossing as give-way/stand-on vessel, overtaking in
both directions) against a virtual obstacle it simulates internally, and
drives the **real** `riskenv.create_unsafe_set()` off it every tick - so
what reaches `tactical_node` is a genuine, evolving unsafe set for each
encounter, not a synthetic polygon.

No Gazebo mover, bridges, or `/agent_state`/`/obstacles_state` source is
needed - the virtual obstacle is simulated inside the node itself, anchored
each time off the agent's live `/odom`. For a demo with real independently-
moving Gazebo obstacles instead (random walk, not COLREG-shaped), see
[turtlebot3_dynamic_obstacles_demo.md](turtlebot3_dynamic_obstacles_demo.md).

## The five encounters

Cycled in order (repeating), by default:

| `encounter_sequence` name | Situation | Rule |
|---|---|---|
| `head_on` | Obstacle spawns dead ahead on a reciprocal course, closing head-on. | 14 |
| `crossing_give_way` | Obstacle spawns on your starboard bow, closing - you are give-way. | 15 |
| `crossing_stand_on` | Obstacle spawns on your port bow, closing - you are stand-on. | 15 |
| `overtaking` | A slower obstacle spawns ahead on the same course - you close on it. | 13 |
| `being_overtaken` | A faster obstacle spawns astern on the same course - it closes on you. | 13 |

`head_on`/`crossing_*` obstacles re-aim at the agent's *live* position every
tick (a simple pursuit intercept), so the encounter still closes even if the
agent manoeuvres away. `overtaking`/`being_overtaken` obstacles hold the
course captured at the agent's pose when the encounter starts and close
purely on the speed differential, matching Rule 13's "same/nearly same
course" definition.

Pass a subset/reorder via `-p encounter_sequence:="['head_on', 'overtaking']"`
if you only want to demo specific ones.

## Running it

```bash
# terminal 1 - sim
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo empty_world.launch.py

# terminal 2 - tactical + immediate layers (TB3-scale params, see base demo)
source ~/ros2_ws/install/setup.bash
ros2 launch hybraut_nav hybraut_nav_tactical_immediate.launch.py
ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
    hybraut_interfaces/action/ExecuteMission \
    "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback

# terminal 3 - COLREG encounter cycle + real riskenv geometry
source ~/ros2_ws/install/setup.bash
ros2 run hybraut_nav colreg_encounter_publisher
```

Don't run `fake_riskenv_publisher` or `risk_envelope_node` alongside this -
all three publish `/hybraut_nav/riskenv` and would collide.

## Watching it work

```bash
ros2 topic echo /hybraut_nav/riskenv                       # real unsafe-set hull, per encounter
ros2 topic echo /hybraut_nav/tactical_node/automaton_state
tail -f ~/log_hybrid_automaton/temporal_automaton.log
```

In RViz (`hybraut_nav_tactical_immediate.launch.py` already opens one), add:
- `/hybraut_nav/riskenv_markers` (`MarkerArray`) - the filled + outlined
  unsafe-set hull, same style `risk_envelope_node` publishes.
- `/hybraut_nav/colreg_encounter_markers` (`MarkerArray`) - the virtual
  obstacle's body + heading arrow + a text label naming the active encounter
  (there's no real Gazebo model standing in for it, so this is the only way
  to see it move).

## Tuning for your room

Defaults are sized for a small TB3 room, not `colav_automaton`'s
vessel-scale defaults - same caveat as the base demo. Worth checking first:

- `initial_range` (default `3.0`m) - how far out obstacles spawn. Keep it
  well outside `dsf` (below) so the encounter doesn't trip
  `unsafe_conditions_guard` the instant it starts.
- `dsf` (default `2.5`m) / `time_of_interest` (default `15.0`s) - riskenv's
  proximity/TCPA thresholds, should roughly track `tactical_node`'s
  `safety_radius`.
- `agent_safety_radius` (default `0.5`) - keep in sync with
  `tactical_node`'s `safety_radius` param.
- `overtaking_slow_speed` / `overtaking_fast_speed` (default `0.12`/`0.45`
  m/s) - must sit below/above the agent's actual cruising speed respectively,
  or the overtake never closes.
- `engagement_duration` (default `40.0`s) - safety-net force-clear if
  `Fallback` is never observed (e.g. `tactical_node` not running).

## Gotchas

- **The obstacle is virtual - it won't appear as a Gazebo body.** Only
  `/hybraut_nav/colreg_encounter_markers` in RViz shows where it is; there's
  nothing to bump into in the sim itself.
- **`overtaking`/`being_overtaken` need the agent actually moving** (i.e. an
  `execute_mission` goal sent to `tactical_node`, which is what gets
  `immediate_node` commanding real motion) - the speed differential is what
  closes the gap, so a stationary agent never gets overtaken or catches up
  to anything.
- Same `use_sim_time`/duplicate-process gotchas as the
  [base demo](turtlebot3_demo.md#gotchas) apply here.
