from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy, DurabilityPolicy

QOS_DEPTH = 10

world_state_qos = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=QOS_DEPTH,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE
)