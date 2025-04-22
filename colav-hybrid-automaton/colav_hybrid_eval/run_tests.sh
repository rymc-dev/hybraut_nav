#!/bin/bash
source /opt/ros/humble/setup.bash
source /workspace/ros2_ws/install/setup.bash  # Fix the path here
source /home/ros2_ws/install/setup.bash
cd /workspace/ros2_ws && rm -rf build install log
export PYTHONPATH=/workspace/ros2_ws/install/colav_hybrid_eval/lib/python3.10/site-packages:$PYTHONPATH
cd /workspace/ros2_ws
colcon build --packages-select colav_hybrid_eval
source /workspace/ros2_ws/install/setup.bash  # Fix the path here
colcon test --packages-select colav_hybrid_eval --event-handlers console_cohesion+
