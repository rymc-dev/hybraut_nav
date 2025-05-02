import os
import json
import yaml
import importlib
from typing import Dict, Any

from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from ament_index_python.packages import get_package_share_directory

# Load JSON Schema
package_name = 'colav_hybrid_automaton'
pkg_share_dir = get_package_share_directory(package_name)
schema_path = os.path.join(pkg_share_dir, 'schemas', 'hybrid_automaton_config.schema.json')

with open(schema_path, 'r') as f:
    schema = yaml.safe_load(f)

def _validate_config_against_schema(config: Dict[str, Any]) -> None:
    """Validates config dict against the predefined JSON schema."""
    try:
        validate(instance=config, schema=schema)
    except SchemaError as e:
        raise SchemaError(f"[Schema Error] Problem with the schema itself: {e}")
    except ValidationError as e:
        raise ValidationError(f"[Validation Error] Config does not match schema: {e}")

def _validate_internal_references(config: Dict[str, Any]) -> None:
    """
    Validates internal references in the config:
    - Modes to transitions
    - Transitions to guards/resets
    - Modes to invariants
    """
    # TODO: Implement reference validation logic
    pass

def _dynamic_import_binds(components: Dict[str, Dict[str, Any]], key_module='module', key_func='function') -> Dict[str, Any]:
    """Generic dynamic import helper for guards, resets, dynamics, and invariants."""
    if len(components) > 0:
        for key, value in components.items():
            module = importlib.import_module(value[key_module])
            del components[key][key_module]
            components[key][key_func] = getattr(module, value[key_func])
    return components

def _dynamic_state_import_binds(states: Dict[str, Any]) -> Dict[str, Any]:
    """Dynamically import ROS2 state types for each state entry."""
    if len(states) > 0:
        for key, value in states.items():
            pkg = importlib.import_module(value['type']['pkg'])
            states[key]['type'] = getattr(pkg, value['type']['msg'])
    return states

def process_automaton_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and processes a hybrid automaton configuration dictionary:
    1. Validates against schema.
    2. Validates internal references.
    3. Dynamically binds Python functions/classes for states, resets, guards, etc.
    
    :param config: Parsed YAML configuration as dictionary
    :return: Processed configuration with dynamically bound components
    :raises SchemaError, ValidationError, ImportError
    """
    _validate_config_against_schema(config)
    _validate_internal_references(config)

    config['states'] = _dynamic_state_import_binds(config['states'])
    config['resets'] = _dynamic_import_binds(config['resets'])
    config['guards'] = _dynamic_import_binds(config['guards'])
    config['dynamics'] = _dynamic_import_binds(config['dynamics'])
    config['invariants'] = _dynamic_import_binds(config['invariants'])

    return config
