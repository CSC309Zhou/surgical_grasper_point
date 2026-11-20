from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from surgical_grasper_point.msg import GrasperPoint, GrasperPointArray
from surgical_perception.msg import InstrumentArray

from .predictor import PointPredictor


class GrasperPointNode(Node):
    def __init__(self):
        super().__init__("surgical_grasper_point")
        read_only = ParameterDescriptor(read_only=True)
        self.declare_parameter("input_topic", "/surgical_perception/instances", read_only)
        self.declare_parameter("device", "cpu", read_only)
        input_topic = self.get_parameter("input_topic").value
        device = self.get_parameter("device").value
        weights = Path(get_package_share_directory("surgical_grasper_point")) / "weights"
        self.predictor = PointPredictor(weights / "point_head.pt2", device)
        self.bridge = CvBridge()
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher = self.create_publisher(GrasperPointArray, "~/points", qos)
        self.subscription = self.create_subscription(InstrumentArray, input_topic, self.process, qos)
        self.get_logger().info(f"已加载抓钳 Point 模型，设备 {device}，输入 {input_topic}")

    def process(self, frame):
        message = GrasperPointArray()
        message.header = frame.header
        message.image_width = frame.image_width
        message.image_height = frame.image_height
        for instance in frame.instances:
            if instance.class_name not in {"grasper1", "grasper2", "grasper"}:
                continue
            if instance.mask.encoding != "mono8":
                raise ValueError(f"抓钳 Mask 应为 mono8，实际为 {instance.mask.encoding}")
            mask = self.bridge.imgmsg_to_cv2(instance.mask, desired_encoding="passthrough")
            if mask.shape != (frame.image_height, frame.image_width):
                raise ValueError("抓钳 Mask 与原图尺寸不一致")
            prediction = self.predictor.predict(mask, instance.bbox_xyxy)
            if prediction is None:
                continue
            point = GrasperPoint()
            point.instance_id = instance.instance_id
            point.bbox_xyxy = instance.bbox_xyxy
            point.point_xy, point.point_box_uv = prediction
            message.points.append(point)
        self.publisher.publish(message)


def main():
    rclpy.init()
    node = None
    try:
        node = GrasperPointNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
