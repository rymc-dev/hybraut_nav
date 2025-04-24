from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_automaton'

setup(
    name=package_name,
    version='0.0.1',
    packages=['hybrid_automaton', 'hybrid_automaton.utils', 'hybrid_automaton.scripts.dynamics', 'hybrid_automaton.scripts.guards', 'hybrid_automaton.scripts.nodes', 'hybrid_automaton.scripts.resets', 'hybrid_automaton.config'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'launch_testing'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='r.mckee@qub.ac.uk',
    description=(
        'Hybrid automaton forms part of the COLAV project.'
    ),
    license='MIT',
    tests_require=['pytest', 'launch_testing', 'parameterized'],
    entry_points={
        'console_scripts': [
            "guards_node = hybrid_automaton.execute_guards_node:main",
            "dynamics_node = hybrid_automaton.execute_dynamics_node:main",
            "resets_node = hybrid_automaton.execute_resets_node:main",
            "chart_node = hybrid_automaton.execute_chart_node:main"
        ],
    },
)
