# !/usr/bin/env python3

""" 
This Node is Layer 3 of the HybrautNav Navigation Stack
This layer produces the low-level actuator commands for the controller or execution 
layer.

- It closes the HybrautNav navigation stack for fast control loops
- enforces safety limits
- interfaces with hardware (rudder, thrusters)
- and allows Layer 2 to stay physics agnostic
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from enum import Enum
from hybraut_nav_controller.controller import Controller, FiniteTimeController
from colav_interfaces.msg import AgentState
from typing import Optional
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher

from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import Twist
from rclpy.service import Service

from typing import Union
from hybraut_interfaces.msg import ContinousDynamics

from std_srvs.srv import Trigger
from rclpy.timer import Timer
import math


class ControllerState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ControllerType(Enum): 
    FINITE_TIME_CONTROLLER = "finite_time_controller"
    
    @staticmethod
    def from_string(controller_type_str: str) -> 'ControllerType':
        """
        Convert string to PlannerType enum.
        
        Args:
            controller_type_str: String representation of ControllerType type
            
        Returns:
            Corresponding PlannerType enum member
            
        Raises:
            ValueError: If planner type string is not recognized
        """
        for pt in ControllerType:
            if pt.value == controller_type_str:
                return pt
        raise ValueError(f'Unknown planner type string: {controller_type_str}')

    @staticmethod
    def initialize_planner(controller_type: 'ControllerType') -> Controller:
        """
        Factory method to create planner instance.
        
        Args:
            planner_type: Type of planner to create
            
        Returns:
            Initialized planner instance
            
        Raises:
            ValueError: If planner type is not recognized
        """
        planner_map = {
            ControllerType.FINITE_TIME_CONTROLLER: FiniteTimeController,
        }
        
        planner_class = planner_map.get(controller_type)
        if planner_class is None:
            raise ValueError(f'Unknown controller type: {controller_type}')
        
        return planner_class()
    
class ControllerNode(Node):
    
    # Controller Type
    DEFAULT_CONTROLLER_TYPE: ControllerType = ControllerType.FINITE_TIME_CONTROLLER
    DEFAULT_CONTROLLER_FREQUENCY: float = 10.0  # Hz   
    
    
    # internal state
    state: ControllerState = ControllerState.INACTIVE
    controller: Optional[Controller] = None
    desired_heading: float = 0.0
    desired_velocity: float = 0.0
    target_waypoint = None
    heading_tolerance: float = 0.1
    velocity_tolerance: float = 0.1
    
    # State variables
    agent_state: Optional[AgentState] = None
    
    # Subscriptions
    agent_state_sub: Subscription = None
    # Publishers
    cmd_vel_pub: Publisher = None
    
    # services 
    toggle_controller_srv: Service = None
    
    # Timer
    control_timer: Timer = None 
    
    
    
    def __init__(self):
        super().__init__('controller_node', namespace='hybraut_nav')
        
        self.__init_parameters__()
        self.__init_subscriptions__()
        self.__init_publishers__()
        self.__init_timers__()
        self.__init_services__()
        self.__init_default_controller__()

    def __init_parameters__(self):
        self.declare_parameter(
            'controller_type', 
            self.DEFAULT_CONTROLLER_TYPE.value,
            ParameterDescriptor(
                description='Type of controller to use. '
                           'Options: Finite Time Controller .'
                           f'(default: {self.DEFAULT_CONTROLLER_TYPE.value})'
            )
        )
        self.declare_parameter(
            'controller_frequency',
            self.DEFAULT_CONTROLLER_FREQUENCY,
            ParameterDescriptor(
                description='Frequency (Hz) at which to run the controller loop. '
                            f'(default: {self.DEFAULT_CONTROLLER_FREQUENCY} Hz)'
            )
        )
        
    def __init_subscriptions__(self): 
        self.agent_state_sub = self.create_subscription(
            msg_type=AgentState, 
            topic='/agent_state',
            callback=lambda msg: self.agent_state_cb(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        
    def __init_publishers__(self):
        self.cmd_vel_pub = self.create_publisher(
            Twist,  # msg_type
            '/cmd_vel',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
    
    def __init_services__(self):
        self.toggle_controller_srv = self.create_service(
            Trigger,
            '/toggle_controller',
            self.toggle_controller_cb
        )

    def __init_timers__(self):
        self.control_timer = self.create_timer(
            timer_period_sec=0.1,  # 10 Hz control loop
            callback=self.control_loop,
            callback_group=ReentrantCallbackGroup()
        ) 

    def __init_default_controller__(self):
        ...

    """ === getters === """
    
    def get_controller_type(self) -> ControllerType: 
        return None
    
    def get_controller_frequency(self) -> float:
        ... 
        
    """ === setters === """
    def set_controller_type(self, new_controller_type: Union[ControllerType, str]):
        ...
        
    def set_controller_frequency(self, new_frequency: float):
        ... 
        
    """ === callbacks === """
    
    def control_loop(self):
        ... 
    
    def continous_dynamics_cb(self, msg: ContinousDynamics):
        """ 
        Handle updates to controller metadata and setpoints from ContinousDynamics message.
        """
        # 1. Validate message type
        if not isinstance(msg, ContinousDynamics):
            raise TypeError("Expected ContinousDynamics message.")
        
        # 1. Check for controller type change 
        if self.get_parameter('controller_type').value != msg.controller_name:
            # Update controller type parameter
            self.set_parameters([rclpy.parameter.Parameter('controller_type', rclpy.Parameter.Type.STRING, msg.controller_name)])

        
        # 2. Check for any setpoint metadata changes, update internal state if changed
        if (
            self.desired_heading != msg.desired_heading or
            self.desired_velocity != msg.desired_velocity or
            self.target_waypoint != msg.target_waypoint or
            self.heading_tolerance != msg.heading_tolerance or
            self.velocity_tolerance != msg.velocity_tolerance
        ):
            # Setpoints changed
            self.desired_heading = msg.desired_heading  # The current desired heading we want to be in
            self.desired_velocity = msg.desired_velocity # The current desired velocity we want to be in
            self.target_waypoint = msg.target_waypoint # This is mainly for controller metadata to see which waypoint, virtual waypoint/real waypoint
            # we are tracking for logging purposes
            self.heading_tolerance = msg.heading_tolerance # This is an important piece of metadata used for controller, it can help loss control
            # by stopping oscillation for heading tolerance when far from the waypoint
            self.velocity_tolerance = msg.velocity_tolerance # This is an import piece of metadata used for controller, it can help loss control
            # by stopping oscillation for velocity tolerance when far from the waypoint
            
    def agent_state_cb(self, msg: AgentState):
        # Convert quaternion to yaw (heading)
        q = msg.pose.orientation
        # Quaternion to Euler (yaw)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        current_heading = math.atan2(siny_cosp, cosy_cosp)
        # desired_heading = msg.
        
        self.controller.update_state(current_heading=msg.orientation.yaw, desired_heading=msg.desired_heading, desired_heading_rate=msg.desired_heading_rate)
        
        
    def toggle_controller_cb(self, request: Trigger.Request, response: Trigger.Response):
        # Toggle controller state
        if self.state == ControllerState.ACTIVE:
            self.state = ControllerState.INACTIVE
            response.success = True
            response.message = "Controller deactivated."
        else:
            self.state = ControllerState.ACTIVE
            response.success = True
            response.message = "Controller activated."
        return response
        
        
        
    """ === helper functions === """
    
def main(args = None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()