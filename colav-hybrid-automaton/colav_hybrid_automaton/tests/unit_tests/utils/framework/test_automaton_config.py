# from hybrid_automaton.utils import duct_and_validate_automaton_config_yml
# import pytest

# from ament_index_python.packages import get_package_share_directory
# import os
# import yaml

# package_name = 'colav_hybrid_automaton'

# pkg_share_dir = get_package_share_directory(package_name)
# config_path = os.path.join(pkg_share_dir, 'config', 'hybrid_automaton_config.yml')

# def test_duct_and_validate_automaton_config_yml():
#     with open(config_path, 'r') as f:
#         config = yaml.safe_load(f)

#     duct_and_validate_automaton_config_yml(config)

# if __name__ == '__main__':
#     test_duct_and_validate_automaton_config_yml()