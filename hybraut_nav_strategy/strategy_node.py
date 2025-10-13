#!/usr/bin/env python3

# TODO: Need to make strategic replans event driven not time driven.

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
from path_planning import (
    RRTStar, RRT, Dijkstra, AStar, Planner,
    Grid as PlannerGrid, Point as PlannerPoint
)

from rclpy.qos import HistoryPolicy, ReliabilityPolicy, DurabilityPolicy


# Constants
QOS_DEPTH = 10

map_qos = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL
)


from rclpy.subscription import Subscription
from rclpy.publisher import Publisher

from typing import Optional
from geometry_msgs.msg import Point
from rclpy.service import Service
import threading

# QoS Profile
qos_profile = QoSProfile(depth=QOS_DEPTH, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)


class StrategyState(Enum):
    """Enumeration for planner states."""
    INACTIVE = "inactive"
    ACTIVE = "active"


class PlannerType(Enum):
    """Enumeration for planner algorithm types."""
    ASTAR = 'AStar'
    DIJKSTRA = 'Dijkstra'
    RRT = 'RRT'
    RRTSTAR = 'RRT*'
    
    @staticmethod
    def from_string(planner_type_str: str) -> 'PlannerType':
        """
        Convert string to PlannerType enum.
        
        Args:
            planner_type_str: String representation of planner type
            
        Returns:
            Corresponding PlannerType enum member
            
        Raises:
            ValueError: If planner type string is not recognized
        """
        for pt in PlannerType:
            if pt.value == planner_type_str:
                return pt
        raise ValueError(f'Unknown planner type string: {planner_type_str}')

    @staticmethod
    def initialize_planner(planner_type: 'PlannerType') -> Planner:
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
            PlannerType.ASTAR: AStar,
            PlannerType.DIJKSTRA: Dijkstra,
            PlannerType.RRT: RRT,
            PlannerType.RRTSTAR: RRTStar
        }
        
        planner_class = planner_map.get(planner_type)
        if planner_class is None:
            raise ValueError(f'Unknown planner type: {planner_type}')
        
        return planner_class()


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
    __map: Optional[PlannerGrid] = None          # stores the latest version of the cost map
    __start_point: Optional[PlannerPoint] = None # stores the agent states point position for planning
    __goal_point: Optional[PlannerPoint] = None  # stores latest valid goal point received on send_goal_srv if goal point mission is active
    __vw_point: Optional[PlannerPoint] = None    # Stores latest virtual waypoint value received on vw topic
    
    # Node State Variables
    __state: StrategyState = StrategyState.INACTIVE # State of StrategyNode by default always INACTIVE
    __planner: Optional[Planner] = None           # planner class instance utilized for making path planning  
    
    # publishers
    __plan_pub: Optional[Publisher] = None        # <<nav_msgs/msg/Path>>
    __waypoint_pub: Optional[Publisher] = None  # <<geometry_msgs/msg/Point>> 
    
    # subscription
    __map_sub: Optional[Subscription] = None      # <<nav_msgs/msg/OccupancyGrid>>
    __agent_sub: Optional[Subscription] = None    # <<nav_msgs/msg/AgentState>> 
    __vw_sub: Optional[Subscription] = None       # <<geometry_msgs/msg/Point>>
    
    # Services 
    __send_goal_srv: Optional[Service] = None     # <<hybraut_interfaces/srv/SendGoal>> :: callback = goal_received_callback
    __cancel_goal_srv: Optional[Service] = None   # <<std_srvs/srv/Trigger>> :: callback = cancel_goal_callback
    
    #  Timers
    __replan_timer: Optional[Timer] = None         # operates at value of 1.0 / replan_frequency node param value, every time calling
                                                     # replan_callback
    __replan_lock: threading.Lock                               
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
        super().__init__('planner', namespace='hybraut_nav', *args, **kwargs)
        
        # Declare and initialize parameters
        self.__init_parameters__()
        
        # Initialize planner
        self.set_planner(self.get_parameter('planner_type').value)

        # Setup services
        self.__init_services__()

        # Setup parameter change callback
        self.add_on_set_parameters_callback(self._parameter_callback)

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
        self.declare_parameter(
            'replan_frequency', 
            self.DEFAULT_REPLAN_FREQUENCY, 
            ParameterDescriptor(
                description='Frequency to replan the global path in Hz '
                           f'(default: {self.DEFAULT_REPLAN_FREQUENCY} Hz)'
            )
        )
        self.declare_parameter(
            'planner_type', 
            self.DEFAULT_PLANNER_TYPE,
            ParameterDescriptor(
                description='Type of global planner to use. '
                           'Options: A*, Dijkstra, RRT, RRT* '
                           f'(default: {self.DEFAULT_PLANNER_TYPE})'
            )
        )
        self.declare_parameter(
            'max_planning_time', 
            self.DEFAULT_MAX_PLANNING_TIME,
            ParameterDescriptor(
                description='Maximum time allowed for planning in seconds '
                           f'(default: {self.DEFAULT_MAX_PLANNING_TIME}s)'
            )
        )
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
        self.__send_goal_srv = self.create_service(
            SendPose,
            'planner/send_goal',
            self._goal_received_callback,
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        
        self.__cancel_goal_srv = self.create_service(
            Trigger,
            'planner/cancel_goal',
            self.__cancel_goal_callback,
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
        self.__map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.__map_callback,
            map_qos,
            callback_group=ReentrantCallbackGroup()
        )
        
        self.__agent_sub = self.create_subscription(
            AgentState,
            '/agent_state',
            self._agent_state_callback,
            QOS_DEPTH,
            callback_group=ReentrantCallbackGroup()
        )
        
        self.__vw_sub = self.create_subscription(
            PoseStamped,
            '/tactical/virtual_waypoint',
            self._virtual_waypoint_callback,
            qos_profile=qos_profile,
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
        self.plan_pub = self.create_publisher(
            Path,
            'planner/plan',
            qos_profile=qos_profile,
            callback_group=ReentrantCallbackGroup()
        )
        # waypoint pub publishes the imminent waypoint 
        self.waypoint_pub = self.create_publisher(
            Point, 
            'planner/waypoint', 
            qos_profile=qos_profile,
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
        self.__replan_timer = self.create_timer(
            1.0 / self.get_replan_frequency(),
            self._replan_callback,
            autostart=(self.get_state() == StrategyState.ACTIVE),
            callback_group=ReentrantCallbackGroup()
        )

    """ === getters === """
    
    def get_replan_frequency(self) -> float:
        """ 
        Getter for the replanning frequency in Hz. 
        Returns: 
            float: Replanning frequency in Hz

        Example: 
            >> freq = planner_node.get_replan_frequency()
            >> print(f"Replan Frequency: {freq} Hz")
            
        Test: tests/hybraut_nav_strategy/unit_tests/test_strategy_node:TestStrategy_node::test_get_replan_frequency 
        """
        return float(self.get_parameter('replan_frequency').value)
    
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
        return str(self.get_parameter('planner_type').value)

    def get_max_planning_time(self) -> float:
        """
        getter for the maximum allowed planning time in seconds.

        Returns:
            float: Maximum planning time in seconds
            
        Example: 
            >> max_time = planner_node.get_max_planning_time()
            >> print(f"Max Planning Time: {max_time} seconds")
        """ 
        return float(self.get_parameter('max_planning_time').value)
    
    def get_description(self) -> str:
        """
        Getter for the description of the planner node.

        Returns:
            str: Description of the planner node
        """
        return str(self.get_parameter('description').value)
    
    def get_state(self) -> StrategyState: 
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
        self.set_parameters([rclpy.parameter.Parameter('planner_type', rclpy.Parameter.Type.STRING, planner_type.value)])
        
        # Acquire the replan lock to prevent race conditions while changing planner
        if hasattr(self, '__replan_lock'):
            self.__replan_lock.acquire()
        try:
            self.__planner = new_planner
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
     
    # TODO: Add logic for if reste_replan_timer is set
    def set_replan_frequency(self, new_replan_frequency: float, reset_replan_timer:Optional[bool] = False):
        """
        Update the replanning frequency.

        Args:
            new_frequency: New frequency in Hz
        """
        if not isinstance(new_replan_frequency, (float, int)):
            raise ValueError("Replan frequency must be a number")
        
        if not (0.01 <= new_replan_frequency <= 10.0):
            self.get_logger().warning("Replan frequency out of bounds (0.01 - 10.0 Hz). Clamping to valid range.")
            return
        
        self.set_parameters([rclpy.parameter.Parameter('replan_frequency', rclpy.Parameter.Type.DOUBLE, new_replan_frequency)])
        if hasattr(self, 'planner_timer') and self.planner_timer is not None:
            self.planner_timer.cancel()
        self.planner_timer = self.create_timer(
            1.0 / new_replan_frequency,
            self._replan_callback,
            autostart=(self.state == StrategyState.ACTIVE),
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info(f'Replan frequency set to {new_replan_frequency} Hz')   

    # TODO: NEEDS COMPLETED
    def set_max_planning_time(self, new_max_planning_time: float, reset_replan_timer): 
        ...
    
    def set_state(self, state: StrategyState):
        """Set the current state of the planner."""
        if not isinstance(state, StrategyState):
            raise Exception("State must be an instance of StrategyState Enum")
        
        # should prob validate that if setting state to false 
        # timer is not running and vice versa
        self.__state = state
        
    """ === helper functions === """
    # NOTE: DONE: NEEDS TESTED
    def is_active(self) -> bool:
        """Check if planner is in active state."""
        return bool(self.__state == StrategyState.ACTIVE)


    """ === Callback Functions === """
    """ === planner callback functions === """
    # NOTE: DONE: NEEDS TESTED
    def _goal_received_callback(self, request: SendPose.Request, 
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
            path:Path = self.__planner.plan_path(grid, start_pt, goal_pt)
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
    def __cancel_goal_callback(self, request: Trigger.Request, 
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
            
            # Step 2: deactivate replan timer
            self._deactivate_replan_timer()

            # Step 3: reset goal related state variables
            self.__goal_point = None
            self.__vw_point = None

            # Step 4: toggle state to inactive
            self.__toggle_state(self.is_active())        
            
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

    def __map_callback(self, msg: OccupancyGrid):
        """
        Callback for cost map updates. 
        
        Args: 
            msg: OccupancyGrid message representing the cost map
        
        Returns: None
        
        raises: Exception logger message if message is invalid
        """
        # Basic validation: check message type and dimensions
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
        self.current_cost_map = msg
        
    def _agent_state_callback(self, msg: AgentState):
        """Callback for agent state updates."""
        if not isinstance(msg, AgentState): 
            self.get_logger().error("Received agent state is not of type AgentState")
            return
        if not isinstance(msg.pose, Pose):
            self.get_logger().error("AgentState.pose is not of type Pose")
            return
        # Optionally: Validate frame_id matches cost map frame
        if hasattr(self, 'current_cost_map') and self.current_cost_map:
            if msg.header.frame_id != self.current_cost_map.header.frame_id:
                self.get_logger().warning(
                    f"Agent pose frame_id ({msg.header.frame_id}) does not match cost map frame_id ({self.current_cost_map.header.frame_id})"
                )
        self.current_agent_pose = PoseStamped(header=msg.header, pose=msg.pose)
        # Optionally: Log agent pose for debugging
        self.get_logger().debug(
            f"Updated agent pose: x={msg.pose.position.x}, y={msg.pose.position.y}, frame_id={msg.header.frame_id}"
        )
    
    # TODO: Work on virtual waypoint callback function
    def _virtual_waypoint_callback(self, msg: PoseStamped):
        if not isinstance(msg, PoseStamped):
            self.get_logger().error("Received virtual waypoint state.")
        
    """ === dynamic configuration callback functions === """
    # NOTE: Done needs tested.
    def _parameter_callback(self, params: List[Parameter]) -> SetParametersResult:
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
        for param in params:
            if param.name == 'planner_frequency':
                self.set_replan_frequency(param.value)
            elif param.name == 'planner_type':
                self._set_planner_type(param.value)
            elif param.name == 'max_planning_time':
                self.set_max_planning_time(param.value)

        return SetParametersResult(successful=True)

    """ === planner functions === """



    """ === Timer State Togglers"""
    
    def __toggle_replan_timer(self): 
        """Toggler the replan timer state"""
        if self.is_active():
            self._deactivate_replan_timer() 
            self.__state = StrategyState.INACTIVE
        else:
            self._activate_replan_timer()
            self.set_state
    
    def _reconfigure_replan_timer(self):
        """
        reconfigures the replan timer with updated frequency.
        
        @flowchart: .diagrams/flowcharts/reconfigure_replan_timer_flowchart.puml
        Tests: 
        ...
        """
        autostart = False
        if self.is_active():
            autostart = True

        self.__replan_timer.destroy()

        self.__replan_timer = self.create_timer(
            1.0 / self.get_replan_frequency(),
            self._replan_callback,
            autostart=autostart,
            callback_group=ReentrantCallbackGroup()
        )
    
    # NOTE: FUNCTION COMPLETE, NEEDS TESTING
    def _activate_replan_timer(self) -> Tuple[bool, str]:
        """
        Activate the replanning timer if not already active without reconfiguration.
        Returns:
            Tuple[bool, str]: (True, message) if activated, (False, message) otherwise.
        """
        try: 
            if self.planner_timer.is_canceled():
                self.planner_timer.reset()
                return (True, "Replan timer activated successfully")
            else: 
                return (False, "Replan timer already active")
        except Exception as e:
            return (False, f"Failed to activate replan timer due to exception: {str(e)}")

    # NOTE: FUNCTION COMPLETE, NEEDS TESTING
    def _deactivate_replan_timer(self) -> Tuple[bool, str]: 
        """ 
        Deactivate the replanning timer if active without reconfiguration.
        Returns:
            Tuple[bool, str]: (True, message) if activated, (False, message) otherwise.
        """
        try: 
            if not self.planner_timer.is_canceled():
                self.planner_timer.cancel()
                return (True, "Replan timer deactivated successfully")
            else: 
                return (False, "Replan timer already inactive")
        except Exception as e:
            return (False, f"Failed to deactivate replan timer due to exception: {str(e)}")

        # TODO: NEED TO UPDATE THIS FUNCTION TO MATCH NEW ALGORITHM
    
    def _replan_callback(self):
        """
        Timer callback to plan and publish path.
        
        Tests: 
        Unit and Integration tests for this function can be found @ 
            -    
            -   
            -   
            
        """
        # Publish current goal pose
        if self.current_goal_pose:
            self.goalpose_publisher.publish(self.current_goal_pose)
        
        # Check if planner should be active
        if not self.is_active():
            self.planner_timer.cancel()
            return

        # Verify all required data is available
        if not self._has_required_data():
            self.get_logger().debug("Missing required data for planning")
            return

        # Attempt to plan and publish path
        try:
            path:Path = self._compute_path()

            if path:
                path.header.frame_id = 'map'
                path.header.stamp = self.get_clock().now().to_msg()
                self._publish_plan(path)
            else: 
                self.get_logger().warn("Path planning returned no valid path, deactiving planner for current goal")
                self._deactivate_callback(Trigger.Request(), Trigger.Response())
        except Exception as e:
            self.get_logger().error(f"Planning failed: {str(e)}")

# ============================================================================
# Independent Testing Code
# ============================================================================

def create_test_cost_map(grid_size: int = 100, resolution: float = 1.0, 
                        node: Node = None) -> OccupancyGrid:
    """
    Create a test cost map with various obstacles.
    
    Args:
        grid_size: Size of the grid (grid_size x grid_size)
        resolution: Resolution in meters per cell
        node: ROS node for getting current time
        
    Returns:
        OccupancyGrid message with obstacles
    """
    import numpy as np
    from std_msgs.msg import Header
    
    cost_map = OccupancyGrid()
    cost_map.header = Header(
        stamp=node.get_clock().now().to_msg() if node else None,
        frame_id='map'
    )
    cost_map.info.resolution = resolution
    cost_map.info.width = grid_size
    cost_map.info.height = grid_size
    cost_map.info.origin.position.x = 0.0
    cost_map.info.origin.position.y = 0.0
    cost_map.info.origin.position.z = 0.0
    cost_map.info.origin.orientation.w = 1.0

    # Initialize grid with free space
    grid_data = [0] * (grid_size * grid_size)

    # Mark unknown borders
    for i in range(grid_size):
        for j in range(grid_size):
            if i == 0 or i == grid_size-1 or j == 0 or j == grid_size-1:
                grid_data[i * grid_size + j] = -1

    # Define obstacles
    obstacles = []
    
    # Vertical wall (30-70, 50)
    obstacles.extend([(i, 50) for i in range(30, 70)])
    
    # Horizontal wall (20, 30-80)
    obstacles.extend([(20, j) for j in range(30, 80)])
    
    # Small square (70-90, 20-40)
    obstacles.extend([(i, j) for i in range(70, 90) for j in range(20, 40)])
    
    # Diagonal island
    obstacles.extend([(50 + k, 70 + k) for k in range(5) 
                     if 50 + k < grid_size and 70 + k < grid_size])
    
    # Random scattered obstacles
    np.random.seed(42)
    for _ in range(10):
        i = np.random.randint(1, grid_size - 1)
        j = np.random.randint(1, grid_size - 1)
        obstacles.append((i, j))

    # Mark obstacles
    for i, j in obstacles:
        idx = i * grid_size + j
        grid_data[idx] = 100

    # Inflate obstacles with decaying cost
    inflation_radius = 3
    for i, j in obstacles:
        for di in range(-inflation_radius, inflation_radius + 1):
            for dj in range(-inflation_radius, inflation_radius + 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    distance = np.sqrt(di**2 + dj**2)
                    if distance <= inflation_radius:
                        idx = ni * grid_size + nj
                        if grid_data[idx] == 0:  # Only inflate free cells
                            cost = int(100 * (inflation_radius - distance) / inflation_radius)
                            grid_data[idx] = max(grid_data[idx], cost)

    cost_map.data = grid_data
    return cost_map


def create_test_poses(grid_size: int = 100, 
                     frame_id: str = 'map') -> tuple[PoseStamped, PoseStamped]:
    """
    Create test start and goal poses.
    
    Args:
        grid_size: Size of the grid
        frame_id: Frame ID for poses
        
    Returns:
        Tuple of (start_pose, goal_pose)
    """
    from geometry_msgs.msg import Point, Quaternion
    from std_msgs.msg import Header
    
    header = Header(frame_id=frame_id)
    
    start_pose = PoseStamped()
    start_pose.header = header
    start_pose.pose.position = Point(x=1.5, y=1.5, z=0.0)
    start_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    goal_pose = PoseStamped()
    goal_pose.header = header
    goal_pose.pose.position = Point(x=grid_size - 2.5, y=grid_size - 2.5, z=0.0)
    goal_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    
    return start_pose, goal_pose


def visualize_path(cost_map: OccupancyGrid, start_pose: PoseStamped, 
                  goal_pose: PoseStamped, path: Path):
    """
    Visualize the planned path on the cost map.
    
    Args:
        cost_map: The occupancy grid
        start_pose: Starting position
        goal_pose: Goal position
        path: Planned path
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    grid_size = cost_map.info.width
    grid_array = [cost_map.data[i * grid_size:(i + 1) * grid_size] 
                  for i in range(grid_size)]
    grid_np = np.array(grid_array)
    
    plt.figure(figsize=(10, 10))
    plt.imshow(grid_np, cmap=plt.cm.gray_r, origin='lower', 
               extent=[0, grid_size, 0, grid_size], alpha=0.5, vmin=-1, vmax=100)
    
    plt.plot(start_pose.pose.position.x, start_pose.pose.position.y, 
             'go', label='Start', markersize=12)
    plt.plot(goal_pose.pose.position.x, goal_pose.pose.position.y, 
             'ro', label='Goal', markersize=12)
    
    x = [pose.pose.position.x for pose in path.poses]
    y = [pose.pose.position.y for pose in path.poses]
    plt.plot(x, y, 'b-o', label='Planned Path', linewidth=2)
    
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('Global Path Planning Visualization')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    """Main function for standalone testing of the planner node."""
    import threading
    import time
    from rclpy.executors import MultiThreadedExecutor
    from colav_interfaces.msg import AgentState
    
    rclpy.init()
    
    # Create nodes
    planner_node = StrategyNode()
    mock_node = Node('mock_node')
    mock_node.received_path = None
    
    # Create publishers
    mock_cost_map_pub = mock_node.create_publisher(OccupancyGrid, '/map', 10)
    mock_agent_state_pub = mock_node.create_publisher(AgentState, '/agent_state', 10)
    
    # Create test data
    grid_size = 100
    cost_map = create_test_cost_map(grid_size, resolution=1.0, node=planner_node)
    start_pose, goal_pose = create_test_poses(grid_size)
    
    # Create agent state
    agent_state = AgentState()
    agent_state.header = start_pose.header
    agent_state.pose = start_pose.pose

    # Setup executor
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(planner_node)
    executor.add_node(mock_node)

    def path_callback(msg: Path):
        """Callback to capture received path."""
        print('Path received!')
        mock_node.received_path = msg

    try:
        # Start executor in background
        executor_thread = threading.Thread(target=executor.spin, daemon=True)
        executor_thread.start()
        time.sleep(1.0)
        
        # Setup path subscription
        mock_node.create_subscription(
            Path, '/hybraut_nav/plan', path_callback,
            qos_profile=qos_profile, callback_group=ReentrantCallbackGroup()
        )
        time.sleep(0.5)
        
        # Publish test data
        mock_cost_map_pub.publish(cost_map)
        time.sleep(1.0)
        mock_agent_state_pub.publish(agent_state)
        time.sleep(1.0)

        # Send goal via service
        client = mock_node.create_client(SendPose, '/hybraut_nav/send_goal')
        if not client.wait_for_service(timeout_sec=5.0):
            print("Service not available!")
            return
        
        future = client.call_async(SendPose.Request(pose=goal_pose))
        rclpy.spin_until_future_complete(mock_node, future)
        print(f"Goal set successfully: {future.result().success}")

        # Wait for path
        while mock_node.received_path is None:
            rclpy.spin_once(mock_node, timeout_sec=1.0)

        print("Path planning complete!")
        print(f"Path contains {len(mock_node.received_path.poses)} waypoints")

        # Visualize result
        visualize_path(cost_map, start_pose, goal_pose, mock_node.received_path)
        time.sleep(10.0)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        executor.shutdown()
        planner_node.destroy_node()
        mock_node.destroy_node()
        rclpy.shutdown()
        if executor_thread.is_alive():
            executor_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()