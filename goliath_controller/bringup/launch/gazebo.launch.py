from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription , ExecuteProcess,TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
import os
from launch.substitutions import LaunchConfiguration
import xacro
from ament_index_python.packages import get_package_share_directory
from controller_manager import spawner

def generate_launch_description():
    share_dir = get_package_share_directory('goliath_controller')
    pkg_path = os.path.join(get_package_share_directory('goliath_controller'))
    xacro_file = os.path.join(share_dir, 'urdf', 'goliath.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()
    robot_controllers=os.path.join(pkg_path, 'config', 'goliath_controller.yaml')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_urdf}
        ]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    gz = ExecuteProcess(
        cmd=[
            'ros2', 'launch', 'ros_gz_sim', 'gz_sim.launch.py', 
            'gz_args:=-r empty.sdf'
        ],
        output='screen'
    )

    # Spawn the robot in Gazebo
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            "goliath_description",
            "-topic",
            "/robot_description",
            "-x",
            "0",
            "-y",
            "0",
            "-z",
            "1.4",
        ],
        output="screen",
    )

    joint_state_broadcaster = TimerAction(
        period=7.0,  # Delay of 3 seconds before starting joint_state_broadcaster
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                output='screen',
                arguments=["joint_state_broadcaster"]
            )
        ]
    )

    position_controller = TimerAction(
        period=10.0,  # Delay of 5 seconds before starting forward_position_controller
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                output='screen',
                arguments=["position_controller"]
            )
        ]
    )
    
    
    return LaunchDescription([
        gz,
        spawn_entity,
        robot_state_publisher_node,
        joint_state_publisher_node,
        position_controller,
        joint_state_broadcaster,
    ])
