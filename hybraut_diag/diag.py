from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List
import subprocess
from pathlib import Path
import logging
from hybraut_models import HybridAutomaton

from hybraut_models.core import ModeRegistry, Mode
from hybraut_models.core.transitions import TransitionRegistry, Transition

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
        self, automaton_model: HybridAutomaton, config: Optional[DiagramConfig] = None
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
            automaton_name = automaton_model.get_name()
            automaton_version = automaton_model.get_version()

            # Generate Mermaid diagram content
            mermaid_lines = self._generate_mermaid_content(
                automaton_name, automaton_version, automaton_model
            )

            # Save .mmd file
            mmd_path = self._save_mermaid_file(mermaid_lines, automaton_name)

            # Convert to desired format
            output_path = self._convert_diagram(mmd_path, automaton_name, config)

            logger.info(f"Successfully generated diagram: {output_path}")
            return mmd_path, output_path

        except Exception as e:
            raise MermaidDiagramGeneratorError(
                f"Failed to generate diagram: {str(e)}"
            ) from e

    def _setup_output_directory(self, output_directory: Optional[str]) -> Path:
        """Setup and validate output directory."""
        if output_directory:
            output_dir = Path(output_directory)
        else:
            # Default to relative path from current file
            current_file = Path(__file__).parent
            output_dir = current_file / ".." / ".github" / "assets" / "diagrams"

        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Output directory: {output_dir}")
        return output_dir

    def _ensure_mermaid_cli(self) -> None:
        """Ensure Mermaid CLI is available."""
        try:
            result = subprocess.run(
                ["mmdc", "--version"], capture_output=True, check=True, timeout=10
            )
            logger.info("Mermaid CLI is available")
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ) as e:
            error_msg = (
                "Mermaid CLI not found or not working. "
                "Please install with: npm install -g @mermaid-js/mermaid-cli"
            )
            logger.error(error_msg)
            raise MermaidDiagramGeneratorError(error_msg) from e

    def _generate_mermaid_content(
        self,
        automaton_name: HybridAutomaton,
        automaton_version: str,
        automaton_model: Dict,
    ) -> List[str]:
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
        mermaid.extend(
            [
                "stateDiagram-v2",
                f"    %% {automaton_name}:{automaton_version} State Diagram",
                "",
            ]
        )

        # Extract data with defaults
        init_mode = automaton_model.get_initial_mode()
        goal_modes = automaton_model.get_goal_modes()

        # Generate diagram sections
        self._add_initial_state(mermaid, init_mode)
        self._add_modes(
            mermaid,
            automaton_model._mode_registry,
            automaton_model._transition_registry,
        )
        self._add_goal_states(mermaid, goal_modes)

        return mermaid

    def _add_initial_state(self, mermaid: List[str], init_mode: str) -> None:
        """Add initial state to diagram."""
        if isinstance(init_mode, int):
            mermaid.extend(["    %% Initial Mode", f"    [*] --> {init_mode}", ""])

    def _add_modes(
        self, mermaid: List[str], modes: ModeRegistry, transitions: TransitionRegistry
    ) -> None:
        """Add modes with detailed information to diagram."""
        if not modes:
            return

        mermaid.append("\t%% Modes")

        for mode_id in modes.get_mode_ids():
            mode: Mode = modes.get_mode(mode_id)

            mode_index = mode_id
            mode_name = mode.get_name()
            invariants = mode.get_invariant_refs()
            dynamics = mode.get_dynamics_ref()
            description = mode.get_description()

            # State definition
            mermaid.append(f"\t%% {mode_name} Mode details")
            mermaid.append(f"    {mode_index} : {mode_index}.{mode_name}")

            # Add detailed note if additional info exists
            if any([invariants, dynamics, description]):
                self._add_mode_note(
                    mermaid, mode_name, mode_index, description, invariants, dynamics
                )

            mermaid.append("")
            mermaid.append(f"\t%% {mode_name} transitions.")
            if mode.get_transition_refs() is not None:
                for transition_ref in mode.get_transition_refs():
                    transition: Transition = transitions.get_transition_by_name(
                        transition_ref
                    )

                    origin_mode = mode_id
                    transition_name = transition.get_name()
                    transition_priority = transition.get_priority()
                    transition_target_mode = transition.get_target_mode()
                    guard_name = transition.get_guard_refs()
                    reset_name = transition.get_reset_refs()

                    self._add_transition_edge(
                        mermaid,
                        transition_name,
                        origin_mode,
                        transition_priority,
                        transition_target_mode,
                        guard_name,
                        reset_name,
                    )

                mermaid.append("")

    def _add_mode_note(
        self,
        mermaid: List[str],
        mode_name: str,
        mode_index: str,
        description: str,
        invariants: str,
        dynamics: str,
    ) -> None:
        """Add detailed note for a mode."""
        mermaid.extend(
            [
                f"    note left of {mode_index}",
            ]
        )

        if description:
            mermaid.append(f"        <b>description</b>")
        if invariants:
            mermaid.append(f"        <b>invariants</b>: {invariants}")
        if dynamics:
            mermaid.append(f"        <b>dynamics</b>: {dynamics}")

        mermaid.append("    end note")

    def _add_transition_edge(
        self,
        mermaid: List[str],
        transition_key: str,
        origin_mode: str,
        priority: int,
        target_mode: str,
        guard: str,
        reset: str,
    ) -> None:
        """Add a single transition edge."""
        transition_label = (
            f"<b>Transition {transition_key}</b>"
            f"[<b>guards</b> = {guard}, <b>resets</b> = {reset}, <b>priority</b> = {priority}]"
        )

        mermaid.append(f"    {origin_mode} --> {target_mode} : {transition_label}")

    def _add_goal_states(self, mermaid: List[str], goal_modes: List[str]) -> None:
        """Add goal states to diagram."""
        if goal_modes:
            mermaid.extend(["    %% Goal Modes"])
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
        self, mmd_path: str, automaton_name: str, config: DiagramConfig
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
                "mmdc",
                "-i",
                mmd_path,
                "-o",
                str(output_path),
                "-t",
                config.theme.value,
                "-b",
                config.background.value,
                "--scale",
                str(config.scale),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )

            logger.info(
                f"Successfully converted to {config.output_format.value}: {output_path}"
            )
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

if __name__ == "__main__":
    from hybraut_factory.amdl.models import HybridAutomatonFactory

    amdl_path = "/home/ryan/ros2_ws/src/hybraut_ros2/example_amdls/hybraut_tb3.amdl.yml"
    with open(amdl_path, "r") as f:
        amdl_content = yaml.safe_load(f)

    automaton_model = HybridAutomatonFactory.register_automaton(amdl_content)

    (
        mmd_path,
        output_path,
    ) = HybridAutomatonModelDiagramGenerator().generate_mermaid_diagrams(
        automaton_model=automaton_model
    )
