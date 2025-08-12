# !/usr/bin/python3
"""

"""


from dataclasses import dataclass, field
from typing import List



from utils import now_to_ros_time_msg

from hybraut_model._guards import GuardRegistry
from hybraut_model._invariants import InvariantRegistry
from hybraut_model._modes import ModeRegistry, Mode
from hybraut_model._resets import ResetRegistry
from hybraut_model._dynamics import DynamicsRegistry
from hybraut_model._states import StateRegistry
from hybraut_model._transitions import TransitionRegistry

from hybraut_model._evaluation_context import EvaluationContext

from hybraut_interfaces.msg import TransitionEvaluationsMSG
from hybraut_interfaces.msg import InvariantEvaluationsMSG
from hybraut_interfaces.msg import AutomatonDynamicsEvaluation


@dataclass
class HybridAutomaton:
    _name: str = field(init=True)
    _description: str = field(init=True)
    _version: str = field(init=True)

    _initial_mode: int = field(init=True)
    _goal_modes: List[int] = field(init=True)

    _states: StateRegistry = field(init=True)
    _guards: GuardRegistry = field(init=True)
    _resets: ResetRegistry = field(init=True)
    _dynamics: DynamicsRegistry = field(init=True)
    _invariants: InvariantRegistry = field(init=True)
    _transitions: TransitionRegistry = field(init=True)
    _modes: ModeRegistry = field(init=True)

    def _generate_evaluation_context(self, current_mode_id: int) -> EvaluationContext:
        """
        utility function for hybrid_automata for generating 
        """
        return EvaluationContext(
            current_mode=current_mode_id,
            states=self._states,
            stamp=now_to_ros_time_msg(),
            guard_registry=self._guards,
            reset_registry=self._resets,
            invariant_registry=self._invariants,
            metadata={}
        )

    def evaluate_transitions(self, current_mode_id: int) -> TransitionEvaluationsMSG:
        """performs transition evaluations for the current mode"""
        current_mode:Mode = self._modes.get_mode(current_mode_id)
        possible_transitions = current_mode.get_transition_refs()
        ctx = self._generate_evaluation_context(current_mode_id)
        transition_evaluations: TransitionEvaluationsMSG = self._transitions.evaluate_transitions(transitions=possible_transitions, ctx=ctx)

        return transition_evaluations

    def perform_resets(self, current_mode_id: int, reset_names: List[str]):
        """execute resets to states"""
        # TODO: Need to finish this.
        current_mode: Mode = self._modes.get_mode(current_mode_id)
        # validate the reset names are valid for the current mode
        ctx = self._generate_evaluation_context(current_mode_id)
        resets = self._resets.get_components_by_names(reset_names)
        return

    def evaluate_invariants(self, current_mode_id: int) -> InvariantEvaluationsMSG:
        """performs invariant evaluations for the current mode"""
        current_mode: Mode = self._modes.get_mode(current_mode_id)
        invariant_names = current_mode.get_invariant_refs()
        ctx = self._generate_evaluation_context(current_mode_id)
        invariant_evaluations: InvariantEvaluationsMSG = self._invariants.evaluate_invariants_by_name(invariant_names, ctx)

        return invariant_evaluations

    def evaluate_dynamics(self, current_mode_id: int) -> AutomatonDynamicsEvaluation:
        current_mode:Mode = self._modes.get_mode(current_mode_id)
        dynamics_names = current_mode.get_dynamics_ref()
        ctx = self._generate_evaluation_context(current_mode_id)
        dynamics_evaluation: AutomatonDynamicsEvaluation = self._dynamics.evaluate_dynamics_by_name(dynamics_names, ctx)
        
        return dynamics_evaluation

    @classmethod
    def register_automaton(cls, node:Node, amdl_dict: dict) -> 'HybridAutomaton':
        name = amdl_dict['automaton_name']
        description = amdl_dict['automaton_description']
        version = amdl_dict['version']

        initial_mode = amdl_dict['initial_mode']
        goal_modes = amdl_dict['goal_modes']

        states = StateRegistry.load_state_registry_from_amdl(node=node, states_dict=amdl_dict['states'])
        guards = GuardRegistry.load_guard_registry_from_amdl(amdl_dict['guards'])
        resets = ResetRegistry.load_reset_registry_from_amdl(amdl_dict.get('resets'))
        dynamics = DynamicsRegistry.load_dynamics_registry_from_amdl(amdl_dict['dynamics'])
        invariants = InvariantRegistry.load_invariant_registry_from_amdl(amdl_dict['invariants'])
        transitions = TransitionRegistry.load_transition_registry_from_amdl(amdl_dict['transitions'])
        modes = ModeRegistry.load_modes_registry_from_amdl(amdl_dict['modes'])

        return cls(
            _name=name,
            _description=description,
            _version=version,
            _initial_mode=initial_mode,
            _goal_modes=goal_modes,
            _states=states,
            _guards=guards,
            _modes=modes,
            _resets=resets,
            _dynamics=dynamics,
            _invariants=invariants,
            _transitions=transitions
        )


"""
the code below is purely for testing and not to be used in production
"""

if __name__ == '__main__':

    import rclpy
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.node import Node
    import threading
    import yaml

    rclpy.init()
    executors = MultiThreadedExecutor(num_threads=2)

    node = Node('mock_node')
    executors.add_node(node)

    thread = threading.Thread(target=executors.spin)

    path = '/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml'
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    automaton:HybridAutomaton = HybridAutomaton.register_automaton(node=node, amdl_dict=data)
    automaton.evaluate_transitions(current_mode_id=0)
    automaton.evaluate_invariants(current_mode_id=0)
    automaton.evaluate_dynamics(current_mode_id=0)
    automaton.perform_resets(current_mode_id=0, reset_names=[])
    # print (automaton)

    rclpy.shutdown()

