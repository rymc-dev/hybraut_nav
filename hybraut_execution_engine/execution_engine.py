# !/usr/bin/env python3

"""
"""

import yaml
import rclpy
from rclpy.node import Node
from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus
from hybraut_executor_watchdog.fsm import FSM
from enum import Enum, auto
from hybraut_model import HybridAutomaton

from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from hybraut_execution_engine.event_handlers.world_state_update_handler import StateBus
from rclpy.qos import QoSProfile, qos_profile_system_default


QOS = qos_profile_system_default
CB_GROUP = ReentrantCallbackGroup()

class ExectorState(Enum): 
    INACTIVE=auto()
    ACTIVE=auto()

class ExecutionEngine(FSM):
    """
    Example subclass demonstrating how to override transition callbacks
    to add custom functionality while maintaining base behavior.
    """

    def evaluate_transitions_callback():
        ... 

    def evalaute_dynamics_callback():
        ...

    def evaluate_invariants_callback():
        ... 

    def __init__(self, node: Node, hybraut_model: HybridAutomaton):

        self.state = ExectorState.INACTIVE
        self.node = node
        self.hybraut_model = hybraut_model

        super().__init__(node=node, cb_group=CB_GROUP, qos=QOS, auto_activate=False)


    def activate(self, *args, **kwargs):
        if self.state == ExectorState.INACTIVE:
            self.error_count = 0
            self.recovery_attempts = 0
            super().activate()
            self.__on_activate_hook__()
            self.state = ExectorState.ACTIVE

        else:
            print ("already active")

    def _activate_evaluators(self):
        from hybraut_execution_engine.evaluators import DynamicEvaluator, InvariantEvaluator, TransitionEvaluator

        transition_evaluator = TransitionEvaluator(
            node=self.node,
            automaton=self.hybraut_model
        )

        invariant_evaluator = InvariantEvaluator(
            node=self.node,
            automaton=self.hybraut_model
        )

        transition_evaluator = TransitionEvaluator(
            node=self.node,
            automaton=self.hybraut_model
        )

        self.node.create_timer(
            timer_period_sec=1.0 / 10,
            callback=transition_evaluator(self.current_mode),
            callback_group=ReentrantCallbackGroup()
        )

        self.node.create_timer(
            timer_period_sec=1.0/10,
            callback=invariant_evaluator(self.current_mode),
            callback_group=ReentrantCallbackGroup()
        )

        self.node.create_timer(
            timer_period_sec=1.0 / 10,
            callback=invariant_evaluator(self.current_mode),
            callback_group=ReentrantCallbackGroup()
        )


    def deactivate(self):
        if self.state == ExectorState.ACTIVE: 
            if self.is_activated:

                super().deactivate()

                self.state = ExectorState.INACTIVE
            else: 
                print ("not activated")
        else: 
            print ("not active")

    def __on_activate_hook__(self, qos:QoSProfile = QOS, cb_group:CallbackGroup =CB_GROUP):
        """Hook called when executor is activated"""
        try:
            state_keys = self.hybraut_model._states.get_component_names()
            states = self.hybraut_model._states.get_components_by_names(state_keys)

            for state in states.values(): 
                state._state_bus = StateBus.create(
                    node=self.node,
                    topic=state._topic,
                    msg_type=state._msg_type,
                    state_callback=state.update_state,
                    qos=qos,
                    cb_group=cb_group
                )
        except Exception as e:
            raise Exception(f"executor::HybrautExecutorError: error during activation hook: {str(e)}")



    def __on_deactivate_hook__(self):
        ... 
        

def main():
    from rclpy.executors import MultiThreadedExecutor, Executor
    import os
    import threading

    rclpy.init()
    node = Node("hybraut_executor_demo")

    try:
        executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
        node = Node("hybraut_watchdog_demo")
        executor.add_node(node)

        event_publisher = node.create_publisher(
            AutomatonEvents, "/automaton/events", 
            qos_profile=QOS, callback_group=ReentrantCallbackGroup()
        )
        
        # Start executor in background thread
        thread = threading.Thread(target=executor.spin, daemon=True)
        thread.start()

        path = '/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml'
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        automaton:HybridAutomaton = HybridAutomaton.register_automaton(node=node, amdl_dict=data) 

        executor = ExecutionEngine(node=node, hybraut_model=automaton)
        executor.activate()

        test_events = [
            (AutomatonEvents.ACTIVATE_MISSION, "mission activated"),
            (AutomatonEvents.ENABLE_GUARD, "mode guard activated"),
            (AutomatonEvents.COMPLETE_TRANSITION, "transition completed"),
            (AutomatonEvents.HANDLE_RECOVERABLE_ERROR, "recoverable error occurred"),
            (AutomatonEvents.ATTEMPT_FIX_PROCESS, "attempting recovery"),
            (AutomatonEvents.COMPLETE_RECOVERY, "system recovered"),
            (AutomatonEvents.FINISH_MISSION, "mission finished"),
            (AutomatonEvents.DEACTIVATE_MISSION, "mission has completed"),
        ]
        
        print(f"\nStarting Custom FSM demo. Initial state: {executor.get_current_state()}")
        
        import time

        for event_type, message in test_events:
            print(f"\nPublishing event: {event_type}")
            event_msg = AutomatonEvents(type=event_type, message=message)
            event_publisher.publish(event_msg)
            time.sleep(0.5)
            print(f"Current state: {executor.get_current_state()}")
            print(f"Valid transitions: {executor.get_valid_transitions()}")
        
        print(f"\nFinal state: {executor.get_current_state()}")
        print(f"Is terminal state: {executor.is_terminal_state()}")

        time.sleep(5.0)

        executor.deactivate()
    except Exception as e:
        print  (f"{str(e)}")

if __name__ == "__main__":
    main()