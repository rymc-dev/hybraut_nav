"""
A simple utility file containing a function
for generating a ROS2 builtin_interfaces.msg.Time
msg utilizing the system time
"""

import time
from builtin_interfaces.msg import Time


def now_to_ros_time_msg():
    """generate a builtin_interface.msg.Time msg instance
    utilizing the current system time.time"""
    now_float = time.time()  # float seconds since epoch, e.g. 1689503045.123456

    sec = int(now_float)
    nanosec = int((now_float - sec) * 1e9)

    time_msg = Time()
    time_msg.sec = sec
    time_msg.nanosec = nanosec

    return time_msg
