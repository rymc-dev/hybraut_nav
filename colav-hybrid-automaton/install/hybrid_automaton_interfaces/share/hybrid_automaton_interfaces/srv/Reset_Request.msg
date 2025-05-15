# Reset.srv
# ROS 2 service definition for issuing reset requests to the Hybrid Automaton framework.
#
# This service allows external systems to request a reset of the automaton's state,
# based on a specified reset name. The reset is applied to the state associated with
# the given transition UUID and transition name.

# NOTE: Do not modify this file.


# --- Request ---
# UUID of the transition to apply the reset to
unique_identifier_msgs/UUID transition_uuid

# Name of the reset function to invoke
string reset_name

