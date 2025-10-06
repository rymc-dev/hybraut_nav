# import pytest
# from hybraut_lifecycle._automaton_lifecycle_node import AutomatonLifecycleNode
# import threading
# import rclpy
# from rclpy.node import Node
# from rclpy.executors import MultiThreadedExecutor
# import os

# import pytest
# import threading
# import rclpy
# from rclpy.node import Node
# from rclpy.executors import MultiThreadedExecutor
# from hybraut_lifecycle._automaton_lifecycle_node import AutomatonLifecycleNode
# from rcl_interfaces.srv import GetParameters, ListParameters, DescribeParameters, GetParameterTypes, SetParameters
# from rcl_interfaces.msg import Parameter
# from lifecycle_msgs.srv import ChangeState, GetState
# from lifecycle_msgs.msg import Transition, State
# from rcl_interfaces.msg import ListParametersResult
# from rcl_interfaces.msg import ParameterDescriptor, ParameterType, ParameterValue
# from typing import List
# from rcl_interfaces.msg import SetParametersResult, ParameterValue

# @pytest.fixture(scope='class')
# def rclpy_context():
#     rclpy.init()
#     yield
#     rclpy.shutdown()

# @pytest.fixture(scope='class')
# def automaton_lifecycle_node(rclpy_context):
#     node = AutomatonLifecycleNode("test_automaton_node")
#     executor = MultiThreadedExecutor(num_threads=6)
#     executor.add_node(node)
#     thread = threading.Thread(target=executor.spin, daemon=True)
#     thread.start()
#     yield node
#     executor.shutdown()
#     node.destroy_node()

# class MockAutomatonLifecycleCLINode(Node):
#     def __init__(self):
#         super().__init__(node_name="mock_automaton_client")

#         self.list_parameters_cli = self.create_client(
#             ListParameters,
#             "/test_automaton_node/list_parameters"
#         )

#         self.describe_parameters_cli = self.create_client(
#             DescribeParameters,
#             "/test_automaton_node/describe_parameters"
#         )

#         self.get_parameters_cli = self.create_client(
#             GetParameters,
#             '/test_automaton_node/get_parameters'
#         )

#         self.set_parameters_cli = self.create_client(
#             SetParameters,
#             '/test_automaton_node/set_parameters'
#         )

#         self.get_state_cli = self.create_client(
#             GetState,
#             '/test_automaton_node/get_state'
#         )

#         self.change_state_cli = self.create_client(
#             ChangeState,
#             '/test_automaton_node/change_state'
#         )

#     def list_params(self) -> ListParametersResult:
#         """
#         this will get a list of params for the ros2 service
#         """
#         future = self.list_parameters_cli.call_async(ListParameters.Request())
#         rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

#         if future.result() is not None:
#             list_paramaters: ListParameters = future.result().result
#             return list_paramaters
#         else: 
#             raise RuntimeError('request for service params did not return result.')

#     def get_parameter_descriptions(self, parameter_names: List[str]) -> List[ParameterDescriptor]: 
#         """
#         This will get the description for a parameter
#         """
#         future = self.describe_parameters_cli.call_async(DescribeParameters.Request(names=parameter_names))
#         rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

#         if future.result() is not None:
#             parameter_descriptors: ParameterDescriptor = future.result().descriptors
#             return parameter_descriptors
#         else: 
#             raise RuntimeError('request for service params did not return result.')

#     def get_parameter_values(self, parameter_names: List[str]) -> List[ParameterValue]: 
#         """
#         This will get the description for a parameter
#         """
#         future = self.get_parameters_cli.call_async(GetParameters.Request(names=parameter_names))
#         rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

#         if future.result() is not None:
#             parameter_values: List[ParameterValue] = future.result().values
#             return parameter_values
#         else: 
#             raise RuntimeError('request for service params did not return result.')
    
#     def set_parameters(self, parameters: List[Parameter]) -> List[SetParametersResult]:
#         """
#         this sets the parameters for the automaton
#         """

#         future = self.set_parameters_cli.call_async(SetParameters.Request(parameters=parameters))
#         rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

#         if future.result() is not None:
#             set_parameter_results: List[SetParametersResult] = future.result().results
#             return set_parameter_results
#         else: 
#             raise RuntimeError('request for service params did not return result.')

#     def get_lifecycle_state(self) -> State:
#         future = self.get_state_cli.call_async(GetState.Request())
#         rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)

#         if future.result() is not None: 
#             current_state:State =  future.result().current_state
#             return current_state
#         else: 
#             raise RuntimeError('request for client state change failed.')

#     def perform_lifecycle_transition(self, transition: Transition) -> bool:
#         """
#         performs a lifecycle transition from one lifecycle state to another.
#         """
#         req = ChangeState.Request(transition=transition)
#         future = self.change_state_cli.call_async(
#             req
#         )
#         rclpy.spin_until_future_complete(self, future)

#         if future.result() is not None:
#             return future.result().success 

