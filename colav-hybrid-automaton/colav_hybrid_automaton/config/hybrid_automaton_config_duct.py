import yaml
import os
import importlib
import jsonschema
import json
from jsonschema import validate

# class HybridAutomatonConfigFunctionRegistry:
#     def __init__(self):
#         self.registry = {}

def dynamic_state_imports(states):
    for idx, state in enumerate(states):
        pkg = importlib.import_module(state['type']['pkg'])
        states[idx]['type'] = getattr(pkg, state['type']['msg'])

    return states

def dynamic_guard_imports(guards):
    for idx, guard in enumerate(guards['definitions']):
        module = importlib.import_module(guard['module'])
        del guard['module']
        guards['definitions'][idx]['module'] = getattr(module, guard['function'])
        
    return guards

def dynamic_reset_imports(resets):
    for idx, reset in enumerate(resets['definitions']):
        module = importlib.import_module(reset['module'])
        del reset['module']
        resets['definitions'][idx]['function'] = getattr(module, reset['function'])

    return resets

def dynamic_invariant_imports(invariants):
    pass

def main():
        
    schema = None
    with open(os.path.join(os.path.dirname(__file__), 'hybrid_automaton_config.schema.json')) as stream:
        try:
            schema = json.load(stream)
        except json.JSONDecodeError as exc:
            print(f"Error loading JSON schema: {exc}")

    config = None
    with open(os.path.join(os.path.dirname(__file__), 'hybrid_automaton_config.yml')) as stream:
        try:
            config = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    try: 
        validate(instance=config, schema=schema)
    except Exception as e:
        print (str(e))
        exit(0)
    print (config)

    # config['states'] = dynamic_state_imports(config['states'])
    # config['guards'] = dynamic_guard_imports(config['guards'])
    # config['resets'] = dynamic_reset_imports(config['resets'])
    # config['invariants'] = dynamic_invariant_imports(config['invariants'])

    # print (config)


if __name__ == '__main__':
    main()