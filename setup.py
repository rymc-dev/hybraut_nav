from setuptools import find_packages, setup
from glob import glob

package_name = 'hybraut_nav'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['tests']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/amdl', glob('share/' + package_name + '/amdl/*.yml')),  # <- fixed
    ],
    install_requires=['setuptools', 'launch_testing'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='r.mckee@qub.ac.uk',
    description=(
        'hybraut_nav is a ros2-rclpy navigation stack based on enabling hybrid automaton tactical layer for informed control.'
    ),
    license='MIT',
    entry_points={
        'console_scripts': [
            'immediate_node = hybraut_nav.launch.launch_immediate_node:main',
            'tactical_node = hybraut_nav.launch.launch_tactical_node:main'
        ],
    },
)
