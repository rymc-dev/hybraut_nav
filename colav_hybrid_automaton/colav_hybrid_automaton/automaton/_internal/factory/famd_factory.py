"""
Formal Automaton Model Description (famd) Factory Module

This module provides a factory for converting a Formal Automaton Model Description (FAMD) yml configuration
into a hybrid automaton runtime registry dict. This can be utilized to create a hybrid automaton instance
which can be utilized within the hybrid automaton lifecyle framework. 
"""

import yaml
import importlib
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess
from pathlib import Path

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


class HybridAutomatonFactory:
    """
    Factory class for creating hybrid automaton instances from a FAMD configuration.
    This class is not intended to be instantiated directly.
    """
    class FAMDValidator:
        def __init__(self, famd: yaml) -> None:
            """Initialize validator with FAMD content."""
            self.famd = famd
            self.errors = []
            self.warnings = []

        def validate(self) -> Tuple[bool, List[str], List[str]]:
            """Run complete validation and return results."""
            try:
                self.errors = []
                self.warnings = []
                
                # Core validation checks
                self._validate_structure()
                self._validate_modes()
                self._validate_transitions()
                self._validate_guards()
                self._validate_resets()
                self._validate_invariants()
                self._validate_dynamics()
                self._validate_states()
                self._validate_references()
                
                is_valid = len(self.errors) == 0
                return is_valid, self.errors, self.warnings
            except yaml.YAMLError as e:
                self.errors.append(f"YAML parsing error: {str(e)}")
                return False, self.errors, self.warnings

        def _validate_structure(self):
            """Validate basic FAMD structure."""
            required_sections = ['states', 'modes', 'transitions', 'guards', 
                            'resets', 'invariants', 'dynamics', 'initial_mode']
            
            for section in required_sections:
                if section not in self.famd:
                    self.errors.append(f"Missing required section: {section}")

        def _validate_modes(self):
            """Validate mode definitions."""
            if 'modes' not in self.famd:
                return
            
            modes = self.famd['modes']
            mode_names = set()
            
            for mode_index, mode_def in modes.items():
                # Check required fields
                required_fields = ['name', 'description', 'dynamics', 'invariants', 'transitions']
                for field in required_fields:
                    if field not in mode_def:
                        self.errors.append(f"Mode with index '{mode_index}' missing required field: {field}")
                
                # Check for duplicate names
                if 'name' in mode_def:
                    name = mode_def['name']
                    if name in mode_names:
                        self.errors.append(f"Duplicate mode name '{name}' found in mode with index '{mode_index}'")
                    mode_names.add(name)
                
                # Validate transition priorities within each mode
                self._validate_mode_transition_priorities(mode_index, mode_def)

        def _validate_mode_transition_priorities(self, mode_name: str, mode_def: Dict):
            """Validate transition priorities within a mode."""
            if 'transitions' not in mode_def:
                return
                
            transitions = mode_def['transitions']
            priorities = []
            
            if not transitions == []:
                for transition_name, transition_info in transitions.items():
                    if 'priority' in transition_info:
                        priority = transition_info['priority']
                        priorities.append((priority, transition_name))
                
                # Check for duplicate priorities
                priority_counts = defaultdict(list)
                for priority, trans_name in priorities:
                    priority_counts[priority].append(trans_name)
                
                for priority, trans_names in priority_counts.items():
                    if len(trans_names) > 1:
                        self.errors.append(
                            f"Mode '{mode_name}' has duplicate priority {priority} "
                            f"for transitions: {', '.join(trans_names)}"
                        )

        def _validate_transitions(self):
            """Validate transition definitions."""
            if 'transitions' not in self.famd:
                return
                
            transitions = self.famd['transitions']
            if not transitions == []:
                for trans_name, trans_def in transitions.items():
                    # Check required fields
                    required_fields = ['origin_modes', 'target_mode', 'guard']
                    for field in required_fields:
                        if field not in trans_def:
                            self.errors.append(f"Transition '{trans_name}' missing required field: {field}")
                    
                    # Validate origin_modes and origin_priorities alignment
                    if 'origin_modes' in trans_def and 'origin_priorities' in trans_def:
                        modes = trans_def['origin_modes']
                        priorities = trans_def['origin_priorities']
                        
                        if len(modes) != len(priorities):
                            self.errors.append(
                                f"Transition '{trans_name}': origin_modes ({len(modes)}) and "
                                f"origin_priorities ({len(priorities)}) must have same length"
                            )
                    
                    # Check that target_mode exists
                    if 'target_mode' in trans_def:
                        target = trans_def['target_mode']
                        if 'modes' in self.famd and target not in self.famd['modes']:
                            self.errors.append(f"Transition '{trans_name}' targets non-existent mode: {target}")
                    
                    # Check that origin_modes exist
                    if 'origin_modes' in trans_def:
                        for origin_mode in trans_def['origin_modes']:
                            if 'modes' in self.famd and origin_mode not in self.famd['modes']:
                                self.errors.append(
                                    f"Transition '{trans_name}' references non-existent origin mode: {origin_mode}"
                                )

        def _validate_guards(self):
            """Validate guard definitions."""
            if 'guards' not in self.famd:
                return
                
            guards = self.famd['guards']
            
            for guard_name, guard_def in guards.items():
                # Check required fields
                required_fields = ['module', 'class_name', 'description', 'state_inputs', 'configuration']
                for field in required_fields:
                    if field not in guard_def:
                        self.errors.append(f"Guard '{guard_name}' missing required field: {field}")
                
                # Validate state_inputs reference existing states
                if 'state_inputs' in guard_def:
                    self._validate_state_references(guard_name, guard_def['state_inputs'], 'guard')

        def _validate_resets(self):
            """Validate reset definitions."""
            if 'resets' not in self.famd:
                return
                
            resets = self.famd['resets']
            
            for reset_name, reset_def in resets.items():
                # Check required fields
                required_fields = ['module', 'class_name', 'description', 'state_inputs', 'reset_targets', 'configuration']
                for field in required_fields:
                    if field not in reset_def:
                        self.errors.append(f"Reset '{reset_name}' missing required field: {field}")
                
                # Validate state references
                if 'state_inputs' in reset_def:
                    self._validate_state_references(reset_name, reset_def['state_inputs'], 'reset')
                if 'state_outputs' in reset_def:
                    self._validate_state_references(reset_name, reset_def['state_outputs'], 'reset')

        def _validate_invariants(self):
            """Validate invariant definitions."""
            if 'invariants' not in self.famd:
                return
                
            invariants = self.famd['invariants']
            
            for inv_name, inv_def in invariants.items():
                # Check required fields
                required_fields = ['module', 'class_name', 'description', 'state_inputs', 'configuration']
                for field in required_fields:
                    if field not in inv_def:
                        self.errors.append(f"Invariant '{inv_name}' missing required field: {field}")
                
                # Validate state_inputs if present
                if 'state_inputs' in inv_def:
                    self._validate_state_references(inv_name, inv_def['state_inputs'], 'invariant')

        def _validate_dynamics(self):
            """Validate dynamics definitions."""
            if 'dynamics' not in self.famd:
                return

            dynamics = self.famd['dynamics']
            
            for dyn_name, dyn_def in dynamics.items():
                # Required top-level fields
                required_fields = ['module', 'class_name', 'state_inputs', 'dynamic_outputs']
                for field in required_fields:
                    if field not in dyn_def:
                        self.errors.append(f"Dynamics '{dyn_name}' missing required field: '{field}'")

                # Validate state_inputs
                if 'state_inputs' in dyn_def:
                    self._validate_state_references(dyn_name, dyn_def['state_inputs'], 'dynamic')

                # Validate dynamic_outputs
                if 'dynamic_outputs' in dyn_def:
                    dyn_out = dyn_def['dynamic_outputs']
                    names = dyn_out.get('dynamic_parameter_names', [])
                    types = dyn_out.get('dynamic_parameter_value_types', [])
                    metrics = dyn_out.get('dynamic_parameter_metrics', [])

                    if not (len(names) == len(types) == len(metrics)):
                        self.errors.append(
                            f"Dynamics '{dyn_name}' has mismatched lengths in dynamic_outputs: "
                            f"{len(names)} names, {len(types)} types, {len(metrics)} metrics"
                        )

        def _validate_states(self):
            """Validate state definitions."""
            if 'states' not in self.famd:
                return
                
            states = self.famd['states']
            
            for state_name, state_def in states.items():
                # Check required fields
                required_fields = ['topic', 'type']
                for field in required_fields:
                    if field not in state_def:
                        self.errors.append(f"State '{state_name}' missing required field: {field}")
                
                # Validate type structure
                if 'type' in state_def:
                    type_def = state_def['type']
                    if not isinstance(type_def, dict) or 'pkg' not in type_def or 'msg' not in type_def:
                        self.errors.append(f"State '{state_name}' type must have 'pkg' and 'msg' fields")

        def _validate_state_references(self, component_name: str, state_list: List[str], component_type: str):
            """Validate that referenced states exist."""
            if 'states' not in self.famd:
                return
                
            available_states = set(self.famd['states'].keys())
            
            for state_ref in state_list:
                if state_ref not in available_states:
                    self.errors.append(
                        f"{component_type.title()} '{component_name}' references non-existent state: {state_ref}"
                    )

        def _validate_references(self):
            """Validate cross-references between components."""
            # Check that modes reference existing dynamics and invariants
            if 'modes' in self.famd:
                for mode_name, mode_def in self.famd['modes'].items():
                    # Check dynamics reference
                    if 'dynamics' in mode_def:
                        dyn_ref = mode_def['dynamics']
                        if 'dynamics' in self.famd and 'dynamic_classes' in self.famd['dynamics']:
                            if dyn_ref not in self.famd['dynamics']['dynamic_classes']:
                                self.errors.append(
                                    f"Mode '{mode_name}' references non-existent dynamics: {dyn_ref}"
                                )
                    
                    # Check invariants reference
                    if 'invariants' in mode_def:
                        inv_ref = mode_def['invariants']
                        if 'invariants' in self.famd and inv_ref not in self.famd['invariants']:
                            self.errors.append(
                                f"Mode '{mode_name}' references non-existent invariant: {inv_ref}"
                            )
                    
                    # Check transition references
                    if 'transitions' in mode_def:
                        if not mode_def['transitions'] == []:
                            for trans_name in mode_def['transitions'].keys():
                                if 'transitions' in self.famd and trans_name not in self.famd['transitions']:
                                    self.errors.append(
                                        f"Mode '{mode_name}' references non-existent transition: {trans_name}"
                                    )
            
            # Check that transitions reference existing guards and resets
            if 'transitions' in self.famd:
                for trans_name, trans_def in self.famd['transitions'].items():
                    # Check guard reference
                    if 'guard' in trans_def:
                        guard_ref = trans_def['guard']
                        if 'guards' in self.famd and guard_ref not in self.famd['guards']:
                            self.errors.append(
                                f"Transition '{trans_name}' references non-existent guard: {guard_ref}"
                            )
                    
                    # Check reset reference
                    if 'reset' in trans_def and trans_def['reset'] is not None:
                        reset_ref = trans_def['reset']
                        if 'resets' in self.famd and reset_ref not in self.famd['resets']:
                            self.errors.append(
                                f"Transition '{trans_name}' references non-existent reset: {reset_ref}"
                            )
            
            # Check initial_mode reference
            if 'initial_mode' in self.famd:
                init_mode = self.famd['initial_mode']
                if 'modes' in self.famd and init_mode not in self.famd['modes']:
                    self.errors.append(f"initial_mode references non-existent mode: {init_mode}")
            
            # Check goal_modes references
            if 'goal_modes' in self.famd:
                for goal_mode in self.famd['goal_modes']:
                    if 'modes' in self.famd and goal_mode not in self.famd['modes']:
                        self.errors.append(f"goal_modes references non-existent mode: {goal_mode}")

        def print_validation_report(self):
            """Print a formatted validation report."""
            print("=" * 60)
            print("COLAV Hybrid Automaton FAMD Structure Validation Report")
            print("=" * 60)
            
            if not self.errors and not self.warnings:
                print("✅ VALIDATION PASSED - No issues found!")
                return
            
            if self.errors:
                print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
                print("-" * 40)
                for i, error in enumerate(self.errors, 1):
                    print(f"{i:2d}. {error}")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                print("-" * 40)
                for i, warning in enumerate(self.warnings, 1):
                    print(f"{i:2d}. {warning}")
            
            print("\n" + "=" * 60)
            if self.errors:
                print("❌ STRUCTURE VALIDATION FAILED - Please fix the errors above")
            else:
                print("✅ STRUCTURE VALIDATION PASSED - Only warnings found")

    class FAMDDiagramGenerator:
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
            automaton_data: Dict, 
            config: Optional[DiagramConfig] = None
        ) -> Tuple[str, str]:
            """
            Generate Mermaid diagrams from automaton data.
            
            Args:
                automaton_data: Dictionary containing automaton configuration
                config: Diagram configuration options
                
            Returns:
                Tuple of (mmd_file_path, output_file_path)
                
            Raises:
                MermaidDiagramGeneratorError: If generation fails
            """
            if config is None:
                config = DiagramConfig()
                
            try:
                automaton_name = automaton_data.get('automaton_name', 'Automaton')
                
                # Generate Mermaid diagram content
                mermaid_lines = self._generate_mermaid_content(automaton_name, automaton_data)
                
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
        
        def _generate_mermaid_content(self, automaton_name: str, automaton_data: Dict) -> List[str]:
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
            init_mode = automaton_data.get('initial_mode', -1)
            goal_modes = automaton_data.get('goal_modes', [])
            modes = automaton_data.get('modes', {})
            transitions = automaton_data.get('transitions', {})
            
            # Generate diagram sections
            self._add_initial_state(mermaid, init_mode)
            self._add_modes(mermaid, modes)
            self._add_transitions(mermaid, transitions)
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
                
            mermaid.append("    %% Modes")
            
            for mode_key, mode_data in modes.items():
                mode_index = mode_key
                mode_name = mode_data.get('name', '')
                invariants = mode_data.get('invariants', '')
                dynamics = mode_data.get('dynamics', '')
                description = mode_data.get('description', '')
                
                # State definition
                mermaid.append(f"    {mode_index} : {mode_index}.{mode_name}")
                
                # Add detailed note if additional info exists
                if any([invariants, dynamics, description]):
                    self._add_mode_note(mermaid, mode_name, mode_index, description, invariants, dynamics)
                
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
                mermaid.append(f"        <b>invariant</b>: {invariants}")
            if dynamics:
                mermaid.append(f"        <b>dynamics</b>: {dynamics}")
                
            mermaid.append("    end note")
        
        def _add_transitions(self, mermaid: List[str], transitions: Dict) -> None:
            """Add transitions to diagram."""
            if not transitions:
                return
                
            mermaid.append("    %% Transitions")
            
            for transition_key, transition_data in transitions.items():
                origin_modes = transition_data.get('origin_modes', [])
                origin_priorities = transition_data.get('origin_priorities', [])
                target_mode = transition_data.get('target_mode', '')
                guard = transition_data.get('guard', '')
                reset = transition_data.get('reset', 'null')
                
                if target_mode is None:
                    logger.warning(f"Skipping transition {transition_key}: no target mode")
                    continue
                
                self._add_transition_edges(
                    mermaid, transition_key, origin_modes, origin_priorities, 
                    target_mode, guard, reset
                )
        
        def _add_transition_edges(
            self, 
            mermaid: List[str], 
            transition_key: str, 
            origin_modes: List[str], 
            origin_priorities: List[int], 
            target_mode: str, 
            guard: str, 
            reset: str
        ) -> None:
            """Add individual transition edges."""
            for idx, origin_mode in enumerate(origin_modes):
                priority = origin_priorities[idx] if idx < len(origin_priorities) else 0
                
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

    def __init__(self):
        raise NotImplementedError("This class is a factory and should not be instantiated directly.")

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

    @staticmethod
    def _dynamic_state_import_binds(states: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically import ROS2 state types for each state entry."""
        if len(states) > 0:
            for key, value in states.items():
                pkg = importlib.import_module(value['type']['pkg'])
                states[key]['type'] = getattr(pkg, value['type']['msg'])
        return states
    
    @staticmethod
    def _validate_famd_content(famd_content: str):
        """Validate FAMD content and return results."""
        validator = HybridAutomatonFactory.FAMDValidator(famd_content)
        is_valid, errors, warnings = validator.validate()
        validator.print_validation_report()
        return is_valid, errors, warnings
    
    @staticmethod
    def _generate_automaton_diagrams(
        automaton_data: Dict, 
        output_directory: Optional[str] = None,
        config: Optional[DiagramConfig] = None
    ) -> Tuple[str, str]:
        """
        Public interface for generating Mermaid diagrams.
        
        Args:
            automaton_data: Dictionary containing automaton configuration
            output_directory: Directory to save diagrams (optional)
            config: Diagram configuration (optional)
            
        Returns:
            Tuple of (mmd_file_path, output_file_path)
            
        Raises:
            MermaidDiagramGeneratorError: If generation fails
        """
        generator = HybridAutomatonFactory.FAMDDiagramGenerator(output_directory)
        return generator.generate_mermaid_diagrams(automaton_data, config)

    def _initialize_automaton(automaton_famd: yaml, component_type: str):
        for component_name, component_def in automaton_famd[component_type].items():
            automaton_famd[component_type][component_name]['instance'] = component_def['class'](
                **component_def.get('configuration', {})
            )
            del automaton_famd[component_type][component_name]['class']
            del automaton_famd[component_type][component_name]['configuration']
        
        return automaton_famd

    @staticmethod
    def hybrid_automaton_registry(automaton_famd: yaml, generate_mmd_diagrams: bool = True) -> Dict[str, Any]:
        """
        Validates and processes a hybrid automaton configuration dictionary:
        1. Validates against schema.
        2. Validates internal references.
        3. Dynamically binds Python functions/classes for states, resets, guards, etc.
    
        :param config: Parsed YAML configuration as dictionary
        :return: Processed configuration with dynamically bound components
        :raises SchemaError, ValidationError, ImportError
        """
        # Phase 1: Validation
        print("🔍 [1/4] Validating FAMD file structure...")
        HybridAutomatonFactory._validate_famd_content(automaton_famd)
        print("")
        
        # Phase 2: Dynamic imports
        print("⚡ [2/4] Dynamically importing components...")
        print("  ├─ Loading state classes...")
        automaton_famd['states'] = HybridAutomatonFactory._dynamic_state_import_binds(automaton_famd['states'])
        print("  ├─ Loading reset functions...")
        automaton_famd['resets'] = HybridAutomatonFactory._dynamic_import_binds(automaton_famd['resets'])
        print("  ├─ Loading guard conditions...")
        automaton_famd['guards'] = HybridAutomatonFactory._dynamic_import_binds(automaton_famd['guards'])
        print("  ├─ Loading dynamics...")
        automaton_famd['dynamics'] = HybridAutomatonFactory._dynamic_import_binds(automaton_famd['dynamics'])
        print("  └─ Loading invariants...")
        automaton_famd['invariants'] = HybridAutomatonFactory._dynamic_import_binds(automaton_famd['invariants'])
        print("✅ [2/4] Component imports completed!")
        
        # Phase 3: Intialize the automaton components with the static configurations
        print("🔧 [3/4] Initializing automaton components...")
        component_types = ['guards', 'resets', 'dynamics', 'invariants']
        for component_type in component_types:
            automaton_famd = HybridAutomatonFactory._initialize_automaton(automaton_famd, component_type)

        print("✅ [3/4] automaton components initialized.")

        # Phase 4: Diagram generation
        print("📊 [4/4] Generating FAMD automaton diagram...")
        HybridAutomatonFactory._generate_automaton_diagrams(automaton_famd)
        print("✅ [4/4] Diagram generation completed!")
        
        print("🎉 FAMD factory process completed successfully!")
        
        return automaton_famd
    

# Example usage with the provided FAMD content
if __name__ == "__main__":
    # Your FAMD content from the document
    famd_content = '''# COLAV Hybrid Automaton Formal Automaton Model Definition (FAMD)
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
      - update_hz: 10.0
      - timeout_sec: 0.5
      - buffer_size: 100

  obstacles_state:
    topic: "/state/obstacles"
    description: "State of the obstacles in the environment."
    type:
      pkg: "colav_interfaces.msg"
      msg: "ObstaclesState"
    params:
      - update_hz: 4.0
      - timeout_sec: 1.0

  unsafe_set_state:
    topic: "/state/unsafe_set"
    description: "State of the unsafe set, indicating unsafe conditions for the agent."
    type:
      pkg: "colav_interfaces.msg"
      msg: "UnsafeSetState"
    params:
      - update_hz: 2.0
      - timeout_sec: 1.5

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
    invariants: trivial_invariant
    transitions:
      enter_emergency_fallback:
        priority: 0
      waypoint_arrival:
        priority: 1
      plan_evasive_maneuver:
        priority: 2
      correct_heading:
        priority: 3

  1:
    name: t2los
    description: "Transition to Line of Sight (T2LOS) mode with proportional yaw rate control"
    dynamics: t2los_pid_controller
    invariants: trivial_invariant
    transitions:
      enter_emergency_fallback:
        priority: 0
      heading_aligned:
        priority: 1
      waypoint_arrival:
        priority: 2

  2:
    name: waypoint_reached
    description: "Waypoint reached mode, indicating successful navigation to a waypoint"
    dynamics: no_op_controller
    invariants: is_goal_waypoint_invariant
    transitions:
      proceed_to_next_waypoint:
        priority: 0

  3:
    name: fallback
    description: "Fallback mode for emergency conditions, no active control"
    dynamics: no_op_controller
    invariants: failing_invariant
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
    '''
    
    automaton = HybridAutomatonFactory.hybrid_automaton_registry(automaton_famd=yaml.safe_load(famd_content))

