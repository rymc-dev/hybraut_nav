# utils/__init__.py

# NOTE: DO NOT MODIFY framework utils or imports below

from .framework.validate_timestamps import is_timestamps_within_tolerance
from .framework.ros_timer_utils import get_current_ros_time, subtract_time
from .framework.node_utils import create_cli
from .framework.yaml_utils import load_yml
from .framework.parse_transition import parse_transition
from .framework.select_highest_priority_transition import select_highest_priority_transition
from .framework.validate_mode import validate_mode

# --- Custom Utilities (you may add to this section) ---

from .colav.unsafe_set_utils import extract_polygon_vertices
from .colav.euclidean_distance import euclidean_distance
from .colav.unsafe_set_utils import is_imminent_collision, is_inside_unsafe_set
from .colav.rotation_utils import (
    quaternion_to_heading,
    normalize_angle,
    delta_heading
)


# ------------------------------------------------------

__all__ = [
    # Framework utils (do not modify)
    "is_timestamps_within_tolerance",
    "get_current_ros_time",
    "create_cli",
    "duct_and_validate_automaton_config_yml",
    "process_automaton_config",
    "load_yml",
    "create_state_subscriptions",
    "create_state_publishers",
    "parse_transition",
    "select_highest_priority_transition",
    "validate_mode",

    # custom utils
    "extract_polygon_vertices",
    "euclidean_distance",
    "quaternion_to_heading",
    "normalize_angle",
    "delta_heading",
    "is_imminent_collision",
    "is_inside_unsafe_set"
]
