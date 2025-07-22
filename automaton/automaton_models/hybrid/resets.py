
from dataclasses import dataclass
from typing import List
from aci_interfaces.reset_interface import ResetInterface
from automaton_interfaces.msg import AutomatonReset, AutomatonResets
from utils import now_to_ros_time_msg
from context import EvaluationContext
from component_interfaces.registry_interface import ComponentRegistry
from component_interfaces.wrapper_interface import WrapperInterface
from typing import Dict, Any, Type
# from states import State
import logging
from automaton_types.component_path import ComponentPath

# Set up module-level logger
logger = logging.getLogger(__name__)


@dataclass
class ResetWrapper(WrapperInterface):

    def _evaluate(self, context: EvaluationContext):
        if not self._is_initialized:
            raise RuntimeError('can not evaluate uninitialized reset')
        
        print ('hello there')
        states = context.get_state_values(self._component_instance.get_state_input_spec_names())
        outputs = self._component_instance(**states)
        target_states = context.get_states(list(outputs.keys()))

        # need to publish the state updates for the correlating topics from the state registry
    
    def __post_init_hook__(self):
        self.initialize()

    @classmethod
    def load_reset_wrapper_from_famd(cls, name: str, reset_dict: Dict[str, Any]) -> 'ResetWrapper':
        """
        Create a ResetWrapper instance from FAMD-style configuration.

        Args:
            name (str): Unique name for the reset component
            reset_dict (Dict[str, Any]): Reset configuration dictionary, must contain a 'component' key and optional 'configuration'

        Returns:
            ResetWrapper: Instantiated reset wrapper with configured reset logic

        Raises:
            Exception: If configuration keys or types are invalid
        """
        # Load the reset component class dynamically
        component_path: ComponentPath = ComponentPath.load_component_from_famd(reset_dict)
        component_cls = component_path.get_component_class()

        # Retrieve expected constructor argument names/types
        expected_configuration_names = component_cls.get_init_input_spec_names()
        expected_configuration_types = component_cls.get_init_input_spec_types()

        # Extract and validate configuration
        configuration = reset_dict.get('configuration', {})
        init_kwargs = {}

        if configuration is not None:
            for idx, config_name in enumerate(expected_configuration_names):
                if config_name not in configuration:
                    raise KeyError(f"Missing required configuration parameter: '{config_name}'")

                config_value = configuration[config_name]
                expected_type = expected_configuration_types[idx]

                if not isinstance(config_value, expected_type):
                    raise TypeError(
                        f"Invalid type for parameter '{config_name}': "
                        f"expected {expected_type.__name__}, got {type(config_value).__name__}"
                    )
                init_kwargs[config_name] = config_value

        # Wrap it in a ResetWrapper (assumed abstraction)
        reset_wrapper = ResetWrapper(
            _name=name, 
            _component_class=component_cls,
            _configuration=init_kwargs
        )

        return reset_wrapper




if __name__ == '__main__':
    dict = {
        "module": "automaton_models.common_behaviours.resets.battery_level_reset",
        "class_name": "BatteryLevelReset",
        "configuration": {
            "low_battery_threshold": 30.0,
            "critical_battery_threshold": 5.0,
            "power_save_factor": 20.0
        }
    }

    reset_wrapper = ResetWrapper.load_reset_wrapper_from_famd("generate_virtual_waypoints_reset", dict)
    from context.evaluation_context import EvaluationContext
    from builtin_interfaces.msg import Time
    from std_msgs.msg import Float64, Int32

    states = {
        "power_save_mode": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Bool"
            }
        },
        "max_performance_factor": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Float64"
            }
        },
        "battery_status": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Int32"
            }
        },
        "return_to_base_required": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Bool"
            }
        },
        "battery_level": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Float64"
            },
            "params": {
                "update_hz": 10.0,
                "timeout_sec": 0.5
            }
        },
        "current_power_mode": {
            "topic": "/state/current_power_mode",
            "description": "current power mode.",
            "type": {
                "pkg": "std_msgs.msg",
                "msg": "Int32"
            },
            "params": {
                "update_hz": 10.0,
                "timeout_sec": 0.5
            }
        }
    }
    from states import StateRegistry
    state_registry = StateRegistry.load_state_registry_from_famd(states_dict=states)
    # state_registry._components['battery_level'].current_state = Float64(_data=80.5)
    # state_registry._components['current_power_mode'].current_state = Int32(_data=2)
    evaluation_context = EvaluationContext(states=state_registry, current_mode=0, stamp=Time, metadata={})
    outputs = reset_wrapper._evaluate(context=evaluation_context)
    print (outputs)

# @dataclass
# class ResetRegistry(ComponentRegistry['ResetWrapper']):
#     """Registry specialized for managing State components."""
    
#     _component_type_name = "Reset"

#     def __post_init__(self):
#         self._component_type_name = "Reset"
#         super().__post_init__()

#     @classmethod
#     def _component_class(cls) -> Type[State]:
#         return State

#     @classmethod
#     def register(cls: Type['ComponentRegistry'], config_dict: Dict[str, Any]) -> Dict[str, ResetWrapper]:
#         """
#         Create and return component instances from configuration dict.
#         Subclasses must implement `_component_class()` returning their component class.
#         """
#         components = {}
#         for name, conf in config_dict.items():
#             try:
#                 component_cls = cls._component_class()
#                 component = component_cls.load_state_from_famd(name, conf)
#                 components[name] = component
#             except Exception as e:
#                 logging.getLogger(__name__).error(f"Failed to load component '{name}': {e}")
#                 raise
#         return components
        
#     @classmethod
#     def load_state_registry_from_famd(cls, states_dict: Dict[str, Any]) -> 'ResetRegistry':
#         logger.info("Loading StateRegistry from FAMD configuration")
#         states = cls.register(states_dict)
#         registry = cls(_components=states)
#         logger.info(f"Created StateRegistry with {len(states)} states")
#         return registry