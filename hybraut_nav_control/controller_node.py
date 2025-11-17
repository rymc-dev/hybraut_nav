# controller_node.py
# **- coding: utf-8 -*-
# !/usr/bin/env python3
""" 
This file contains implementation of Layer 3 of the HybrautNav Navigation Stack
This layer produces the low-level actuator commands for the controller or execution 
layer.

- It closes the HybrautNav navigation stack for fast control loops
- enforces safety limits
- interfaces with hardware (rudder, thrusters)
- and allows Layer 2 to stay physics agnostic

NOTE: This version of controller only considers velocity and continous
      dynamics of the hybraut_tactical_layer will only generate desired 
      headings for the moment for the moment
"""

import math
from typing import Optional, Union

from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import os

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from rclpy.service import Service
from rclpy.timer import Timer

from rcl_interfaces.msg import ParameterDescriptor

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger

from hybraut_nav_controller.controller import Controller
from hybraut_nav.qos import world_state_qos
from hybraut_interfaces.msg import ContinousDynamics

from hybraut_nav_controller.controller import Controller, ControllerType
from hybraut_nav.state import NodeState


DEFAULT_CONTROLLER_TYPE: ControllerType = ControllerType.FINITE_TIME_CONTROLLER
DEFAULT_CONTROLLER_FREQUENCY: float = 10.0  # Hz
DEFAULT_CRUISE_SPEED: float = 0.2 # m/s   
    

