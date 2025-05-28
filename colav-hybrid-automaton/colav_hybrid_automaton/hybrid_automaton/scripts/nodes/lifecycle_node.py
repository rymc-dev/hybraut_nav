import rclpy
from rclpy.lifecycle import State, TransitionCallbackReturn, LifecycleNode
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType, ParameterDescriptor
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition
import time

class LifecycleNodeHybridAutomaton(LifecycleNode):

  expected_lifecycle_nodes = [
     '/hybrid_automaton/dynamics_node',
     '/hybrid_automaton/transition_engine',
     '/hybrid_automaton/transition_evaluator',
     '/hybrid_automaton/resets_node'
  ]

  def __init__(self, node_name, namespace, **kwargs) -> None:
    super().__init__(node_name, namespace=namespace,**kwargs)

    node_names_and_namespaces = self.get_node_names_and_namespaces()
    self.expected_lifecycle_nodes.append(f'/{namespace}/{node_name}')
    lifecycle_nodes = []
    self.config_file_path = ''
    self.eval_hz = 1.0

    self.declare_parameter(
        'config_yml_path',
        value=self.config_file_path,
        descriptor=ParameterDescriptor(
            description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
        )
    )
    self.declare_parameter(
        'transition_evaluation_hz',
        value=self.eval_hz,
        descriptor=ParameterDescriptor(
            description="Frequency (in Hz) at which transition conditions are evaluated."
        )
    )
    self.declare_parameter(
        'waypoint_x',
        value=0.0,
        descriptor=ParameterDescriptor(
            description="Waypoint position x (in meters) for goal waypoint position."
        )
    )
    self.declare_parameter(
        'waypoint_y',
        value=0.0,
        descriptor=ParameterDescriptor(
            description="Waypoint position y (in meters) for goal waypoint position."
        )
    )
    self.declare_parameter(
        'waypoint_z',
        value=0.0,
        descriptor=ParameterDescriptor(
            description="Waypoint position z (in meters) for goal waypoint position."
        )
    )
    self.declare_parameter(
        'waypoint_acceptance_radius',
        value=0.0,
        descriptor=ParameterDescriptor(
            description="Acceptance radius (in meters) for Hybrid Automaton current waypoint."
        )
    )
    self.waypoint = None

    # for node_name_and_namespace in node_names_and_namespaces:
    #     service_names = self.get_service_names_and_types_by_node(node_name_and_namespace[0], node_name_and_namespace[1])
    #     for srv_name, _ in service_names:
    #         if '/change_state' in srv_name:
    #             lifecycle_nodes.append(f"{node_name_and_namespace[1]}/{node_name_and_namespace[0]}")
    #             break
            
    # if set(self.expected_lifecycle_nodes) == set(lifecycle_nodes):
    #     self.get_logger().info("All expected lifecycle nodes are available.")
    # else:
    #     missing = set(self.expected_lifecycle_nodes) - set(lifecycle_nodes)
    #     self.get_logger().error(f"Missing nodes: {missing}")
    #     raise Exception(f"Missing nodes: {missing}")

    self.get_logger().info('/hybrid_automaton/lifecycle_node initialized!')

  def on_configure(self, state: State) -> TransitionCallbackReturn:
      self.get_logger().info(
          f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'"
      )

      try:
          self.config_file_path = self.get_parameter('config_yml_path').value
          self.eval_hz = self.get_parameter('transition_evaluation_hz').value

          parameters = SetParameters.Request(parameters=[
              Parameter(
                  name='config_yml_path',
                  value=ParameterValue(
                      type=ParameterType.PARAMETER_STRING,
                      string_value=self.config_file_path
                  )
              ),
              Parameter(
                  name='transition_evaluation_hz',
                  value=ParameterValue(
                      type=ParameterType.PARAMETER_DOUBLE,
                      double_value=self.eval_hz
                  )
              )
          ])
      except Exception as e:
          self.get_logger().error(f"Failed to prepare parameters: {e}")
          return TransitionCallbackReturn.FAILURE
      rate = self.create_rate(0.2)
      rate.sleep() # wait till params have been set for each of the managed nodes.
      param_clients = [
          '/hybrid_automaton/transition_engine/set_parameters',
          '/hybrid_automaton/transition_evaluator/set_parameters',
          '/hybrid_automaton/dynamics_node/set_parameters',
          '/hybrid_automaton/resets_node/set_parameters'
      ]

      # Send updated parameters to each managed node
      for srv in param_clients:
          if not self._send_parameters(srv, parameters):
              return TransitionCallbackReturn.FAILURE

      # Transition each node to 'configured' state
      transition_clients = [
          '/hybrid_automaton/transition_engine/change_state',
          '/hybrid_automaton/transition_evaluator/change_state',
          '/hybrid_automaton/dynamics_node/change_state'
      ]

      for srv in transition_clients:
          if not self._send_state_transition(srv, Transition.TRANSITION_CONFIGURE, 'configure'):
              return TransitionCallbackReturn.FAILURE

      return TransitionCallbackReturn.SUCCESS

  def _send_parameters(self, service_name: str, request: SetParameters.Request) -> bool:
      try:
          client = self.create_client(SetParameters, service_name)
          if not client.wait_for_service(timeout_sec=2.0):
              self.get_logger().error(f"Service {service_name} unavailable.")
              return False
          client.call_async(request)
          self.get_logger().info(f"Parameters sent to {service_name}")
          return True
      except Exception as e:
          self.get_logger().error(f"Failed to send parameters to {service_name}: {e}")
          return False

  def _send_state_transition(self, service_name: str, transition_id: int, label: str) -> bool:
      try:
          client = self.create_client(ChangeState, service_name)
          if not client.wait_for_service(timeout_sec=2.0):
              self.get_logger().error(f"Service {service_name} unavailable.")
              return False
          future = client.call_async(ChangeState.Request(transition=Transition(id=transition_id, label=label)))
          self.get_logger().info(f"Transition '{label}' sent to {service_name}")
        #   while rclpy.ok():
        #      rclpy.spin_once(self, timeout_sec=0.1)
        #      if future.done():
        #         break
             
        #   if future.result() is not None:
        #     response = future.result()
        #   else: 
        #      self.get_logger().error('future is not done!')
          return True
      except Exception as e:
          self.get_logger().error(f"Failed to transition {service_name}: {e}")
          return False


  def on_activate(self, state: State) -> TransitionCallbackReturn:
    self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")
    try:
      self.waypoint = {
          'x': self.get_parameter('waypoint_x').value,
          'y':  self.get_parameter('waypoint_y').value,
          'z':  self.get_parameter('waypoint_z').value,
          'acceptance_radius': self.get_parameter('waypoint_acceptance_radius').value 
      }
    except Exception as e: 
       self.get_logger().error(f"{str(e)}")
       return TransitionCallbackReturn.FAILURE
    
    # publish the goal waypoint on activate to the hybrid automaton waypoints state

    # Ok now that this has been done we can iterate through the managed nodes starting their activate transition to make the hybrid automaton active
    transition_clients = [
        '/hybrid_automaton/transition_engine/change_state',
        '/hybrid_automaton/transition_evaluator/change_state',
        '/hybrid_automaton/dynamics_node/change_state',
        '/hybrid_automaton/resets_node/change_state'
    ]
    for srv in transition_clients:
      if not self._send_state_transition(srv, Transition.TRANSITION_ACTIVATE, 'activate'):
          return TransitionCallbackReturn.FAILURE

    return TransitionCallbackReturn.SUCCESS

  def on_deactivate(self, state: State) -> TransitionCallbackReturn:
    self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

    self.waypoint = None
    transition_clients = [
      '/hybrid_automaton/transition_engine/change_state',
      '/hybrid_automaton/transition_evaluator/change_state',
      '/hybrid_automaton/dynamics_node/change_state',
      '/hybrid_automaton/dynamics_node/change_state'
    ]
    for srv in transition_clients:
      if not self._send_state_transition(srv, Transition.TRANSITION_DEACTIVATE, 'deactivate'):
          return TransitionCallbackReturn.FAILURE

    return TransitionCallbackReturn.SUCCESS
  
  def on_cleanup(self, state: State) -> TransitionCallbackReturn:
     # return super().on_cleanup(state)
     return TransitionCallbackReturn.SUCCESS

  def on_shutdown(self, state: State) -> TransitionCallbackReturn:
    self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")

    self.waypoint = None
    transition_clients = [
      '/hybrid_automaton/transition_engine/change_state',
      '/hybrid_automaton/transition_evaluator/change_state',
      '/hybrid_automaton/dynamics_node/change_state',
      '/hybrid_automaton/dynamics_node/change_state'
    ]
    for srv in transition_clients:
      if State.state_id == State.PRIMARY_STATE_ACTIVE:
        transition_id = Transition.TRANSITION_ACTIVE_SHUTDOWN
      elif state.state_id == State.PRIMARY_STATE_INACTIVE:
        transition_id = Transition.TRANSITION_INACTIVE_SHUTDOWN
      elif state.state_id == State.PRIMARY_STATE_UNCONFIGURED:
        transition_id = Transition.TRANSITION_UNCONFIGURED_SHUTDOWN

      if not self._send_state_transition(srv, transition_id, 'shutdown'):
          return TransitionCallbackReturn.FAILURE

    return TransitionCallbackReturn.SUCCESS

from rclpy.executors import MultiThreadedExecutor

def main(args=None) -> None:
  rclpy.init(args=args)
  lifecycle_node = LifecycleNodeHybridAutomaton("lifecycle_node", "hybrid_automaton")
  executor = MultiThreadedExecutor(num_threads=4)
  executor.add_node(lifecycle_node)
  executor.spin()
  executor.shutdown()
  lifecycle_node.destroy_node()
  rclpy.shutdown()

if __name__ == "__main__":
  main()
