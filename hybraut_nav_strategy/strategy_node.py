#!/usr/bin/env python3

""" 
Layer one of the hybraut navigation stack: the global planner.

This node subscribes to global cost map updates, goal poses, and agent states.
It operates on a timer, planning a global path when a new goal is received,
which can be passed to layer two (the local planner hybrid automaton), 
then to a controller.

UML Reference:
    See state machine diagram: ./diagrams/strategy_node_state_machine.puml
    See class diagram: .diagrams/strategy_node_class_class_diagram.uml
"""

# TODO: Need to integrate this functions with there UML diagrams and documentation

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.timer import Timer
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from std_msgs.msg import Header
from typing import Tuple
from typing import List
from rclpy.parameter import Parameter
from rcl_interfaces.msg import SetParametersResult

from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped, Pose
from colav_interfaces.msg import AgentState
from hybraut_interfaces.srv import SendPose
from std_srvs.srv import Trigger

from enum import Enum
import sys
from typing import Union
import os

# Import path planning modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hybraut_nav_strategy.path_planning import (
    RRTStar, RRT, Dijkstra, AStar, Planner,
    Grid as PlannerGrid, Point as PlannerPoint
)

from rclpy.qos import HistoryPolicy, ReliabilityPolicy, DurabilityPolicy
from hybraut_nav.qos import map_qos, world_state_qos


from rclpy.subscription import Subscription
from rclpy.publisher import Publisher

from typing import Optional
from geometry_msgs.msg import Point
from rclpy.service import Service
import threading
from hybraut_nav_strategy.path_planning import PlannerType
from hybraut_nav.state import NodeState


