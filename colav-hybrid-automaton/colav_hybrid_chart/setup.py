from setuptools import find_packages, setup
from glob import glob

package_name = 'colav_hybrid_chart'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test', 'scripts', 'utils']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        (f'lib/python3.10/site-packages/{package_name}/scripts', glob('scripts/*.py')),
        (f'lib/python3.10/site-packages/{package_name}/config', glob('config/*.py')),
        (f"lib/python3.10/site-packages/{package_name}/utils", glob("utils/*.py")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ryan McKee',
    maintainer_email='r.mckee@qub.ac.uk',
    description=( 
        'colav hybrid chart manages the control logic of the hybrid automaton.'
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
             "colav_hybrid_chart_node = colav_hybrid_chart.execute_colav_hybrid_chart:main"
        ],
    },
)
