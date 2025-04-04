from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy

QOS_PROFILE = QoSProfile(
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=QoSReliabilityPolicy.BEST_EFFORT
)