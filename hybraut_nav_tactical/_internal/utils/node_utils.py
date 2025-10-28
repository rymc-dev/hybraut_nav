from rclpy.node import Node


def create_cli(
    node: Node,
    srv_name: str,
    srv_type,
    timeout_sec: float = 5.0
):
    """Creates a ROS client for specifid service and type"""
    try:
        cli = node.create_client(srv_type=srv_type, srv_name=srv_name)
        while not cli.wait_for_service(timeout_sec):
            raise RuntimeError(
                f'timeout occured while waiting for {srv_name} service...')
    except Exception as e:
        node.get_logger().error(
            f"node_utils::create_cli: exception occured: {str(e)}")
        raise e

    return cli
