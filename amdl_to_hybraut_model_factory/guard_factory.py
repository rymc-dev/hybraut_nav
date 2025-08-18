# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory for Loading dynamics from AMDL (Automaton Model Definition Language) DSL files.
This factory is used to create instances of DynamicsWrapper and DynamicsRegistry from
the provided AMDL configuration.
"""

from hybraut_model.guards import GuardWrapper, GuardRegistry
from typing import Dict, Any
import logging


class GuardFactory:
    """ """

    @classmethod
    def load_guard_from_amdl(
        cls, guard_name: str, guard_dict: Dict[str, Any]
    ) -> "GuardWrapper":
        component_path = ComponentPath.load_component_from_famd(guard_dict)
        component_class = component_path.get_component_class()
        configuration = guard_dict.get("configuration", None)
        return cls(
            _name=guard_name,
            _component_class=component_class,
            _configuration=configuration,
        )

    @classmethod
    def register(cls, guard_dict: Dict[str, Any]) -> Dict[str, GuardWrapper]:
        components = {}
        for name, conf in guard_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_guard_from_amdl(
                    guard_name=name, guard_dict=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to import component '{name}': {e}"
                )

        return components

    @classmethod
    def load_guard_registry_from_amdl(
        cls, guard_dict: Dict[str, Any]
    ) -> "GuardRegistry":
        """generates the guard_registry from amdl"""
        logger.info("Loading GuardRegistry from 'amdl' configuration")
        guards = cls.register(guard_dict)
        registry = cls(_components=guards)
        logger.info(f"Created GuardRegistry with {len(guards)} guards")
        return registry
