# Mode.msg 
# ROS 2 interface for the Hybrid Automaton Framework.
# Provides real-time updates of the current Hybrid Automaton mode.

# NOTE: Do not modify this .msg definition.

unique_identifier_msgs/UUID mode_uuid  # Unique identifier for this mode update instance
string mode  # The current Hybrid Automaton mode (e.g., "GO_FORWARD", "GO_RIGHT", etc.)
builtin_interfaces/Time stamp  # Timestamp indicating when the mode was last updated
string origin_transition  # The transition that triggered the mode change (e.g., "cruise_to_waypoint_reached")
