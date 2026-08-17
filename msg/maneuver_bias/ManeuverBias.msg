# ManeuverBias.msg
# COLREGs-informed avoidance-side bias for the tactical layer's virtual
# waypoint side selection, as produced by
# colav_automaton.classification.classify_unsafe_set_obstacles() /
# Maneuver.as_bias() from the same obstacle list risk_envelope_node folds
# into the /hybraut_nav/riskenv unsafe region.
#
# Consumed by hybraut_nav_tactical/tactical_node.py, which pushes {side,
# urgency} into the automaton's 'maneuver_bias' auxiliary state -
# colav_automaton.resets.generate_new_virtual_waypoint reads that to
# override its default purely-geometric "easiest side" choice.

std_msgs/Header header

string side               # "port" or "starboard" - which side to route around
float64 urgency           # 0-1, how strongly this overrides the geometric default
bool give_way             # whether the agent is obligated to give way (vs. stand on)
string encounter          # COLREGs encounter category (head_on, crossing_give_way, ...)
string reason              # human-readable rule citation, for logging/debugging
