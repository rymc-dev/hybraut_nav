import threading
from dataclasses import dataclass, field
from typing import List

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from guards import GuardRegistry
from invariants import InvariantRegistry
from modes import ModeRegistry
from resets import ResetRegistry
from states import StateRegistry
from transitions import TransitionRegistry


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
    _invariants: InvariantRegistry = field(init=True)
    _transitions: TransitionRegistry = field(init=True)
    _modes: ModeRegistry = field(init=True)
    
    _evaluation_frequency: int = field(init=False)
    _control_frequency: int = field(init=False)

    _event_bus: any = field(init=False)

    @classmethod
    def register_automaton(cls, node:Node, amdl_dict: dict) -> 'HybridAutomaton':
        name = amdl_dict['automaton_name']
        description = amdl_dict['automaton_description']
        version = amdl_dict['version']

        initial_mode = amdl_dict['initial_mode']
        goal_modes = amdl_dict['goal_modes']

        states = StateRegistry.load_state_registry_from_amdl(node=node, states_dict=amdl_dict['states'])
        guards = GuardRegistry.load_guard_registry_from_amdl(amdl_dict['guards'])
        resets = ResetRegistry.load_reset_registry_from_amdl(amdl_dict['resets'])
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
            _invariants=invariants,
            _transitions=transitions
        )

import yaml

if __name__ == '__main__':
    rclpy.init()
    executors = MultiThreadedExecutor(num_threads=2)

    node = Node('mock_node')
    executors.add_node(node)

    thread = threading.Thread(target=executors.spin)

    path = '/home/ryan/ros2_ws/src/colav-hybrid-automaton/automaton/colav_behaviours/colav-famd.yml'
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    print (data)
    automaton = HybridAutomaton.register_automaton(node=node, amdl_dict=data)

    print (automaton)

    rclpy.shutdown()

