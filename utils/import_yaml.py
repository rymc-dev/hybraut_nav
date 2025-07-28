import yaml

def load_yml(yml_path: str):
    with open(yml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config