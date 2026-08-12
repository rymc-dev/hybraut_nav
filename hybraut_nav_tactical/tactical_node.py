# !/usr/bin/env python3
"""
Tactical Node for HybrautNav Navigation Stack is the second layer
responsible for tactical decision-making in navigation tasks.

It hosts a `colav_automaton.ColavAutomaton` (a `hybrid_automaton.Automaton`
definition) and drives it in real time:
    - odometry (`/odom`) is injected into the automaton's continuous state
      so guards/flows plan against the agent's real position/heading/speed.
    - the risk envelope (unsafe set) computed upstream by a risk_env-based
      ROS wrapper is subscribed to on `/hybraut_nav/riskenv` and pushed into
      the automaton's auxiliary state so COLAV guards (los_clear_to_waypoint,
      unsafe_conditions, safe_conditions) and the virtual-waypoint reset can
      route around it.
    - the automaton's resulting continuous state (the reference dynamics the
      active discrete mode's flow produces) is republished on
      `/hybraut_nav/continous_dynamics` for the immediate layer's controller
      to track, outputting yaw/velocity commands.
"""

import threading
import asyncio

import numpy as np
import rclpy
from rclpy.lifecycle import State, TransitionCallbackReturn, Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, PolygonStamped
from std_msgs.msg import Float64MultiArray
from scipy.spatial.transform import Rotation as R

from colav_automaton import ColavAutomaton
from hybrid_automaton import Automaton, ContinuousState, AuxiliaryState, RunResult


