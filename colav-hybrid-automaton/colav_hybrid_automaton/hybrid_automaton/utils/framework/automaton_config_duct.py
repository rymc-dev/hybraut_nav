import json
import yaml
import os
import jsonschema
import json
from jsonschema import validate
import importlib
from jsonschema.exceptions import SchemaError, ValidationError
from ament_index_python.packages import get_package_share_directory

package_name = 'colav_hybrid_automaton'

pkg_share_dir = get_package_share_directory(package_name)
config_path = os.path.join(pkg_share_dir, 'schemas', 'hybrid_automaton_config.schema.json')

with open(config_path, 'r') as f:
    schema = yaml.safe_load(f)

def validate_config_against_config_schema(config:yaml):
    try:
        pass
    except SchemaError as e:
        raise SchemaError(f'automaton_config_duct::validate_config_against_config_schema: something is wrong with schema: {str(e)}')
    except ValidationError as e:
        raise ValidationError(f'Something went wrong wehe valiadting your schema: {str(e)}') 
    
def validate_config_internal_references(config:yaml):
    """
    This function will validate the internal references for the configuration passed in to ensure that 
    every reference whether mode to transition, transition to guards and resets and mode to invariants 
    are all valid and accounted for.
    """
    pass

def dynamic_state_import_binds(states: dict): 
    """dynamically import ROS2 State type to dict"""
    for key, value in states.items():
        pkg = importlib.import_module(value['type']['pkg'])
        states[key]['type'] = getattr(pkg, value['type']['msg'])

    return states

def dynamic_reset_import_binds(resets: dict):
    for key, value in resets.items():
        module = importlib.import_module(value['module'])
        del resets[key]['module']
        resets[key]['function'] = getattr(module, value['function'])

    return resets

def dynamic_guard_import_binds(guards: dict):
    for key, value in guards.items():
        module = importlib.import_module(value['module'])
        del guards[key]['module']
        guards[key]['function'] = getattr(module, value['function'])
        
    return guards

def dynamic_dynamic_import_binds(dynamics: dict):
    for key, value in dynamics.items():
        module = importlib.import_module(value['module'])
        del dynamics[key]['module']
        dynamics[key]['function'] = getattr(module, value['function'])

    return dynamics

def dynamic_invariant_import_binds(invariants: dict):
    for key, value in invariants.items():
        module = importlib.import_module(value['module'])
        del invariants['key']['module']
        invariants[key]['function'] = getattr(module, value['function'])
    
    return invariants


def duct_and_validate_automaton_config_yml(config: yaml) -> yaml:
    """
    This function validates and ducts a config yml making it a usable python dict
    showing configuration for the Hybrid Automaton 
    
    Functionality includes: 
    1. Validates yml against schema
    2. Validates component references are valid
    3. dynamically imports functions.

    :raises: schemaException if yml invalid, ConfigException if Automaton References are invalid to each other, or Import Failed exception if any dynamic imports and binding fails
    """
    validate(instance=config, schema=schema)
    # validate_config_against_config_schema(config=config)
    # validate_config_internal_references(config=config)
    config['states'] = dynamic_state_import_binds(config['states'])
    config['resets'] = dynamic_reset_import_binds(config['resets'])
    config['guards'] = dynamic_guard_import_binds(config['guards'])
    config['dynamics'] = dynamic_dynamic_import_binds(config['dynamics'])
    config['invariants'] = dynamic_dynamic_import_binds(config['invariants'])