from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("input_topic", default_value="/surgical_perception/instances"),
        DeclareLaunchArgument("device", default_value="cpu"),
        Node(
            package="surgical_grasper_point",
            executable="point_node",
            name="surgical_grasper_point",
            output="screen",
            parameters=[{
                "input_topic": ParameterValue(LaunchConfiguration("input_topic"), value_type=str),
                "device": ParameterValue(LaunchConfiguration("device"), value_type=str),
            }],
        ),
    ])
