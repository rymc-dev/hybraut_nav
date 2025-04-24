from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_eval'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test', 'scripts', 'utils']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        (f'lib/python3.10/site-packages/{package_name}/scripts/nodes', glob('scripts/nodes/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/scripts/guards', glob('scripts/guards/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/scripts/resets', glob('scripts/resets/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/scripts/dynamics', glob('scripts/dynamics/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/config', glob('config/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/utils', glob('utils/*.py')),
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
