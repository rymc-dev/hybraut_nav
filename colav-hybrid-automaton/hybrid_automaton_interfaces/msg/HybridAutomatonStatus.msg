# HybridAutomatonStatus.msg
# ROS 2 constants interface for Hybrid Automaton status enumeration
#
# This message defines constant values representing the internal states 
# of a hybrid automaton lifecycle. Use these constants to ensure 
# consistent status reporting across all nodes.

# Used when moving from configured state to active
uint8 INITIALIZING=0

# Currently executing within an active mode (continuous evolution)
uint8 ACTIVE_MODE=1

# A transition is occurring between modes (guard condition triggered, reset in progress)
uint8 TRANSITIONING=2

# Final goal or terminal condition has been reached; automaton is shutting down cleanly
uint8 COMPLETED=3

# Automaton is being externally stopped or deactivated
uint8 DEACTIVATING=4

# An unrecoverable error occurred during execution, transition, or mode evaluation
uint8 ERROR=5

# The actual status value
uint8 status
builtin_interfaces/Time stamp