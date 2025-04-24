from builtin_interfaces.msg import Time, Duration

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