# @pytest.fixture(scope='class')
# def automaton_lifecycle_cli_node(rclpy_context):
#     node = MockAutomatonLifecycleCLINode()
#     executor = MultiThreadedExecutor(num_threads=2)
#     executor.add_node(node)

#     thread = threading.Thread(target=executor.spin, daemon=True)
#     thread.start()
#     yield node
#     executor.shutdown()
#     node.destroy_node()

# @pytest.mark.usefixtures("automaton_lifecycle_node", "automaton_lifecycle_cli_node")
# class TestAutomatonLifecycleNode():
#     """
#     test suite for the automaton lifecycle node
#     we will test each phase of the lifecycle, for proper
#     parameter initialization, timers, subscription, publisher
#     and actionserver
#     """

#     @pytest.mark.order(1)
#     def validate_node_initialization(self, automaton_lifecycle_node: AutomatonLifecycleNode):
#         """validates the initialization of teh hybrid automaton lifecycle node"""
#         assert automaton_lifecycle_node.get_name() == "test_automaton_node"

#     @pytest.mark.order(2)
#     def validate_initial_lifecycle_state_is_unconfigured(self,automaton_lifecycle_cli_node: MockAutomatonLifecycleCLINode):
#         """validate hybrid automaton lifecycle node initializizes and is in state unconfigured by default"""
#         current_state: State = automaton_lifecycle_cli_node.get_lifecycle_state()
#         assert current_state.id == State.PRIMARY_STATE_UNCONFIGURED
#         assert current_state.label == 'unconfigured'

#     @pytest.mark.order(3)
#     def validate_unconfigured_state_parameters(self, automaton_lifecycle_cli_node: MockAutomatonLifecycleCLINode):
#         """validate the lifecycle nodes unconfigured state params contains the required configuration path parameter"""
#         parameter_descriptors:List[ParameterDescriptor] = automaton_lifecycle_cli_node.get_parameter_descriptions(parameter_names=['famd_path'])
        
#         try:
#             descriptor: ParameterDescriptor = parameter_descriptors[0]
#         except IndexError:
#             pytest.fail("No parameter descriptors returned (expected at least one).")

#         assert descriptor.name == 'famd_path'
#         assert descriptor.type == ParameterType.PARAMETER_STRING
#         assert descriptor.description == 'absolute path to the hybrid automatons famd file.'
#         assert descriptor.dynamic_typing == False

#         parameter_values: List[ParameterValue] = automaton_lifecycle_cli_node.get_parameter_values(parameter_names=['famd_path'])

#         try:
#             value: ParameterValue = parameter_values[0]
#         except IndexError:
#             pytest.fail("No parameter value for the famd_path received.")

#         assert value.type == ParameterType.PARAMETER_STRING
#         assert value.string_value == '/path/to/famd.yml'


#         print (parameter_values)

#     # TODO: Need to check the logs for the automaton_lifecycle node to see if valid exception is being thrown.
#     @pytest.mark.order(4)
#     def test_invalid_transition_to_inactive_invalid_famd_file_path(self, automaton_lifecycle_cli_node: MockAutomatonLifecycleCLINode):
#         # Send a invalid path to the famd file and attempt transition should stop the transition
#         parameter_values = [
#             Parameter(
#                 name='famd_path',
#                 value=ParameterValue(
#                     type=ParameterType.PARAMETER_STRING,
#                     string_value="/invalid/path/to/famd.yml"
#                 )
#             )
#         ]
#         set_param_results:List[SetParametersResult] = automaton_lifecycle_cli_node.set_parameters(parameter_values)    
#         assert set_param_results[0].successful == True

#         transition_success: bool = automaton_lifecycle_cli_node.perform_lifecycle_transition(transition=Transition(id=Transition.TRANSITION_CONFIGURE, label='configure'))
#         assert transition_success == False
#         current_state: State = automaton_lifecycle_cli_node.get_lifecycle_state()
#         assert current_state.id == State.PRIMARY_STATE_UNCONFIGURED
#         assert current_state.label == 'unconfigured'
    
#     @pytest.mark.order(5)
#     def test_transition_to_active_and_active_state_attributes(self, automaton_lifecycle_cli_node):
#         # Send a invalid path to the famd file and attempt transition should stop the transition
#         test_famd_path = os.path.join(os.path.dirname(__file__), 'test_hybrid_automaton.famd.yaml')
        
#         parameter_values = [
#             Parameter(
#                 name='famd_path',
#                 value=ParameterValue(
#                     type=ParameterType.PARAMETER_STRING,
#                     string_value=test_famd_path
#                 )
#             )
#         ]
#         set_param_results:List[SetParametersResult] = automaton_lifecycle_cli_node.set_parameters(parameter_values)    
#         assert set_param_results[0].successful == True

