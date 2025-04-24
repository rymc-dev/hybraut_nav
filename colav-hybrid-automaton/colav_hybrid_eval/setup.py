from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_eval'

setup(
    name=package_name,
    version='0.0.1',
    packages=['colav_hybrid_eval.utils', 'colav_hybrid_eval.scripts.dynamics', 'colav_hybrid_eval.scripts.guards', 'colav_hybrid_eval.scripts.nodes', 'colav_hybrid_eval.scripts.resets', 'colav_hybrid_eval.config'],
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
        'colav hybrid eval contains different service functions for different scenario evaluations.'
    ),
    license='MIT',
    tests_require=['pytest', 'launch_testing', 'parameterized'],
    entry_points={
        'console_scripts': [
            "guards_node = colav_hybrid_eval.execute_guards_node:main",
            "dynamics_node = colav_hybrid_eval.execute_dynamics_node:main",
            "resets_node = colav_hybrid_eval.execute_resets_node:main"
        ],
    },
)
