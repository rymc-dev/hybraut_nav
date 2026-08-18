# HybrautNav Architecture

Software tools for maritime autonomy — from the generic `hybrid-automaton`
framework, through the maritime-specific `colav-automaton` (v1.0.6), into the
`hybraut_nav` ROS 2 stack and its `hybraut_nav_colreg_sim` test harness.

---

## 1. Framework stack

Three layers of increasing specificity: a generic hybrid-automaton runtime,
a maritime COLAV automaton built on it, and the ROS 2 stack that runs it
against a live vehicle.

```mermaid
flowchart TB
    subgraph L1["Generic runtime — PyPI: hybrid-automaton v1.0.0"]
        HA["Automaton\nStates · Transitions · Guards · Resets · Invariants · Flows"]
    end

    subgraph L2["Maritime COLAV logic — PyPI: colav-automaton v1.0.6"]
        CA["ColavAutomaton(...) → Automaton\n3 states, 5 transitions"]
        MODS["guards · resets · invariants · dynamics · classification"]
    end

    subgraph L3["ROS 2 integration — hybraut_nav"]
        TN["tactical_node\n(hybraut_nav_tactical)"]
    end

    HA -->|"built on"| CA
    MODS -.->|"compose"| CA
    CA -->|"instantiated + driven by"| TN

    style L1 fill:#eef2f7,stroke:#5c7a99
    style L2 fill:#e8f3ec,stroke:#4c8c6b
    style L3 fill:#fbeee0,stroke:#c17a3d
```

**Key point for discussion:** `hybraut_nav` never touches hybrid-automaton
directly for logic — it depends on it only for the shared types
(`Automaton`, `ContinuousState`, `AuxiliaryState`, `RunResult`). All COLAV
domain logic lives one layer down, in `colav-automaton`.

---

## 2. `colav-automaton` — discrete state machine

The automaton driving the tactical layer. Always "under way" while in
`Transit`; steers on LOS (line-of-sight) guidance and reroutes around the
unsafe region on the fly.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Transit
    Transit --> Transit: e3 · LOS blocked → generate virtual waypoint (priority 1)
    Transit --> Fallback: e2 · unsafe conditions (priority 2)
    Fallback --> Transit: e4 · safe conditions restored
    Transit --> Waypoint_Reached: e1 · waypoint reached (priority 0)
    Waypoint_Reached --> Transit: e5 · pop virtual waypoint
```

| State | Flow | Behaviour |
|---|---|---|
| **Transit** | `flow_los_heading` | Only "under way" state — always steers via LOS guidance toward the current (real or virtual) waypoint. |
| **Fallback** | `hold_position_dynamics` | Entered when the safety-radius circle intersects the unsafe region. Brakes and holds heading — no active replanning — until `safe_conditions_guard` clears or `fallback_timeout` elapses. |
| **Waypoint_Reached** | `constant_heading_dynamics` | Terminal-ish: pops the next queued virtual waypoint and resumes, or ends the leg if none remain. |

`e3` outranks `e2` on priority (min-wins) so a reroute always gets first
refusal over bracing in Fallback when both guards fire in the same step.

---

## 3. `colav-automaton` — internal module architecture

Every guard / reset / invariant / dynamics function reads and writes the
same shared `RuntimeContext` — the data contract the automaton passes
around each evaluation step.

```mermaid
flowchart LR
    CTX[("RuntimeContext\ncontinuous_state · auxiliary_states\n(waypoints · unsafe_region · maneuver_bias)")]

    subgraph modules["colav_automaton/"]
        G["guards.py\nlos_clear_to_waypoint\nunsafe_conditions\nsafe_conditions\nwaypoint_reached\nvirtual_waypoints"]
        R["resets.py\ngenerate_new_virtual_waypoint\npop_virtual_waypoint"]
        I["invariants.py\nfailing_invariant\nfallback_recoverable_invariant"]
        D["dynamics.py\nflow_los_heading\nhold_position_dynamics\nconstant_heading_dynamics"]
        C["classification.py\nclassify_unsafe_set_obstacles\nmaneuver_bias (Rules 13/14/15/18)"]
    end

    CTX --> G --> CTX
    CTX --> R --> CTX
    CTX --> I --> CTX
    CTX --> D --> CTX
    C -->|"aggregate_maneuvers → maneuver_bias"| CTX
    CTX -->|"AuxiliaryState('maneuver_bias')"| R
