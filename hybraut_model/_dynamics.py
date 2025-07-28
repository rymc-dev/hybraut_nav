from dataclasses import dataclass

from typing import Type, Dict, Any

from hybraut_interfaces.msg import AutomatonDynamicsEvaluation

from hybraut_aci_interfaces import DynamicsInterface
from hybraut_model._evaluation_context import EvaluationContext
from hybraut_model.component_interfaces.wrapper_interface import WrapperInterface
from hybraut_model.automaton_types.component_path import ComponentPath
import logging

logger = logging.getLogger(__name__)


@dataclass
class DynamicsWrapper(WrapperInterface):
    """ 
    wrapper for a instance of dynamics implementation
    """

    _component_class: Type[DynamicsInterface]

    def __post_init_hook__(self):
        self.initialize()

    def _evaluate(self, context) -> AutomatonDynamicsEvaluation:
        if not self._is_initialized:
            raise RuntimeError("Component instance is None. Call activate first.")
        
        msg: AutomatonDynamicsEvaluation = AutomatonDynamicsEvaluation()
        states = context.get_state_values(self._component_instance.get_state_input_spec_names())
        component_info = self._component_instance.get_component_info()
        msg.dynamic_name = component_info['class_name']
        msg.dynamic_description = component_info['description']
        msg.dynamic_parameter_names = component_info['output_spec_param_names']
        msg.dynamics_parameter_units = component_info['output_spec_param_units']

        try:
            msg.dynamic_parameter_values = self._component_instance(**states)
        except Exception as e:
            msg.error = True
            msg.message = f"exception occured during dynamics evaluation: {e}"

        return msg
    
    @classmethod
    def load_dynamics_from_amdl(cls, dynamics_name: str, dynamics_dict: Dict[str, Any]):
        component_path = ComponentPath.load_component_from_famd(dynamics_dict)
        component_class = component_path.get_component_class()
        configuration = dynamics_dict.get('configuration')

        return cls(
            _name=dynamics_name,
            _component_class=component_class,
            _configuration=configuration
        )
    

from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_aci_interfaces._dynamics_interface import DynamicsInterface

class DynamicsRegistry(ComponentRegistry['DynamicsInterface']):
    """Registry specialized for managing dynamics"""

    def __post_init__(self):
        self._component_type_name = "Dynamics"
        super().__post_init__()

    def get_dynamics_names(self):
        if self._components is None:
            return []
        
        return list(self._components.keys())
    
    def get_dynamics_by_name(self, dynamics_name: str): 
        if dynamics_name in self._components.keys():
            return self._components[dynamics_name]
        
    def evaluate_dynamics_by_name(self, dynamics_name: str, ctx: EvaluationContext) -> AutomatonDynamicsEvaluation:
        dynamics = self.get_dynamics_by_name(dynamics_name)
        try:
            return dynamics._evaluate(ctx)
        except Exception as e:
            logger.info(f"{str(e)}")

    @classmethod
    def _component_class(cls) -> Type[DynamicsWrapper]:
        return DynamicsWrapper
    
    @classmethod
    def register(cls, dynamics_dict: Dict[str, Any]) -> Dict[str, DynamicsWrapper]:
        components = {}
        for name, conf in dynamics_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_dynamics_from_amdl(
                    dynamics_name=name,
                    dynamics_dict=conf
                )
                components[name] = component
            except Exception as e: 
                logging.getLogger(__name__).error(f"Failed to import component '{name}': {e}")
            
        return components
    
    @classmethod
    def load_dynamics_registry_from_amdl(cls, dynamics_dict: Dict[str, Any]) -> 'DynamicsWrapper': 
        """generates the dyanmics registry from amdl"""
        logger.info("Loading DynamicsRegistry from 'amdl' configuration")
        dynamics = cls.register(dynamics_dict)
        registry = cls(_components=dynamics)
        logger.info(f"Created DynamicsRegistry with {len(dynamics)} dynamics")
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

    dynamics_name = 'pid_controller'

    dynamics_dict = {
        "pid_controller": {
            "module": "automaton_models.common_behaviours.dynamics.pid_controller",
            "class_name": "PIDControllerDynamics",
            "configuration": {
                "control_frequency": 100,
                "max_velocity": 30.0,
                "derivative_filter_alpha": 0.1,
                "integral_max": 0.2,
                "target_velocity": 25.0, # updated cruise speed
                "yaw_kp": 0.3, # gentle heading proportional gain
                "yaw_ki": 0.01, # small integral for smooth correction
                "yaw_kd": 0.05, # small derivative gain to damp oscillations
                "vel_kp": 0.5, # moderate velocity proportional gain
                "vel_ki": 0.05, # small integral to avoid windup
                "vel_kd": 0.05, # small derivative for smooth velocity changes
                "error_tolerance": 0.01, # precision in heading error
                "max_yaw_rate": 0.1 # limit yaw rate to gentle turns
            }
        }
    }

    states = {
        "agent_state": {
            "topic": "/state/agent",
            "description": "State of the agent including position, velocity and heading.",
            "type": {
                "pkg": "colav_interfaces.msg",
                "msg": "AgentState"
            }
        },
        "waypoints_state": {
            "topic": "/state/waypoints",
            "description": "State of the waypoints including current waypoint and virtual waypoints.",
            "type": {
                "pkg": "colav_interfaces.msg",
                "msg": "WaypointsState"
            }
        }
    }

    from hybraut_model._states import StateRegistry
    state_registry = StateRegistry.load_state_registry_from_amdl(node=node, states_dict=states)
    state_registry.activate_components(node)

    from hybraut_model._evaluation_context import EvaluationContext
    from builtin_interfaces.msg import Time

    evaluation_context = EvaluationContext(
        states=state_registry,
        current_mode=1,
        stamp=Time(),
        metadata={}
    )

    dynamics: DynamicsRegistry = DynamicsRegistry.load_dynamics_registry_from_amdl(
        dynamics_dict=dynamics_dict
    )
    dynamics_output = dynamics.evaluate_dynamics_by_name("pid_controller", evaluation_context)
    print (dynamics)

    rclpy.shutdown()


