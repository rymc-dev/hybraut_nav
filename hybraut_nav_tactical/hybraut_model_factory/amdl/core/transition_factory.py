#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transition Factory Module for Hybraut Model
"""

import logging
from typing import Dict, Any

from hybraut_nav_tactical.hybraut_model.core.transitions import TransitionRegistry, Transition
from hybraut_nav_tactical.hybraut_model.const.urgency import UrgencyEnums

logger = logging.getLogger(__name__)


class TransitionFactory:
    """
    Factory class for creating and registering transition models in the Hybraut framework.
    """

    component_cls = Transition  # explicit reference to the component class

    @classmethod
    def load_transition_from_amdl(
        cls, transition_name: str, transition_amdl: Dict[str, Any]
    ) -> Transition:
        """
        Create a Transition instance from a configuration dictionary.
        """
        try:
            target_mode = transition_amdl["target_mode"]
            guard_ref = transition_amdl["guard"]
            reset_ref = transition_amdl.get("reset")
            urgency = UrgencyEnums(transition_amdl.get("urgency", 1))

            return cls.component_cls(
                name=transition_name,
                target_mode=target_mode,
                guard_refs=guard_ref,
                reset_refs=reset_ref,
                priority=-1,  # priority is a value set when transition is loaded into mode
                urgency=urgency,
            )
        except KeyError as e:
            raise ValueError(f"Missing required transition field: {e}") from e
        except Exception as e:
            logger.error(f"Failed to create transition '{transition_name}': {e}")
            raise

    @classmethod
    def register_transitions_from_amdl(
        cls, transitions_amdl: Dict[str, Any]
    ) -> Dict[str, Transition]:
        """
        Create multiple Transition instances from a configuration dictionary.
        """
        components: Dict[str, Transition] = {}

        for transition_name, transition_amdl in transitions_amdl.items():
            try:
                components[transition_name] = cls.load_transition_from_amdl(
                    transition_name, transition_amdl
                )
            except Exception as e:
                logger.error(f"Failed to load transition '{transition_name}': {e}")
                raise

        return components

    @classmethod
    def load_transition_registry_from_amdl(
        cls, transitions_amdl: Dict[str, Any]
    ) -> TransitionRegistry:
        """
        Create a TransitionRegistry from a configuration dictionary.
        """
        logger.info("Loading TransitionRegistry")
        transitions = cls.register_transitions_from_amdl(transitions_amdl)
        registry = TransitionRegistry(_components=transitions)
        logger.info(f"Created TransitionRegistry with {len(transitions)} transitions")

        return registry
