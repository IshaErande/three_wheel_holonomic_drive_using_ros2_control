import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Path Setup
    pkg_description = get_package_share_directory('three_wheel_holonomic_description')
    urdf_file = os.path.join(pkg_description, 'urdf', 'three_wheel_holonomic.urdf.xacro')
    rviz_config_file = os.path.join(pkg_description, 'rviz', 'three_wheel_holonomic.rviz')

    # 2. Robot State Publisher (Runs Xacro to generate robot_description)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_file])
        }]
    )

    # 3. Joint State Publisher GUI (Sliding bars for your continuous joints)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # 4. RViz2
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz2_node
    ])