class TacticalNode(Node):

    def __init__(self, node_name: str = 'tactical_node', namespace: str = 'hybraut_nav', **kwargs) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)

        self._automaton: Automaton = None
        self._activation_thread: threading.Thread = None
        self._run_result: RunResult = None
        self._publish_timer = None

        # live state - kept up to date regardless of lifecycle state so that
        # whichever value is freshest is ready the moment we activate.
        self._x = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self._riskenv_vertices = np.empty((0, 2))

        # TODO: demo waypoint route until the strategic layer feeds real
        # waypoints in - go to (5, 5) then to (0, 0).
        self._demo_waypoints = [np.array([5.0, 5.0]), np.array([0.0, 0.0])]

        # handles into the running automaton's state objects - populated in
        # on_activate(). The runtime stores these by reference (it does not
        # copy them), so pushing into these objects directly from ROS
        # callbacks is enough to feed live data into the automaton.
        self._continuous_state: ContinuousState = None
        self._waypoints_aux: AuxiliaryState = None
        # NOTE: this MUST stay named 'unsafe_region' - colav_automaton's
        # guards/resets (guards.py, resets.py) hardcode that key when
        # looking up ctx.auxiliary_states. Only the ROS-facing topic and
        # local variables/subscriptions are named 'riskenv'.
        self._riskenv_aux: AuxiliaryState = None

        self.__init_subscriptions__()
        self._continuous_dynamics_pub = self.create_publisher(
            Float64MultiArray,
            '/hybraut_nav/continous_dynamics',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

        self._unconfigured_params_state = False
        self._inactive_params_state = False

        self._toggle_unconfigured_params_state()

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")

        try:
            self._automaton = ColavAutomaton(
                heading_tolerance=self.get_parameter('heading_tolerance').value,
                k_theta=self.get_parameter('k_theta').value,
                k_v=self.get_parameter('k_v').value,
                constant_velocity=self.get_parameter('constant_velocity').value,
                acceptance_radius=self.get_parameter('acceptance_radius').value,
                los_distance_threshold=self.get_parameter('los_distance_threshold').value,
                longitudinal_offset_distance=self.get_parameter('longitudinal_offset_distance').value,
                lateral_offset_distance=self.get_parameter('lateral_offset_distance').value
            )
            self._toggle_unconfigured_params_state()
            self._toggle_inactive_params_state()
        except Exception as e:
            raise Exception(f"{str(e)}")


        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try:
            dt = self.get_parameter('dt').value
            sensor_update_rate = self.get_parameter('sensor_update_rate').value
            publish_rate = self.get_parameter('continuous_dynamics_publish_rate').value

            self._continuous_state = ContinuousState(
                name='agent_state',
                x0=self._x.copy(),
                x_labels=['x', 'y', 'theta', 'v', 'yaw_rate'],
            )

            self._waypoints_aux = AuxiliaryState(name='waypoints', aux0=self._demo_waypoints[-1])
            for waypoint in reversed(self._demo_waypoints[:-1]):
                self._waypoints_aux.add(waypoint)

            self._riskenv_aux = AuxiliaryState(name='unsafe_region', aux0=self._riskenv_vertices.copy())

            self._activation_thread = threading.Thread(
                target=lambda: self._activation_thread_fn(dt, sensor_update_rate),
                daemon=True
            )
            self._activation_thread.start()

            self._publish_timer = self.create_timer(
                1.0 / publish_rate,
                self._publish_continuous_dynamics_cb,
                callback_group=ReentrantCallbackGroup()
            )

            self._toggle_inactive_params_state()
        except Exception as e:
            raise SystemError(f"{str(e)}")

        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Stopping tactical automaton...")

        try:
            if self._publish_timer:
                self._publish_timer.cancel()
                self.destroy_timer(self._publish_timer)
                self._publish_timer = None

            # Tell the automaton to stop gracefully
            if self._automaton:
                self._automaton.deactivate()

            # Wait for thread to complete naturally (don't force stop the loop)
            if self._activation_thread and self._activation_thread.is_alive():
                self._activation_thread.join(timeout=5.0)  # Increased timeout for safety

                if self._activation_thread.is_alive():
                    self.get_logger().warning("Activation thread did not exit cleanly")

            if self._run_result is not None:
                self.get_logger().info(self._run_result.summary())

            self._toggle_inactive_params_state()

        except Exception as e:
            self.get_logger().error(f"Error during deactivation: {str(e)}")
            raise SystemError(str(e))
        finally:
            # Clean up references
            self._activation_thread = None
            self._continuous_state = None
            self._waypoints_aux = None
            self._riskenv_aux = None
            if hasattr(self, "_loop"):
                delattr(self, "_loop")

        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state):
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try:
            self._toggle_inactive_params_state()
            self._toggle_unconfigured_params_state()
        except Exception as e:
            raise SystemError(f"{str(e)}")

        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")

        try:
            ...
        except Exception as e:
            return TransitionCallbackReturn.FAILURE

        return TransitionCallbackReturn.SUCCESS


    """ subscriptions """

    def __init_subscriptions__(self):
        self.odom_sub = self.create_subscription(
            msg_type=Odometry,
            topic='/odom',
            callback=lambda msg: self._odom_rcv(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        self.base_link_sub=self.create_subscription(
            msg_type=TransformStamped,
            topic='/base_link',
            callback=lambda msg: print (msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

        # TODO: continous_x state needs to be below
        # tf2_ros.Buffer().lookup_transform("odom", "base_link") # APPLYS ROTATION THEN TRANSLATION

        self.riskenv_sub = self.create_subscription(
            msg_type=PolygonStamped,
            topic='/hybraut_nav/riskenv',
            callback=lambda msg: self._riskenv_rcv(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

    """ asyncio activation"""
    def _activation_thread_fn(self, dt: float, sensor_update_rate: float):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._run_result = self._loop.run_until_complete(self._automaton.activate(
                initial_continuous_state=self._continuous_state,
                initial_auxiliary_states=[self._waypoints_aux, self._riskenv_aux],
                enable_real_time_mode=True,
                enable_self_integration=True,
                delta_time=dt,
                continuous_state_provider=self._continuous_state_provider,
                continuous_state_provision_rate=max(1, round(1.0 / sensor_update_rate)),
                should_write_logs=True,
                output_dir="./log_hybrid_automaton/"
            ))
        finally:
            self._loop.close()

    """ === odometry callback ==="""
    def _odom_rcv(self, msg: Odometry):
        quat = np.array([msg.pose.pose.orientation.__getattribute__(attr) for attr in ['x', 'y', 'z', 'w']])
        eul = R.from_quat(quat).as_euler('xyz')  # radians
        yaw = eul[2]
        self._x = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            yaw,
            msg.twist.twist.linear.x,
            msg.twist.twist.angular.z
        ])

    """ === risk envelope (unsafe set) callback === """
    def _riskenv_rcv(self, msg: PolygonStamped):
        """
        Consumes the hull vertices of the risk envelope (unsafe set), as
        produced by `riskenv.create_unsafe_set`, and pushes them straight
        into the automaton's 'unsafe_region' auxiliary state so the COLAV
        guards/resets see the latest risk data on their next evaluation.
        """
        vertices = np.array([[p.x, p.y] for p in msg.polygon.points], dtype=float)
        self._riskenv_vertices = vertices
        if self._riskenv_aux is not None:
            self._riskenv_aux.add(vertices)


    """ === parameters toggles === """

    def _toggle_unconfigured_params_state(self):
        """toggles ROS2 parameters available in unconfigured state"""
        try:
            if not self._unconfigured_params_state:
                self.declare_parameter(
                    'heading_tolerance',
                    0.2,
                    ParameterDescriptor(
                        name='heading_tolerance',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='heading tolerance. '
                                'cfg for guards for colav_automaton '
                                f'(default: {0.2})'
                    )
                )
                self.declare_parameter(
                    'k_theta',
                    1.0,
                    ParameterDescriptor(
                        name='k_theta',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='k_thate. '
                                'k_theta, control gains for theta controllers.'
                                f'(default: {1.0})'
                    )
                )
                self.declare_parameter(
                    'k_v',
                    1.0,
                    ParameterDescriptor(
                        name='k_v',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='k_v. '
                                'control gains for velocity controllers. '
                                f'(default: {1.0})'
                    )
                )
                self.declare_parameter(
                    'constant_velocity',
                    2.0,
                    ParameterDescriptor(
                        name='constant_velocity',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='constant_velocity. '
                                'constant_velocity for colav_automaton'
                                f'(default: {2.0})'
                    )
                )
                self.declare_parameter(
                    'acceptance_radius',
                    20.0,
                    ParameterDescriptor(
                        name='acceptance_radius',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='acceptance_radius'
                                'acceptance radius for waypoint reached guards in colav_automaton.'
                                f'(default: {20.0})'
                    )
                )
                self.declare_parameter(
                    'los_distance_threshold',
                    200.0,
                    ParameterDescriptor(
                        name='los_distance_threshold',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='los_distance_threshold. '
                                'los_distance_threshold for colav_automaton guards.'
                                f'(default: {200.0})'
                    )
                )
                self.declare_parameter(
                    'longitudinal_offset_distance',
                    100.0,
                    ParameterDescriptor(
                        name='longitudinal_offset_distance',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='longitudinal_offset_distance. '
                                'longitudinal_offset_distance for resets for colav_automaton '
                                f'(default: {100.0})'
                    )
                )
                self.declare_parameter(
                    'lateral_offset_distance',
                    100.0,
                    ParameterDescriptor(
                        name='declare_parameter',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='lateral_offset_distance. '
                                'lateral_offset_distance for resets for colav_automaton '
                                f'(default: {0.2})'
                    )
                )
            else:
                self.undeclare_parameter('heading_tolerance')
                self.undeclare_parameter('k_theta')
                self.undeclare_parameter('k_v')
                self.undeclare_parameter('constant_velocity')
                self.undeclare_parameter('acceptance_radius')
                self.undeclare_parameter('los_distance_threshold')
                self.undeclare_parameter('longitudinal_offset_distance')
                self.undeclare_parameter('lateral_offset_distance')
        except Exception as e:
            raise SystemError(str(e))

        self._unconfigured_params_state = not(self._unconfigured_params_state)

    def _toggle_inactive_params_state(self):
        """toggles ROS2 parameters available in inactive state"""
        try:
            if not self._inactive_params_state:
                self.declare_parameter(
                    'dt',
                    0.01,
                    ParameterDescriptor(
                        name='dt',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='dt. '
                                'delta time for evaluation steps. '
                                f'(default: {0.01})'
                    )
                )
                self.declare_parameter(
                    'sensor_update_rate',
                    0.01,
                    ParameterDescriptor(
                        name='sensor_update_rate',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='sensor_update_rate. '
                                'period (seconds) at which live odometry is re-injected '
                                'into the automaton continuous state. '
                                f'(default: {0.01})'
                    )
                )
                self.declare_parameter(
                    'continuous_dynamics_publish_rate',
                    50.0,
                    ParameterDescriptor(
                        name='continuous_dynamics_publish_rate',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='continuous_dynamics_publish_rate. '
                                'rate (Hz) at which the automaton continuous state is '
                                'republished on /hybraut_nav/continous_dynamics for the '
                                'immediate layer. '
                                f'(default: {50.0})'
                    )
                )
            else:
                self.undeclare_parameter('dt')
                self.undeclare_parameter('sensor_update_rate')
                self.undeclare_parameter('continuous_dynamics_publish_rate')
        except Exception as e:
            raise SystemError(str(e))

        self._inactive_params_state = not(self._inactive_params_state)

    """ === injection / publishing functions === """

    def _continuous_state_provider(self, ctx) -> np.ndarray:
        """
        Poll-based provider for the automaton runtime: periodically
        re-injects the agent's real (odometry-derived) continuous state so
        guards/flows stay anchored to reality rather than drifting purely
        off the integrated reference dynamics.
        """
        return self._x.copy()

    def _publish_continuous_dynamics_cb(self):
        """Publishes the automaton's current continuous state (the reference
        dynamics for the immediate layer's controller to track) at a fixed
        rate."""
        if self._continuous_state is None:
            return

        msg = Float64MultiArray()
        msg.data = self._continuous_state.latest().tolist()
        self._continuous_dynamics_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TacticalNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
