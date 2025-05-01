import json
import yaml
import os
import jsonschema
import json
from jsonschema import validate
import importlib
from jsonschema.exceptions import SchemaError, ValidationError

schema = None

def validate_config_against_config_schema(config:yaml):
    try:
        validate(instance=config, schema=schema)
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

def dynamic_state_import_binds(states): 
    """dynamically import ROS2 State type to dict"""
    for idx, state in enumerate(states):
        pkg = importlib.import_module(state['type']['pkg'])
        states[idx]['type'] = getattr(pkg, state['type']['msg'])

    return state

def dynamic_reset_import_binds(resets):
    for idx, reset in enumerate(resets['definitions']):
        module = importlib.import_module(reset['module'])
        del reset['module']
        resets['definitions'][idx]['function'] = getattr(module, reset['function'])

    return resets

def dynamic_guard_import_binds(guards):
    for idx, guard in enumerate(guards['definitions']):
        module = importlib.import_module(guard['module'])
        del guard['module']
        guards['definitions'][idx]['module'] = getattr(module, guard['function'])
        
    return guards

def dynamic_dynamic_import_binds(dynamics):
    pass

def dynamic_invariant_import_binds(invariants):
    pass

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

    validate_config_against_config_schema(config=config)
    validate_config_internal_references(config=config)