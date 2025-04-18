from builtin_interfaces.msg import Time
import time


def get_current_ros_time() -> Time:
    """
    get_current_ros_time
    Gets the current time.now and converts it to a ros2 Time Stamp

    returns: builtin_interfaces.msg.Time
    """
    now = time.time()  # seconds since epoch as float
    sec = int(now)
    nanosec = int((now - sec) * 1e9)

    ros_time = Time()
    ros_time.sec = sec
    ros_time.nanosec = nanosec
    return ros_time
