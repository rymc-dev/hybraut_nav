# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides the ResetFactory class for creating reset components from AMDL-style configuration.
It includes functionality for loading reset components dynamically and validating their configurations.
It is designed to be used within the Hybraut ROS2 framework.
"""

from hybraut_model.resets import ResetRegistry, ResetWrapper
from typing import Dict, Any


class ResetFactory:
    """
    Factory class for creating reset components from amdl-style configuration.
    This class is responsible for loading reset components dynamically
    """

    @classmethod
    def load_reset_wrapper_from_amdl(
        cls, reset_name: str, reset_dict: Dict[str, Any]
    ) -> ResetWrapper:
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
        component_path: ComponentPath = ComponentPath.load_component_from_famd(
            reset_dict
        )
        component_cls = component_path.get_component_class()

        # Retrieve expected constructor argument names/types
        expected_configuration_names = component_cls.get_init_input_spec_names()
        expected_configuration_types = component_cls.get_init_input_spec_types()

        # Extract and validate configuration
        configuration = reset_dict.get("configuration", {})
        init_kwargs = {}

        if configuration is not None:
            for idx, config_name in enumerate(expected_configuration_names):
                if config_name not in configuration:
                    raise KeyError(
                        f"Missing required configuration parameter: '{config_name}'"
                    )

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
            _name=reset_name, _component_class=component_cls, _configuration=init_kwargs
        )

        return reset_wrapper

    @classmethod
    def register(cls, reset_dict: Dict[str, Any]) -> Dict[str, ResetWrapper]:
        components = {}
        if reset_dict is not None:
            for name, conf in reset_dict.items():
                try:
                    component_cls = cls._component_class()
                    component = component_cls.load_reset_wrapper_from_amdl(
                        reset_name=name, reset_dict=conf
                    )
                    components[name] = component
                except Exception as e:
                    logging.getLogger(__name__).error(
                        f"Failed to import component '{name}': {e}"
                    )

        return components

    @classmethod
    def load_reset_registry_from_amdl(
        cls, reset_dict: Dict[str, Any]
    ) -> "ResetRegistry":
        """reset dictionary"""
        logger.info("Loading ResetRegistry from 'amdl' configuration")
        resets = cls.register(reset_dict)
        registry = cls(_components=resets)
        logger.info(f"Created ResetRegistry with {len(resets)} resets")
        return registry
