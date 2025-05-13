# DynamicsTimer.msg
# ROS 2 interface for the Hybrid Automaton framework.
# Publishes timing information related to dynamic updates.
# Used to monitor synchronization and detect delays or missed updates 
# in the hybrid automaton's control modes.

# PURPOSE: This message tracks the elapsed time since the last dynamics update.
# It supports runtime evaluation of system responsiveness and timeout detection.

# NOTE: Do not modify this file.


# UUID of the most recent dynamic update
unique_identifier_msgs/UUID previous_dynamic_uuid

# Duration since the last dynamics update was received
builtin_interfaces/Duration elapsed

# Configured timeout duration for dynamics updates
builtin_interfaces/Duration timeout

# Timeout value in seconds (for convenience or compatibility)
float64 timeout_sec

# True if the elapsed time has exceeded the timeout threshold
bool expired