```

`classification.py` is the COLREGs layer (since v1.0.4): it scores each
tracked ship's encounter geometry (Rule 13 overtaking, 14 head-on, 15
crossing) weighted by Rule 18 vessel-type right-of-way, and produces a
`{side, urgency}` bias that overrides the automaton's default "easiest
side" geometric heuristic in `generate_new_virtual_waypoint`.

---

## 4. `riskenv` — risk envelope computation

The geometric core feeding both `unsafe_region` and, downstream, COLREGs
classification. Pure CPA/TCPA geometry — no COLREGs knowledge lives here.

```mermaid
flowchart LR
    A["Agent\nposition · heading · speed\nyaw_rate · safety_radius"]
    O["Obstacle[]\nsame fields, + AIS tag"]
    METR["calculate_obstacle_metrics_for_agent\n→ ObstacleWithMetrics\n(DCPA, TCPA per obstacle)"]

    subgraph IOI["Indices of Interest (per-obstacle filters, all vs dsf)"]
        I1["I1 — proximity\nagent↔obstacle distance ≤ dsf"]
        I2["I2 — clustering\nan I1 obstacle with another\nobstacle also within dsf"]
        I3["I3 — predicted approach\nDCPA ≤ dsf AND TCPA ≤ time_of_interest"]
    end

    UNION["unionise_indices_of_interest\n(I1 ∪ I2 ∪ I3, de-duplicated)"]
    HULL["gen_uIoI_convhull\n→ unsafe_region vertices\n(or [] if no risk)"]

    A --> METR
    O --> METR
    METR --> I1 & I2 & I3
    I1 --> UNION
    I2 --> UNION
    I3 --> UNION
    UNION --> HULL
```

| Index | Question it answers | Criterion |
|---|---|---|
| **I1** | Is this obstacle close *right now*? | Euclidean distance (minus combined safety radii) ≤ `dsf` |
| **I2** | Is it boxed in / clustered with another obstacle? | An I1 obstacle with a second obstacle also within `dsf` of it — the agent can't slip between them |
| **I3** | Will it become close soon? | Predicted `DCPA ≤ dsf` **and** `TCPA ≤ time_of_interest`, from dead-reckoned CPA geometry |

`create_unsafe_set(agent, obstacles, dsf, time_of_interest)` is the single
top-level orchestrator — `risk_envelope_node` calls it once per synchronised
`/odom` + `/obstacles_state` pair and republishes the resulting hull as
`/hybraut_nav/riskenv`, which is exactly the `unsafe_region` auxiliary state
`colav-automaton`'s guards (§2) evaluate against — see §6 for that ROS wiring.

---

## 5. From geometric risk to COLREGs maneuver bias

`colav_automaton.classification` doesn't recompute risk from scratch — it
**reuses `riskenv`'s own `calc_I1/I2/I3` and CPA metrics** to decide which
ships are "of interest" before applying any COLREGs logic, so a distant ship
`riskenv` itself would ignore can never out-vote a closer, genuine threat.

```mermaid
flowchart TB
    OBS["/obstacles_state\n(AIS-style: position, heading, speed, vessel type)"]
    RE["riskenv:\ncalculate_obstacle_metrics_for_agent\n+ calc_I1 / calc_I2 / calc_I3"]
    FILT["classify_unsafe_set_obstacles\n→ obstacles 'of interest'\n(same I1/I2/I3 filter as unsafe_region)"]

    subgraph PER["per obstacle: classify_encounter → determine_maneuver"]
        ENC["Encounter geometry\nHEAD_ON · CROSSING_GIVE_WAY · CROSSING_STAND_ON\nOVERTAKING · OVERTAKEN\n(relative bearing vs ±112.5° abaft-the-beam)"]
        R18["Rule 18 weighting\nvessel-type priority\n(power-driven → not-under-command)"]
        PROX["proximity/urgency scaling\nfrom DCPA / TCPA"]
    end

    AGG["aggregate_maneuvers\nhighest urgency wins,\nstarboard breaks ties"]
    BIAS["Maneuver.as_bias()\n{side, urgency}"]

    OBS --> RE --> FILT --> ENC
    ENC --> R18 --> PROX --> AGG
    AGG --> BIAS
    BIAS -->|"/hybraut_nav/maneuver_bias"| TN["tactical_node\n→ generate_new_virtual_waypoint"]
