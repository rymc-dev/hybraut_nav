# !/usr/bin/env python3
""" 
Tactical Node for HybrautNav Navigation Stack is the second layer 
responsible for tactical decision-making in navigation tasks.
"""

from hybraut_interfaces.msg import HybridAutomatonState
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from rclpy.service import Service
from hybraut_interfaces.srv import SendPose
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from ament_index_python.packages import get_package_share_directory
import os
from hybraut_nav_tactical.tactical_models.models import HybridAutomaton
from hybraut_nav.state import NodeState


class TacticalNode(Node):
    
    state = NodeState.INACTIVE
    DEFAULT_AMDL_PATH = os.path.join(
        get_package_share_directory('hybraut_nav'),
        'amdl',
        'demo_tactical_layer.amdl.yml'
    )
    automata_state_pub: Publisher[HybridAutomatonState]    
    toggle_srv: Service[SendPose]
    
    def __init__(self):
        super().__init__('tactical_node', namespace='hybraut_nav')
        self.__init_parameters__()
        self.__init_services__()
        
    def __init_parameters__(self):
        self.declare_parameter(
            'amdl_path',
            value=self.DEFAULT_AMDL_PATH,
            descriptor=ParameterDescriptor(
                description='Path to the AMDL file defining the hybrid automaton.'
            )
        )
        
    def __init__publishers__(self):
        ... 
        
    def __init_subscribers__(self):
        ... 
    
        
    def __init_services__(self):
        self.toggle_srv = self.create_service(
            SendPose,
            'toggle_automaton',
            self.handle_toggle_automaton
        )
        
    def get_amdl_path(self) -> str: 
        return self.get_parameter('amdl_path').get_parameter_value().string_value
    
    def handle_toggle_automaton(self, request: SendPose.Request, response: SendPose.Response):
        # Handle the service request to toggle the automaton
        self.get_logger().info("Toggling hybrid automaton state")
        return response
    
    def on_activation(self):
        automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
            amdl_path=self.get_amdl_path(),
            generate_mmd_diagrams=False
        )
        automaton_model.create_mode_publisher()
        
        