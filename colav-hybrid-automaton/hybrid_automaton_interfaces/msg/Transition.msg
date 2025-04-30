# Transitions.msg
# ROS 2 interface for the Hybrid Automaton framework.
#
# This message enables real-time evaluation of control mode transitions 
# based on the current operational state. Each transition corresponds to one 
# of the control modes defined in the configuration file:
# `/hybrid_automaton/config/hybrid_automaton_config.yml` 
# (e.g., GO_FORWARD, GO_RIGHT, etc.).
#
# NOTE: Do not modify anything outside the boundaries marked 
# 'Custom Transition Parameters Start' and 'Custom Transition Parameters End'.
# Only edit within that section to define or update your custom transition parameters.


# Unique identifier for this transition evaluation instance.
unique_identifier_msgs/UUID transition_uuid

# Current Hybrid Automaton mode (e.g., GO_FORWARD, GO_RIGHT, etc.).
string mode

# Names of transitions evaluated in this update cycle.
string[] evaluated_transitions

# --- Custom Transition Parameters Start ---
# Define or modify guard evaluation results below.
# Each field must be of type `bool`, representing whether the guard condition passed (true) or failed (false).

# Guard statuses for transitions originating from CRUISE mode
bool cruise_to_t2los_1
bool cruise_to_t2los_2
bool cruise_to_waypoint_reached
bool cruise_to_fb  # Fallback transition for CRUISE mode

# Guard statuses for transitions originating from T2LOS mode
bool t2los_to_cruise
bool t2los_to_fb     # Fallback transition for T2LOS mode
bool t2los_to_waypoint_reached

# Guard status for transition from WAYPOINT_REACHED to CRUISE mode
bool waypoint_reached_to_cruise

# --- Custom Transition Parameters End ---

# Timestamp when this transition update was published.
builtin_interfaces/Time stamp

# Metadata indicating success of the update.
# If unsuccessful, the error message will describe the issue.
bool success
string error_message
