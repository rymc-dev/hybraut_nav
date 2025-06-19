# HybridAutomatonOutput.msg
# ROS 2 message for the hybrid automaton framework output
#
# This message provides comprehensive state information from the hybrid automaton,
# enabling external agents to monitor system behavior, performance, and current
# operational status with full context for decision-making and debugging.
#
# NOTE: Do not modify anything outside the boundaries marked
# 'Additional Output Data Start' to 'Additional Output Data End'

# === Core Identity & State ===
unique_identifier_msgs/UUID automaton_uuid     # Unique identifier for this automaton instance
hybrid_automaton_interfaces/HybridAutomatonMode mode                                    # Current active control mode (e.g., GO_FORWARD, AVOID_OBSTACLE)
string previous_mode                        # Previous control mode (useful for transition analysis)
hybrid_automaton_interfaces/HybridAutomatonStatus status                                  # Execution status (INITIALIZING, ACTIVE, TRANSITIONING, COMPLETE, ERROR, PAUSED)

# === Dynamics & Control ===
hybrid_automaton_interfaces/HybridAutomatonDynamicParameter dynamics  # Current system dynamics and control outputs

# === Transition Information ===
builtin_interfaces/Duration time_since_last_transition     # Time elapsed since last mode transition
builtin_interfaces/Duration time_in_current_mode          # Total time spent in current mode

bool transition_pending                                    # is transition pending
hybrid_automaton_interfaces/HybridAutomatonGuardEvaluations guards

int32 transition_count                                    # Total number of transitions executed

# === Performance & Health ===
float64 cycle_frequency                        # Current execution frequency (Hz)
float64 average_cycle_time                     # Average time per execution cycle (seconds)

# === Timing Information ===
builtin_interfaces/Time stamp                  # Timestamp when this message was generated
builtin_interfaces/Duration elapsed_time       # Total runtime since automaton initialization

# === Goal & Progress ===
bool goal_reached                              # True if the automaton has reached its objective
float64 progress_percentage                    # Completion progress (0.0 to 100.0)

# --- Additional Output Data Start ---
colav_interfaces/Waypoint[] waypoints_state        # Internal state waypoints for COLAV Hybrid Automaton
# --- Additional Output Data End ---

# === Error Handling & Diagnostics ===
bool error                                     # True if any error condition exists
string message                                # Context information, success details, or error descriptions