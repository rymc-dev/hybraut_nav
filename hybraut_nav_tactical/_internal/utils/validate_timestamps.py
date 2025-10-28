from builtin_interfaces.msg import Time, Duration

def is_timestamps_within_tolerance(
        t1: Time, t2: Time, tolerance: Duration) -> bool:
    """
    Check whether two timestamps are within the specified tolerance.

    Returns:
        True if timestamps differ by no more than tolerance, False otherwise.
    """

    diff = abs((t1.sec + t1.nanosec * 1e-9) - (t2.sec + t2.nanosec * 1e-9))
    max_diff = tolerance.sec + tolerance.nanosec * 1e-9
    return diff <= max_diff