```

| Encounter (Rule) | Default side | Give-way? | Base urgency |
|---|---|---|---|
| Rule 14 — Head-on | Starboard | ✅ | 0.9 |
| Rule 15 — Crossing, obstacle to starboard | Starboard | ✅ | 0.8 |
| Rule 13 — Overtaking | Starboard | ✅ | 0.5 |
| Rule 17 — Crossing, obstacle to port (stand-on) | Starboard | ❌ | 0.15 |
| Rule 13 — Being overtaken (stand-on) | Starboard | ❌ | 0.1 |

Urgency is then bumped for Rule 18 (outranked by the obstacle's vessel type)
and for closing proximity (DCPA/TCPA-derived), before `aggregate_maneuvers`
collapses every "of interest" ship down to the single highest-urgency
`{side, urgency}` bias that overrides `generate_new_virtual_waypoint`'s
default geometric "easiest side" choice.

**Discussion point:** this is a two-stage risk pipeline, not one —
`riskenv` answers *"is there risk, and where geometrically"* (the hull);
`colav_automaton.classification` answers *"given that risk, what does
COLREGs require us to do about it"* (the bias). `risk_envelope_node`
computes and publishes both from the same synchronised obstacle snapshot
each cycle.

---

## 6. `hybraut_nav` — ROS 2 layer architecture

Four navigation layers plus a risk layer, each one console-script node.

```mermaid
flowchart TB
    STRAT["Strategy\nstrategy_node\nGlobal path planning (A*, Dijkstra, RRT, RRT*)\nover the static costmap"]
    TACT["Tactical\ntactical_node\nHosts ColavAutomaton — reacts to odom + risk envelope,\nrepublishes reference continuous dynamics"]
    IMM["Immediate\nimmediate_node\nGuidance/control — tracks tactical's reference heading,\noutputs cmd_vel"]
    RISK["Risk\nrisk_envelope_node\nFuses agent + obstacle state into a risk envelope\nvia riskenv + colav_automaton.classification"]

    STRAT -->|"ExecuteMission action\n(one waypoint/leg)"| TACT
    RISK -->|"/hybraut_nav/riskenv\nPolygonStamped"| TACT
    RISK -->|"/hybraut_nav/maneuver_bias\nManeuverBias"| TACT
    TACT -->|"/hybraut_nav/continous_dynamics\nFloat64MultiArray"| IMM
    IMM -->|"/cmd_vel\nTwistStamped"| VEH(["Vehicle / simulated hull"])
    VEH -->|"/odom"| TACT
    VEH -->|"/odom"| IMM
    VEH -->|"/odom"| RISK

    style STRAT fill:#fbeee0,stroke:#c17a3d
    style TACT fill:#e8f3ec,stroke:#4c8c6b
    style IMM fill:#eef2f7,stroke:#5c7a99
    style RISK fill:#f6e9ee,stroke:#a3527a
```

`tactical_node` is the integration point from Section 1 — it constructs
`ColavAutomaton(...)` once at startup from ROS parameters, and drives it
one leg at a time via the `execute_mission` action server.

---

## 7. Tactical layer — one leg, live

How `tactical_node` feeds live ROS data into the automaton and republishes
its reference for `immediate_node` to track. `run_until_complete()` blocks
one executor thread for the whole leg; a separate publish-timer thread
keeps sensors, feedback, and cancellation flowing concurrently.

```mermaid
sequenceDiagram
    participant Strat as strategy_node
    participant TN as tactical_node
    participant HA as ColavAutomaton
    participant Risk as risk_envelope_node
    participant Imm as immediate_node

    Strat->>TN: ExecuteMission goal (target waypoint)
    TN->>HA: activate(continuous_state, [waypoints, unsafe_region, maneuver_bias])
    activate HA

    loop every sensor_update_rate (odom-driven guards stay grounded)
        TN-->>HA: continuous_state_provider() splices real (x, y)
    end

    loop every dt (0.01 s)
        Risk-->>TN: /hybraut_nav/riskenv (unsafe region hull)
        Risk-->>TN: /hybraut_nav/maneuver_bias (COLREGs side + urgency)
        HA->>HA: evaluate guards → transition / flow one step
    end

    loop every continuous_dynamics_publish_rate (50 Hz)
        TN->>Imm: /hybraut_nav/continous_dynamics (reference x,y,θ,v,yaw_rate)
        TN->>Strat: action feedback (automaton_state, transitions_count)
    end

    HA-->>TN: RunResult (TERMINAL_REACHED / CANCELLED / failed)
    deactivate HA
    TN->>Strat: action result (success / message)
