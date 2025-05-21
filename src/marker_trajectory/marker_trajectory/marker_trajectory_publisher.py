#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node

# Import the service and message types.
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity
from geometry_msgs.msg import Pose, Point, Quaternion

class MarkerTrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('marker_trajectory_publisher')
        # Create a client for the SetEntityPose service.
        self.client = self.create_client(SetEntityPose, '/world/default/set_pose')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /world/default/set_pose service...')
        # Set up a timer to call the service periodically.
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        # The name of the marker entity (must match what was used when spawning)
        self.marker_name = "aruco_marker"

    def timer_callback(self):
        # Compute elapsed time.
        current_time = self.get_clock().now().nanoseconds / 1e9
        t = current_time - self.start_time


        # Define a thin ellipsoid in front of the camera:
        #   - major axis swing left/right (x)
        #   - tiny vertical bob (z)
        #   - fixed forward offset so it never leaves the FOV (y)
        major = 0.6      # half‐width of ellipse in x (m)
        minor = 0.1      # half‐height of ellipse in z (m)
        y_offset = 0   # forward distance from camera (m)
        x = major * math.cos(t)
        y = y_offset + 0.0 * math.sin(t)   # no swing in y
        z = minor * math.sin(t) + 0.3       # center at 1.0 m height

        # # Define a circular trajectory (modify as needed)
        # radius = 2.0  # meters
        # z = radius * math.cos(t)
        # x = radius * math.sin(t)
        # y = 0.3       # constant height

        # Build the geometry_msgs/Pose message.
        pose_msg = Pose()
        pose_msg.position = Point(x=x, y=y, z=z)
        # Use an identity quaternion (no rotation)
        pose_msg.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

        # Create an Entity message for the marker.
        entity_msg = Entity()
        entity_msg.name = self.marker_name

        # Build the service request.
        req = SetEntityPose.Request()
        req.entity = entity_msg
        req.pose = pose_msg

        self.get_logger().info(f'Sending pose: x={x:.2f}, y={y:.2f}, z={z:.2f}')
        future = self.client.call_async(req)
        future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Pose update succeeded.")
            else:
                self.get_logger().warn("Pose update failed.")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = MarkerTrajectoryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Keyboard interrupt, shutting down.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
