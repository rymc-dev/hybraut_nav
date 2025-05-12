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
string[] transition_names # key
bool[] transition_values # value
int32[] transition_priority # priorite for transitions 

# Timestamp when this transition update was published.
builtin_interfaces/Time stamp

# Metadata indicating success of the update.
# If unsuccessful, the error message will describe the issue.
bool success
string error_message
