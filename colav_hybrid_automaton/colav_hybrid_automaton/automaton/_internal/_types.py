from dataclasses import dataclass, field
from colav_hybrid_automaton.automaton.guards import  GuardABC
from typing import Any, List
from colav_hybrid_automaton.automaton.resets import ResetABC
from colav_hybrid_automaton.automaton.invariants import InvariantABC
from colav_hybrid_automaton.automaton.dynamics import DynamicsABC
from typing import TypedDict, Dict
from typing import Optional
import importlib
import yaml
# We utilize data classes to define the hybrid automaton in the automaton lifecycle to simplify the storage
# instead of always using dicts defined on the fly.

@dataclass
class State: 

    # details for ros2 state topic
    topic: str
    msg_type: Any

    # current runtime state
    current_state: Optional[Any] = None
    
    # metadata for states for strict sync checking
    update_hz: Optional[float] = -1
    timeout_sec: Optional[float] = -1.0

    @classmethod
    def update_current_state(cls, current_state):
        current_state = current_state

    @classmethod
    def from_famd(cls, state_famd_data: dict):
        topic = state_famd_data.get('topic', '')

        # Import message class dynamically
        pkg_path = state_famd_data['type']['pkg']
        msg_name = state_famd_data['type']['msg']
        try:
            module = importlib.import_module(pkg_path)
            msg_type = getattr(module, msg_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot import '{msg_name}' from '{pkg_path}': {e}")

        return cls(
            current_state=None,
            topic=topic,
            msg_type=msg_type,
        )


@dataclass
class Transition:
    """transition between modes"""
    name: str
    target_mode_key: int
    guard: 'Transition.Guard'
    reset: Optional['Transition.Reset'] = None

    @classmethod
    def from_famd(cls, transition_name, transition_famd, guards_famd, resets_famd):
        print ('hello world')
        target_mode_key = transition_famd['target_mode']
        guard_name = transition_famd['guard']
        reset_name = transition_famd.get('reset', None)

        guard: 'Transition.Guard' = cls.Guard.from_famd(
            guard_name = guard_name, guard_famd = guards_famd[guard_name]
        )
        if reset_name == None: # just guard for this transition
            return cls(
              name = transition_name,
              target_mode_key = target_mode_key,
              guard = guard
          )
        else: # Guard + reset
            reset: 'Transition.Reset' = cls.Reset.from_famd(
                reset_name = reset_name, reset_famd = resets_famd[reset_name]
            )
            return cls(
                name = transition_name,
                target_mode_key = target_mode_key,
                guard = guard,
                reset = reset
            )
          
    @dataclass
    class Guard: 
        name: str
        description: str
        instance: GuardABC
        state_inputs: List[State] 

        @classmethod
        def from_famd(cls, guard_name, guard_famd):
            module = guard_famd['module']
            class_name = guard_famd['class_name']
            
            try:
              guard_class = getattr(importlib.import_module(module), class_name)
            except (ImportError, AttributeError) as e:
                raise ImportError(f"Cannot import '{class_name}' from '{module}': {e}")

            init_kwargs = guard_famd['configuration']
            guard_instance:GuardABC = guard_class(**init_kwargs)
            guard_info = guard_instance.get_guard_info()
            guard_description = guard_info['description']
            
            return cls(
                name=guard_name,
                description=guard_description,
                instance=guard_instance,
                state_inputs=guard_famd['state_inputs']
            )

    @dataclass
    class Reset:
        name: str   
        description: str
        instance: ResetABC
        state_inputs: dict[str, State] = field(default_factory=dict)
        reset_targets: dict[str, State] = field(default_factory=dict)

        @classmethod
        def from_famd(cls, reset_name,  reset_famd):
            
            module = reset_famd['module']
            class_name = reset_famd['class_name']
            
            try:
              guard_class = getattr(importlib.import_module(module), class_name)
            except (ImportError, AttributeError) as e:
                raise ImportError(f"Cannot import '{class_name}' from '{module}': {e}")

            init_kwargs = reset_famd['configuration']
            reset_instance:ResetABC = guard_class(**init_kwargs)
            reset_info = reset_instance.get_reset_info()
            reset_description = reset_info['description']
            
            return cls(
                name = reset_name,
                description = reset_description,
                instance = reset_instance,
                state_inputs = reset_famd['state_inputs'],
                reset_targets = reset_famd['reset_targets']
            )

@dataclass
class Invariant:
    instance: InvariantABC
    description: str
    state_inputs: List[State] = field(default_factory=list)

    @classmethod
    def from_famd(cls, invariant_famd_data):
        module = invariant_famd_data['module']
        class_name = invariant_famd_data['class_name']
        
        try:
            invariant_class = getattr(importlib.import_module(module), class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot import '{class_name}' from '{module}': {e}")

        init_kwargs = invariant_famd_data['configuration']
        invariant_instance: InvariantABC = invariant_class(**init_kwargs)

        invariant_info = invariant_instance.get_invariant_info()
        invariant_description = invariant_info['description']

        return cls(
            instance=invariant_instance,
            description=invariant_description,
            state_inputs=invariant_famd_data['state_inputs']
        )

@dataclass
class Dynamics:
    """Dynamics/controller for modes"""
    name: str
    description: str
    instance: DynamicsABC
    state_inputs: List[State] = field(default_factory=list)

    @classmethod
    def from_famd(cls, dynamic_famd_data):
        # Import message class dynamically
        pkg_path = dynamic_famd_data['module']
        dynamic_class_name = dynamic_famd_data['class_name']
        try:
            dynamics_class = getattr(importlib.import_module(pkg_path), dynamic_class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot import '{dynamic_class_name}' from '{pkg_path}': {e}")
        
        init_kwargs = dynamic_famd_data['configuration']
        dynamics_instance:DynamicsABC = dynamics_class(**init_kwargs)
        
        instance_details = dynamics_instance.get_dynamics_info()
        class_name = instance_details['class_name']
        description = instance_details['description']

        return cls(
            name = class_name,
            description = description,
            instance = dynamics_instance,
            state_inputs = dynamic_famd_data['state_inputs']
        )

@dataclass
class Mode:
    """Mode in the hybrid automaton"""
    description: str
    transitions: Dict[str, Transition] = field(default_factory=dict)
    invariants: Dict[str, Invariant] = field(default_factory=dict)
    dynamics: Optional[Dynamics] = None

    @classmethod
    def from_famd(cls, mode_famd_data, famd_data):
        description = mode_famd_data.get('description', '')
        transitions_data = famd_data.get('transitions', {})
        guards_data = famd_data.get('guards', {})
        resets_data = famd_data.get('resets', {})
        invariants_data = famd_data.get('invariants', {})
        dynamics_data = famd_data.get('dynamics', {})

        # transitions
        transitions = {}
        transitions_list = [
            (list(t.keys())[0], list(t.values())[0]['priority'])
            for t in mode_famd_data['transitions']
        ]

        # Sort by priority (second item in each tuple)
        transitions_sorted = sorted(transitions_list, key=lambda x: x[1])

        # Unpack into separate lists
        keys_sorted = [name for name, _ in transitions_sorted]
        priorities_sorted = [priority for _, priority in transitions_sorted]

        for idx, transition_key in enumerate(keys_sorted):
            transitions[priorities_sorted[idx]] = Transition.from_famd(
                transition_name = transition_key,
                transition_famd=transitions_data[transition_key],
                guards_famd=guards_data,
                resets_famd=resets_data
            )


        # invariants
        invariants = {}
        invariant_keys = mode_famd_data['invariants']
        for invariant_key in invariant_keys:
          invariant_famd = invariants_data[invariant_key]
          invariants[invariant_key] = Invariant.from_famd(invariant_famd)

        # get the dynamics dataclass
        dynamics_key = mode_famd_data['dynamics']
        dynamic_famd = dynamics_data[dynamics_key]
        dynamics = Dynamics.from_famd(dynamic_famd)

        return cls(
            description = description,
            transitions = transitions,
            invariants = invariants,
            dynamics = dynamics
        )

    
    def get_sorted_transitions(self) -> List[tuple[str, Transition]]:
        """Get transitions sorted by priority (lowest priority number = highest priority)"""
        return sorted(self.transitions.items(), key=lambda x: x[1].priority)
    
    def add_transition(self, name: str, transition: Transition) -> None:
        """Add a transition to this mode"""
        self.transitions[name] = transition
    
    def add_invariant(self, name: str, invariant: Invariant) -> None:
        """Add an invariant to this mode"""
        self.invariants[name] = invariant

@dataclass
class HybridAutomaton:
    """
    Pythonic dataclass representation of the hybrid automaton 
    configuration defined in the FAMD TANK file, with instantiated functions
    """
    # Metadata
    name: str
    description: str = ""
    
    # Frequencies
    transition_evaluation_frequency_hz: float = 10.0
    control_frequency_hz: float = 50.0
    
    # Mode configuration
    goal_modes_keys: List[int] = field(default_factory=list)
    initial_mode_key: int = 0
    
    # Runtime state
    current_mode_key: int = 0
    
    # Automaton components
    states: Dict[str, State] = field(default_factory=dict)
    modes: Dict[int, Mode] = field(default_factory=dict)

    @classmethod
    def from_famd(cls, famd_data: yaml):
        """
        Initialize HybridAutomaton from FAMD yaml data
        
        Args:
            famd_data: Dictionary containing the complete FAMD configuration
                      with instantiated components (guards, resets, dynamics, invariants)
        
        Returns:
            HybridAutomaton: Fully initialized hybrid automaton
        """
        # Extract metadata
        name = famd_data.get('automaton_name', 'unnamed automaton')
        description = famd_data.get('automaton_description', '')

        # Extract frequencies
        transition_freq = famd_data.get('transition_evaluation_frequency_hz', 10.0)
        control_freq = famd_data.get('control_frequency_hz', 50.0)
    
        # Extract mode configuration
        goal_modes = famd_data.get('goal_modes', [])
        initial_mode = famd_data.get('initial_mode', 0)
        current_mode = initial_mode

        # Intialize States
        # initialize states
        states = {}
        for state_key, state_val in famd_data.get('states').items():
            states[state_key] = State.from_famd(state_val)

        modes = {}
        for mode_key, mode_val in famd_data.get('modes').items():
            modes[mode_key] = Mode.from_famd(mode_val, famd_data)

        print (modes)

        return cls(
            name=name,
            description=description,
            transition_evaluation_frequency_hz=transition_freq,
            control_frequency_hz=control_freq,
            goal_modes_keys=goal_modes,
            initial_mode_key=initial_mode,
            current_mode_key=current_mode,
            states=states,
            modes=modes
        )

    @staticmethod
    def _dynamic_state_import_binds(states: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically import ROS2 state types for each state entry."""
        if len(states) > 0:
            for key, value in states.items():
                pkg = importlib.import_module(value['type']['pkg'])
                states[key]['type'] = getattr(pkg, value['type']['msg'])
        return states

    @staticmethod
    def _dynamic_import_binds(components: Dict[str, Dict[str, Any]], key_module='module', key_class='class_name') -> Dict[str, Any]:
        """Generic dynamic import helper for guards, resets, dynamics, and invariants."""
        if len(components) > 0:
            for key, value in components.items():
                module = importlib.import_module(value[key_module])
                class_name = value[key_class]
                del components[key][key_module]
                del components[key][key_class]
                components[key]['class'] = getattr(module, class_name)
        return components


if __name__ == '__main__':
    famd_content = yaml.safe_load('''# COLAV Hybrid Automaton Formal Automaton Model Definition (FAMD)
# ============================================================================
# ROS2 Hybrid Automaton Framework Configuration (COLAV Hybrid Automaton)
# ============================================================================
# This defines the configuration for the Hybrid Automaton used in ROS2.
# It includes mode declarations, transitions, guards, resets, invariants,
# initial states, and parameter settings in a structured and interpretable format.
#
# IMPORTANT:
# - Python function links (guards/resets) must point to valid, importable symbols.
# - Functions must be exposed via __init__.py with __all__ to enable automatic access.
# - Module paths must be within the Python build path (not direct file paths).
#
# Hybrid Automaton formalism:
#   HA = (Q, Q_goal, X, F, Init, Inv, E, G, R)
#
#   Q      = modes
#   Q_goal = goal_modes # Optional
#   X      = states
#   F      = dynamics
#   Init   = initial_mode
#   Inv    = invariants
#   E      = transitions
#   G      = guards
#   R      = resets
#
# additional param:
# params: This provides metatdata related to the hybrid automaton

# ============================================================================
# Continuous States (X)
# These are received via ROS2 topics. Metadata is included per state.
# Each of these states have buffers associated with buffer_size set in params
# ============================================================================
states:
  agent_state:
    topic: "/state/agent"
    description: "State of the agent including position, velocity and heading."
    type:
      pkg: "colav_interfaces.msg"
      msg: "AgentState"
    params:
      update_hz: 10.0
      timeout_sec: 0.5
      buffer_size: 100

  obstacles_state:
    topic: "/state/obstacles"
    description: "State of the obstacles in the environment."
    type:
      pkg: "colav_interfaces.msg"
      msg: "ObstaclesState"
    params:
      update_hz: 4.0
      timeout_sec: 1.0

  unsafe_set_state:
    topic: "/state/unsafe_set"
    description: "State of the unsafe set, indicating unsafe conditions for the agent."
    type:
      pkg: "colav_interfaces.msg"
      msg: "UnsafeSetState"
    params:
      update_hz: 2.0
      timeout_sec: 1.5

  waypoints_state:
    topic: "/state/waypoints"
    description: "State of the waypoints including current waypoint and virtual waypoints."
    type:
      pkg: "colav_interfaces.msg"
      msg: WaypointsState

# ============================================================================
# Reset Functions (R)
# Executed during transitions to modify continuous state.
# ============================================================================
resets:
  remove_virtual_waypoint_reset:
    module: colav_hybrid_automaton.automaton.resets
    class_name: RemoveVirtualWaypointReset
    description: "Remove the first virtual waypoint from the waypoints state and update the current waypoint."
    state_inputs:
      - "waypoints_state"
    reset_targets:
      - "waypoints_state"
    configuration: {}

  generate_virtual_waypoint_reset:
    module: colav_hybrid_automaton.automaton.resets
    class_name: GenerateVirtualWaypointReset
    description: "Generate a virtual waypoint based on the agent's position and obstacles, and add it to the waypoints state updating the current waypoint to it."
    state_inputs:
      - "agent_state"
      - "obstacles_state"
      - "unsafe_set_state"
      - "waypoints_state"
    reset_targets:
      - "waypoints_state"
    configuration:
      longitudinal_offset_distance: 30.0
      lateral_offset_distance: 5.0
      virtual_waypoint_acceptance_radius: 20.0

# ============================================================================
# Guard Conditions (G)
# Boolean functions checked during transition evaluation.
# ============================================================================
guards:
  los_clear_to_waypoint_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: LOSClearToWaypointGuard
    description: "Checks if the line of sight from agent position to the current waypoint is clear."
    state_inputs:
      - "agent_state"
      - "obstacles_state"
      - "unsafe_set_state"
      - "waypoints_state"
    configuration:
      los_distance_threshold: 100.0

  heading_within_tolerance_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: HeadingWithinToleranceGuard
    description: "Checks if the agent's heading is within a specified tolerance of the waypoint direction."
    state_inputs:
      - "agent_state"
      - "waypoints_state"
    configuration:
      heading_tolerance: 0.2

  heading_not_within_tolerance_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: HeadingNotWithinToleranceGuard
    description: "Checks if the agent's heading is not within a specified tolerance of the waypoint direction."
    state_inputs:
      - "agent_state"
      - "waypoints_state"
    configuration:
      heading_tolerance: 0.2

  virtual_waypoints_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: VirtualWaypointsGuard
    description: "Checks if there are virtual waypoints available in the waypoints state."
    state_inputs:
      - "waypoints_state"
    configuration: {}

  unsafe_conditions_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: UnsafeConditionsGuard
    description: "Checks if the agent is in unsafe conditions based on obstacles and unsafe set."
    state_inputs:
      - "agent_state"
      - "obstacles_state"
      - "unsafe_set_state"
    configuration: {}

  waypoint_reached_guard:
    module: colav_hybrid_automaton.automaton.guards
    class_name: WaypointReachedGuard
    description: "Checks if the agent has reached the current waypoint."
    state_inputs:
      - "agent_state"
      - "waypoints_state"
    configuration: {}

# ============================================================================
# Invariants (Inv)
# Leave empty if no mode constraints exist.
# ============================================================================
invariants:
  is_goal_waypoint_invariant:
    module: colav_hybrid_automaton.automaton.invariants
    class_name: IsGoalWaypointInvariant
    description: "Checks if the current waypoint is the goal waypoint."
    state_inputs:
      - "waypoints_state"
    configuration: {}

  trivial_invariant:
    module: colav_hybrid_automaton.automaton.invariants
    class_name: TrivialInvariant
    description: "A trivial invariant that always holds true."
    state_inputs: []
    configuration: {}

  failing_invariant:
    module: colav_hybrid_automaton.automaton.invariants
    class_name: FailingInvariant
    description: "An invariant that always fails, used for fallback mode."
    state_inputs: []
    configuration: {}

# ============================================================================
# Transitions (E)
# Mapping of transition names to guard and reset functions.
# ============================================================================
transitions:
  plan_evasive_maneuver:
    origin_modes:
      - 0
    origin_priorities:
      - 2
    target_mode: 1
    guard: "los_clear_to_waypoint_guard"
    reset: "generate_virtual_waypoint_reset"

  correct_heading:
    origin_modes:
      - 0
    origin_priorities:
      - 3
    target_mode: 1
    guard: "heading_not_within_tolerance_guard"
    reset: null

  enter_emergency_fallback:
    origin_modes:
      - 0
      - 1
    origin_priorities:
      - 0
      - 0
    target_mode: 3
    guard: "unsafe_conditions_guard"
    reset: null

  waypoint_arrival:
    origin_modes:
      - 0
      - 1
    origin_priorities:
      - 1
      - 2
    target_mode: 2
    guard: "waypoint_reached_guard"
    reset: null

  heading_aligned:
    origin_modes:
      - 1
    origin_priorities:
      - 0
    target_mode: 0
    guard: "heading_within_tolerance_guard"
    reset: null

  proceed_to_next_waypoint:
    origin_modes:
      - 2
    origin_priorities:
      - 0
    target_mode: 0
    guard: "virtual_waypoints_guard"
    reset: "remove_virtual_waypoint_reset"

# ============================================================================
# Dynamics (F)
# Controllers used for continuous evolution within each mode.
# ============================================================================
dynamics:
  cruise_pid_controller:
    module: colav_hybrid_automaton.automaton.dynamics
    class_name: PIDControllerDynamics
    description: "pid controller tuned for cruise mode."
    state_inputs:
      - "agent_state"
      - "waypoints_state"
    dynamic_outputs:
      dynamic_parameter_names:
        - "velocity"
        - "yaw_rate"
      dynamic_parameter_value_types:
        - float
        - float
      dynamic_parameter_metrics:
        - "m/s"
        - "rad/s"
    configuration:
      target_velocity: 25.0 # updated cruise speed
      yaw_kp: 0.3 # gentle heading proportional gain
      yaw_ki: 0.01 # small integral for smooth correction
      yaw_kd: 0.05 # small derivative gain to damp oscillations
      vel_kp: 0.5 # moderate velocity proportional gain
      vel_ki: 0.05 # small integral to avoid windup
      vel_kd: 0.05 # small derivative for smooth velocity changes
      error_tolerance: 0.01 # precision in heading error
      max_yaw_rate: 0.1 # limit yaw rate to gentle turns

  t2los_pid_controller:
    module: colav_hybrid_automaton.automaton.dynamics
    class_name: PIDControllerDynamics
    description: "pid controller tuned for transition to line of sight (T2LOS) mode."
    state_inputs:
      - "agent_state"
      - "waypoints_state"
    dynamic_outputs:
      dynamic_parameter_names:
        - "velocity"
        - "yaw_rate"
      dynamic_parameter_value_types:
        - float
        - float
      dynamic_parameter_metrics:
        - "m/s"
        - "rad/s"
    configuration:
      target_velocity: 25.0 # updated cruise speed
      yaw_kp: 0.3 # gentle heading proportional gain
      yaw_ki: 0.01 # small integral for smooth correction
      yaw_kd: 0.05 # small derivative gain to damp oscillations
      vel_kp: 0.5 # moderate velocity proportional gain
      vel_ki: 0.05 # small integral to avoid windup
      vel_kd: 0.05 # small derivative for smooth velocity changes
      error_tolerance: 0.01 # precision in heading error
      max_yaw_rate: 0.1 # limit yaw rate to gentle turns

  no_op_controller:
    module: colav_hybrid_automaton.automaton.dynamics
    class_name: NoOpControllerDynamics
    description: "No operation controller, used in waypoint reached and fallback mode for returning state 0 yaw rate and velocity."
    state_inputs: []
    dynamic_outputs:
      dynamic_parameter_names:
        - "velocity"
        - "yaw_rate"
      dynamic_parameter_value_types:
        - float
        - float
      dynamic_parameter_metrics:
        - "m/s"
        - "rad/s"
    configuration: {}

# ============================================================================
# Modes (Q)
# Discrete states, each associated with dynamics, invariants, and transitions.
# ============================================================================
modes:
  0:
    name: cruise
    description: "Cruise mode with pid controller tuned for cruise mode."
    dynamics: cruise_pid_controller
    invariants:
      - trivial_invariant
    transitions:
      - enter_emergency_fallback:
          priority: 0
      - waypoint_arrival:
          priority: 1
      - plan_evasive_maneuver:
          priority: 2
      - correct_heading:
          priority: 3

  1:
    name: t2los
    description: "Transition to Line of Sight (T2LOS) mode with proportional yaw rate control"
    dynamics: t2los_pid_controller
    invariants:
      - trivial_invariant
    transitions:
      - enter_emergency_fallback:
          priority: 0
      - heading_aligned:
          priority: 1
      - waypoint_arrival:
          priority: 2

  2:
    name: waypoint_reached
    description: "Waypoint reached mode, indicating successful navigation to a waypoint"
    dynamics: no_op_controller
    invariants:
      - is_goal_waypoint_invariant
    transitions:
      - proceed_to_next_waypoint:
          priority: 0

  3:
    name: fallback
    description: "Fallback mode for emergency conditions, no active control"
    dynamics: no_op_controller
    invariants:
      - failing_invariant
    transitions: []

# ============================================================================
# Goal Modes (Q_goal)
# ============================================================================
goal_modes:
  - 2

# ============================================================================
# Initial Mode (Init)
# This is the mode the hybrid automaton will initially enter on
# automaton activation
# ============================================================================
initial_mode: 0

# ============================================================================
# Parameters
# these are parameters of the hybrid automaton set on
# activation
# ============================================================================
parameters:
  goal_waypoint:
    type:
      pkg: "colav_interfaces.msg"
      msg: "Waypoint"

  evaluation_frequency:
    type: float

  control_frequency:
    type: float

automaton_name: "colav_hybrid_automaton"
automaton_description: "automaton for collision avoidance"
transition_evaluation_frequency_hz: 10.0
control_frequency_hz: 10.0
    ''')
    automaton = HybridAutomaton.from_famd(famd_content)

    print (automaton)