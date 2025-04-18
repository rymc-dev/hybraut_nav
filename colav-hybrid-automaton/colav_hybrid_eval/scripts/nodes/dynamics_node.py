#!/usr/bin/python3
"""
A real-time ROS 2 node that evaluates and publishes the control dynamics
of an agent based on its current state and control mode.

The `DynamicsNode` operates within a hybrid control architecture, switching
between different controller implementations such as CRUISE, T2LOS (Trajectory-To-Line-of-Sight),
FALLBACK, and WAYPOINT_REACHED. Each controller is responsible for generating
appropriate dynamics based on situational inputs like agent state and waypoints.

This node subscribes to:
- Control mode updates (String)
- Agent state updates (AgentUpdate)
- Waypoint updates (Waypoints)

It publishes:
- DynamicsUpdate messages, containing evaluated dynamics and metadata

Services:
- `/dynamics_node/start_dynamics_evaluation`: Starts dynamics evaluation
- `/dynamics_node/stop_dynamics_evaluation`: Placeholder for stopping evaluation

Key Features:
- Modular design using a dictionary for control mode-to-function mapping
- Timed callback for continuous dynamics evaluation
- Built-in error handling and diagnostics via ROS 2 logging
- Easily extendable to support new control modes or logic

This class is central to ensuring real-time reactive behavior in the agent,
enabling adaptive control across dynamic scenarios.

Attributes:
    _MODES (dict): Maps control mode IDs to their string names.
    _DYNAMICS (dict): Maps control mode names to their corresponding function handlers.
    _control_mode (str): Current active control mode.
    _agent_state (AgentUpdate): Latest received state of the agent.
    _waypoint (Waypoint): Active navigation waypoint for trajectory guidance.
    _dynamics_pub (Publisher): ROS publisher for `DynamicsUpdate` messages.

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""


# === Standard Library Imports ===
from colav_hybrid_eval.config.qos_config import QOS_PROFILE
from scripts.dynamics import (
    dynamics_CRUISE,
    dynamics_T2LOS,
    dynamics_FB,
    dynamics_WAYPOINT_REACHED
)
from colav_hybrid_eval.utils import get_current_ros_time
from colav_interfaces.msg import (
    AgentUpdate,
    Waypoints,
    DynamicsUpdate,
    Dynamics
)
from std_msgs.msg import String
from std_srvs.srv import Trigger
from rclpy.node import Node
import rclpy
import os
import sys

# Add two directories back to sys.path: necessary for local debugging when the package isn't built with colcon,
# allowing imports to work correctly without relying on the build process.
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..')))

# === ROS 2 Core Imports ===

# === ROS2 STD Interface Imports ===

# === COLAV Interface Messages ===

# === COLAV Hybrid Evaluation Utilities ===

# === COLAV Hybrid Evaluation Utilities ===

# === Configuration ===


class InitializationError(Exception):
    """Custom exception for initialization-related failures."""

    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message


class DynamicsNode(Node):
    """
    DynamicsNode is an rclpy node that implemenst real-time dynamics evaluations
    for the COLAV Hybrid Automaton specific to the control mode we are in.

    This node provides services to srtart and stop the dynamics evaluation process.
    It continously evaluates dyanmics in real time based on the incoming waypoint and
    agent_state data we receive from subscribed topics and publishes the results to
    a dedicated `dynamics` topic.
    """

    _MODES = {  # Dict shows different control modes
        1: "CRUISE",
        2: "T2LOS",
        3: "FB",
        4: "WAYPOINT_REACHED"
    }

    _DYNAMICS = {  # Dict shows the dynamics controllers associated the different modes
        _MODES[1]: dynamics_CRUISE,
        _MODES[2]: dynamics_T2LOS,
        _MODES[3]: dynamics_FB,
        _MODES[4]: dynamics_WAYPOINT_REACHED
    }

    def __init__(
        self,
        namespace: str = "hybrid_automaton",
        name: str = "dynamics_node"
    ):
        """
        Initializes the dynamics_node
        """
        super().__init__(name, namespace=namespace)

        self._control_mode = None
        self._agent_state = None
        self._obstalces_state = None
        self._waypoint = None

        self._init_node_srvs()
        self.get_logger().info(f"{namespace}/{name} node initialised!")

    def _init_node_srvs(self, node_name: str = "dynamics_node"):
        """
        Initializes node services
        - the start_dynamic_evaluations and stop_dynamics_evaluations
        - Raises InitializationError if exception thrown during service creation
        """
        try:
            return {
                "start_dynamic_evaluations": self.create_service(
                    srv_type=Trigger,
                    srv_name=f'{node_name}/start_dynamics_evaluation',
                    callback=self._start_dynamics_evaluation_callback

                ),
                "stop_dynamics_evaluations": self.create_service(
                    srv_type=Trigger,
                    srv_name=f'{node_name}/stop_dynamics_evaluation',
                    callback=self._stop_dynamics_evaluation_callback
                )
            }
        except Exception:
            raise InitializationError(
                'Node Services',
                "Excpetion occured initializing start/stop guard_evaluations services for this node")

    def _start_dynamics_evaluation_callback(
            self,
            request: Trigger.Request,
            response: Trigger.Response):
        """callback for starting dynamics evaluation callback"""
        try:
            self._dynamics_pub = self.create_publisher(
                msg_type=DynamicsUpdate,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE
            )
            self._control_mode_sub = self.create_subscription(
                msg_type=String,
                topic='/hybrid_automaton/mode',
                callback=lambda msg: self.__setattr__(
                    '_control_mode',
                    msg.data),
                qos_profile=QOS_PROFILE)
            self._agent_state_sub = self.create_subscription(
                msg_type=AgentUpdate,
                topic='/agent_update',
                callback=lambda msg: self.__setattr__('_agent_state', msg),
                qos_profile=QOS_PROFILE
            )
            self._waypoints_sub = self.create_subscription(
                msg_type=Waypoints,
                topic='/hybrid_automaton/waypoints',
                callback=self._waypoints_callback,
                qos_profile=QOS_PROFILE
            )
            self._dynamics_timer = self.create_timer(
                float(0.1),
                self._update_dynamics_callback
            )
            response.success = True
            response.message = "dynamics evaluation successfully started!"
        except Exception as e:
            self.get_logger().error(
                f'error when attempting to start dynamics_evaluation: {str(e)}')
            response.success = False
            response.message = f"Error occured: {str(e)}"

        return response

    def _waypoints_callback(self, msg: Waypoints):
        """callback to get the current waypoint"""
        if len(msg.waypoints) > 0:
            self._waypoint = msg.waypoints[0]

    def _stop_dynamics_evaluation_callback(
            self,
            request: Trigger.Request,
            response: Trigger.Response):
        pass

    def _update_dynamics_callback(self):
        """updating dynamics"""
        dynamics_update = DynamicsUpdate()
        try:
            if self._control_mode not in list(self._MODES.values()):
                raise ValueError(
                    f'control mode received: {self._control_mode} not in MODES')

            if self._control_mode == self._MODES[1]:
                # CRUISE DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[1]](
                    agent_state=self._agent_state, dt=0.1)  # TODO: NEED DT TO BE CONFIGED BY COLAV_PARAMS
                dynamics_update.control_mode = self._MODES[1]

            elif self._control_mode == self._MODES[2]:
                # T2LOS DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[2]](
                    agent_state=self._agent_state, waypoint=self._waypoint)
                dynamics_update.control_mode = self._MODES[2]

            elif self._control_mode == self._MODES[3]:
                # FALLBACK DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[3]]()
                dynamics_update.control_mode = self._MODES[3]

            elif self._control_mode == self._MODES[4]:
                # WAYPOINT_REACHE DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[4]]()
                dynamics_update.control_mode = self._MODES[4]

            else:  # EDGE CASE
                raise RuntimeError('something went wrong here.')

            dynamics_update.dynamics = dynamics
            dynamics_update.error = False
        except Exception as e:
            dynamics_update.error = True
            dynamics_update.error_message = f"Error occured: {str(e)}"

        dynamics_update.timestamp = get_current_ros_time()
        self._dynamics_pub.publish(dynamics_update)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicsNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occured: {str(e)}')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
