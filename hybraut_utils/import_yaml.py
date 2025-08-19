"""
A simple utility file containing yml_import function
"""

import yaml


def import_yaml(yml_path: str):
    """utility function for importing data from a yml file and converting to a dict"""
    with open(yml_path, "r") as f:
        config = yaml.safe_load(f)

    return config
