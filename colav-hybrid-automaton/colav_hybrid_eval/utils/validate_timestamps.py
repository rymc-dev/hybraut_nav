from builtin_interfaces.msg import Time, Duration
import time


def validate_timestamps_within_tolerance(
        t1: Time, t2: Time, tolerance: Duration):
    """
    Check whether two timestamps are within the specified tolerance

    raises: Exception
    """

    diff = abs((t1._sec + t1._nanosec * 1e-9) - (t2._sec + t2._nanosec * 1e-9))
    max_diff = tolerance.sec + tolerance.nanosec * 1e-9
    if diff >= max_diff:
        raise TimeoutError('Timeout Exception occured')


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
