# !/usr/bin/env python
"""
Main entry point for the Hybraut Diagram Generator.
Mainly for testing and showing how the diagram generator works, not for use in production.
"""

import yaml
from hybraut_diag_gen import HybrautDiag

"""=== Code below here is for testing not for production use. ==="""


def main():
    from hybraut_factory.amdl.models import HybridAutomatonFactory

    amdl_path = "/home/ryan/ros2_ws/src/hybraut_ros2/example_amdls/hybraut_tb3.amdl.yml"
    with open(amdl_path, "r") as f:
        amdl_content = yaml.safe_load(f)
    automaton_model = HybridAutomatonFactory.register_automaton(amdl_content)
    generator = HybrautDiag()
    mmd_path, output_path = generator.generate_mermaid_diagrams(
        automaton_model=automaton_model
    )


if __name__ == "__main__":
    main()
