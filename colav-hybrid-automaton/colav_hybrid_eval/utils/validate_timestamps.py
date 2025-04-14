from builtin_interfaces.msg import Time, Duration
import time

def timestamps_within_tolerance(t1: Time, t2: Time, tolerance: Duration) -> bool:
    """Check whether two timestamps are within the specified tolerance."""
    print (t1._sec)
    print (t1._nanosec)
    print (t2._sec)
    print (t2._nanosec)
    print (tolerance)

    diff = abs((t1._sec + t1._nanosec * 1e-9) - (t2._sec + t2._nanosec * 1e-9))
    max_diff = tolerance.sec + tolerance.nanosec * 1e-9
    return diff <= max_diff

def get_current_ros_time() -> Time:
    now = time.time()  # seconds since epoch as float
    sec = int(now)
    nanosec = int((now - sec) * 1e9)

    ros_time = Time()
    ros_time.sec = sec
    ros_time.nanosec = nanosec
    return ros_time
