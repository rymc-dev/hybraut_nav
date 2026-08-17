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
`spawn_offset_distance` ahead of the agent's *start* pose (captured off the
first `/odom` message) - a fixed point, not wherever the agent currently is,
so every encounter stays staged in the same spot for the whole demo. The
node also runs its own `ExecuteMission` action client and auto-sends one
mission goal waypoint behind that anchor, so the agent drives through the
staged encounter zone on its own - no manual `execute_mission` goal needed.
For a demo with real independently-moving Gazebo obstacles instead (random
walk, not COLREG-shaped), see
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

Every obstacle holds the straight-line course/speed computed once when the
encounter starts - it never re-aims at the agent's live position, so the
encounter is a genuine fixed geometry the agent has to navigate around
(rather than an obstacle that chases wherever the agent manoeuvres to).
`overtaking`/`being_overtaken` close purely on the speed differential,
matching Rule 13's "same/nearly same course" definition.

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

# terminal 3 - COLREG encounter cycle + real riskenv geometry
source ~/ros2_ws/install/setup.bash
ros2 run hybraut_nav colreg_encounter_publisher
```

`colreg_encounter_publisher` auto-sends its own `execute_mission` goal to
`tactical_node` once terminal 2's action server is up - no manual
`ros2 action send_goal` needed. Pass `-p send_goal_waypoint:=false` on
terminal 3 to disable that and drive the agent yourself instead, e.g.:
```bash
ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
    hybraut_nav/action/ExecuteMission \
    "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback
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

- `initial_range` (default `3.0`m) - how far out obstacles spawn from the
  anchor. Keep it well outside `dsf` (below) so the encounter doesn't trip
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
- `spawn_offset_distance` (default `2.0`m) - how far ahead of the agent's
  start pose every encounter is anchored.
- `goal_behind_distance` (default `6.0`m) - how far past the anchor
  (`spawn_offset_distance` further along the start heading) the auto-sent
  goal waypoint sits. Must clear the farthest obstacle spawn - by default
  that's `overtaking`'s, `initial_range * overtaking_range_scale` past the
  anchor - with headroom, or the agent stops short of it. Increase it if you
  raise `initial_range`/`overtaking_range_scale`.
- `send_goal_waypoint` (default `true`) - set `false` to skip the auto-sent
  goal and drive the agent yourself instead.

## Gotchas

- **The obstacle is virtual - it won't appear as a Gazebo body.** Only
  `/hybraut_nav/colreg_encounter_markers` in RViz shows where it is; there's
  nothing to bump into in the sim itself.
- **`overtaking`/`being_overtaken` need the agent actually moving** (i.e. an
  `execute_mission` goal sent to `tactical_node`, which is what gets
  `immediate_node` commanding real motion) - the speed differential is what
  closes the gap, so a stationary agent never gets overtaken or catches up
  to anything. `colreg_encounter_publisher` sends that goal itself by
  default (`send_goal_waypoint`); if you disabled it, remember to send one
  manually.
- Same `use_sim_time`/duplicate-process gotchas as the
  [base demo](turtlebot3_demo.md#gotchas) apply here.
