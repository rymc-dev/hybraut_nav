from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_automaton'

setup(
    name=package_name,
    version='0.0.1',
    packages=['hybrid_automaton', 'hybrid_automaton.utils', 'hybrid_automaton.utils.framework', 'hybrid_automaton.utils.colav', 'hybrid_automaton.scripts.dynamics', 'hybrid_automaton.scripts.guards', 'hybrid_automaton.scripts.nodes', 'hybrid_automaton.scripts.resets', 'hybrid_automaton.scripts.invariants', 'hybrid_automaton.config'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yml')),
        ('share/' + package_name + '/schemas', glob('schemas/*.schema.json'))
    ],
    install_requires=['setuptools', 'launch_testing'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='r.mckee@qub.ac.uk',
    description=(
        'Hybrid automaton forms part of the COLAV project.'
    ),
    license='MIT',
    entry_points={
        'console_scripts': [
            "dynamic_feedback_node = hybrid_automaton.execute_dynamics_manager_node:main",
            "lifecycle_manager_node = hybrid_automaton.execute_lifecycle_manager_node:main",
            "transition_engine_node = hybrid_automaton.execute_transition_engine_node:main",
            "transition_evaluation_node = hybrid_automaton.execute_transition_evaluation_node:main",
            "state_resets_srv_node = hybrid_automaton.execute_state_resets_srv_node:main"
        ],
    },
)
