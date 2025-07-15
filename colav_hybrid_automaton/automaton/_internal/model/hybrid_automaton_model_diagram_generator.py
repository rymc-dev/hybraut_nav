from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List
import subprocess
from pathlib import Path
import logging
from automaton._internal.model.hybrid_automaton_model import HybridAutomaton

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    """Supported output formats for diagrams."""
    SVG = "svg"
    PNG = "png"

class Theme(Enum):
    """Available Mermaid themes."""
    DEFAULT = "default"
    NEUTRAL = "neutral"
    DARK = "dark"
    FOREST = "forest"
    BASE = "base"

class Backgroud(Enum):
    """Available background options for diagrams."""
    TRANSPARENT = "transparent"
    WHITE = "white"
    BLACK = "black"

@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    theme: Theme = Theme.FOREST
    background: Backgroud = Backgroud.WHITE
    scale: int = 2
    output_format: OutputFormat = OutputFormat.SVG

class MermaidDiagramGeneratorError(Exception):
    """Custom exception for diagram generation errors."""
    pass

class HybridAutomatonModelDiagramGenerator:
    """
    Generator for Mermaid state diagrams from hybrid automaton data.
    
    This class handles the complete workflow of generating Mermaid diagrams
    from automaton configuration data and converting them to various formats.
    """
    
    def __init__(self, output_directory: Optional[str] = None):
        """
        Initialize the diagram generator.
        
        Args:
            output_directory: Directory to save generated diagrams.
                            If None, uses default relative path.
        """
        self._output_dir = self._setup_output_directory(output_directory)
        self._ensure_mermaid_cli()
    
    def generate_mermaid_diagrams(
        self, 
        automaton_model: HybridAutomaton, 
        config: Optional[DiagramConfig] = None
    ) -> Tuple[str, str]:
        """
        Generate Mermaid diagrams from automaton data.
        
        Args:
            automaton_mode: Dictionary containing automaton configuration
            config: Diagram configuration options
            
        Returns:
            Tuple of (mmd_file_path, output_file_path)
            
        Raises:
            MermaidDiagramGeneratorError: If generation fails
        """
        if config is None:
            config = DiagramConfig()
            
        try:
            automaton_name = automaton_model.name
            
            # Generate Mermaid diagram content
            mermaid_lines = self._generate_mermaid_content(automaton_name, automaton_model)
            
            # Save .mmd file
            mmd_path = self._save_mermaid_file(mermaid_lines, automaton_name)
            
            # Convert to desired format
            output_path = self._convert_diagram(mmd_path, automaton_name, config)
            
            logger.info(f"Successfully generated diagram: {output_path}")
            return mmd_path, output_path
            
        except Exception as e:
            raise MermaidDiagramGeneratorError(f"Failed to generate diagram: {str(e)}") from e
    
    def _setup_output_directory(self, output_directory: Optional[str]) -> Path:
        """Setup and validate output directory."""
        if output_directory:
            output_dir = Path(output_directory)
        else:
            # Default to relative path from current file
            current_file = Path(__file__).parent
            output_dir = current_file / '..' / '.github' / 'assets' / 'diagrams'
        
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Output directory: {output_dir}")
        return output_dir
    
    def _ensure_mermaid_cli(self) -> None:
        """Ensure Mermaid CLI is available."""
        try:
            result = subprocess.run(
                ['mmdc', '--version'], 
                capture_output=True, 
                check=True,
                timeout=10
            )
            logger.info("Mermaid CLI is available")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            error_msg = (
                "Mermaid CLI not found or not working. "
                "Please install with: npm install -g @mermaid-js/mermaid-cli"
            )
            logger.error(error_msg)
            raise MermaidDiagramGeneratorError(error_msg) from e
    
    def _generate_mermaid_content(self, automaton_name: HybridAutomaton, automaton_model: Dict) -> List[str]:
        """
        Generate Mermaid state diagram content from automaton data.
        
        Args:
            automaton_name: Name of the automaton
            automaton_data: Automaton configuration data
            
        Returns:
            List of Mermaid diagram lines
        """
        mermaid = []
        
        # Header
        mermaid.extend([
            "stateDiagram-v2",
            f"    %% {automaton_name} State Diagram",
            ""
        ])
        
        # Extract data with defaults
        init_mode = automaton_model.initial_mode
        goal_modes = automaton_model.goal_modes
        
        # Generate diagram sections
        self._add_initial_state(mermaid, init_mode)
        self._add_modes(mermaid, automaton_model.modes)
        self._add_goal_states(mermaid, goal_modes)
        
        return mermaid
    
    def _add_initial_state(self, mermaid: List[str], init_mode: str) -> None:
        """Add initial state to diagram."""
        if isinstance(init_mode, int):
            mermaid.extend([
                "    %% Initial Mode",
                f"    [*] --> {init_mode}",
                ""
            ])
    
    def _add_modes(self, mermaid: List[str], modes: Dict) -> None:
        """Add modes with detailed information to diagram."""
        if not modes:
            return
            
        mermaid.append("\t%% Modes")
        
        for mode_key, mode_data in modes.items():
            mode_index = mode_key
            mode_name = mode_data.name
            invariants = mode_data.invariants
            dynamics = mode_data.dynamics
            description = mode_data.description
            
            # State definition
            mermaid.append(f"\t%% {mode_name} Mode details")
            mermaid.append(f"    {mode_index} : {mode_index}.{mode_name}")
            
            # Add detailed note if additional info exists
            if any([invariants, dynamics, description]):
                self._add_mode_note(mermaid, mode_name, mode_index, description, invariants, dynamics)
            
            mermaid.append("")
            mermaid.append(f'\t%% {mode_name} transitions.')
            for transition in mode_data.transitions:
                origin_mode = mode_key
                transition_name = transition.name
                transition_priority = transition.priority
                transition_target_mode = transition.target_mode
                guard_name = transition.guard.get_guard_info()['class_name']
                reset_name = 'Null'
                if transition.reset is not None:
                    reset_name = transition.reset.get_reset_info()['class_name']

                self._add_transition_edge(
                    mermaid, transition_name, origin_mode, transition_priority,
                    transition_target_mode, guard_name, reset_name
                )

            mermaid.append("")
    
    def _add_mode_note(
        self, 
        mermaid: List[str], 
        mode_name: str, 
        mode_index: str, 
        description: str, 
        invariants: str, 
        dynamics: str
    ) -> None:
        """Add detailed note for a mode."""
        mermaid.extend([
            f"    note left of {mode_index}",
            "        =====================",
            f"        <b>{mode_index}.{mode_name}</b>",
            "        ====================="
        ])
        
        if description:
            mermaid.append(f"        <b>description</b>: {description}")
        if invariants:
            mermaid.append(f"        <b>invariants</b>: {[f"{invariant.instance.get_invariant_info()['class_name']}, {invariant.description}" for invariant in invariants]}")
        if dynamics:
            mermaid.append(f"        <b>dynamics</b>: {f"{dynamics.instance.get_dynamics_info()['class_name']}, {dynamics.description}"}")
            
        mermaid.append("    end note")
    
    # def _add_transitions(self, mermaid: List[str], transitions: Dict) -> None:
    #     """Add transitions to diagram."""
    #     if not transitions:
    #         return
            
    #     mermaid.append("    %% Transitions")
        
    #     for transition_key, transition_data in transitions.items():
    #         origin_modes = transition_data.get('origin_modes', [])
    #         origin_priorities = transition_data.get('origin_priorities', [])
    #         target_mode = transition_data.get('target_mode', '')
    #         guard = transition_data.get('guard', '')
    #         reset = transition_data.get('reset', 'null')
            
    #         if target_mode is None:
    #             logger.warning(f"Skipping transition {transition_key}: no target mode")
    #             continue
            
    #         self._add_transition_edges(
    #             mermaid, transition_key, origin_modes, origin_priorities, 
    #             target_mode, guard, reset
    #         )
    
    def _add_transition_edge(
        self,
        mermaid: List[str],
        transition_key: str,
        origin_mode: str,
        priority: int,
        target_mode: str,
        guard: str,
        reset: str
    ) -> None:
        """Add a single transition edge."""
        transition_label = (
            f"<b>{priority}.{transition_key}</b>  "
            f"[<b>guard</b> = {guard}, <b>reset</b> = {reset}]"
        )
        
        mermaid.append(f"    {origin_mode} --> {target_mode} : {transition_label}")
        
    def _add_goal_states(self, mermaid: List[str], goal_modes: List[str]) -> None:
        """Add goal states to diagram."""
        if goal_modes:
            mermaid.extend([
                "    %% Goal Modes"
            ])
            for goal_mode in goal_modes:
                mermaid.append(f"    {goal_mode} --> [*]")
            mermaid.append("")
    
    def _save_mermaid_file(self, mermaid_lines: List[str], automaton_name: str) -> str:
        """
        Save Mermaid diagram to .mmd file.
        
        Args:
            mermaid_lines: Lines of Mermaid diagram code
            automaton_name: Name for the output file
            
        Returns:
            Path to saved .mmd file
            
        Raises:
            MermaidDiagramGeneratorError: If saving fails
        """
        filename = f"{automaton_name}.famd.mmd"
        file_path = self._output_dir / filename
        
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(mermaid_lines))
            
            logger.info(f"Mermaid diagram saved to: {file_path}")
            return str(file_path)
            
        except IOError as e:
            raise MermaidDiagramGeneratorError(f"Failed to save .mmd file: {e}") from e
    
    def _convert_diagram(
        self, 
        mmd_path: str, 
        automaton_name: str, 
        config: DiagramConfig
    ) -> str:
        """
        Convert .mmd file to specified output format.
        
        Args:
            mmd_path: Path to .mmd file
            automaton_name: Name for output file
            config: Diagram configuration
            
        Returns:
            Path to converted diagram file
            
        Raises:
            MermaidDiagramGeneratorError: If conversion fails
        """
        output_filename = f"{automaton_name}.famd.{config.output_format.value}"
        output_path = self._output_dir / output_filename
        
        try:
            cmd = [
                'mmdc',
                '-i', mmd_path,
                '-o', str(output_path),
                '-t', config.theme.value,
                '-b', config.background.value,
                '--scale', str(config.scale)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=30
            )
            
            logger.info(f"Successfully converted to {config.output_format.value}: {output_path}")
            if result.stdout:
                logger.debug(f"mmdc output: {result.stdout}")
                
            return str(output_path)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to convert diagram: {e.stderr}"
            logger.error(error_msg)
            raise MermaidDiagramGeneratorError(error_msg) from e
        except subprocess.TimeoutExpired:
            error_msg = "Diagram conversion timed out"
            logger.error(error_msg)
            raise MermaidDiagramGeneratorError(error_msg)
        

import yaml

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
    automaton_model = HybridAutomaton.from_famd(famd_content)

    mmd_path, output_path = HybridAutomatonModelDiagramGenerator().generate_mermaid_diagrams(automaton_model=automaton_model)