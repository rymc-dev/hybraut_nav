from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

continous_dynamics_qos = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=5
)