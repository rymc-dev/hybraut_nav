# !/usr/bin/env python3

""" """

import yaml
import rclpy
from rclpy.node import Node
from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus
from hybraut_executor_watchdog.fsm import FSM
from enum import Enum, auto
from hybraut_models import HybridAutomaton

from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup

from hybraut_execution_engine.event_handlers.world_state_update_handler import (
    WorldStateHandler,
    WorldStateHandlerHub,
)

from hybraut_execution_engine.evaluators import (
    DynamicEvaluator,
    InvariantEvaluator,
    TransitionEvaluator,
)
from rclpy.callback_groups import ReentrantCallbackGroup

from rclpy.timer import Timer

# from hybraut_execution_engine.event_handlers.world_state_update_handler import StateBus
from rclpy.qos import QoSProfile, qos_profile_system_default


QOS = qos_profile_system_default
CB_GROUP = ReentrantCallbackGroup()


class ExectorState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()


class ExecutionEngine(FSM):
    """
    Example subclass demonstrating how to override transition callbacks
    to add custom functionality while maintaining base behavior.
    """

    def __init__(
        self,
        node: Node,
        hybraut_model: HybridAutomaton,
        **cfg_kwargs,  # cfg_kwargs allow for option args for the hee like transition_evaluation_hz, invariant_evaluation_hz, dynamics_evaluation_hz
    ):

        self.state = ExectorState.INACTIVE
        self.node = node
        self.hybraut_model = hybraut_model
        self._engine_state_tracker = None
        self._event_publisher = node.create_publisher(
            AutomatonEvents,
            "/automaton/events",
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup(),
        )

        self._initialize_hee_evaluators(**cfg_kwargs)

        super().__init__(node=node, cb_group=CB_GROUP, qos=QOS, auto_activate=False)

    def _initialize_hee_evaluators(
        self,
        transitions_evaluation_hz: int = 10,
        invariants_evaluation_hz: int = 10,
        dynamics_evaluation_hz: int = 10,
    ):

        transition_evaluator: TransitionEvaluator = TransitionEvaluator(
            node=self.node,
            automaton=self.hybraut_model,
            state_tracker=self._engine_state_tracker,
            event_publisher=self._event_publisher,
        )

        dynamics_evaluator: DynamicEvaluator = DynamicEvaluator(
            node=self.node,
            automaton=self.hybraut_model,
            state_tracker=self._engine_state_tracker,
            event_publisher=self._event_publisher,
        )

        invariant_evaluator: InvariantEvaluator = InvariantEvaluator(
            node=self.node,
            automaton=self.hybraut_model,
            state_tracker=self._engine_state_tracker,
            event_publisher=self._event_publisher,
        )

        self._transition_evaluators_timer: Timer = self.node.create_timer(
            timer_period_sec=1.0 / transitions_evaluation_hz,
            callback=transition_evaluator(),
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
        )

        self._dynamics_evaluator_timer: Timer = self.node.create_timer(
            timer_period_sec=1.0 / dynamics_evaluation_hz,
            callback=dynamics_evaluator(),
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
        )

        self._invariant_evaluator_timer: Timer = self.node.create_timer(
            timer_period_sec=1.0 / invariants_evaluation_hz,
            callback=invariant_evaluator(),
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
        )

    """ === Execution Engine Activation functionality === """

    def activate(self, *args, **kwargs):
        if self.state == ExectorState.INACTIVE:
            self.error_count = 0
            self.recovery_attempts = 0
            super().activate()  # activate the base class watchdog
            self.__on_activate_hook__()  # activate the event handlers and evaluators for hybraut_model.
            self.state = ExectorState.ACTIVE

        else:
            print("already active")

    def __on_activate_hook__(
        self, qos: QoSProfile = QOS, cb_group: CallbackGroup = CB_GROUP
    ):
        """Hook called when executor is activated"""
        try:
            # Step 1: initialize the world state handlers
            state_keys = self.hybraut_model._state_registry.get_state_names()
            states = self.hybraut_model._state_registry.get_states_by_name(state_keys)
            self.world_state_handler_hub: WorldStateHandlerHub = WorldStateHandlerHub()

            for state in states.values():
                self.world_state_handler_hub.add_state_handler(
                    WorldStateHandler.create(
                        node=self.node,
                        state=state,
                        qos=qos,
                        cb_group=cb_group,
                    )
                )

            # step 2: initialize the evaluation entities
            self._activate_evaluators()

            # step 3: intiialize the main thread event handlers
            self._activate_event_handlers()

        except Exception as e:
            raise Exception(
                f"executor::HybrautExecutorError: error during activation hook: {str(e)}"
            )

    def _activate_evaluators(self):
        """=== activates the automaton async evaluators ==="""
        self._transition_evaluators_timer.start()
        self._invariant_evaluator_timer.start()
        self._dynamics_evaluator_timer.start()

    def _activate_event_handlers(self):
        """=== will activate the HEE event handlers ==="""
        ...

    """" === Execution Engine Deactivation functionality === """

    def deactivate(self):
        if self.state == ExectorState.ACTIVE:
            if self.is_activated:

                super().deactivate()

                self.state = ExectorState.INACTIVE
            else:
                print("not activated")
        else:
            print("not active")

    def __on_deactivate_hook__(self): ...

    """ === string representations === """

    def __str__(self): ...

    def __repr__(self): ...


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
            AutomatonEvents,
            "/automaton/events",
            qos_profile=QOS,
            callback_group=ReentrantCallbackGroup(),
        )

        # Start executor in background thread
        thread = threading.Thread(target=executor.spin, daemon=True)
        thread.start()

        path = "/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml"
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        automaton: HybridAutomaton = HybridAutomaton.register_automaton(
            node=node, amdl_dict=data
        )

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

        print(
            f"\nStarting Custom FSM demo. Initial state: {executor.get_current_state()}"
        )

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
        print(f"{str(e)}")


if __name__ == "__main__":
    main()
