
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
from hybraut_lifecycle._internal.factory.famd_validator import FAMDValidator
from hybraut_lifecycle._internal.automaton import HybridAutomaton
from hybraut_lifecycle._internal.automaton.hybrid_automaton_model_diagram_generator import HybridAutomatonModelDiagramGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class HybridAutomatonFactory:
    
    """
    Factory class for creating hybrid automaton instances from a FAMD configuration.
    This class is not intended to be instantiated directly.
    """
    def __init__(self):
        raise NotImplementedError("This class is a factory and should not be instantiated directly.")

    @staticmethod
    def hybrid_automaton_registry(automaton_famd_path: str, generate_mmd_diagrams: bool = True) -> HybridAutomaton:
        """
        Validates and processes a hybrid automaton configuration dictionary:
        1. Validates against schema.
        2. Validates internal references.
        3. Dynamically binds Python functions/classes for states, resets, guards, etc.
    
        :param config: Parsed YAML configuration as dictionary
        :return: Processed configuration with dynamically bound components
        :raises SchemaError, ValidationError, ImportError
        """
        # Phase 1: load the famd.yaml file and store it in a variable
        print(f"📄 [1/4] Reading YAML config → {automaton_famd_path}")
        with open(automaton_famd_path, 'r') as f:
          automaton_famd = yaml.safe_load(f)
        print("✅ [1/4] YAML Read!.")

        # Phase 2: validation
        print("🔍 [2/4] Validating FAMD file structure...")
        FAMDValidator(automaton_famd).validate()
        print("✅ [2/4] FAMD Validated!.")
        
        # Phase 3: Dynamic imports
        print("⚡ [3/4] Parsing FAMD to Hybrid Automaton initialized model...")
        automaton_model = HybridAutomaton.from_famd(automaton_famd)
        print("✅ [3/4] automaton components initialized.")

        # Phase 4: Diagram generation
        print("📊 [4/4] Generating FAMD automaton diagram...")
        if generate_mmd_diagrams:
          HybridAutomatonModelDiagramGenerator().generate_mermaid_diagrams(automaton_model=automaton_model)
          print("✅ [4/4] Diagram generation completed!")
        else: 
          print("⏭️ [4/4] Skipping diagram generation!")
       
        print("🎉 Success! FAMD factory process completed - HybridAutomaton object ready")
        
        return automaton_model
    

# Example usage with the provided FAMD content
if __name__ == "__main__":
    # Your FAMD content from the document
  automaton_famd_path = '/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml'
  automaton = HybridAutomatonFactory.hybrid_automaton_registry(automaton_famd_path=automaton_famd_path)

