import time
from builtin_interfaces.msg import Time

def now_to_ros_time_msg():
    now_float = time.time()  # float seconds since epoch, e.g. 1689503045.123456

    sec = int(now_float)
    nanosec = int((now_float - sec) * 1e9)

    time_msg = Time()
    time_msg.sec = sec
    time_msg.nanosec = nanosec

    return time_msg