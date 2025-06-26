import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import TimerAction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# usage
# ros2 launch colav_hybrid_automaton automaton.launch.py \
#     configuration_path:=/path/to/custom_config.yml \
#     evaluation_frequency:=50 \
#     control_frequency:=20

package_name = 'colav_hybrid_automaton'
pkg_share_dir = get_package_share_directory(package_name)

default_config_path = os.path.join(pkg_share_dir, 'automaton', 'config', 'colav-famd.yml')

def generate_launch_description():

    # Declare launch arguments
    configuration_path_arg = DeclareLaunchArgument(
        'configuration_path',
        default_value=default_config_path,
        description='Path to the hybrid automaton configuration YAML file'
    )

    evaluation_frequency_arg = DeclareLaunchArgument(
        'evaluation_frequency',
        default_value='100',
        description='Evaluation frequency in Hz'
    )

    control_frequency_arg = DeclareLaunchArgument(
        'control_frequency',
        default_value='100',
        description='Control frequency in Hz'
    )

    # Substitutions for use in Node parameters
    configuration_path = LaunchConfiguration('configuration_path')
    evaluation_frequency = LaunchConfiguration('evaluation_frequency')
    control_frequency = LaunchConfiguration('control_frequency')

    # Automaton node
    automaton = Node(
        package=package_name,
        executable='automaton',
        output='screen',
        parameters=[{
            'configuration_path': configuration_path,
            'evaluation_frequency': evaluation_frequency,
            'control_frequency': control_frequency
        }]
    )

    # mission_manager = Node(
    #     package=package_name,
    #     executable='mission_manager',
    #     output='screen'
    # )

    # Launch lifecycle transition client (delayed)
    lifecycle_client = TimerAction(
        period=2.0,  # wait 2 seconds to ensure automaton node is up
        actions=[
            Node(
                package=package_name,
                executable='automaton_configure_client',  # name of your lifecycle client script
                name='automaton_lifecycle_client',
                output='screen',
                arguments=['automaton']  # pass automaton node name as argument
            )
        ]
    )

    # # Launch mission manager (delayed further)
    # delayed_mission_manager = TimerAction(
    #     period=5.0,
    #     actions=[
    #         Node(
    #             package=package_name,
    #             executable='mission_manager',
    #             output='screen'
    #         )
    #     ]
    # )


    return LaunchDescription([
        configuration_path_arg,
        evaluation_frequency_arg,
        control_frequency_arg,
        automaton,
        lifecycle_client,
        # delayed_mission_manager
    ])