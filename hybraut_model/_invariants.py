import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_default

from hybraut_interfaces.msg import InvariantEvaluationMSG, InvariantEvaluationsMSG

from hybraut_aci_interfaces import InvariantInterface
from hybraut_model.automaton_types.component_path import ComponentPath
from hybraut_model.component_interfaces import WrapperInterface
from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_model._evaluation_context import EvaluationContext

# Set up module-level logger
logger = logging.getLogger(__name__)


@dataclass
class InvariantBus:
    """ 
    InvariantBus
    invariant bus is utilized for uplishing invariant events
    """

    _topic: str = field(default="/automaton/invariant_event", init=False)
    _msg_type: Type = field(
        init=False,
        default_factory=InvariantEvaluationsMSG
    )
    _qos: Optional[QoSProfile] = field(
        init=False,
        default_factory=lambda: qos_profile_default
    )
    _cb_group: Optional[CallbackGroup] = field(
        init = True,
        default_factory=ReentrantCallbackGroup()
    )
    _node: Node = field(init=True, default=None)

    _invariant_publisher: Publisher     = field(default=None, init=False)
    _is_initialized: bool               = field(default=False, init=False)

    def __post_init__(self):
        self._create_invariant_publisher(self._node)
        self._is_initialized = True

    def _create_invariant_publisher(self, node: Node):
        """this creates the state publisher for the reset bus"""
        self._invariant_publisher = node.create_publisher(
            msg_type=self._msg_type,
            topic=self._topic,
            qos_profile=self._qos,
            callback_group=self._cb_group
        )

@dataclass
class InvariantWrapper(WrapperInterface):
    """
    Wrapper for invariant components that evaluate conditions that must hold within a state.
    """
    _component_class: Type[InvariantInterface]

    def __post_init_hook__(self):
        self.initialize()

    def _evaluate(self, context: EvaluationContext) -> InvariantEvaluationMSG:
        """"""
        if not self._is_initialized:
            raise RuntimeError("Component instance is None, call activate() first")
        
        msg: InvariantEvaluationMSG = InvariantEvaluationMSG()
        states = context.get_state_values(self._component_instance.get_state_input_spec_names())
        component_info = self._component_instance.get_component_info()
        msg.invariant_name = component_info['class_name']
        msg.invariant_description = component_info['description']
        try:
            msg.holds = self._component_instance(**states)
        except Exception as e:
            msg.error = True
            msg.message = f"exception occured during invariant evaluation: '{str(e)}'"

        return msg
    
    @classmethod
    def load_invariant_from_amdl(cls, invariant_name: str, invariant_dict: Dict[str, Any]) -> 'InvariantWrapper':
        component_path = ComponentPath.load_component_from_famd(invariant_dict)
        component_class = component_path.get_component_class()
        configuration = invariant_dict.get('configuration', {})

        return cls(
            _name = invariant_name,
            _component_class = component_class,
            _configuration = configuration
        )

class InvariantRegistry(ComponentRegistry['InvariantWrapper']):
    """Registry specialized for managing Invariant components"""

    def __post_init__(self):
        self._component_type_name = "Invariant"
        super().__post_init__()

    def get_invariant_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())
    
    def get_invariant_by_name(self, invariant_name: str):
        if invariant_name in self._components.keys():
            return self._components[invariant_name]
        
    def evaluate_invariant_by_name(self, invariant_name: str, ctx: EvaluationContext) -> InvariantEvaluationMSG:
        """evaluate guard by name"""
        invariant = self.get_invariant_by_name(invariant_name)
        try:
            return invariant._evaluate(ctx)
        except Exception as e:
            logger.info(f"{str(e)}")

    def evaluate_invariants_by_name(self, invariant_names: List[str], ctx: EvaluationContext) -> List[InvariantEvaluationsMSG]:
        invariant_evaluations_msg: InvariantEvaluationsMSG = InvariantEvaluationsMSG(
            current_mode = ctx.current_mode,
            stamp = ctx.stamp
        )

        invariant_evaluation_msgs: List[InvariantEvaluationMSG] = []
        for invariant_name in invariant_names:
            invariant_evaluation_msgs.append(self.evaluate_invariant_by_name(invariant_name, ctx))
        
        error = False
        error_messages = []
        for invariant_evaluation in invariant_evaluation_msgs:
            if invariant_evaluation.error == True:
                error = True
                error_messages.append(invariant_evaluation.message)

        overall_holds = True
        for invariant_evaluation in invariant_evaluation_msgs:
            if not invariant_evaluation.holds:
                overall_holds = False

        invariant_evaluations_msg.overall_holds = overall_holds
        invariant_evaluations_msg.error = error
        invariant_evaluations_msg.message = " ".join(error_messages)

        return invariant_evaluations_msg

    @classmethod
    def _component_class(cls) -> Type[InvariantWrapper]:
        return InvariantWrapper

    @classmethod
    def register(cls, invariants_dict: Dict[str, Any]) -> Dict[str, InvariantWrapper]:
        components = {}
        for name, conf in invariants_dict.items():
            try: 
                component_cls = cls._component_class()
                component = component_cls.load_invariant_from_amdl(name, conf)
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to import component '{name}': {e}")

        return components

    @classmethod
    def load_invariant_registry_from_amdl(cls, invariants_dict: Dict[str, Any]) -> 'InvariantRegistry':
        """generates the guard_registry from amdl"""
        logger.info("Loading GuardRegistry from 'amdl' configuration")
        invariants = cls.register(invariants_dict)
        registry = cls(_components=invariants)
        logger.info(f"Created GuardRegistry with {len(invariants)} guards")
        return registry

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading

if __name__ == '__main__':
    rclpy.init()
    
    node = Node('mock_node')

    executor = MultiThreadedExecutor(num_threads=2)
    thread = threading.Thread(target=executor.spin)
    thread.start()

    executor.add_node(node)

    invariant_name = "timeout_invariant"
    invariants_dict = {
        "timeout_invariant": {
            "module": "automaton_models.common_behaviours.invariants.timeout_invariant",
            "class_name": "TimeoutInvariant",
            "configuration": {
                "timeout_sec": 10.0,
                "entry_time": 1.0
            }
        }
    }

    states = {
        "current_time": {
            "topic": "/state/current_time",
            "description": "the current time for the system",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Float64"
            }
        }
    }
    from hybraut_model._states import StateRegistry
    state_registry = StateRegistry.load_state_registry_from_amdl(node=node, states_dict=states)
    state_registry.activate_components(node)

    from builtin_interfaces.msg import Time

    evaluation_context = EvaluationContext(
        states=state_registry,
        current_mode=1,
        stamp=Time(),
        metadata={}
    )

    invariant_registry: InvariantRegistry = InvariantRegistry.load_invariant_registry_from_amdl(
        node=node,
        invariants_dict=invariants_dict
    )
    invariant_evaluations: List[InvariantEvaluationMSG] = invariant_registry.evaluate_invariants_by_name(
        invariant_names=invariants_dict.keys(),
        evaluation_context=evaluation_context
    )

    print (invariant_evaluations)

    rclpy.shutdown()