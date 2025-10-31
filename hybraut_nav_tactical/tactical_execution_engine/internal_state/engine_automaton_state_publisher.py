# !/usr/bin/python

"""
state publisher
"""

from rclpy.node import Node
from hybraut_interfaces.msg import AutomatonRuntimeState
from builtin_interfaces.msg import Duration
from rclpy.publisher import Publisher
from rclpy.timer import Timer
from tactical_execution_engine.internal_state.engine_automaton_state_tracker import EngineAutomatonStateTracker
from rclpy.qos import qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup

class EngineAutomatonStatePublisher:
    """
    state publisher
    """

    def __init__(self, node: Node, engine_automaton_state_tracker: EngineAutomatonStateTracker, publish_rate_hz: float = 1.0):
        """Constructor for the EngineAutomatonStatePublisher class."""
        self.node: Node = node
        self.engine_automaton_state_tracker: EngineAutomatonStateTracker = engine_automaton_state_tracker
        self.publisher: Publisher = node.create_publisher(
            msg_type=AutomatonRuntimeState,
            topic="/automaton/runtime_state",
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup(),
        )
        self.timer: Timer = node.create_timer(1.0 / publish_rate_hz, self.publish_state)

    def publish_state(self):
        """publishers the state of the automaton as a ROS message"""
        state = self.engine_automaton_state_tracker.get_runtime_state()
        active_duration = state.get("active_duration", 0.0)
        time_since_last_transition = state.get("time_since_last_transition", 0.0)
        current_mode = state.get("current_mode", -1)
        q_goals = state.get("q_goals", [])
        transition_count = state.get("transition_count", 0)

        msg = AutomatonRuntimeState(
            active_duration=self.gen_time_to_duration(active_duration),
            time_since_last_transition=self.gen_time_to_duration(
                time_since_last_transition
            ),
            current_mode=current_mode,
            q_goals=q_goals,
            transition_count=transition_count,
            stamp=self.node.get_clock().now().to_msg(),
        )
        self.publisher.publish(msg)

    def gen_time_to_duration(self, duration_sec: float) -> Duration:
        msg = Duration()
        msg.sec = int(duration_sec)  # whole seconds
        msg.nanosec = int(
            (duration_sec - msg.sec) * 1_000_000_000
        )  # fractional part to ns
        return msg


def main():
    import rclpy
    from rclpy.node import Node
    import threading
    from rclpy.executors import SingleThreadedExecutor

    rclpy.init()

    mock_node = Node("mock_node")
    executor = SingleThreadedExecutor()
    executor.add_node(mock_node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    engine_automaton_state_tracker: EngineAutomatonStateTracker = EngineAutomatonStateTracker(node=mock_node, initial_mode=0, q_goals=[1])

    state_publisher: EngineAutomatonStatePublisher = EngineAutomatonStatePublisher(
        node=mock_node, engine_automaton_state_tracker=engine_automaton_state_tracker, publish_rate_hz=1.0
    )
    
    from rclpy.subscription import Subscription  
    rcv_msgs = []
    state_subscription: Subscription = mock_node.create_subscription(
        msg_type=AutomatonRuntimeState,
        topic="/automaton/runtime_state",
        callback=lambda msg: rcv_msgs.append(msg),
        qos_profile=qos_profile_system_default,
        callback_group=ReentrantCallbackGroup(),
    )
    
    state_publisher.publish_state()
    import time
    time.sleep(0.1)
    assert rcv_msgs[-1].transition_count == 0, "initial transition count should be 0"


    time.sleep(1.0)
    engine_automaton_state_tracker.record_transition()
    # print(engine_automaton_state_tracker.get_runtime_state())
    state_publisher.publish_state()
    time.sleep(0.1)
    assert rcv_msgs[-1].transition_count == 1, "transition count should be 1"

    time.sleep(1.0)
    engine_automaton_state_tracker.record_transition()
    # print(engine_automaton_state_tracker.get_runtime_state())
    state_publisher.publish_state()
    time.sleep(0.1)
    assert rcv_msgs[-1].transition_count == 2, "transition count should be 2"

    time.sleep(5.0)
    # print()
    engine_automaton_state_tracker.record_transition()
    state_publisher.publish_state()
    time.sleep(0.1)
    assert rcv_msgs[-1].transition_count == 3, "transition count should be 3"


    executor.shutdown()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