```

---

## 8. `hybraut_nav_colreg_sim` — simulation & COLREGs test harness

Wires the full `hybraut_nav` stack against a Gazebo world with scripted
AIS-style traffic, so COLREGs encounters (head-on, crossing, overtaking)
can be exercised end-to-end without hardware.

```mermaid
flowchart TB
    SCEN["scenarios/COLREG_*.xml\n(CommonOcean scenario format)"]
    LOADER["scenario_loader.py\nvessel_catalog.py"]
    GZ["gz_sim.launch.py\nGazebo + ros_gz_bridge\nspawns *_vessel.urdf traffic"]
    AIS["vessel_ais_bridge.py\n→ /obstacles_state"]
    ASB["agent_state_bridge.py\n/odom → /agent_state"]
    GOAL["scenario_goal_sender.py\nplanningProblem/goalState\n→ navigate_to_goal action"]
    MAP["map_publisher.py\n→ /map"]

    subgraph STACK["hybraut_nav (Section 4)"]
        S2["strategy_node"]
        T2["tactical_node"]
        I2["immediate_node"]
        R2["risk_envelope_node"]
    end

    RVIZ["RViz\nhybraut_nav_strategic_tactical_immediate_colreg_demo.rviz"]

    SCEN --> LOADER --> GZ
    GZ -->|"spawned vessel poses"| AIS --> R2
    GZ -->|"ego /odom"| ASB -->|"/agent_state"| S2
    MAP -->|"/map"| S2
    SCEN --> GOAL -->|"single-waypoint goal"| S2
    S2 --> T2 --> I2 -->|"/cmd_vel"| GZ
    R2 -->|"riskenv + maneuver_bias"| T2
    T2 -.-> RVIZ
    I2 -.-> RVIZ

    style STACK fill:#e8f3ec,stroke:#4c8c6b
```

**Tuning note for the deck:** the launch file retunes several
`colav-automaton` parameters away from library defaults for a ~15 kn
hydrofoil (e.g. `constant_velocity=7.7`, `safety_radius=10.0`,
`los_distance_threshold=150.0`) and `risk_envelope_node`'s `dsf`/
`time_of_interest` so COLREG encounters emerge as vessels actually close,
rather than being flagged "of interest" from `t=0`.

---

## 9. Tooling summary

| Component | Package | Version | Role |
|---|---|---|---|
| `hybrid-automaton` | PyPI | 1.0.0 | Generic hybrid-automaton runtime (states/guards/resets/invariants/flows) |
| `colav-automaton` | PyPI | **1.0.6** | Maritime COLAV automaton + COLREGs-informed classification, built on `hybrid-automaton` |
| `riskenv` | PyPI | 1.0.0 | CPA/TCPA geometry + I1/I2/I3 indices of interest → unsafe-set convex hull; also the shared metric layer `colav-automaton`'s classification reuses |
| `hybraut_nav` | ROS 2 (rclpy) | — | 4-layer navigation stack (Strategy / Tactical / Immediate / Risk) hosting `ColavAutomaton` |
| `hybraut_nav_colreg_sim` | ROS 2 (rclpy) | — | Gazebo + scripted-AIS COLREGs test harness for the full stack |

---

*Diagrams generated from the current source tree (`hybraut_nav`,
`hybraut_nav_colreg_sim`, `hybrid-automaton`, `colav-automaton`) —
re-derive if any of these packages' READMEs or launch files change.*