class ControllerNode(Node):
    """ 
    ControllerNode forms apart of the HybrautNav Navigation Stack.
    
    It is responsible for generating Low-Level Actuator Commands based 
    on both the continous dynamics received from the L2 Tactical Layer
    Hybrid Autmoaton and the current state of the agent vehicle, It utilizes
    a controller to compute the necessary commands for Twist messages to 
    follow the desired trajectory as defined within the continous dynamics. 
    
    This Node Does not implement the actual controller but instaed provides the 
    interfaces to plug into the HybrautNav Navigation Stack and manages dynamic
    reconfiguration of controller parameters like what controller we should
    be using in the controller Loop in real time via manual changes of parameters
    by human in the loop or updates from continous dynamic messages which request for 
    controller to be changes based on control mode we are in.
    """    
    
    # Controller Type

    # internal state
    state: NodeState = NodeState.INACTIVE
    controller: Optional[Controller] = None
    desired_heading: float = 0.0
    desired_velocity: float = 0.0
    target_waypoint = None
    heading_tolerance: float = 0.1
    velocity_tolerance: float = 0.1
    
    # State variables
    agent_state: Optional[Odometry] = None
    
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
        self.add_on_set_parameters_callback(self.on_parameter_change)
        self.__init_services__()
        self.__init_default_controller__()

    def __init_parameters__(self):
        self.declare_parameter(
            'controller_type', 
            DEFAULT_CONTROLLER_TYPE.value,
            ParameterDescriptor(
                description='Type of controller to use. '
                           'Options: Finite Time Controller .'
                           f'(default: {DEFAULT_CONTROLLER_TYPE.value})'
            )
        )
        self.declare_parameter(
            'controller_frequency',
            DEFAULT_CONTROLLER_FREQUENCY,
            ParameterDescriptor(
                description='Frequency (Hz) at which to run the controller loop. '
                            f'(default: {DEFAULT_CONTROLLER_FREQUENCY} Hz)'
            )
        )
        self.declare_parameter(
            'cruise_speed',
            DEFAULT_CRUISE_SPEED, 
            ParameterDescriptor(
                description='Velocity (m/s) in which the controller will' \
                    f'operate a cruise speed, this version of hybraut_nav_controller' \
                    f'outputs a constant cruise speed for `cmd_vel` based on this' \
                    f'(default: {DEFAULT_CRUISE_SPEED})'
            )
        )
        
    def __init_subscriptions__(self): 
        self.agent_state_sub = self.create_subscription(
            msg_type=Odometry, 
            topic='/odom',
            callback=lambda msg: self.agent_state_cb(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        self.continous_dynamics_sub = self.create_subscription(
            msg_type=ContinousDynamics,
            topic='tactical_node/continuous_dynamics',
            callback=lambda msg: self.continous_dynamics_cb(msg),
            qos_profile=world_state_qos, # need to decide on a qos for continous dynamics for tactical layer
            callback_group=ReentrantCallbackGroup()
        )
        
    def __init_publishers__(self):
        self.cmd_vel_pub = self.create_publisher(
            TwistStamped,  # msg_type
            '/cmd_vel',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
    
    def __init_services__(self):
        """ initializes services"""
        self.toggle_controller_srv = self.create_service(
            Trigger,
            'controller_node/toggle',
            self.toggle_controller_cb,
            callback_group=ReentrantCallbackGroup()
        )

    def __init_timers__(self):
        self.control_timer = self.create_timer(
            timer_period_sec=1 / self.get_controller_frequency(),  # 10 Hz control loop
            callback=self.control_loop,
            callback_group=ReentrantCallbackGroup(),
            autostart=False
        ) 

    def __init_default_controller__(self):
        self.controller = ControllerType.initialize_controller(self.get_controller_type())

    """ === getters === """
    
    def get_controller_type(self) -> ControllerType: 
        return self.get_parameter('controller_type').value
    
    def get_controller_frequency(self) -> float:
        return self.get_parameter('controller_frequency').value
    
    def get_cruise_speed(self) -> float:
        return self.get_parameter('cruise_speed').value
        
    """ === setters === """
    def set_controller_type(self, new_controller_type: Union[ControllerType, str]):
        if isinstance(new_controller_type, str):
            new_controller_type = ControllerType.from_string(new_controller_type)
        
        if not isinstance(new_controller_type, ControllerType):
            raise TypeError("new_controller_type must be a ControllerType or string.")
        
        # Update parameter
        self.set_parameters([rclpy.parameter.Parameter('controller_type', rclpy.Parameter.Type.STRING, new_controller_type.value)])
        self.get_logger().info(f"Controller type set to {new_controller_type.value}")
        
    def set_controller_frequency(self, new_frequency: float):
        ... 
        
    """ === callbacks === """
    
    def on_parameter_change(self, params): 
        for param in params: 
            ... 
    
    def control_loop(self):
        """ 
        Main control loop to compute and publish actuator commands.
        
        Runs at the frequency defined by 'controller_frequency' parameter.
        
        Example: 
            >>> TODO
        
        Tests: 
        ...
        """
        from geometry_msgs.msg import Twist
        if self.state == NodeState.ACTIVE:
            try:  
                yaw_rate = self.controller.step()
            except Exception as e: 
                self.get_logger().error(f"Controller step failed: {e}")
                return
                
            twist = TwistStamped()

            twist.twist.angular.z = yaw_rate
            twist.twist.linear.x = self.get_cruise_speed()
            
            self.cmd_vel_pub.publish(twist)
    
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

        desired_heading = msg.desired_heading # placeholder for now
        desired_heading_rate = 0.2 # This is static for now, a constant turning rate
        # 2. Check for any setpoint metadata changes, update internal state if changed
        self.controller.update_continous_dynamics(desired_heading=desired_heading , desired_heading_rate=0.2)

    def agent_state_cb(self, msg: Odometry):
        # Convert quaternion to yaw (heading)
        q = msg.pose.pose.orientation
        # Quaternion to Euler (yaw)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        current_heading = math.atan2(siny_cosp, cosy_cosp)
                
        self.controller.update_state(current_heading=current_heading)
        
    def toggle_controller_cb(self, request: Trigger.Request, response: Trigger.Response):
        # Toggle controller state
        if self.state == NodeState.ACTIVE:
            self.state = NodeState.INACTIVE
            response.success = True
            response.message = "Controller deactivated."
            self.control_timer.cancel()
        else:
            self.state = NodeState.ACTIVE
            response.success = True
            response.message = "Controller activated."
            self.control_timer.reset()
            
        return response