#         transition_success: bool = automaton_lifecycle_cli_node.perform_lifecycle_transition(transition=Transition(id=Transition.TRANSITION_CONFIGURE, label='configure'))
#         assert transition_success == True
#         current_state: State = automaton_lifecycle_cli_node.get_lifecycle_state()
#         assert current_state.id == State.PRIMARY_STATE_INACTIVE
#         assert current_state.label == 'inactive'

#     @pytest.mark.order(6)
#     def validate_inactive_lifecycle_state(self, automaton_lifecycle_node: AutomatonLifecycleNode, automaton_lifecycle_cli_node: MockAutomatonLifecycleCLINode):
#         """
#         in this test we will validate the propertys of the inactive mode,
#         this mode should generate several publishers, subscriptions and inactive
#         timers, as well as waypoint parameters which can be utilized for defining the mission request for the 
#         automaton, we should also innitialize the action server in this mode.
#         """
#         from hybraut_lifecycle._internal.automaton.hybrid_automaton_model import HybridAutomaton

#         assert isinstance(automaton_lifecycle_node.__getattribute__('automaton_model'), HybridAutomaton), \
#             'automaton model for the lifecycle node has not been initialized correctly'
        
#         # lets do a simple validation of the automaton_models modes and such to ensure it was initialized correctly
#         automaton_model:HybridAutomaton = automaton_lifecycle_node.__getattribute__('automaton_model')
#         assert automaton_model.name == 'test_hybrid_automaton'
#         assert automaton_model.control_frequency_hz == 10.0
#         assert automaton_model.transition_evaluation_frequency_hz == 5.0
#         assert automaton_model.current_mode == automaton_model.initial_mode
#         assert len(automaton_model.modes) == 2
#         assert automaton_model.modes[0].name == 'test_mode'
#         assert len(automaton_model.modes[0].transitions) == 1
#         assert automaton_model.modes[1].name == 'goal_mode'
#         assert len(automaton_model.modes[1].transitions) == 0       

#         assert len(automaton_model.states) == 1
#         assert 'test_state' in automaton_model.states
#         from rclpy.publisher import Publisher
#         from rclpy.subscription import Subscription
#         assert isinstance(automaton_model.states['test_state'].publisher, Publisher)
#         # assert isinstance(automaton_lifecycle_node.get_subscriptions_info_by_topic(automaton_model.states['test_state'].topic)) 
#         automaton_lifecycle_cli_node.get_publisher_names_and_types_by_node(node_name='test_automaton_node', node_namespace=None)

#         publishers = automaton_lifecycle_node.get_publisher_names_and_types_by_node(
#             node_name='test_automaton_node',
#             node_namespace=''
#         )

#         subscriptions = automaton_lifecycle_node.get_subscriber_names_and_types_by_node(
#             node_name='test_automaton_node',
#             node_namespace=''
#         )


        

#     def validate_inactive_lifecycle_state_params(self):
#         pass

#     @pytest.mark.order(7)
#     def test_transition_to_shutdown():
#         pass


# def main():
#     # Manually mimic the pytest fixture lifecycle for debugging
#     rclpy.init()

#     try:
#         # Start lifecycle node
#         lifecycle_node = AutomatonLifecycleNode("test_automaton_node")
#         lifecycle_executor = MultiThreadedExecutor(num_threads=6)
#         lifecycle_executor.add_node(lifecycle_node)
#         lifecycle_thread = threading.Thread(target=lifecycle_executor.spin, daemon=True)
#         lifecycle_thread.start()

#         # Start CLI node
#         cli_node = MockAutomatonLifecycleCLINode()
#         cli_executor = MultiThreadedExecutor(num_threads=2)
#         cli_executor.add_node(cli_node)
#         cli_thread = threading.Thread(target=cli_executor.spin, daemon=True)
#         cli_thread.start()

#         # === Now call the test function directly for debugging ===
#         print("[DEBUG] Running test_initialization_and_unconfigured_state() manually")

#         # Optional: set breakpoints here
#         TestAutomatonLifecycleNode().validate_node_initialization(lifecycle_node)
#         TestAutomatonLifecycleNode().validate_initial_lifecycle_state_is_unconfigured(cli_node)
#         TestAutomatonLifecycleNode().validate_unconfigured_state_parameters(cli_node)
#         TestAutomatonLifecycleNode().test_invalid_transition_to_inactive_invalid_famd_file_path(cli_node)
#         TestAutomatonLifecycleNode().test_transition_to_active_and_active_state_attributes(cli_node)
#         TestAutomatonLifecycleNode().validate_inactive_lifecycle_state(lifecycle_node, cli_node)
#         # TestAutomatonLifecycleNode().test_initialization(lifecycle_node, cli_node)


#         print("[DEBUG] Test completed successfully.")

#     finally:
#         # Teardown
#         lifecycle_executor.shutdown()
#         lifecycle_node.destroy_node()

#         cli_executor.shutdown()
#         cli_node.destroy_node()

#         rclpy.shutdown()


# if __name__ == '__main__':
#     main()