class StrategyNode(Node):
    """
    Global planner for the Hybraut_nav navigation stack.
    
    Plans a global path relative to the agent's current state to a goal pose 
    using a specified planning algorithm (A*, Dijkstra, RRT, RRT*).
    
    This is Layer one of the HybrautNav navigation stack generating optimal 
    trajectories in the static cost map layer, cost map being a continous representation 
    of a 2d environemnt where each cell represents traversability cost. 
    
    ROS Standard Cost Map use cell state convention: 
    - -1: Unknown
    - 0: Free
    - 1-99: Increasing cost of traversal
    - 100: Insurmountable obstacle
    
    The paths generated from this are utilized by the Tactical Layer layer 2,
    This layer is a hybrid automaton defined utilzind 'AMDL' (Automaton Modeling Description Language)
    to generate local paths within an event horizon of the agent which optimally will follow the global path
    but if needed can generate virtual waypoints considering the second layer of the cost map (dynamic obstacles). 
    The local paths are then passed to a controller (layer 3) to generate control commands for the agent.
    """

    # Parameter Defaults
    DEFAULT_REPLAN_FREQUENCY: float = 0.1               # default replan hz is 0.1 every 10 seconds
    DEFAULT_MAX_PLANNING_TIME: float = 5.0              # DEFAULT max planning type is 5 seconds
    DEFAULT_PLANNER_TYPE: str = PlannerType.ASTAR.value # DEFAULT planner type is A* 

    # World State Variables
    _map: Optional[PlannerGrid] = None          # stores the latest version of the cost map
    _start_point: Optional[PlannerPoint] = None # stores the agent states point position for planning
    _goal_point: Optional[PlannerPoint] = None  # stores latest valid goal point received on send_goal_srv if goal point mission is active
    _vw_point: Optional[PlannerPoint] = None    # Stores latest virtual waypoint value received on vw topic
    
    # Node State Variables
    _state: NodeState = NodeState.INACTIVE # State of StrategyNode by default always INACTIVE
    _planner: Optional[Planner] = None           # planner class instance utilized for making path planning  
    
    # publishers
    _plan_pub: Optional[Publisher] = None        # <<nav_msgs/msg/Path>>
    _goal_point_pub: Optional[Publisher] = None  # <<geometry_msgs/msg/Point>> 
    
    # subscription
    _map_sub: Optional[Subscription] = None      # <<nav_msgs/msg/OccupancyGrid>>
    _agent_sub: Optional[Subscription] = None    # <<nav_msgs/msg/AgentState>> 
    _vw_sub: Optional[Subscription] = None       # <<geometry_msgs/msg/Point>>
    
    # Services 
    _activate_srv: Optional[Service] = None     # <<hybraut_interfaces/srv/SendGoal>> :: callback = goal_received_callback
    _deactivate_srv: Optional[Service] = None   # <<std_srvs/srv/Trigger>> :: callback = cancel_goal_callback
    
    #  Timers
    _replan_timer: Optional[Timer] = None         # operates at value of 1.0 / replan_frequency node param value, every time calling                                      # replan_callback
    _replan_lock: threading.Lock                               
    
    """ === Node Initialization === """

    def __init__(self, *args, **kwargs):
        """ 
        Initializes the planner node, setting parameters for dynamic 
        reconfiguration, setting up services for API interactition with planner,
        subscriptions for world state updates required for planning, 
        and publishers for planned paths and goal poses.
        Also sets up a timer for periodic replanning without starting it immediately.
        
        Args: 
            *args: Variable length argument list for Node
            **kwargs: Arbitrary keyword arguments for Node
        Returns: 
            None
        Raises:
            Exception: if any initialization step fails
        """
        super().__init__('strategy_node', namespace='hybraut_nav', *args, **kwargs)
        
        # Declare and initialize parameters
        self.__init_parameters__()
        
        # Initialize planner
        self.set_planner(self.get_parameter('planner').value)

        # Setup services
        self.__init_services__()

        # Setup parameter change callback
        self.add_on_set_parameters_callback(self._parameter_update_cb)

        # Setup subscriptions
        self.__init_subscriptions__()

        # Setup publishers
        self.__init_publishers__()
        
        # Setup timer
        self.__init_timer__()

        # NOTE: DONE, needs testing
    
    def __init_parameters__(self):
        """ 
        Declares node parameters for dynamic reconfiguration 
        of this planner node.
        
        Args: 
            None
            
        Returns: 
            None
        
        Raises:
            Exception: if parameters cannot be declared
        """
        # self.declare_parameter(
        #     'replan_frequency', 
        #     self.DEFAULT_REPLAN_FREQUENCY, 
        #     ParameterDescriptor(
        #         description='Frequency to replan the global path in Hz '
        #                    f'(default: {self.DEFAULT_REPLAN_FREQUENCY} Hz)'
        #     )
        # )
        self.declare_parameter(
            'planner', 
            self.DEFAULT_PLANNER_TYPE,
            ParameterDescriptor(
                description='Type of global planner to use. '
                           'Options: A*, Dijkstra, RRT, RRT* '
                           f'(default: {self.DEFAULT_PLANNER_TYPE})'
            )
        )
        # self.declare_parameter(
        #     'max_planning_time', 
        #     self.DEFAULT_MAX_PLANNING_TIME,
        #     ParameterDescriptor(
        #         description='Maximum time allowed for planning in seconds '
        #                    f'(default: {self.DEFAULT_MAX_PLANNING_TIME}s)'
        #     )
        # )
        self.declare_parameter(
            'description',
            self.__doc__ or "Global Planner Node for Hybraut Navigation Stack",
            ParameterDescriptor(
                description='Description of the planner node'
            )
        )

    # NOTE: DONE, needs testing
    def __init_services__(self):
        """ 
        Create services for planner activation and goal setting 
        and deactivation. 
        
        Args:
            None
        Returns: 
            None
        Raises: 
            Exception: if services cannot be created
        """
        self._activate_srv = self.create_service(
            SendPose,
            'planner/activate',
            self._goal_rcv_cb,
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        
        self._deactivate_srv = self.create_service(
            Trigger,
            'planner/deactivate',
            self._cancel_goal_cb,
            callback_group=MutuallyExclusiveCallbackGroup()
        )

    # NOTE: DONE, needs testing
    def __init_subscriptions__(self):
        """ 
        initializes topic subscriptions for world state updates required
        for path planning. These being the occupancy grid cost map, /map,
        and the agent state, /agent_state.
        
        Args:
            None
        
        Returns:
            None
        
        Raises: 
            None
        """
        self._map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            lambda msg: self._map_rcv_cb(msg),
            map_qos,
            callback_group=ReentrantCallbackGroup()
        )
        
        self._agent_sub = self.create_subscription(
            AgentState,
            '/agent_state',
            lambda msg: self._agent_state_rcv_cb(msg),
            world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

    # NOTE: DONE, needs testing
    def __init_publishers__(self):
        """
        Create topic publishers for planned paths and goal poses. 
        Args: 
            None
        Returns:
            None
        Raises:
            Exception: if publishers cannot be created        
        """
        self._plan_pub = self.create_publisher(
            Path,
            'planner/plan',
            qos_profile=world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )
        
        self._goal_pose_pub = self.create_publisher(
            PoseStamped,
            'planner/goal_pose',
            qos_profile=world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

    # NOTE: DONE, needs testing
    def __init_timer__(self):
        """ 
        Initialize a timer for periodic replanning
        without starting it immediately.The timer will call the _replan_callback method
        at the frequency defined by the replan_frequency parameter.
        
        Args: 
            None
            
        Returns: 
            None
    
        Raises: 
            Exception: if timer cannot be created  
        """
        pass
        # self.__replan_timer = self.create_timer(
        #     1.0 / self.get_replan_frequency(),
        #     self._replan_callback,
        #     autostart=(self.get_state() == NodeState.ACTIVE),
        #     callback_group=ReentrantCallbackGroup()
        # )

    """ === getters === """
    
    # def get_replan_frequency(self) -> float:
    #     """ 
    #     Getter for the replanning frequency in Hz. 
    #     Returns: 
    #         float: Replanning frequency in Hz

    #     Example: 
    #         >> freq = planner_node.get_replan_frequency()
    #         >> print(f"Replan Frequency: {freq} Hz")
            
    #     Test: tests/hybraut_nav_strategy/unit_tests/test_strategy_node:TestStrategy_node::test_get_replan_frequency 
    #     """
    #     return float(self.get_parameter('replan_frequency').value)
    
    def get_planner_type(self) -> str: 
        """ 
        getter for planner type as a string.
        
        Returns: 
            str: Planner type as string
            
        Example: 
            >> ptype = planner_node.get_planner_type()
            >> print(f"Current Planner Type: {ptype}") 
            
        Test: tests/hybraut_nav_strategy/unit_tests/test_strategy_node:TestStrategy_node::test_get_planner_type
        """
        return str(self.get_parameter('planner').value)

    # def get_max_planning_time(self) -> float:
    #     """
    #     getter for the maximum allowed planning time in seconds.

    #     Returns:
    #         float: Maximum planning time in seconds
            
    #     Example: 
    #         >> max_time = planner_node.get_max_planning_time()
    #         >> print(f"Max Planning Time: {max_time} seconds")
    #     """ 
    #     return float(self.get_parameter('max_planning_time').value)
    
    def get_description(self) -> str:
        """
        Getter for the description of the planner node.

        Returns:
            str: Description of the planner node
        """
        return str(self.get_parameter('description').value)
    
    def get_state(self) -> NodeState: 
        """
        Getter for the current state of the planner."""
        return self.__state
    
    """ === setters === """
    # TODO: Complete
    def set_planner(self, new_planner_type: Union[PlannerType, str], reset_replan_timer:Optional[bool]=False):
        """
        Setter for the planning algorithm type.
        
        Args: 
            planner_type: PlannerType: Type of planner to set
            reset_replan_timer: bool: This is an attribute that determines if you want to 
                                      restart the timer with the new planner type active,
                                      it will lock planner replan which changing attribute
            
        example:
            >>> set_planner(PlannerType.ASTAR)
            >>> set_planner(PlannerType.RRTSTAR)
        Raises:
            ValueError: if planner type is not recognized
            
        Tests: 
            -   
        """
        # initialize the planner from either PlannerType or string repr arg
        # passed into this function
        try:
            # Convert string to PlannerType if needed
            planner_type = (
                new_planner_type if isinstance(new_planner_type, PlannerType)
                else PlannerType.from_string(new_planner_type)
            )
            new_planner = PlannerType.initialize_planner(planner_type)
        except Exception as e:
            self.get_logger().error(f"Failed to set planner: {e}")
            raise

        # update ros2 param for parameter planner type with new planner type
        # self.set_parameters([rclpy.parameter.Parameter('planner_type', rclpy.Parameter.Type.STRING, planner_type.value)])
        
        # Acquire the replan lock to prevent race conditions while changing planner
        if hasattr(self, '__replan_lock'):
            self.__replan_lock.acquire()
        try:
            self._planner = new_planner
        finally:
            # Release the lock after updating planner
            if hasattr(self, '__replan_lock'):
                self.__replan_lock.release()
        
        
        
        
        # if not isinstance(planner_type, PlannerType) and not isinstance(planner_type, str):
        #     self.get_logger().error("invalid planner_type, can either be the string representation or the PlannerType enum")
            
        # # TODO: Do more logic for both str and PlannerType
        
        # try:
        #     self.planner = PlannerType.initialize_planner(planner_type)
        # except ValueError as e:
        #     self.get_logger().error(str(e))
     
    # # TODO: Add logic for if reste_replan_timer is set
    # def set_replan_frequency(self, new_replan_frequency: float, reset_replan_timer:Optional[bool] = False):
    #     """
    #     Update the replanning frequency.

    #     Args:
    #         new_frequency: New frequency in Hz
    #     """
    #     if not isinstance(new_replan_frequency, (float, int)):
    #         raise ValueError("Replan frequency must be a number")
        
    #     if not (0.01 <= new_replan_frequency <= 10.0):
    #         self.get_logger().warning("Replan frequency out of bounds (0.01 - 10.0 Hz). Clamping to valid range.")
    #         return
        
    #     self.set_parameters([rclpy.parameter.Parameter('replan_frequency', rclpy.Parameter.Type.DOUBLE, new_replan_frequency)])
    #     if hasattr(self, 'planner_timer') and self.planner_timer is not None:
    #         self.planner_timer.cancel()
    #     self.planner_timer = self.create_timer(
    #         1.0 / new_replan_frequency,
    #         self._replan_callback,
    #         autostart=(self.state == NodeState.ACTIVE),
    #         callback_group=ReentrantCallbackGroup()
    #     )
    #     self.get_logger().info(f'Replan frequency set to {new_replan_frequency} Hz')   

    # TODO: NEEDS COMPLETED
    # def set_max_planning_time(self, new_max_planning_time: float, reset_replan_timer): 
    #     ...
    
    def set_state(self, state: NodeState):
        """Set the current state of the planner."""
        if not isinstance(state, NodeState):
            raise Exception("State must be an instance of NodeState Enum")
        
        # should prob validate that if setting state to false 
        # timer is not running and vice versa
        self.__state = state
        
    """ === helper functions === """
    # NOTE: DONE: NEEDS TESTED
    def is_active(self) -> bool:
        """Check if planner is in active state."""
        return bool(self.__state == NodeState.ACTIVE)


    """ === Callback Functions === """
    """ === planner callback functions === """
    
    # def _replan_event(self): 
    #     """ 
    #     Event handler triggered by replan events such as deviation from course
    #     """
    #     ...
    
    # NOTE: DONE: NEEDS TESTED
    def _goal_rcv_cb(self, request: SendPose.Request, 
                          response: SendPose.Response) -> SendPose.Response:
        """
        Service callback to set a new goal pose and activate the planner.
        
        @flowchart: .diagrams/goal_received_callback_flowchart.puml
        

        Args:
            request: Service request containing goal pose
            response: Service response to populate
            
        Returns:
            Response with success status
        """
        # Step 1. Validate request, 
        #   - 1.0. validate that the request pose is a PoseStamped
        #   - 1.1. check if pose is valid
        #   - 1.2. check if pose frame_id matches agent state frame_id, both should be in 'map' frame
        #   - 1.3. check if the pose is within the bounds of the current cost map
        #   - 1.4. check that the pose is not too close to the agent's current position
        # 
        # if any of these checks fail, return response.success = False, response.message = 'reason', log an error message and return
        # Validate world state data availability for planning
        def _validate_goal(request_pose: PoseStamped) -> tuple[bool, str]:
            # Validate world state data
            if not (isinstance(self.__start_point, PoseStamped) and isinstance(self.__map, OccupancyGrid)):
                return False, "Cannot set goal: Missing World State Data (agent pose or cost map)"
            # Validate request pose type
            if not isinstance(request_pose, PoseStamped):
                return False, "Cannot set goal: Invalid goal pose"
            # Validate frame_id matches cost map
            cost_map_frame_id = self.__map.header.frame_id
            if request_pose.header.frame_id != cost_map_frame_id or self.__start_point.header.frame_id != cost_map_frame_id:
                return False, "Goal pose and agent state frame_id must match cost map frame_id"
            # Validate pose within cost map bounds
            map_origin_x = self.__map.info.origin.position.x
            map_origin_y = self.__map.info.origin.position.y
            map_width = self.__map.info.width * self.__map.info.resolution
            map_height = self.__map.info.height * self.__map.info.resolution
            pose_x = request_pose.pose.position.x
            pose_y = request_pose.pose.position.y
            if not (map_origin_x <= pose_x <= map_origin_x + map_width) or \
               not (map_origin_y <= pose_y <= map_origin_y + map_height):
                return False, "Goal pose is out of cost map bounds"
            return True, ""

        valid, message = _validate_goal(request.pose)
        if not valid:
            response.success = False
            response.message = message
            self.get_logger().warning(f"Received goal but validation failed: {message}")
            return response
        
        # Step 2: Attempt to generate initial plan between agent pose and goal pose
        #     2.1. if fails return response.success = False, return reason and return from function
        #     2.2. if succeeds, proceed to step 3
        try: 
            def _convert_msg_to_planner_args(
                grid: OccupancyGrid,                      
                start: PoseStamped, 
                goal: PoseStamped
            ) -> Tuple[PlannerGrid, PlannerPoint, PlannerPoint]:
                """ 
                A utiltiy function to convert ROS messages to planner-specific data structures.
                
                Args: 
                    - grid: nav_msgs/OccupancyGrid message representing the cost map
                    - start: geometry_msgs/PoseStamped message representing the start pose
                    - goal: geometry_msgs/PoseStamped message representing the goal pose
                
                Returns: 
                    - Tuple containing: 
                        - PlannerGrid: Internal grid representation for the planner
                        - PlannerPoint: Start point in planner's format
                        - PlannerPoint: Goal point in planner's format
                        
                example: 
                    >>> grid, start_pt, goal_pt = _convert_msg_to_planner_args(grid, start, goal)
                """
                grid: PlannerGrid = PlannerGrid.from_ros_msg(grid)
                start_pt: PlannerPoint = PlannerPoint.from_ros_msg(start)
                goal_pt: PlannerPoint = PlannerPoint.from_ros_msg(goal) 
                
                return (grid, start_pt, goal_pt)
            
            grid, start_pt, goal_pt = _convert_msg_to_planner_args(self.__map, self.__start_point, request.pose)
            path:Path = self._planner.plan_path(grid, start_pt, goal_pt)
        except Exception as e: 
            response.success = False
            response.message = f"Planning failed: {str(e)}"
            self.get_logger().error(f"Planning failed when setting new goal: {str(e)}")
            return response 
        
        # 3. If all check pass: 
        #   3.1. set the current goal pose
        #   3.2. if planner is inactive, activate it and start the replan timer
        #   3.3. initialize subscription to /hybraut_nav/virtual_waypoints topic to receive virtual waypoints from Layer 2 (Tactical layer) this means that we will replan when we recieve this  
        #   3.4. toggle state to active 
        #   3.4. return response.success = True
        # publish the path
        
        self.__goal_point = request.pose
        self.__toggle_state(self.__is_active()) # Toggle state to active is not already active
        self._activate_replan_timer()
        self.__plan_pub.publish(path)
        
        response.success = True
        response.message = "Goal set and planner activated"
        
        # initialize the virtual waypoint subscription
        # TODO: Implement the virtual waypoint subscription callback
        # self.__virtual_waypoint_subscription = self.create_subscription(
        #     PoseStamped,
        #     "/hybraut_nav/virtual_waypoints",
        #     self.__virtual_waypoints_callback
        # )
        return response

    # NOTE: DONE: NEEDS TESTED
    def _cancel_goal_cb(self, request: Trigger.Request, 
                            response: Trigger.Response) -> Trigger.Response:
        """
        Service callback to deactivate the planning for current goal.
        
        @flowchart: .diagrams/cancel_goal_callback_flowchart.puml
        
        Args:
            request: Service request (empty)
            response: Service response to populate
            
        Returns:
            Response with success status
        """
        
        try: 
            # Step 1: check if planner is already inactive
            if not self.is_active():
                response.success = False
                response.message = "Planner is already inactive"
                return response
            
            # # Step 2: deactivate replan timer
            # self._deactivate_replan_timer()

            # Step 3: reset goal related state variables
            self.__goal_point = None
            self.__vw_point = None

            # Step 4: toggle state to inactive
            # self.toggle_state(self.is_active())        
            
            # set successful deactivation response
            response.success = True
            response.message = "Planner deactivated and current goal cancelled"
        except Exception as e: 
            # handle unexpected exceptions gracefully
            response.success = False
            response.message = f"Unexpected error during deactivation: {str(e)}"


        # return response
        return response

    """ === World State Callback Functions === """

    def _map_rcv_cb(self, msg: OccupancyGrid):
        """
        Callback for cost map updates. 
        
        Args: 
            msg: OccupancyGrid message representing the cost map
        
        Returns: None
        
        raises: Exception logger message if message is invalid
        """
        # Basic validation: check message type and dimensions
        
        # should check if there is a difference betwene previous map and current map 
        if not isinstance(msg, OccupancyGrid):
            self.get_logger().error("Received cost map is not of type OccupancyGrid")
            return
        if msg.info.width == 0 or msg.info.height == 0 or msg.info.resolution <= 0:
            self.get_logger().error("Received cost map has invalid dimensions or resolution")
            return
        if not msg.data or len(msg.data) != msg.info.width * msg.info.height:
            self.get_logger().error("Received cost map data size does not match grid dimensions")
            return
        
        # If valid, update the current cost map
        self._map:PlannerGrid = PlannerGrid.from_ros_msg(msg)
        
    def _agent_state_rcv_cb(self, msg: AgentState):
        """Callback for agent state updates."""
        if not isinstance(msg, AgentState): 
            self.get_logger().error("Received agent state is not of type AgentState")
            return
        
        # Optionally: Validate frame_id matches cost map frame
        if hasattr(self, '_map') and self._map:
            if msg.header.frame_id != self._map.header.frame_id:
                self.get_logger().warning(
                    f"Agent pose frame_id ({msg.header.frame_id}) does not match cost map frame_id ({self._map.header.frame_id})"
                )
                
        current_agent_pose = PoseStamped(header=msg.header, pose=msg.pose)
        self._start_point:PlannerPoint = PlannerPoint.from_ros_msg(current_agent_pose)


    """ === dynamic configuration callback functions === """
    # NOTE: Done needs tested.
    def _parameter_update_cb(self, params: List[Parameter]) -> SetParametersResult:
        """
        Handle dynamic parameter changes.
        
        Args:
            params: List of parameters that changed
            
        Returns:
            Result indicating success or failure
        
        Tests: 
            Unit and integration test for this function can be found at: 
            - 
            -  
            -   
        """
        try: 
            for param in params:
                # if param.name == 'planner_frequency':
                #     self.set_replan_frequency(param.value)
                if param.name == 'planner':
                    self.set_planner(param.value)
                # elif param.name == 'max_planning_time':
                #     self.set_max_planning_time(param.value)
        except Exception as e: 
            return SetParametersResult(successful=False, reason=str(e))
        
        return SetParametersResult(successful=True)

    """ === planner functions === """



    # """ === Timer State Togglers"""
    
    # def _toggle_replan_timer(self): 
    #     """Toggler the replan timer state"""
    #     if self.is_active():
    #         self._deactivate_replan_timer() 
    #         self.__state = NodeState.INACTIVE
    #     else:
    #         self._activate_replan_timer()
    #         self.set_state
    
    # def _reconfigure_replan_timer(self):
    #     """
    #     reconfigures the replan timer with updated frequency.
        
    #     @flowchart: .diagrams/flowcharts/reconfigure_replan_timer_flowchart.puml
    #     Tests: 
    #     ...
    #     """
    #     autostart = False
    #     if self.is_active():
    #         autostart = True

    #     self.__replan_timer.destroy()

    #     self.__replan_timer = self.create_timer(
    #         1.0 / self.get_replan_frequency(),
    #         self._replan_callback,
    #         autostart=autostart,
    #         callback_group=ReentrantCallbackGroup()
    #     )
    
    # # NOTE: FUNCTION COMPLETE, NEEDS TESTING
    # def _activate_replan_timer(self) -> Tuple[bool, str]:
    #     """
    #     Activate the replanning timer if not already active without reconfiguration.
    #     Returns:
    #         Tuple[bool, str]: (True, message) if activated, (False, message) otherwise.
    #     """
    #     try: 
    #         if self.planner_timer.is_canceled():
    #             self.planner_timer.reset()
    #             return (True, "Replan timer activated successfully")
    #         else: 
    #             return (False, "Replan timer already active")
    #     except Exception as e:
    #         return (False, f"Failed to activate replan timer due to exception: {str(e)}")

    # # NOTE: FUNCTION COMPLETE, NEEDS TESTING
    # def _deactivate_replan_timer(self) -> Tuple[bool, str]: 
    #     """ 
    #     Deactivate the replanning timer if active without reconfiguration.
    #     Returns:
    #         Tuple[bool, str]: (True, message) if activated, (False, message) otherwise.
    #     """
    #     try: 
    #         if not self.planner_timer.is_canceled():
    #             self.planner_timer.cancel()
    #             return (True, "Replan timer deactivated successfully")
    #         else: 
    #             return (False, "Replan timer already inactive")
    #     except Exception as e:
    #         return (False, f"Failed to deactivate replan timer due to exception: {str(e)}")

    #     # TODO: NEED TO UPDATE THIS FUNCTION TO MATCH NEW ALGORITHM
    
    # def _replan_callback(self):
    #     """
    #     Timer callback to plan and publish path.
        
    #     Tests: 
    #     Unit and Integration tests for this function can be found @ 
    #         -    
    #         -   
    #         -   
            
    #     """
    #     # Publish current goal pose
    #     if self.current_goal_pose:
    #         self.goalpose_publisher.publish(self.current_goal_pose)
        
    #     # Check if planner should be active
    #     if not self.is_active():
    #         self.planner_timer.cancel()
    #         return

    #     # Verify all required data is available
    #     if not self._has_required_data():
    #         self.get_logger().debug("Missing required data for planning")
    #         return

    #     # Attempt to plan and publish path
    #     try:
    #         path:Path = self._compute_path()

    #         if path:
    #             path.header.frame_id = 'map'
    #             path.header.stamp = self.get_clock().now().to_msg()
    #             self._publish_plan(path)
    #         else: 
    #             self.get_logger().warn("Path planning returned no valid path, deactiving planner for current goal")
    #             self._deactivate_callback(Trigger.Request(), Trigger.Response())
    #     except Exception as e:
    #         self.get_logger().error(f"Planning failed: {str(e)}")


def main(args=None):
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init(args=args)
    node = StrategyNode()
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

# ============================================================================
# Independent Testing Code
# ============================================================================
