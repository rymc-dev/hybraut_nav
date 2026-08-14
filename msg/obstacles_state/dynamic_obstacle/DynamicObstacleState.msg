# DynamicObstacle.msg
# Represents a dynamic obstacle in a 2d Environment

string tag                  # Tag for a dynamic obstacle
string type                 # Type classification for a dynamic obstacle 

geometry_msgs/Pose pose     # Pose of the dynamic obstacle  
float64 velocity            # velocity (m/s)
float64 acceleration        # acceleration ((m/s)^2)
float64 yaw_rate            # the yaw per second in radians (rad/s)

# The geometric shape representing the obstacle
hybraut_nav/DynamicObstacleGeometry geometry # dynamic obstacle geometry.
float64 safety_radius   # safety perimeter radius (m)