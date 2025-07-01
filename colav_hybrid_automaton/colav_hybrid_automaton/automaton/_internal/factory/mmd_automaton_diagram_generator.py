"""
Mermaid Diagram Generator for Hybrid Automaton Visualization

This module provides functionality to generate Mermaid state diagrams from 
hybrid automaton configuration data and convert them to various output formats.
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

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


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    theme: Theme = Theme.FOREST
    background: str = "transparent"
    scale: int = 2
    output_format: OutputFormat = OutputFormat.SVG


class MermaidDiagramGeneratorError(Exception):
    """Custom exception for diagram generation errors."""
    pass


class MermaidDiagramGenerator:
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
        init_mode = automaton_data.get('initial_mode', '')
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
        if init_mode:
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
            mode_index = mode_data.get('index', '')
            invariants = mode_data.get('invariants', '')
            dynamics = mode_data.get('dynamics', '')
            description = mode_data.get('description', '')
            
            # State definition
            mermaid.append(f"    {mode_key} : {mode_index}.{mode_key}")
            
            # Add detailed note if additional info exists
            if any([invariants, dynamics, description]):
                self._add_mode_note(mermaid, mode_key, mode_index, description, invariants, dynamics)
            
            mermaid.append("")
    
    def _add_mode_note(
        self, 
        mermaid: List[str], 
        mode_key: str, 
        mode_index: str, 
        description: str, 
        invariants: str, 
        dynamics: str
    ) -> None:
        """Add detailed note for a mode."""
        mermaid.extend([
            f"    note left of {mode_key}",
            "        =====================",
            f"        <b>{mode_index}.{mode_key}</b>",
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
            
            if not target_mode:
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
                '-b', config.background,
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


def _load_yml(yml_path: str) -> Dict:
    """Load YAML configuration file."""
    try:
        with open(yml_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise MermaidDiagramGeneratorError(f"Configuration file not found: {yml_path}")
    except yaml.YAMLError as e:
        raise MermaidDiagramGeneratorError(f"Invalid YAML file: {e}")


def generate_mermaid_diagrams(
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
    generator = MermaidDiagramGenerator(output_directory)
    return generator.generate_mermaid_diagrams(automaton_data, config)


def main():
    """Main execution function for testing."""
    try:
        from ament_index_python.packages import get_package_share_directory
        
        # Get package directory and load automaton data
        package_name = 'colav_hybrid_automaton'
        pkg_share_directory = get_package_share_directory(package_name)
        config_path = os.path.join(pkg_share_directory, 'automaton', 'config', 'colav-famd.yml')
        
        # Load automaton data
        automaton_data = _load_yml(config_path)
        
        # Create custom config for dark theme
        diagram_config = DiagramConfig(
            theme=Theme.DARK,
            background='transparent',
            output_format=OutputFormat.SVG
        )
        
        # Generate diagrams
        mmd_path, output_path = generate_mermaid_diagrams(automaton_data, config=diagram_config)
        
        logger.info(f"Generated files:")
        logger.info(f"  Mermaid file: {mmd_path}")
        logger.info(f"  Output file: {output_path}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == '__main__':
    main()