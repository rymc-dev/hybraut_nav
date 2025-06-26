from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_automaton'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['tests', 'schemas', 'config']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/automaton' + '/config', glob('colav_hybrid_automaton/automaton/colav-famd.yml')),
        ('share/' + package_name + '/automaton' + '/schemas', glob('colav_hybrid_automaton/automaton/factory/schemas/famd.schema.json')) 
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
            "mission_manager = colav_hybrid_automaton.automaton_mission_manager:main",
            "automaton = colav_hybrid_automaton.automaton.automaton_node:main",
            "automaton_configure_client =  colav_hybrid_automaton.automaton_lifecycle_transition_cli:main"
        ],
    },
)
