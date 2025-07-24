from setuptools import find_packages, setup
from glob import glob

package_name = 'hybraut_ros2'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['tests']),
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
        'hybraut_ros2 is a rclpy-ros2 framework for Hybrid Automaton generation.'
    ),
    license='MIT',
    entry_points={
        'console_scripts': [
        ],
    },
)
