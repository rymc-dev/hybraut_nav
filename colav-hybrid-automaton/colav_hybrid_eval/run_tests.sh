#!/bin/bash
source /opt/ros/humble/setup.bash
source /home/ros2_ws/install/setup.bash 
cd /workspace/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_eval
python3 -m pytest