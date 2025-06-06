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
            "mission_control_node = hybrid_automaton.execute_hybrid_automaton_mission_control_node:main",
            "lifecycle_node = hybrid_automaton.execute_hybrid_automaton_node:main"
        ],
    },
)
