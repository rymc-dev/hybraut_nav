# Output.msg
# ROS 2 message for the hybrid automaton framework output
#
# This message provides the output of the hybrid automaton, allowing external agents 
# to receive system state information, including dynamics, status, and relevant metadata 
# such as the automaton UUID and timestamp.
#
# NOTE: Do not modify anything outside the boundaries marked
# 'Additional Output Data Start' to 'Additional Output Data End'

unique_identifier_msgs/UUID automaton_uuid  # Unique identifier for the automaton instance

string mode       # Current system mode of the automaton
string status                                # Status string (e.g., "ACTIVE", "COMPLETE", etc.)

hybrid_automaton_interfaces/DynamicParameter dynamics             # Current system dynamics
builtin_interfaces/Duration time_since_last_transition # Time since the last mode transition
hybrid_automaton_interfaces/TransitionPending transition_pending  # Indicates if a transition is pending

builtin_interfaces/Time stamp            # Timestamp of this output message
builtin_interfaces/Duration elapsed_time     # Elapsed time since automaton started

# --- Additional Output Data Start ---

colav_interfaces/Waypoint[] waypoints  # Internal state waypoints for COLAV Hybrid Automaton

# --- Additional Output Data End ---

bool error               # True if an error has occurred
string message           # Additional context or information (e.g., success details or error descriptions)
