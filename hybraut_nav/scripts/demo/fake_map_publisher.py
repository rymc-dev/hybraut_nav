#!/usr/bin/env python3
"""
fake_map_publisher

Standalone demo node that stands in for a real map source (e.g.
`nav2_map_server`) when there isn't one available (e.g. a bare TurtleBot3
Gazebo sim). Publishes a single static, entirely free `nav_msgs/OccupancyGrid`
on `/map` - the world `strategy_node` plans A* routes over - so the
strategic-driven demo can validate/accept goals and plan without a real
costmap pipeline.

Published with `hybraut_nav.qos.map_qos` (TRANSIENT_LOCAL), matching what
`strategy_node` subscribes with, so a late-joining `strategy_node` still
gets it. Also re-published on a slow timer as a belt-and-braces measure.

Also broadcasts a static identity `map -> odom` transform on `/tf_static`
(once, on startup) - a bare TurtleBot3 sim only ever gets you `odom ->
base_footprint` (from Gazebo) and the URDF's static link tree; nothing
bridges that to a `map` frame without a real localization source. This is a
stand-in for that bridge, same spirit as the map itself: fine for a demo
where the map and odom origins coincide, not a substitute for real
localization (AMCL, SLAM, etc.) if the two ever diverge.

NOTE: this is a flat, obstacle-free map - it stands in for "having a costmap
at all", not for real occupancy data. Point `nav2_map_server` at a real saved
map instead of this if you need actual obstacles reflected in the plan.
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Header
from tf2_ros import StaticTransformBroadcaster

from hybraut_nav.qos import map_qos


class FakeMapPublisher(Node):

    def __init__(self):
        super().__init__('fake_map_publisher')

        self.declare_parameter(
            'resolution',
            0.05,
            ParameterDescriptor(
                description='Metres per cell. (default: 0.05)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'width',
            400,
            ParameterDescriptor(
                description='Grid width in cells. With the default resolution, '
                            '400 cells = 20m. (default: 400)',
                type=ParameterType.PARAMETER_INTEGER
            )
        )
        self.declare_parameter(
            'height',
            400,
            ParameterDescriptor(
                description='Grid height in cells. With the default resolution, '
                            '400 cells = 20m. (default: 400)',
                type=ParameterType.PARAMETER_INTEGER
            )
        )
        self.declare_parameter(
            'origin_x',
            -10.0,
            ParameterDescriptor(
                description='World x (m) of the grid origin (bottom-left cell). '
                            'Default centres a 20m-wide grid on (0, 0). (default: -10.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'origin_y',
            -10.0,
            ParameterDescriptor(
                description='World y (m) of the grid origin (bottom-left cell). '
                            'Default centres a 20m-tall grid on (0, 0). (default: -10.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'frame_id',
            'map',
            ParameterDescriptor(
                description="frame_id stamped on the published grid - must match "
                            "the goal pose's frame_id sent to planner/activate. "
                            '(default: map)',
                type=ParameterType.PARAMETER_STRING
            )
        )
        self.declare_parameter(
            'republish_period',
            5.0,
            ParameterDescriptor(
                description='Seconds between re-publishes, on top of the initial '
                            'one - belt-and-braces given TRANSIENT_LOCAL should '
                            'already cover late subscribers. (default: 5.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'odom_frame_id',
            'odom',
            ParameterDescriptor(
                description="child frame_id for the static map -> odom transform "
                            "this node broadcasts, bridging the TF tree (RViz's "
                            "Fixed Frame, RobotModel/TF displays) down to whatever "
                            "frame Gazebo's odometry is actually rooted at. Set to "
                            "'' to skip broadcasting the transform entirely (e.g. "
                            "if you have a real localization source instead). "
                            '(default: odom)',
                type=ParameterType.PARAMETER_STRING
            )
        )
        self.declare_parameter(
            'publish_map_transform',
            True,
            ParameterDescriptor(
                description='Whether to broadcast the static map -> odom transform '
                            'at all. (default: true)',
                type=ParameterType.PARAMETER_BOOL
            )
        )

        self._map_pub = self.create_publisher(OccupancyGrid, '/map', map_qos)
        self._tf_broadcaster = StaticTransformBroadcaster(self)

        self._publish_map()
        self._timer = self.create_timer(
            self.get_parameter('republish_period').value,
            self._publish_map,
        )

        if self.get_parameter('publish_map_transform').value and self.get_parameter('odom_frame_id').value:
            self._publish_map_transform()

        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        resolution = self.get_parameter('resolution').value
        self.get_logger().info(
            f'fake_map_publisher up - publishing a {width * resolution:.1f}m x '
            f'{height * resolution:.1f}m entirely free map on /map'
        )

    def _publish_map(self):
        resolution = self.get_parameter('resolution').value
        width = self.get_parameter('width').value
        height = self.get_parameter('height').value

        msg = OccupancyGrid()
        msg.header = Header(
            stamp=self.get_clock().now().to_msg(),
            frame_id=self.get_parameter('frame_id').value,
        )
        msg.info.map_load_time = self.get_clock().now().to_msg()
        msg.info.resolution = resolution
        msg.info.width = width
        msg.info.height = height
        msg.info.origin.position.x = self.get_parameter('origin_x').value
        msg.info.origin.position.y = self.get_parameter('origin_y').value
        msg.info.origin.orientation.w = 1.0
        msg.data = [0] * (width * height)  # entirely free space

        self._map_pub.publish(msg)

    def _publish_map_transform(self):
        """
        Broadcasts a static identity transform from the published map's
        frame_id to `odom_frame_id`, once, on /tf_static - StaticTransform
        Broadcaster uses TRANSIENT_LOCAL durability itself, so late TF
        listeners (e.g. RViz started afterwards) still get it without a
        re-publish timer.
        """
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = self.get_parameter('frame_id').value
        transform.child_frame_id = self.get_parameter('odom_frame_id').value
        transform.transform.rotation.w = 1.0  # identity - map and odom origins coincide
        self._tf_broadcaster.sendTransform(transform)
        self.get_logger().info(
            f"fake_map_publisher: broadcasting static identity transform "
            f"'{transform.header.frame_id}' -> '{transform.child_frame_id}'"
        )


def main(args=None):
    rclpy.init(args=args)
    node = FakeMapPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
