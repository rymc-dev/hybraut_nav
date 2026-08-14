# AgentState.msg
# ROS interface for agent state information

std_msgs/Header header           # Standard ROS header with timestamp and frame_id

string agent_tag                # Unique identifier for this agent
geometry_msgs/Pose pose         # Current position and orientation
float64 velocity                # Current speed (m/s)
float64 acceleration            # Current acceleration (m/s²)
float64 yaw_rate               # Angular velocity around z-axis (rad/s)
float64 beam                   # Vessel width (m)
float64 loa                    # Length overall (m)
float64 safety_radius          # Safety perimeter radius (m)