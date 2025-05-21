#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseStamped
from px4_msgs.msg import VehicleOdometry
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from rclpy.time import Time

class WrapperNode(Node):
    def __init__(self):
        super().__init__('wrapper_node')
        self.get_logger().info("Constructor reached!")

        # QoS for /target_pose: BEST_EFFORT, KEEP_LAST(1), VOLATILE
        pose_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )
        self.sub_pose = self.create_subscription(
            PoseStamped, '/target_pose', self.cb_pose, qos_profile=pose_qos)
        self.pub_pose = self.create_publisher(
            Odometry, '/target', qos_profile=pose_qos)

        # QoS for /fmu/out/vehicle_odometry: BEST_EFFORT, KEEP_LAST(1), TRANSIENT_LOCAL
        vo_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        self.sub_vo = self.create_subscription(
            VehicleOdometry, '/fmu/out/vehicle_odometry', self.cb_vo, qos_profile=vo_qos)
        self.pub_vo = self.create_publisher(
            Odometry, '/odometry', qos_profile=vo_qos)

        dep_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        self.sub_dep = self.create_subscription(
            Image, '/depth_camera', self.cb_dep, qos_profile=dep_qos)
        self.pub_dep = self.create_publisher(
            Image, '/depth', qos_profile=dep_qos)

        self.get_logger().info('Wrapper_node started with pose, odom, and depth passthrough')

    def cb_pose(self, ps: PoseStamped):
        self.get_logger().info(f"Got PoseStamped @ {ps.header.stamp.sec}.{ps.header.stamp.nanosec}")
        od = Odometry()
        od.header = ps.header
        od.pose.pose = ps.pose
        self.pub_pose.publish(od)
        self.get_logger().info(" → Published /target_odom")

    def cb_dep(self, img: Image):
        # Directly republish the depth image
        # (you could modify img.encoding here if needed)
        self.pub_dep.publish(img)
        self.get_logger().debug("Republished depth image on /depth")

    def cb_vo(self, v: VehicleOdometry):
        # Convert PX4’s uint64 timestamp (ns since boot) into ROS 2 Time
        # ros_time = Time(nanoseconds=v.timestamp).to_msg()
        ros_time = Time(nanoseconds=int(v.timestamp_sample)).to_msg()
        self.get_logger().info(f"Got VehicleOdometry @ px4_ts={v.timestamp}, ros_ts={ros_time.sec}.{ros_time.nanosec}")

        od = Odometry()
        od.header.stamp = ros_time
        od.header.frame_id = 'world'
        od.child_frame_id = 'fcu'    # fixed child frame

        # copy position
        od.pose.pose.position.x = float(v.position[1])
        od.pose.pose.position.y = float(v.position[0])
        od.pose.pose.position.z = -float(v.position[2])

        # copy orientation (w, x, y, z)
        od.pose.pose.orientation.w = float(v.q[0])
        od.pose.pose.orientation.x = float(v.q[2])
        od.pose.pose.orientation.y = float(v.q[1])
        od.pose.pose.orientation.z = -float(v.q[3])

        # copy linear velocity
        od.twist.twist.linear.x = float(v.velocity[1])
        od.twist.twist.linear.y = float(v.velocity[0])
        od.twist.twist.linear.z = -float(v.velocity[2])

        self.pub_vo.publish(od)
        self.get_logger().info(" → Published /odom")

def main(args=None):
    rclpy.init(args=args)
    node = WrapperNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
