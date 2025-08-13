# !/usr/bin/python

""" 
runtime tracker for the hybraut execution engine
"""

import rclpy
from rclpy.node import Node
from rclpy.time import Duration
from typing import List

# TODO: Lets initialize the watchdog in here

class EngineStateTracker:
    """
    tracks the execution during runtime for the hybraut model
    """

    def __init__(self, node: Node, initial_mode: int, q_goals: List[int]):
        """ 
        contains the state of the hybraut engine.
        """
        self.node = node 
        self.start_time = node.get_clock().now()
        self.last_transition_time = self.start_time
        self.current_mode = initial_mode
        self.transition_count = 0
        self.q_goals = q_goals

    def set_current_mode(self, mode):
        self.current_mode = mode

    def record_transition(self):
        now = self.node.get_clock().now()
        self.last_transition_time = now
        self.transition_count+=1

    def get_runtime_state(self):
        now = self.node.get_clock().now()
        return {
            "active_duration": (now - self.start_time).nanoseconds / 1e9,
            "time_since_last_transition": (now - self.last_transition_time).nanoseconds / 1e9,
            "current_mode": self.current_mode,
            "q_goals": self.q_goals,
            "transition_count": self.transition_count
        }
    
    def reset(self): 
        self.start_time = self.node.get_clock()
        self.last_transition_time = self.start_time
        self.current_mode = None
        self.q_goals = None
        self.transition_count = 0


# def main():
#     import rclpy
#     from rclpy.node import Node
#     import threading
#     from rclpy.executors import SingleThreadedExecutor


#     rclpy.init()

#     mock_node = Node('mock_node')
#     executor = SingleThreadedExecutor()
#     executor.add_node(mock_node)

#     thread = threading.Thread(target=executor.spin)
#     thread.start()

#     runtime_tracker = RuntimeTracker(
#         node = mock_node,
#         initial_mode=0,
#         q_goals=[1]
#     )

#     print (runtime_tracker.get_runtime_state())

#     import time
#     time.sleep(1.0)
#     runtime_tracker.record_transition()
#     print (runtime_tracker.get_runtime_state())

#     time.sleep(1.0)
#     runtime_tracker.record_transition()
#     print (runtime_tracker.get_runtime_state())

#     time.sleep(5.0)
#     print (runtime_tracker.get_runtime_state())

#     executor.shutdown()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()


