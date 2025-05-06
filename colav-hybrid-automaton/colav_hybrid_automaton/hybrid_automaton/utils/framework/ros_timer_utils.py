from builtin_interfaces.msg import Time, Duration
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

def subtract_time(t1: Time, t0: Time) -> Duration:
    sec_diff = t1.sec - t0.sec
    nanosec_diff = t1.nanosec - t0.nanosec

    # Normalize nanoseconds to be in [0, 1e9)
    if nanosec_diff < 0:
        sec_diff -= 1
        nanosec_diff += int(1e9)

    return Duration(sec=sec_diff, nanosec=nanosec_diff)
