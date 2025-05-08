# #!/usr/bin/python3
# """
# This module defines the reset `ResetNode` class, a real time ROS 2 node that manages
# and performs system state variable resets on request for the COLAV Hybrid Automaton.
# Operating within the hybrid evaluation framework, providing services to make
# resets if required. it continously updates the values within it .... TODO: Finish this

# ....

# Key Features:
#    ....
#    ....

# This class is crucial for ensuring that the system can perform resets on transitions
# it is a necessity this is running for the colav_hybrid_automaton.

# Version: 0.0.1
# Author: Ryan McKee
# Date: April 17, 2025
# """


from rclpy.node import Node
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from ament_index_python.packages import get_package_share_directory
import rclpy
from hybrid_automaton.config import QOS_PROFILE
from hybrid_automaton_interfaces.srv import Reset
from hybrid_automaton.utils import (
    load_yml,
    process_automaton_config,
    create_state_subscriptions,
    create_state_publishers
)
from rcl_interfaces.msg import ParameterDescriptor

default_hybrid_automaton_config = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'colav_hybrid_automaton_config.yml')

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""

    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message

class StateResetSrvNode(Node):

    def __init__(
        self,
        name: str = 'resets_node',
        namespace: str = 'hybrid_automaton'
    ):
        """
        initialise the node
        """
        super().__init__(name, namespace=namespace)

        self.declare_parameter(
            'hybrid_automaton_config_path',
            value=default_hybrid_automaton_config,
            descriptor=ParameterDescriptor(description='Path to the Hybrid Automaton configuration file')
        )
        self.config = load_yml(
            self.get_parameter('hybrid_automaton_config_path').get_parameter_value().string_value
        )
        self.config = process_automaton_config(self.config)

        create_state_subscriptions(node=self)
        create_state_publishers(node=self)
        # Create a subscription and publisher to /hybrid_automaton/waypoints
        self.create_service(
            srv_type=Reset,
            srv_name='/hybrid_automaton/reset_states',
            callback=self._reset_callback
        )

    def _reset_callback(
            self,
            request: Reset.Request,
            response: Reset.Response):
        """
        callback for reset request
        - performs reset function on state variables depending on transition name passed in
        - throws exception if transition name does not have a reset associated
        - throws exception if something unexpected goes wrong.
        """
        try:
            reset_name = request.reset_name

            if reset_name in list(self.config['resets'].keys()):
                reset_func = self.config['resets'][reset_name]['function']
                input_names = self.config['resets'][reset_name]['state_inputs']
                state_inputs = [self.config['states'][state_name]['state'] for state_name in input_names]
                reset_outputs = reset_func(*state_inputs)
                state_outputs = self.config['resets']['remove_first_waypoint']['state_outputs']
                for idx, state_output in enumerate(state_outputs):
                    self.config['states'][state_output]['pub'].publish(reset_outputs[idx])
                
                response._success = True
                response._message = f"Reset '{reset_name}' successfully applied to state variables: '{state_outputs}'"
            else: 
                raise ValueError('invalid reset request sent')
        except Exception as e:
            self.get_logger().error(
                f'Error occured during reset_callback: {str(e)}')
            response._success = False
            response._message = f"{str(e)}"

        return response


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = StateResetSrvNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occured: {str(e)}')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
