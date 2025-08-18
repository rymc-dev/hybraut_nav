from hybraut_model._states import State, StateRegistry
from typing import Dict, Any, List
import logging
from hybraut_model.automaton_types import MsgType


logger = logging.getLogger(__name__)

from hybraut_model._dynamics import DynamicsWrapper, DynamicsRegistry
from hybraut_model.automaton_types import ComponentPath


class _DynamicsFactory:

    component_cls = DynamicsWrapper

    @classmethod
    def load_dynamics_from_amdl(
        cls, dynamics_name: str, dynamics_dict: Dict[str, Any]
    ) -> DynamicsWrapper:
        component_path = ComponentPath.load_component_from_famd(dynamics_dict)
        component_class = component_path.get_component_class()
        configuration = dynamics_dict.get("configuration")
        output = dynamics_dict.get("output")
        output_topic = output.get("topic")
        msg_type_info = MsgType(**output["type"])
        msg_type = msg_type_info.import_msg_type()

        return cls(
            _name=dynamics_name,
            _component_class=component_class,
            _configuration=configuration,
            _output_topic=output_topic,
            _output_msg_type=msg_type,
        )

    @classmethod
    def register(cls, dynamics_dict: Dict[str, Any]) -> Dict[str, DynamicsWrapper]:
        components = {}
        for name, conf in dynamics_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_dynamics_from_amdl(
                    dynamics_name=name, dynamics_dict=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to import component '{name}': {e}"
                )

        return components

    @classmethod
    def load_dynamics_registry_from_amdl(
        cls, dynamics_dict: Dict[str, Any]
    ) -> DynamicsRegistry:
        """generates the dyanmics registry from amdl"""
        logger.info("Loading DynamicsRegistry from 'amdl' configuration")
        dynamics = cls.register(dynamics_dict)
        registry = cls(_components=dynamics)
        logger.info(f"Created DynamicsRegistry with {len(dynamics)} dynamics")
        return registry


class _InvariantFactory: ...


class _GuardFactory: ...


class _ResetFactory: ...


class _TransitionFactory: ...


class _ModeFactory: ...


class _StateFactory:
    component_cls = State
    logger = logging.getLogger(__name__)

    @classmethod
    def _component_class(cls) -> type:
        """
        Return the component class to instantiate.
        Subclasses can override this method to provide different component types.
        """
        return cls.component_cls

    @classmethod
    def load_state_from_amdl(cls, state_name: str, state_dict: Dict[str, Any]) -> State:
        """
        Create a State instance from FAMD (Formal Automaton Model Description) configuration.

        This factory method enables creation of State objects from configuration
        dictionaries, typically loaded from YAML or JSON files.

        Args:
            name (str): Unique name for the state
            state_dict (Dict[str, Any]): Configuration dictionary containing:
                - topic (str): ROS2 topic name
                - type (dict): Message type specification with 'pkg' and 'msg'
                - params (dict): Optional parameters like 'update_hz', 'timeout_sec'

        Returns:
            State: Configured State instance

        Raises:
            KeyError: If required configuration keys are missing
            ImportError: If message type cannot be imported

        Example:
            >>> config = {
            ...     "topic": "/robot/pose",
            ...     "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            ...     "params": {"update_hz": 10.0, "timeout_sec": 0.5}
            ... }
            >>> state = State.load_state_from_famd("pose_state", config)
        """
        try:
            # Extract and validate message type
            msg_type_info = MsgType(**state_dict["type"])
            msg_type = msg_type_info.import_msg_type()

            # Extract optional parameters
            params = state_dict.get("params", {})
            update_hz = params.get("update_hz")
            timeout_sec = params.get("timeout_sec")
            max_errors = params.get("max_errors", 10)

            logger.info(f"Loading state '{state_name}' from FAMD configuration")

            return State(
                name=state_name,
                topic=state_dict["topic"],
                msg_type=msg_type,
                update_hz=update_hz,
                timeout_sec=timeout_sec,
                max_errors=None,
            )

        except KeyError as e:
            error_msg = (
                f"Missing required key in state configuration for '{state_name}': {e}"
            )
            logger.error(error_msg)
            raise KeyError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load state '{state_name}' from FAMD: {e}"
            logger.error(error_msg)
            raise

    @classmethod
    def register(cls, config_dict: Dict[str, Any]) -> Dict[str, State]:
        """
        Create and return component instances from a configuration dictionary.
        """
        components: Dict[str, State] = {}

        for name, conf in config_dict.items():
            try:
                components[name] = cls.load_state_from_amdl(
                    state_name=name, state_dict=conf
                )
            except Exception:
                cls.logger.exception(f"Failed to load component '{name}'")
                raise
        return components

    @classmethod
    def load_state_registry_from_amdl(
        cls, states_dict: Dict[str, Any]
    ) -> StateRegistry:
        """
        Load multiple states and return a StateRegistry instance.
        """
        cls.logger.info("Loading StateRegistry from 'amdl' configuration")
        states = cls.register(config_dict=states_dict)
        registry = cls(_components=states)
        cls.logger.info(f"Created StateRegistry with {len(states)} states")
        return registry


class HybridAutomatonFactory: ...
