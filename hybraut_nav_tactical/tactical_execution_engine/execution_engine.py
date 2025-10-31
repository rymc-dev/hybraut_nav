# !/usr/bin/env python3

""" 
Execution Engine is key component of the hybraut_ros2 package.
It encapsulate the hybraut_model for and automaton you initialize
and converts it into an active entity utilising three components defined 
within the engine itself, 

    - evaluators - async evaluators running on times where on each tick an evaluation occurs. 
    - internal state - an initialized class which stores internal state information of the hybraut_model
                       this information include current_mode, time elapsed, time elapsed since transition
                       among several other things, runs on the main thread. can be accessed by evaluators
    - event handlers - several subscriptions with event callbacks that cause internal state changes
    - watchdog - A Finite State Machine integrated within the ros eco system which represents the status of the hee with it's 
               - states, and transitions to different states utilizing ros2 events that correlate with transitions.
            
The execution engine itself has two states. INACTIVE and ACTIVE. these states can be toggled using the toggle function
"""

import yaml
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from rclpy.timer import Timer
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default

from hybraut_interfaces.msg import TransitionEvent
from tactical_execution_engine.watchdog.fsm import FSM

from hybraut_models import HybridAutomaton

from tactical_execution_engine.event_handlers.world_state_update_handler import (
    WorldStateHandler,
    WorldStateHandlerHub,
)

from tactical_execution_engine.evaluators import (
    DynamicEvaluator,
    InvariantEvaluator,
    TransitionEvaluator,
)
from rclpy.publisher import Publisher

from tactical_execution_engine.internal_state import EngineAutomatonStateTracker
from rclpy.clock import Clock

QOS = qos_profile_system_default
CB_GROUP = ReentrantCallbackGroup()
SYSTEM_CLOCK: Clock = None

class EngineState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    
    @staticmethod
    def description(state):
        descriptions = {
            EngineState.INACTIVE: "Hybraut Execution Engine is in `INACTIVE` state. In this state we simple have an initialized hee with no goal mission received, so watchdog, evaluators, event_handlers are not running on their timers",
            EngineState.ACTIVE: "Hybraut Execution Engine is in `ACTIVE` state. In this state the hee is running different features that make the hybraut model initialized in hee an active entitty"
        }


