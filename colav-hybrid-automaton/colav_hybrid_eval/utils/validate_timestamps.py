from builtin_interfaces.msg import Time, Duration

def validate_timestamps(op_timestamp: Time, arg_timestamp: Time, tolerance:Duration) -> bool:
    """Validate if two timestamps are within the given duration tolerance."""
    print ( (op_timestamp.sec + op_timestamp.nanosec * 1e-9))
    print ((arg_timestamp.sec + arg_timestamp.nanosec * 1e-9))
    time_diff = abs(
        (op_timestamp.sec + op_timestamp.nanosec * 1e-9) -
        (arg_timestamp.sec + arg_timestamp.nanosec * 1e-9)
    )
    print (time_diff)
    tolerance_sec = tolerance.sec + tolerance.nanosec * 1e-9
    print (tolerance_sec)
    return time_diff <= tolerance_sec