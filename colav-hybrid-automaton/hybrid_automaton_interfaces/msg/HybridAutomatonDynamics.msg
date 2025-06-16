# Dynamics.msg
# ROS 2 interface for the Hybrid Automaton framework.
# Enables real-time updates of control mode dynamics based on the current operational state.
# Each update corresponds to one of the control modes defined in the 
# `/hybrid_automaton/config/hybrid_automaton_config.yml` (e.g., GO_FORWARD, GO_RIGHT, etc.).

# NOTE: Do not modify anything outside the boundaries marked 
# 'Custom Dynamics Parameters Start' and 'Custom Dynamics Parameters End'.
# Only edit within that section to define or update your custom dynamics.

# The name of the current control mode. Must match one of the configured mode names.
string mode

hybrid_automaton_interfaces/HybridAutomatonDynamicParameter dynamic_parameters

# Timestamp of when the dynamic update was published.
builtin_interfaces/Time stamp

# Metadata for update status.
# Indicates whether the update was successfully applied, and provides error details if not.
bool success
string message