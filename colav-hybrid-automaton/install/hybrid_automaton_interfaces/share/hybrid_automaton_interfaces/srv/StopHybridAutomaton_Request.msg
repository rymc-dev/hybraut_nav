# StopHybridAutomaton
# ROS 2 service for terminating the Hybrid Automaton Framework.
#
# This service stops or terminates the currently operating Hybrid Automaton instance.
# The automaton specified by the `automaton_uuid` will be stopped, and the system will cease its current operations.
#
# NOTE: Do not modify anything outside the boundaries marked

# --- Request ---
builtin_interfaces/Time stamp             # Timestamp for synchronization of the request
unique_identifier_msgs/UUID automaton_uuid  # Unique identifier for the Hybrid Automaton instance to be stopped
string stop_reason                       # Optional: A reason for stopping the automaton (e.g., "mission_complete", "manual_stop", "error")

