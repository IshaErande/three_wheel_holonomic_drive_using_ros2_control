import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # --- Paths ---
    description_pkg = get_package_share_directory('three_wheel_holonomic_description')
    urdf_file = os.path.join(description_pkg, 'urdf', 'three_wheel_holonomic.urdf.xacro')
    rviz_config_file = os.path.join(description_pkg, 'rviz', 'three_wheel_holonomic_config.rviz')

    # --- 1. Robot State Publisher ---
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', urdf_file]), 'use_sim_time': True}]
    )

    # --- 2. Start Gazebo (Empty World) ---
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(), # '-r' starts simulation unpaused
    )

    # --- 3. Spawn Robot in Gazebo ---
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'three_wheel_holonomic',
            '-z', '0.1'  # Drop it slightly from the sky so it doesn't clip the floor
        ],
        output='screen'
    )

    # --- 4. ROS-Gazebo Clock Bridge ---
    # This is critical! It takes the simulator time and publishes it to ROS 2
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # --- 5. Controller Spawners ---
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    omni_wheel_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['omni_wheel_controller', '--controller-manager', '/controller_manager'],
    )

    # --- 6. RViz2 ---
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_launch,
        spawn_entity,
        clock_bridge,
        joint_state_broadcaster_spawner,
        omni_wheel_controller_spawner,
        rviz2_node
    ])