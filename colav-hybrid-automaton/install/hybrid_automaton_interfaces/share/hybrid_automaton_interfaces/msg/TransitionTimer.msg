# TransitionTimer.msg
# ROS 2 interface for the Hybrid Automaton framework.
# Publishes timing information related to dynamic updates.
# Used to monitor synchronization and detect delays or missed updates 
# in the hybrid automaton's control modes.

# PURPOSE: This message tracks the elapsed time since the last transition evaluation.
# It supports runtime evalution of system responsiveness and  timeout detection.

# NOTE: Do not modify this file.


# UUID of previous transition_evaluation
unique_identifier_msgs/UUID previous_transition_uuid

# Duration since the last transition evaluation
builtin_interfaces/Duration elapsed

# Configured timeout duration for transition evaluation
builtin_interfaces/Duration timeout

# Timeout value in seconds (for comvenience of compatibility)
float64 timeout_sec

# True if elapsed time has exceeded the timeout threshold
bool expired