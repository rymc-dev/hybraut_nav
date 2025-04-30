# Dynamics.msg
# ROS 2 interface for the Hybrid Automaton framework.
# Enables real-time updates of control mode dynamics based on the current operational state.
# Each update corresponds to one of the control modes defined in the 
# `/hybrid_automaton/config/hybrid_automaton_config.yml` (e.g., GO_FORWARD, GO_RIGHT, etc.).

# NOTE: Do not modify anything outside the boundaries marked 
# 'Custom Dynamics Parameters Start' and 'Custom Dynamics Parameters End'.
# Only edit within that section to define or update your custom dynamics.


# UUID uniquely identifying this dynamic update instance
unique_identifier_msgs/UUID dynamic_uuid

# The name of the current control mode. Must match one of the configured mode names.
string mode

# --- Custom Dynamics Parameters Start ---
# Add or modify fields below to define the dynamic behavior for your control modes.

float64 velocity      # Linear velocity of the system
float64 yaw_rate      # Angular velocity around the Z-axis (yaw rate)

# --- Custom Dynamic Parameters End ---


# Timestamp of when the dynamic update was published.
builtin_interfaces/Time stamp

# Metadata for update status.
# Indicates whether the update was successfully applied, and provides error details if not.
bool success
string error_message