class ExecutionEngine(FSM):
    """
    Example subclass demonstrating how to override transition callbacks
    to add custom functionality while maintaining base behavior.
    """
    
    evaluators = {
        "transition_evaluator": TransitionEvaluator,
        "dynamics_evaluator": DynamicEvaluator,
        "invariant_evaluator": InvariantEvaluator
    }
    
    event_handlers = {
        
    }
    
    def __init__(
        self,
        node: Node,
        hybraut_model: HybridAutomaton,
        **cfg_kwargs,  # cfg_kwargs allow for option args for the hee like transition_evaluation_hz, invariant_evaluation_hz, dynamics_evaluation_hz
    ):
        """
        Initialize engine with cfg for EngineState.INACTIVE
        """
        
        # Initialize the inactive watchdog which acts as the base class for execution engine,
        # It keeps track of the overall status of the engine
        super().__init__(node=node, cb_group=CB_GROUP, qos=QOS, auto_activate=False)
        
        # Initialize Engine init attributes
        self._node: Node = node
        self._hybraut_model: HybridAutomaton = hybraut_model
        
        # Intiiaizle Engine Inactive State Attributes
        self._engine_state: EngineState = EngineState.INACTIVE
        self._event_publisher: Publisher        
        self._engine_automaton_state_tracker: EngineAutomatonStateTracker = None
        self._world_state_handler_hub: WorldStateHandlerHub = None
        
        self._initialize_evaluators(**cfg_kwargs)

        self._node.get_logger().info(f"Hybraut Execution Engine has been initialized and is currently in '{self.engine_state}'")

    def _initialize_evaluators(
        self,
        evaluator_hz: int = 10,
        cb_group: CallbackGroup = ReentrantCallbackGroup
    ):
        """ 
        initializes the timers associated with evaluators
        defined in class static variables
        """
        
        for evaluator_name, evaluator_type in self.evaluators: 
            evaluator = evaluator_type(
                node=self._node,
                automaton=self._hybraut_model,
                engine_automaton_state_tracker=self._engine_automaton_state_tracker,
                event_publisher=self._event_publisher
            )    
            
            self.__setattr__(
                name=f"{evaluator_name}_timer",
                value=self._node.create_timer(
                    timer_period_sec=1.0 / evaluator_hz,
                    callback=evaluator(),
                    callback_group=cb_group,
                    clock=SYSTEM_CLOCK,
                    autostart=False
                )    
            )

    """ === Execution Engine Activation/Deactivation toggler function === """

    def toggle(self, *args, **kwargs):
        """ 
        A function utilized for toggling between Hybraut Exection Engine `(HEE)`
        `ACTIVE` and `INACTVE` engine states
        """
       
        if self._engine_state == EngineState.INACTIVE:
            """ === Activate Hybraut Execution Engine (HEE) === """
            self._node.get_logger().info(f"Execution Engine activation requested, attemping activation...")
            
            self.error_count = 0
            self.recovery_attempts = 0
            try:
                self.__on_activate_hook__()
            except Exception as e:
                self._node.get_logger().error(f"fatal activation exception occured: {str(e)}")
                
            self._engine_state = EngineState.ACTIVE
            self._node.get_logger().info(f"Execution Engine successfully activated!")
            
        # Toggle Deactivation
        elif self._engine_state == EngineState.ACTIVE:
            """ === Deactivate Hybraut Execution Engine (HEE) ==="""
            self._node.get_logger().info(f"Execution Engine deactivation requested, attempted deactivation...")
            
            self.error_count = 0
            self.recovery_attempts = 0
            try:
                self.__on_deactivate_hook__()
            except Exception as e:
                self._node.get_logger().error(f"fatal deactivation exception occured: {str(e)}")
                raise e
            
            self._engine_state = EngineState.INACTIVE
            self._node.get_logger().info(f"Execution Engine successfully deactivated!")

    """ === Activation toggler hooks === """
    
    def __on_activate_hook__(
        self, qos: QoSProfile = QOS, cb_group: CallbackGroup = CB_GROUP
    ):
        """activation hook, performs attribute initialization and starts active engine components"""
        try:
            # Step 1: initialize the world state handlers
            state_keys = self._hybraut_model._state_registry.get_state_names()
            states = self._hybraut_model._state_registry.get_states_by_name(state_keys)
            self._world_state_handler_hub: WorldStateHandlerHub = WorldStateHandlerHub()

            for state in states.values():
                self._world_state_handler_hub.add_state_handler(
                    WorldStateHandler.create(
                        node=self._node,
                        state=state,
                        qos=qos,
                        cb_group=cb_group,
                    )
                )
                
            # step 2: initialize the evaluation entities
            self._activate_evaluators()

            # step 3: intiialize the main thread event handlers
            self._activate_event_handlers()
            
            self._event_publisher = self._node.create_publisher(
                TransitionEvent,
                "/automaton/events",
                qos_profile=qos_profile_system_default,
                callback_group=ReentrantCallbackGroup(),
            )

        except Exception as e:
            raise Exception(
                f"executor::HybrautExecutorError: error during activation hook: {str(e)}"
            )

    def _activate_evaluators(self):
        """=== activates the automaton async evaluators ==="""
        for evaluator_name in list(self.evaluators.keys()):
            timer_name = f"{evaluator_name}_timer"
            timer: Timer = self.__getattribute__(
                timer_name
            )
            timer.reset()

    def _activate_event_handlers(self):
        """=== will activate the HEE event handlers ==="""
        ...

    """ === Deactivation toggler hooks === """

    def __on_deactivate_hook__(self): ...

    """ === string representations === """

    def __str__(self): 
        """string representation of the hybraut execution engine"""
        ...

    def __repr__(self): 
        """representation of the hybraut execution engine, contains state information as well"""
        ...


""" === Code below is for local testing, note for production use === """

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
            TransitionEvent,
            "/automaton/events",
            qos_profile=QOS,
            callback_group=ReentrantCallbackGroup(),
        )

        # Start executor in background thread
        thread = threading.Thread(target=executor.spin, daemon=True)
        thread.start()

        path = "/home/ryan/ros2_ws/src/hybraut_ros2/example_amdls/hybraut_tb3.amdl.yml"
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        from hybraut_model_factory.amdl import HybridAutomatonFactory
        
        automaton: HybridAutomaton = HybridAutomatonFactory.register_automaton(
            amdl_dict=data
        )

        executor: ExecutionEngine = ExecutionEngine(node=node, hybraut_model=automaton)
        executor.toggle()

        test_events = [
            (TransitionEvent.ACTIVATE_MISSION, "mission activated"),
            (TransitionEvent.ENABLE_GUARD, "mode guard activated"),
            (TransitionEvent.COMPLETE_TRANSITION, "transition completed"),
            (TransitionEvent.HANDLE_RECOVERABLE_ERROR, "recoverable error occurred"),
            (TransitionEvent.ATTEMPT_FIX_PROCESS, "attempting recovery"),
            (TransitionEvent.COMPLETE_RECOVERY, "system recovered"),
            (TransitionEvent.FINISH_MISSION, "mission finished"),
            (TransitionEvent.DEACTIVATE_MISSION, "mission has completed"),
        ]

        print(
            f"\nStarting Custom FSM demo. Initial state: {executor.get_current_state()}"
        )

        import time

        for event_type, message in test_events:
            print(f"\nPublishing event: {event_type}")
            event_msg = TransitionEvent(type=event_type, message=message)
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
