import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # --- 1. Define Package Paths ---
    description_pkg = get_package_share_directory('three_wheel_holonomic_description')
    bringup_pkg = get_package_share_directory('three_wheel_holonomic_bringup')
    
    urdf_file = os.path.join(description_pkg, 'urdf', 'three_wheel_holonomic.urdf.xacro')
    rviz_config_file = os.path.join(description_pkg, 'rviz', 'three_wheel_holonomic_config.rviz')
    controllers_file = os.path.join(bringup_pkg, 'config', 'three_wheel_holonomic_controllers.yaml')

    # --- 2. Process Xacro ---
    robot_description_content = Command(['xacro ', urdf_file])
    robot_description = {'robot_description': robot_description_content}

    # --- 3. Define Nodes ---
    
    # Node 1: Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': False}] # Changed to False
    )

    # Node 2: Controller Manager (ros2_control_node)
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[robot_description, controllers_file, {'use_sim_time': False}] # Changed to False
    )

    # Node 3: Spawner for Joint State Broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Node 4: Spawner for Omni Wheel Controller
    omni_wheel_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['omni_wheel_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # Node 5: RViz2
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': False}], # Changed to False
        output='screen'
    )

    # --- 4. Return Launch Description ---
    return LaunchDescription([
        robot_state_publisher_node,
        controller_manager_node,
        joint_state_broadcaster_spawner,
        omni_wheel_controller_spawner,
        rviz2_node
    ])