include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "base_link",
  published_frame = "base_link",
  odom_frame = "odom",
  provide_odom_frame = true,
  publish_frame_projected_to_2d = true,
  use_pose_extrapolator = true,
  use_odometry = true,
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 0,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 1,
  lookup_transform_timeout_sec = 0.3,
  submap_publish_period_sec = 0.5,
  pose_publish_period_sec = 0.01,
  trajectory_publish_period_sec = 0.05,
  rangefinder_sampling_ratio = 1.0,
  odometry_sampling_ratio = 1.0,
  fixed_frame_pose_sampling_ratio = 1.0,
  imu_sampling_ratio = 1.0,
  landmarks_sampling_ratio = 1.0,
}

MAP_BUILDER.use_trajectory_builder_3d = true
MAP_BUILDER.num_background_threads = 6

TRAJECTORY_BUILDER_3D.min_range = 0.18
TRAJECTORY_BUILDER_3D.max_range = 30.0
TRAJECTORY_BUILDER_3D.num_accumulated_range_data = 1
TRAJECTORY_BUILDER_3D.voxel_filter_size = 0.12
TRAJECTORY_BUILDER_3D.high_resolution_adaptive_voxel_filter.max_length = 1.0
TRAJECTORY_BUILDER_3D.high_resolution_adaptive_voxel_filter.min_num_points = 100
TRAJECTORY_BUILDER_3D.high_resolution_adaptive_voxel_filter.max_range = 15.0
TRAJECTORY_BUILDER_3D.low_resolution_adaptive_voxel_filter.max_length = 2.5
TRAJECTORY_BUILDER_3D.low_resolution_adaptive_voxel_filter.min_num_points = 150
TRAJECTORY_BUILDER_3D.low_resolution_adaptive_voxel_filter.max_range = 30.0
TRAJECTORY_BUILDER_3D.motion_filter.max_time_seconds = 0.5
TRAJECTORY_BUILDER_3D.motion_filter.max_distance_meters = 0.08
TRAJECTORY_BUILDER_3D.motion_filter.max_angle_radians = math.rad(1.0)
TRAJECTORY_BUILDER_3D.submaps.high_resolution = 0.10
TRAJECTORY_BUILDER_3D.submaps.high_resolution_max_range = 15.0
TRAJECTORY_BUILDER_3D.submaps.low_resolution = 0.30
TRAJECTORY_BUILDER_3D.submaps.num_range_data = 30

POSE_GRAPH.optimize_every_n_nodes = 30
POSE_GRAPH.constraint_builder.sampling_ratio = 0.10
POSE_GRAPH.constraint_builder.min_score = 0.55
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.60
POSE_GRAPH.optimization_problem.ceres_solver_options.max_num_iterations = 20

return options
