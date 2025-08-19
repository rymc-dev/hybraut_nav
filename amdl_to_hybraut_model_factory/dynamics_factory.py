# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory for Loading dynamics from AMDL (Automaton Model Definition Language) DSL files.
This factory is used to create instances of DynamicsWrapper and DynamicsRegistry from
the provided AMDL configuration.
"""

from hybraut_model.dynamics import DynamicsWrapper, DynamicsRegistry
from typing import Dict, Any
from hybraut_model.automaton_types import ComponentPath, MsgType
import logging

logger = logging.getLogger(__name__)


class DynamicsFactory:

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
    def register_dynamics_from_amdl(
        cls, dynamics_dict: Dict[str, Any]
    ) -> Dict[str, DynamicsWrapper]:
        components = {}
        for name, conf in dynamics_dict.items():
            try:
                component = cls.load_dynamics_from_amdl(
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
        dynamics = cls.register_dynamics_from_amdl(dynamics_dict)
        registry = DynamicsRegistry(_components=dynamics)
        return registry
