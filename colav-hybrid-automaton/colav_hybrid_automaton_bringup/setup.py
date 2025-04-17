from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_automaton_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test', 'scripts', 'utils']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='r.mckee@qub.ac.uk',
    description=( 
        'colav hybrid eval contains different service functions for different scenario evaluations.'
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
