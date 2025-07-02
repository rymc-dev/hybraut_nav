from threading import Lock
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum
from typing import List, Dict, Any
from rclpy.publisher import Publisher
from builtin_interfaces.msg import Time
from hybrid_automaton_interfaces.msg import HybridAutomatonGuardEvaluations
from rclpy.logging import RcutilsLogger
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.utils import validate_mode
from hybrid_automaton_interfaces.msg import HybridAutomatonMode
from typing import NamedTuple


class ModeTypeMapValue(NamedTuple):
    value: int
    name: str

class StateMapValue(NamedTuple):
    state_name: str
    state_value: Any


def evaluate_guards_timer_callback(
    lock: Lock,
    current_mode: HybridAutomatonMode, 
    current_mode_transitions: Dict[int, str],
    automaton_modes: List[ModeTypeMapValue],
    automaton_status: HybridAutomatonStatusEnum,
    automaton_states: List[StateMapValue],
    stamp: Time,
    
    status_publisher: Publisher,
    guards_evaluation_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    callback evaluates transitions available for the current Hybrid automaton mode.
    """
    try:
        with lock:
            eval: HybridAutomatonGuardEvaluations = HybridAutomatonGuardEvaluations(stamp=stamp) 
            try:
                if status is HybridAutomatonStatus.STATUS_TRANSITIONING:            
                    return
                else:
                    eval.mode = validate_mode(available_modes, mode)

                    eval.success = True
                    eval.transition_names = []
                    eval.guard_evaluations = []
                    eval.guard_priority = []

                    error_messages = []
                    for transition_key in mode_transitions:
                        try:
                            transition_config = mode_transitions[transition_key]
                            state_inputs = [states[s] for s in transition_config['guard']['state_inputs']]
                            guard_eval = bool(transition_config['guard']['function'](*state_inputs))
                            
                            eval.transition_names.append(transition_key)
                            eval.guard_evaluations.append(guard_eval)
                            eval.guard_priority.append(transition_config['priority'])
                        except Exception as e:
                            error_messages.append(f"{transition_key}: {str(e)}")
                            eval.success = False

                    if error_messages:
                        raise ValueError(f"guards exceptions: \n" + "- ".join(error_messages))

                    if any(eval.guard_evaluations):
                        status = HybridAutomatonStatus.STATUS_TRANSITIONING
                        # status_publisher.publish(String(data=str(HybridAutomatonStatus.TRANSITIONING.name))) # TODO: Return these when status callback has been tested.
                    else:
                        status = HybridAutomatonStatus.STATUS_ACTIVE_MODE
                        # status_publisher.publish(String(data=str(HybridAutomatonStatus.EXECUTING_MODE.name)))

                    
            except Exception as e:
                # status_publisher.publish(String(data=str(HybridAutomatonStatus.ERROR.name)))
                eval.success = False
                eval.message = f"exception occured during '{mode}' transition evaluation: '{str(e)}'" 

            guards_evaluation_publisher.publish(eval)

    except Exception as e: 
        logger.error(f"unexpected exception occured in 'colav_hybrid_automaton.automaton.callbacks.transition_callbacks.evaluate_transitions_timer_callback': '{str(e)}'")
        

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
from colav_interfaces.msg import AgentState, WaypointsState

if __name__ == '__main__':
    # 1. Start rclpy
    rclpy.init()

    # 2. Create Test Node, for publishers and subscriptions
    test_node = Node('test_node')   

    # 3. Create test_node publishers for guard_evaluation_callback test
    status_publisher = test_node.create_publisher(
        msg_type=HybridAutomatonStatus,
        topic='/hybrid_automaton/status',
        qos_profile=10
    )
    guard_publisher = test_node.create_publisher(
        msg_type=HybridAutomatonGuardEvaluations,
        topic="/hybrid_automaton/guards",
        qos_profile=10
    )

    # 4. Create test_node subscriptions to topics that guard evaluations callback will publish its evaluations to
    status_values = []
    test_node.create_subscription(
        msg_type=HybridAutomatonStatus,
        topic='/hybrid_automaton/status',
        callback=lambda msg: status_values.append(msg),
        qos_profile=10
    )
    guard_evaluation_values = []
    guard_sub = test_node.create_subscription(
        msg_type=HybridAutomatonGuardEvaluations,
        topic="/hybrid_automaton/guards",
        callback=lambda msg: guard_evaluation_values.append(msg),
        qos_profile=10
    )

    # 5. Create multi threading executor for test node and start background thread for it.
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(test_node)
    threading.Thread(target=executor.spin, daemon=True).start()

    # 6. Mock required guards_evaluation_timer_callback data.
    guard_evaluation_lock = threading.Lock()

    current_mode = HybridAutomatonMode.MODE_CRUISE
    states = {'agent_state': AgentState(), 'waypoints_state': WaypointsState()}

    evaluate_guards_timer_callback(
        lock=guard_evaluation_lock,
        mode=current_mode,
        available_modes={0: "MODE_CRUISE", 1:"MODE_T2LOS", 2:"MODE_FALLBACK", 3:"MODE_WAYPOINT_REACHED", 255: "MODE_INACTIVE"},
        status=HybridAutomatonStatus.STATUS_ACTIVE_MODE,
        states=states,
        stamp=test_node.get_clock().now().to_msg(),
        mode_transitions={},
        status_publisher=status_publisher,
        guards_evaluation_publisher=guard_publisher,
        logger=test_node.get_clock().now().to_msg()
    )
    print ('hello world')


    rclpy.shutdown()