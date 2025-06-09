from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, RegisterEventHandler
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch_ros.actions import LifecycleNode, Node


pkg_name = 'colav_hybrid_automaton'

def generate_launch_description():
    # Declare arguments
    configuration_path_arg = DeclareLaunchArgument(
        'configuration_path',
        default_value=''
    )
    evaluation_frequency_arg = DeclareLaunchArgument(
        'evaluation_frequency',
        default_value='100'
    )
    control_frequency_arg = DeclareLaunchArgument(
        'control_frequency',
        default_value='100'
    )

    configuration_path = LaunchConfiguration('configuration_path')
    evaluation_frequency = LaunchConfiguration('evaluation_frequency')
    control_frequency = LaunchConfiguration('control_frequency')

    # Lifecycle node
    automaton_node = LifecycleNode(
        package=pkg_name,
        executable='automaton',
        name='hybrid_automaton',
        namespace='',
        output='screen',
        parameters=[{
            'configuration_path': configuration_path,
            'evaluation_frequency': evaluation_frequency,
            'control_frequency': control_frequency
        }]
    )

    # Lifecycle transition client (configure node)
    transition_client_node = Node(
        package='colav_hybrid_automaton',
        executable='lifecycle_transition_client',
        name='automaton_lifecycle_client',
        namespace='',
        output='screen',
        arguments=['hybrid_automaton'],
    )

    # Start this client after a few seconds to allow lifecycle node startup
    transition_client_timer = TimerAction(
        period=3.0,
        actions=[transition_client_node]
    )

    # Mission Manager node (only launched after the client exits)
    mission_manager_node = Node(
        package='colav_hybrid_automaton',
        executable='mission_manager',
        name='mission_manager',
        namespace='',
        output='screen'
    )

    # Event handler: after transition client exits, launch mission_manager
    launch_mission_manager = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=transition_client_node,
            on_exit=[mission_manager_node]
        )
    )

    return LaunchDescription([
        configuration_path_arg,
        evaluation_frequency_arg,
        control_frequency_arg,
        automaton_node,
        transition_client_timer,
        launch_mission_manager
    ])
