# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory for Loading dynamics from AMDL (Automaton Model Definition Language) DSL files.
This factory is used to create instances of DynamicsWrapper and DynamicsRegistry from
the provided AMDL configuration.
"""

from typing import Dict, Any
import logging

from hybraut_nav_tactical.hybraut_model.core.guards import GuardWrapper, GuardRegistry
from hybraut_nav_tactical.hybraut_model.ldr import ComponentPath


logger = logging.getLogger(__name__)


class GuardFactory:
    """
    generates guard wrapper and registry
    """

    component_cls = GuardWrapper

    @classmethod
    def load_guard_from_amdl(
        cls, guard_name: str, guard_dict: Dict[str, Any]
    ) -> GuardWrapper:
        """loads an individual GuardWrapper from AMDL"""
        component_path = ComponentPath.load_component_from_famd(guard_dict)
        component_class = component_path.get_component_class()
        configuration = guard_dict.get("configuration", None)

        return GuardWrapper(
            name=guard_name,
            component_class=component_class,
            configuration=configuration,
        )

    @classmethod
    def register_guards_from_amdl(
        cls, guard_dict: Dict[str, Any]
    ) -> Dict[str, GuardWrapper]:
        """loads a list of guards from AMDL"""
        components = {}
        for name, conf in guard_dict.items():
            try:
                component = cls.load_guard_from_amdl(guard_name=name, guard_dict=conf)
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to import component '{name}': {e}"
                )

        return components

    @classmethod
    def load_guards_registry_from_amdl(
        cls, guard_dict: Dict[str, Any]
    ) -> "GuardRegistry":
        """generates the guard_registry from amdl"""
        logger.info("Loading GuardRegistry from 'amdl' configuration")
        guards = cls.register_guards_from_amdl(guard_dict)
        registry = GuardRegistry(_components=guards)
        logger.info(f"Created GuardRegistry with {len(guards)} guards")
        return registry
