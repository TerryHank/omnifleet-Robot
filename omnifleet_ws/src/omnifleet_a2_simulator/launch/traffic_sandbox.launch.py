from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    simulator_share = FindPackageShare('omnifleet_a2_simulator')
    description_share = FindPackageShare('omnifleet_a2_description')
    planner_share = FindPackageShare('omnifleet_a2_planner')

    model = LaunchConfiguration('model')
    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')
    use_rviz = LaunchConfiguration('use_rviz')
    enable_navigation = LaunchConfiguration('enable_navigation')
    controller_config = PathJoinSubstitution(
        [simulator_share, 'config', 'ackermann_ros2_control.yaml']
    )
    robot_description = ParameterValue(
        Command([
            'xacro ', model,
            ' use_gazebo:=false',
            ' use_gazebo_classic:=true',
            ' sim_controller_config:=', controller_config,
        ]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('gazebo_ros'), 'launch', 'gazebo.launch.py'])
        ),
        launch_arguments={
            'world': world,
            'gui': gui,
            'verbose': 'false',
            'server_required': 'true',
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
    )
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', 'omnifleet_a2',
            '-topic', '/robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.12', '-Y', '0.0',
        ],
    )

    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '60',
        ],
    )
    ackermann_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=[
            'omnifleet_a2_ackermann_controller',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '60',
        ],
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([planner_share, 'launch', 'navigation.launch.py'])
        ),
        condition=IfCondition(enable_navigation),
        launch_arguments={
            'params_file': PathJoinSubstitution([planner_share, 'config', 'nav2_glim.yaml']),
            'use_sim_time': 'true',
            'autostart': 'true',
            'terrain_mode': '2d',
            'local_obstacle_mode': 'obstacle',
            'planner_mode': 'hybrid_astar',
            'controller_mode': 'rpp',
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value=PathJoinSubstitution(
                [description_share, 'urdf', 'lunshi_ackermann.urdf.xacro']
            ),
        ),
        DeclareLaunchArgument(
            'world',
            default_value=PathJoinSubstitution(
                [simulator_share, 'worlds', 'omnifleet_a2_traffic_sandbox.world']
            ),
        ),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='false'),
        DeclareLaunchArgument('enable_navigation', default_value='true'),
        gazebo,
        robot_state_publisher,
        Node(
            package='omnifleet_a2_simulator',
            executable='traffic_map_publisher.py',
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='map_to_odom_sim',
            output='screen',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0',
                '--yaw', '0', '--pitch', '0', '--roll', '0',
                '--frame-id', 'map', '--child-frame-id', 'odom',
            ],
            parameters=[{'use_sim_time': True}],
        ),
        spawn_robot,
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_robot,
                on_exit=[joint_state_spawner, ackermann_spawner],
            )
        ),
        TimerAction(period=8.0, actions=[navigation]),
        Node(
            condition=IfCondition(use_rviz),
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', PathJoinSubstitution([description_share, 'rviz', 'lunshi_ackermann.rviz'])],
            parameters=[{'use_sim_time': True}],
        ),
    ])
