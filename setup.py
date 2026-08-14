from setuptools import find_packages, setup
from glob import glob

package_name = 'hybraut_nav'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['tests']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/worlds/models/simple_mover',
            glob('worlds/models/simple_mover/*.sdf')),
        ('share/' + package_name + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools', 'launch_testing'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='ryanmckee47@icloud.com',
    description=(
        'hybraut_nav is a ros2-rclpy navigation stack based on enabling hybrid automaton tactical layer for informed control.'
    ),
    license='MIT',
    entry_points={
        'console_scripts': [
            'strategy_node = hybraut_nav_strategy.strategy_node:main',
            'immediate_node = hybraut_nav_immediate.immediate_node:main',
            'tactical_node = hybraut_nav_tactical.tactical_node:main',
            'risk_envelope_node = hybraut_nav_risk.risk_envelope_node:main',
            'fake_riskenv_publisher = hybraut_nav.scripts.demo.fake_riskenv_publisher:main',
            'colreg_encounter_publisher = hybraut_nav.scripts.demo.colreg_encounter_publisher:main',
            'fake_map_publisher = hybraut_nav.scripts.demo.fake_map_publisher:main',
            'mover_random_walk = hybraut_nav.scripts.demo.mover_random_walk:main',
            'agent_state_bridge = hybraut_nav.scripts.demo.agent_state_bridge:main',
            'obstacles_state_bridge = hybraut_nav.scripts.demo.obstacles_state_bridge:main'
        ],
    },
)
