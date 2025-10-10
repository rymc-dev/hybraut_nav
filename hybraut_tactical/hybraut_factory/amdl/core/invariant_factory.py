# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invariant factory for Hybraut model.
This module provides the InvariantFactory class, which is responsible for creating
and managing invariants in the Hybraut model.
It includes methods for adding, removing, and retrieving invariants.
This class is part of the amdl_to_hybraut_model_factory package.
It is designed to be used in the context of Hybraut model development and manipulation.
It is expected to be used in conjunction with other components of the Hybraut model framework.
This module is essential for ensuring the integrity and consistency of invariants
within the Hybraut model.
"""

from hybraut_models.core.invariants import InvariantWrapper, InvariantRegistry
from typing import Dict, Any, Type
from hybraut_models.ldr import ComponentPath
import logging

logger = logging.getLogger(__name__)


class InvariantFactory:
    """
    invariant factory for Hybraut model.
    This class provides methods to create and manage invariants
    in the Hybraut model.
    """

    _component_class = InvariantWrapper

    @classmethod
    def load_invariant_from_amdl(
        cls, invariant_name: str, invariant_dict: Dict[str, Any]
    ) -> "InvariantWrapper":
        component_path = ComponentPath.load_component_from_famd(invariant_dict)
        component_class = component_path.get_component_class()
        configuration = invariant_dict.get("configuration", {})

        return InvariantWrapper(
            name=invariant_name,
            component_class=component_class,
            configuration=configuration,
        )

    @classmethod
    def register_invariants_from_amdl(
        cls, invariants_dict: Dict[str, Any]
    ) -> Dict[str, InvariantWrapper]:
        components = {}
        for name, conf in invariants_dict.items():
            try:
                component = cls.load_invariant_from_amdl(name, conf)
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to import component '{name}': {e}"
                )

        return components

    @classmethod
    def load_invariant_registry_from_amdl(
        cls, invariants_dict: Dict[str, Any]
    ) -> "InvariantRegistry":
        """generates the guard_registry from amdl"""
        logger.info("Loading GuardRegistry from 'amdl' configuration")
        invariants = cls.register_invariants_from_amdl(invariants_dict)
        registry = InvariantRegistry(_components=invariants)
        return registry
