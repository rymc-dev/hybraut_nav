import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor 
from lifecycle_msgs.srv import GetState
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from hybrid_automaton_interfaces.action import HybridAutomaton
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup

class HybridAutomatonManager(Node):
    
    def __init__(
        self,
        name: str,
        namespace: str
    ):
        super().__init__(name, namespace=namespace)

        self._state_cli = self.create_client(
            srv_type=GetState,
            srv_name='/colav/hybrid_automaton_lifecycle/get_state'
        )
        if not self._state_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton_lifecycle/get_state: srv not available!')

        self._change_state_cli = self.create_client(
            srv_type=ChangeState,
            srv_name='/colav/hybrid_automaton_lifecycle/change_state'
        )
        if not self._change_state_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton_lifecycle/get_state: srv not available!')
        
        self._automaton_params_setter_cli = self.create_client(
            srv_type=SetParameters,
            srv_name='/colav/hybrid_automaton_lifecycle/set_parameters'
        )
        if not self._automaton_params_setter_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton_lifecycle/set_parameters: srv not available!')

        self._default_configuration_path = '/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav-hybrid-automaton/colav_hybrid_automaton/config/colav_hybrid_automaton_config.yml'
        self._default_evaluation_frequency = 1
        self._default_control_frequency = 100

        # set default params for automaton

        future = self._automaton_params_setter_cli.call_async(
            SetParameters.Request(
                parameters=[
                    Parameter(
                        name='configuration_path', 
                        value=ParameterValue(type=ParameterType.PARAMETER_STRING, string_value=self._default_configuration_path)
                    ),
                    Parameter(
                        name='evaluation_frequency',
                        value=ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=self._default_evaluation_frequency)
                    ),
                    Parameter(
                        name='control_frequency',
                        value=ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=self._default_control_frequency)
                    )
            ]))
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            if not future.result().success: 
                self.get_logger().error('setting params failed for configuration')

        # Transition to inactive state
        future = self._change_state_cli.call_async(
            ChangeState.Request(transition=Transition(id=Transition.TRANSITION_CONFIGURE))
        )
        rclpy.spin_until_future_complete(self,future, timeout_sec=5.0)
        if future.done():
            if not future.result().success:
                self.get_logger().error('transition request to configure for hybrid automaton lifecycle failed')


        self._hybrid_automaton_action_server = ActionServer(
            self,
            HybridAutomaton,
            'hybrid_automaton_action_server',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            callback_group=ReentrantCallbackGroup
        )



def main():
    rclpy.init()
    node = HybridAutomatonManager(name='hybrid_automaton_manager', namespace='colav')
    executor = MultiThreadedExecutor(num_threads=6)

    try:
        executor.add_node(node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()