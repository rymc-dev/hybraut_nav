
# --- Response ---
unique_identifier_msgs/UUID automaton_uuid  # Echo the automaton_uuid to confirm which automaton was stopped

bool success                             # Indicates whether the Hybrid Automaton was successfully terminated
string message                           # Optional: Detailed message providing additional information (e.g., "Successfully stopped", "Error: automaton not found")
