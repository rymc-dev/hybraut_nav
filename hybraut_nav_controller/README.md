# hybraut controller

This package contains Layer 3 of the the HybrautNav navigation stack. This layer will handle global path planning an optimal trajectory only considering the static environment the agent is operating in given by the ROS2 cost map.

controller node has a service for activation and deactivation
when actived it listens to continous dynamics published by the tactical layer hybrid automaton, this hybrid automaton publishes messages like this# Guidance / control confi`guration output from the hybrid automaton

string controller_name          # e.g. "LOS", "FiniteTime", "COLAV"
float64 desired_heading          # desired psi_d [rad]
float64 desired_velocity          # reference surge speed [m/s]
geometry_msgs/Point target_waypoint  # optional, the current/virtual waypoint (x, y)
float64 heading_tolerance         # how close is "close enough" to the target heading
float64 velocity_tolerance        # optional

where the controller_name is used to switch out controller, generate desired heading and velocity target waypoint and heading_tolerance velocity toleratnce an so on.