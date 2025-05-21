#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from px4_msgs.msg import VehicleLocalPosition
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, Point
from visualization_msgs.msg import Marker
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped

class PathVisualizer(Node):
    def __init__(self):
        super().__init__('path_visualizer')

        # QoS: use RELIABLE so RViz can subscribe
        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Publishers
        self.path_pub   = self.create_publisher(Path,   '/drone_path',        qos)
        self.marker_pub = self.create_publisher(Marker, '/drone_path_marker', qos)

        # Store trajectory
        self.poses = []

        # Static TF: world → local_origin
        self._static_broadcaster = StaticTransformBroadcaster(self)
        static_tf = TransformStamped()
        static_tf.header.stamp = self.get_clock().now().to_msg()
        static_tf.header.frame_id = 'world'
        static_tf.child_frame_id = 'local_origin'
        static_tf.transform.translation.x = 0.0
        static_tf.transform.translation.y = 0.0
        static_tf.transform.translation.z = 0.0
        static_tf.transform.rotation.x = 0.0
        static_tf.transform.rotation.y = 0.0
        static_tf.transform.rotation.z = 0.0
        static_tf.transform.rotation.w = 1.0
        self._static_broadcaster.sendTransform(static_tf)

        # Subscriber
        self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position',
            self.local_position_cb,
            qos
        )

        self.get_logger().info('Started PathAndMarkerPublisher')

    def local_position_cb(self, msg: VehicleLocalPosition):
        # 1) Build PoseStamped
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'local_origin'
        pose.pose.position.x = msg.x
        pose.pose.position.y = msg.y
        pose.pose.position.z = msg.z

        # Append to trajectory
        self.poses.append(pose)

        # 2) Publish Path
        path = Path()
        path.header.stamp = pose.header.stamp
        path.header.frame_id = pose.header.frame_id
        path.poses = list(self.poses)
        self.path_pub.publish(path)

        # 3) Publish LINE_STRIP Marker
        line_marker = Marker()
        line_marker.header = pose.header
        line_marker.ns    = 'drone_path'
        line_marker.id    = 0
        line_marker.type  = Marker.LINE_STRIP
        line_marker.action= Marker.ADD
        line_marker.scale.x = 0.05
        line_marker.color.r = 0.0
        line_marker.color.g = 1.0
        line_marker.color.b = 0.0
        line_marker.color.a = 1.0

        # Build list of geometry_msgs/Point
        pts = []
        for p in self.poses:
            pt = Point()
            pt.x = p.pose.position.x
            pt.y = p.pose.position.y
            pt.z = p.pose.position.z
            pts.append(pt)
        line_marker.points = pts
        self.marker_pub.publish(line_marker)

        # 4) Publish SPHERE Marker at current position
        sphere = Marker()
        sphere.header = pose.header
        sphere.ns    = 'drone_marker'
        sphere.id    = 1
        sphere.type  = Marker.SPHERE
        sphere.action= Marker.ADD
        sphere.pose.position = pose.pose.position
        sphere.pose.orientation.w = 1.0
        sphere.scale.x = 0.2
        sphere.scale.y = 0.2
        sphere.scale.z = 0.2
        sphere.color.r = 1.0
        sphere.color.g = 0.0
        sphere.color.b = 0.0
        sphere.color.a = 1.0
        self.marker_pub.publish(sphere)

def main(args=None):
    rclpy.init(args=args)
    node = PathVisualizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
