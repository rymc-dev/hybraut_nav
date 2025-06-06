from rclpy.node import Node 

def reset_callback(self: Node, transition):
    """performs state reset"""
    reset_name = None
    self.get_logger().info(f"performing reset '{self._mode_transitions[transition]}' for transition.")
    reset_func = self._configuration['resets'][reset_name]['function']
    input_names = self._configuration['resets'][reset_name]['state_inputs']
    state_inputs = [self._configuration['states'][state_name]['state'] for state_name in input_names]
    reset_outputs = reset_func(*state_inputs)
    state_outputs = self._configuration['resets']['remove_first_waypoint']['state_outputs']
    for idx, state_output in enumerate(state_outputs):
        # self._configuration['states'][state_output]['pub'].publish(reset_outputs[idx])
        self._waypoints_publisher.publish(reset_outputs[idx])