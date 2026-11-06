#!/usr/bin/env python3
"""Persist and apply the panel controls to the Nav2 YAML used by this T2."""
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import threading
import subprocess
import signal
import time

import yaml
import parameter_links
import navigation_restart
import height_linkage
import mola_sampling
import collision_model
from omnifleet_local_navigation.navigation_strategy import navigation_strategy, save_navigation_strategy

YAML_FILE = Path('/home/iecme/omnifleet_ws/src/planning/omnifleet_planner/config/nav2_t2.yaml')
BACKUPS = Path('/home/iecme/.local/share/omnifleet_t2/nav2-parameter-backups')
SELECTED_FILE = Path('/home/iecme/.local/share/omnifleet_t2/nav2-selected-algorithms.json')
HEIGHT_FILE = Path('/home/iecme/.local/share/omnifleet_t2/map-height.json')
HEIGHT_KEYS = {'map_z_min': 'slice_z_min', 'map_z_max': 'slice_z_max'}


def robot_topic(name):
    """Return an absolute ROS name in the local domain."""
    return '/' + name.lstrip('/')


def map_heights():
    return json.loads(HEIGHT_FILE.read_text()) if HEIGHT_FILE.exists() else {'slice_z_min': -0.03, 'slice_z_max': 2.0}


def reset_mola_map(get_parameters, set_parameters, sleep=time.sleep, clock=time.monotonic, before_reset=None):
    before = get_parameters()
    module = next((k for k in before if k == 'lidar_odom' or k.endswith(':lidar_odom')), None)
    if module is None or 'reset_state' not in before[module]:
        raise ValueError('当前 MOLA 不提供地图重置接口')
    heights = {k: before[module][k] for k in ('slice_z_min', 'slice_z_max') if k in before[module]}
    if before_reset is not None:
        before_reset()
    set_parameters({module: {'reset_state': True}})
    deadline = clock() + 8.0
    while clock() < deadline:
        current = get_parameters().get(module, {})
        if current.get('reset_state') is False:
            set_parameters({module: {'active': True, 'mapping_enabled': True, **heights}})
            return
        sleep(0.1)
    raise TimeoutError('重置请求已提交，但尚未确认完成；请检查 MOLA 状态后再操作')

LOCAL_ROOT = ('local_costmap', 'local_costmap', 'ros__parameters')
LOCAL = LOCAL_ROOT + ('inflation_layer',)
GLOBAL = ('global_costmap', 'global_costmap', 'ros__parameters', 'inflation_layer')
CONTROL = ('controller_server', 'ros__parameters', 'FollowPath')
CONTROL_RPP = ('controller_server', 'ros__parameters', 'FollowPathRPP')
CONTROL_MPPI = ('controller_server', 'ros__parameters', 'FollowPathMPPI')
PLANNER_SMAC = ('planner_server', 'ros__parameters', 'GridBased')
PLANNER_NAVFN = ('planner_server', 'ros__parameters', 'GridNavFn')
PLANNER_THETA = ('planner_server', 'ros__parameters', 'GridThetaStar')
# id -> YAML parent, parameter leaves, ROS node, ROS parameter prefix, range[, type]
SPECS = {
    'rpp_rotate_to_heading_min_angle': (CONTROL_RPP, ('rotate_to_heading_min_angle',), '/controller_server', 'FollowPathRPP.', .01, math.pi),
    'automatic_recovery': (('bt_navigator','ros__parameters'), ('automatic_recovery',), '/omnifleet_navigation_policy', '', 0., 1., 'bool'),
    'automatic_replanning': (('bt_navigator','ros__parameters'), ('automatic_replanning',), '/omnifleet_navigation_policy', '', 0., 1., 'bool'),
    'replanning_interval': (('bt_navigator','ros__parameters'), ('replanning_interval',), '/omnifleet_navigation_policy', '', .2, 60.),
    'goal_yaw_tolerance': (('controller_server', 'ros__parameters', 'general_goal_checker'), ('yaw_goal_tolerance',), '/controller_server', 'general_goal_checker.', 0., math.pi),
    'local_radius': (LOCAL, ('inflation_radius',), '/local_costmap/local_costmap', 'inflation_layer.', 0., 3.),
    'local_scaling': (LOCAL, ('cost_scaling_factor',), '/local_costmap/local_costmap', 'inflation_layer.', .01, 20.),
    'local_padding': (LOCAL_ROOT, ('footprint_padding',), '/local_costmap/local_costmap', '', 0., .3),
    'global_radius': (GLOBAL, ('inflation_radius',), '/global_costmap/global_costmap', 'inflation_layer.', 0., 3.),
    'global_padding': (('global_costmap', 'global_costmap', 'ros__parameters'), ('footprint_padding',), '/global_costmap/global_costmap', '', 0., .3),
    'global_scaling': (GLOBAL, ('cost_scaling_factor',), '/global_costmap/global_costmap', 'inflation_layer.', .01, 20.),
    'linear_speed': (CONTROL, ('max_vel_x', 'max_speed_xy'), '/controller_server', 'FollowPath.', .05, 1.5),
    'angular_speed': (CONTROL, ('max_vel_theta',), '/controller_server', 'FollowPath.', .1, 3.),
    'obstacle_scale': (CONTROL, ('BaseObstacle.scale',), '/controller_server', 'FollowPath.', 0., 5.),
    'path_align_scale': (CONTROL, ('PathAlign.scale',), '/controller_server', 'FollowPath.', 0., 100.),
    'path_dist_scale': (CONTROL, ('PathDist.scale',), '/controller_server', 'FollowPath.', 0., 100.),
    'planner_cost_multiplier': (PLANNER_SMAC, ('cost_travel_multiplier',), '/planner_server', 'GridBased.', 0., 20.),
    'planner_allow_unknown': (PLANNER_SMAC, ('allow_unknown',), '/planner_server', 'GridBased.', 0., 1., 'bool'),
    'planner_tolerance': (PLANNER_SMAC, ('tolerance',), '/planner_server', 'GridBased.', 0., 5.),
    'planner_use_final_orientation': (PLANNER_SMAC, ('use_final_approach_orientation',), '/planner_server', 'GridBased.', 0., 1., 'bool'),
    'planner_max_planning_time': (PLANNER_SMAC, ('max_planning_time',), '/planner_server', 'GridBased.', .05, 30.),
    'planner_downsample_costmap': (PLANNER_SMAC, ('downsample_costmap',), '/planner_server', 'GridBased.', 0., 1., 'bool'),
    'planner_max_iterations': (PLANNER_SMAC, ('max_iterations',), '/planner_server', 'GridBased.', 1., 5000000., 'int'),
    'navfn_tolerance': (PLANNER_NAVFN, ('tolerance',), '/planner_server', 'GridNavFn.', 0., 5.),
    'navfn_allow_unknown': (PLANNER_NAVFN, ('allow_unknown',), '/planner_server', 'GridNavFn.', 0., 1., 'bool'),
    'navfn_use_astar': (PLANNER_NAVFN, ('use_astar',), '/planner_server', 'GridNavFn.', 0., 1., 'bool'),
    'navfn_use_final_orientation': (PLANNER_NAVFN, ('use_final_approach_orientation',), '/planner_server', 'GridNavFn.', 0., 1., 'bool'),
    'theta_allow_unknown': (PLANNER_THETA, ('allow_unknown',), '/planner_server', 'GridThetaStar.', 0., 1., 'bool'),
    'theta_use_final_orientation': (PLANNER_THETA, ('use_final_approach_orientation',), '/planner_server', 'GridThetaStar.', 0., 1., 'bool'),
    'theta_how_many_corners': (PLANNER_THETA, ('how_many_corners',), '/planner_server', 'GridThetaStar.', 4., 8., 'int'),
    'theta_w_euc_cost': (PLANNER_THETA, ('w_euc_cost',), '/planner_server', 'GridThetaStar.', 0., 20.),
    'theta_w_traversal_cost': (PLANNER_THETA, ('w_traversal_cost',), '/planner_server', 'GridThetaStar.', 0., 20.),
    'dwb_min_speed_xy': (CONTROL, ('min_speed_xy',), '/controller_server', 'FollowPath.', 0., 1.5),
    'dwb_min_speed_theta': (CONTROL, ('min_speed_theta',), '/controller_server', 'FollowPath.', 0., 3.),
    'dwb_min_vel_x': (CONTROL, ('min_vel_x',), '/controller_server', 'FollowPath.', -1.5, 1.5),
    'dwb_sim_time': (CONTROL, ('sim_time',), '/controller_server', 'FollowPath.', .1, 5.),
    'dwb_vx_samples': (CONTROL, ('vx_samples',), '/controller_server', 'FollowPath.', 1., 100., 'int'),
    'dwb_vtheta_samples': (CONTROL, ('vtheta_samples',), '/controller_server', 'FollowPath.', 1., 200., 'int'),
    'rpp_desired_linear_vel': (CONTROL_RPP, ('desired_linear_vel',), '/controller_server', 'FollowPathRPP.', .01, 1.5),
    'rpp_lookahead_dist': (CONTROL_RPP, ('lookahead_dist',), '/controller_server', 'FollowPathRPP.', .05, 5.),
    'rpp_min_lookahead_dist': (CONTROL_RPP, ('min_lookahead_dist',), '/controller_server', 'FollowPathRPP.', .05, 5.),
    'rpp_max_lookahead_dist': (CONTROL_RPP, ('max_lookahead_dist',), '/controller_server', 'FollowPathRPP.', .05, 8.),
    'rpp_lookahead_time': (CONTROL_RPP, ('lookahead_time',), '/controller_server', 'FollowPathRPP.', .05, 10.),
    'rpp_rotate_to_heading_angular_vel': (CONTROL_RPP, ('rotate_to_heading_angular_vel',), '/controller_server', 'FollowPathRPP.', .05, 3.),
    'rpp_max_angular_accel': (CONTROL_RPP, ('max_angular_accel',), '/controller_server', 'FollowPathRPP.', .05, 10.),
    'rpp_use_regulated_linear_velocity_scaling': (CONTROL_RPP, ('use_regulated_linear_velocity_scaling',), '/controller_server', 'FollowPathRPP.', 0., 1., 'bool'),
    'rpp_use_cost_regulated_linear_velocity_scaling': (CONTROL_RPP, ('use_cost_regulated_linear_velocity_scaling',), '/controller_server', 'FollowPathRPP.', 0., 1., 'bool'),
    'rpp_cost_scaling_dist': (CONTROL_RPP, ('cost_scaling_dist',), '/controller_server', 'FollowPathRPP.', 0., 5.),
    'rpp_cost_scaling_gain': (CONTROL_RPP, ('cost_scaling_gain',), '/controller_server', 'FollowPathRPP.', 0., 10.),
    'rpp_inflation_cost_scaling_factor': (CONTROL_RPP, ('inflation_cost_scaling_factor',), '/controller_server', 'FollowPathRPP.', .01, 20.),
    'rpp_use_rotate_to_heading': (CONTROL_RPP, ('use_rotate_to_heading',), '/controller_server', 'FollowPathRPP.', 0., 1., 'bool'),
    'mppi_time_steps': (CONTROL_MPPI, ('time_steps',), '/controller_server', 'FollowPathMPPI.', 1., 200., 'int'),
    'mppi_model_dt': (CONTROL_MPPI, ('model_dt',), '/controller_server', 'FollowPathMPPI.', .005, 1.),
    'mppi_batch_size': (CONTROL_MPPI, ('batch_size',), '/controller_server', 'FollowPathMPPI.', 100., 10000., 'int'),
    'mppi_iteration_count': (CONTROL_MPPI, ('iteration_count',), '/controller_server', 'FollowPathMPPI.', 1., 10., 'int'),
    'mppi_vx_max': (CONTROL_MPPI, ('vx_max',), '/controller_server', 'FollowPathMPPI.', .01, 1.5),
    'mppi_vx_min': (CONTROL_MPPI, ('vx_min',), '/controller_server', 'FollowPathMPPI.', -1.5, 1.5),
    'mppi_wz_max': (CONTROL_MPPI, ('wz_max',), '/controller_server', 'FollowPathMPPI.', .05, 5.),
    'mppi_temperature': (CONTROL_MPPI, ('temperature',), '/controller_server', 'FollowPathMPPI.', .001, 10.),
    'mppi_gamma': (CONTROL_MPPI, ('gamma',), '/controller_server', 'FollowPathMPPI.', 0., 10.),
}

SPECS.update({'goal_xy_tolerance': (('controller_server', 'ros__parameters', 'general_goal_checker'), ('xy_goal_tolerance',), '/controller_server', 'general_goal_checker.', 0.01, 1, 'double'), 'progress_distance': (('controller_server', 'ros__parameters', 'progress_checker'), ('required_movement_radius',), '/controller_server', 'progress_checker.', 0.01, 1, 'double'), 'progress_time': (('controller_server', 'ros__parameters', 'progress_checker'), ('movement_time_allowance',), '/controller_server', 'progress_checker.', 1, 120, 'double'), 'rpp_approach_distance': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('approach_velocity_scaling_dist',), '/controller_server', 'FollowPathRPP.', 0.01, 3, 'double'), 'rpp_approach_min_speed': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('min_approach_linear_velocity',), '/controller_server', 'FollowPathRPP.', 0.01, 1.5, 'double'), 'rpp_velocity_scaled_lookahead': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('use_velocity_scaled_lookahead_dist',), '/controller_server', 'FollowPathRPP.', 0, 1, 'bool'), 'rpp_interpolation': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('use_interpolation',), '/controller_server', 'FollowPathRPP.', 0, 1, 'bool'), 'rpp_curve_radius': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('regulated_linear_scaling_min_radius',), '/controller_server', 'FollowPathRPP.', 0.01, 5, 'double'), 'rpp_curve_min_speed': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('regulated_linear_scaling_min_speed',), '/controller_server', 'FollowPathRPP.', 0.01, 1.5, 'double'), 'dwb_accel_x': (('controller_server', 'ros__parameters', 'FollowPath'), ('acc_lim_x',), '/controller_server', 'FollowPath.', 0.01, 5, 'double'), 'dwb_decel_x': (('controller_server', 'ros__parameters', 'FollowPath'), ('decel_lim_x',), '/controller_server', 'FollowPath.', -5, -0.01, 'double'), 'dwb_accel_theta': (('controller_server', 'ros__parameters', 'FollowPath'), ('acc_lim_theta',), '/controller_server', 'FollowPath.', 0.01, 10, 'double'), 'dwb_decel_theta': (('controller_server', 'ros__parameters', 'FollowPath'), ('decel_lim_theta',), '/controller_server', 'FollowPath.', -10, -0.01, 'double'), 'dwb_goal_rotate_scale': (('controller_server', 'ros__parameters', 'FollowPath'), ('RotateToGoal.scale',), '/controller_server', 'FollowPath.', 0, 100, 'double'), 'dwb_goal_slowing': (('controller_server', 'ros__parameters', 'FollowPath'), ('RotateToGoal.slowing_factor',), '/controller_server', 'FollowPath.', 0.01, 30, 'double'), 'dwb_goal_lookahead': (('controller_server', 'ros__parameters', 'FollowPath'), ('RotateToGoal.lookahead_time',), '/controller_server', 'FollowPath.', -1, 5, 'double'), 'dwb_goal_distance': (('controller_server', 'ros__parameters', 'FollowPath'), ('xy_goal_tolerance',), '/controller_server', 'FollowPath.', 0.01, 1, 'double'), 'dwb_stopped_speed': (('controller_server', 'ros__parameters', 'FollowPath'), ('trans_stopped_velocity',), '/controller_server', 'FollowPath.', 0.001, 0.5, 'double'), 'mppi_obstacle_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'CostCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.CostCritic.', 0, 100, 'double'), 'mppi_path_align_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAlignCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.PathAlignCritic.', 0, 100, 'double'), 'mppi_path_follow_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathFollowCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.PathFollowCritic.', 0, 100, 'double'), 'mppi_goal_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'GoalCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.GoalCritic.', 0, 100, 'double'), 'mppi_goal_angle_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'GoalAngleCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.GoalAngleCritic.', 0, 100, 'double'), 'mppi_path_angle_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAngleCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.PathAngleCritic.', 0, 100, 'double'), 'planner_downsampling_factor': (('planner_server', 'ros__parameters', 'GridBased'), ('downsampling_factor',), '/planner_server', 'GridBased.', 1, 8, 'int')})

SPECS.update({'rpp_allow_reversing': (('controller_server', 'ros__parameters', 'FollowPathRPP'), ('allow_reversing',), '/controller_server', 'FollowPathRPP.', 0, 1, 'bool'), 'mppi_path_forward_preference': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAngleCritic'), ('forward_preference',), '/controller_server', 'FollowPathMPPI.PathAngleCritic.', 0, 1, 'bool'), 'mppi_prefer_forward_enabled': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PreferForwardCritic'), ('enabled',), '/controller_server', 'FollowPathMPPI.PreferForwardCritic.', 0, 1, 'bool'), 'mppi_prefer_forward_weight': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PreferForwardCritic'), ('cost_weight',), '/controller_server', 'FollowPathMPPI.PreferForwardCritic.', 0, 100, 'double'), 'mppi_prefer_forward_distance': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PreferForwardCritic'), ('threshold_to_consider',), '/controller_server', 'FollowPathMPPI.PreferForwardCritic.', 0, 10, 'double'), 'mppi_path_angle_enabled': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAngleCritic'), ('enabled',), '/controller_server', 'FollowPathMPPI.PathAngleCritic.', 0, 1, 'bool'), 'mppi_use_path_orientations': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAlignCritic'), ('use_path_orientations',), '/controller_server', 'FollowPathMPPI.PathAlignCritic.', 0, 1, 'bool'), 'mppi_goal_angle_enabled': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'GoalAngleCritic'), ('enabled',), '/controller_server', 'FollowPathMPPI.GoalAngleCritic.', 0, 1, 'bool'), 'mppi_goal_angle_distance': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'GoalAngleCritic'), ('threshold_to_consider',), '/controller_server', 'FollowPathMPPI.GoalAngleCritic.', 0, 10, 'double'), 'hybrid_motion_model_for_search': (('planner_server', 'ros__parameters', 'GridHybrid'), ('motion_model_for_search',), '/planner_server', 'GridHybrid.', 0, 0, 'string'), 'hybrid_minimum_turning_radius': (('planner_server', 'ros__parameters', 'GridHybrid'), ('minimum_turning_radius',), '/planner_server', 'GridHybrid.', 0.05, 5, 'double'), 'hybrid_reverse_penalty': (('planner_server', 'ros__parameters', 'GridHybrid'), ('reverse_penalty',), '/planner_server', 'GridHybrid.', 1, 20, 'double'), 'hybrid_change_penalty': (('planner_server', 'ros__parameters', 'GridHybrid'), ('change_penalty',), '/planner_server', 'GridHybrid.', 0, 20, 'double'), 'hybrid_non_straight_penalty': (('planner_server', 'ros__parameters', 'GridHybrid'), ('non_straight_penalty',), '/planner_server', 'GridHybrid.', 1, 20, 'double'), 'hybrid_cost_penalty': (('planner_server', 'ros__parameters', 'GridHybrid'), ('cost_penalty',), '/planner_server', 'GridHybrid.', 0, 20, 'double'), 'hybrid_angle_quantization_bins': (('planner_server', 'ros__parameters', 'GridHybrid'), ('angle_quantization_bins',), '/planner_server', 'GridHybrid.', 8, 360, 'int'), 'hybrid_analytic_expansion_ratio': (('planner_server', 'ros__parameters', 'GridHybrid'), ('analytic_expansion_ratio',), '/planner_server', 'GridHybrid.', 0.1, 20, 'double'), 'hybrid_analytic_expansion_max_length': (('planner_server', 'ros__parameters', 'GridHybrid'), ('analytic_expansion_max_length',), '/planner_server', 'GridHybrid.', 0.1, 20, 'double'), 'hybrid_tolerance': (('planner_server', 'ros__parameters', 'GridHybrid'), ('tolerance',), '/planner_server', 'GridHybrid.', 0, 5, 'double'), 'hybrid_max_planning_time': (('planner_server', 'ros__parameters', 'GridHybrid'), ('max_planning_time',), '/planner_server', 'GridHybrid.', 0.05, 30, 'double'), 'hybrid_allow_unknown': (('planner_server', 'ros__parameters', 'GridHybrid'), ('allow_unknown',), '/planner_server', 'GridHybrid.', 0, 1, 'bool'), 'hybrid_smooth_path': (('planner_server', 'ros__parameters', 'GridHybrid'), ('smooth_path',), '/planner_server', 'GridHybrid.', 0, 1, 'bool')})

SPECS.update({
    'mppi_path_align_offset': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathAlignCritic'), ('offset_from_furthest',), '/controller_server', 'FollowPathMPPI.PathAlignCritic.', 1, 200, 'int'),
    'mppi_path_follow_distance': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'PathFollowCritic'), ('threshold_to_consider',), '/controller_server', 'FollowPathMPPI.PathFollowCritic.', 0, 10, 'double'),
    'mppi_goal_distance': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'GoalCritic'), ('threshold_to_consider',), '/controller_server', 'FollowPathMPPI.GoalCritic.', 0, 10, 'double'),
})


# Humble Lattice caches motion tables and smoother settings until reload.
SPECS.update({'lattice_filepath': (('planner_server', 'ros__parameters', 'GridLattice'), ('lattice_filepath',), '/planner_server', 'GridLattice.', 0, 0, 'string'), 'lattice_smooth_path': (('planner_server', 'ros__parameters', 'GridLattice'), ('smooth_path',), '/planner_server', 'GridLattice.', 0, 1, 'bool'), 'lattice_smoother_max_iterations': (('planner_server', 'ros__parameters', 'GridLattice', 'smoother'), ('max_iterations',), '/planner_server', 'GridLattice.smoother.', 1, 100000, 'int'), 'lattice_smoother_w_smooth': (('planner_server', 'ros__parameters', 'GridLattice', 'smoother'), ('w_smooth',), '/planner_server', 'GridLattice.smoother.', 0, 10, 'double'), 'lattice_smoother_w_data': (('planner_server', 'ros__parameters', 'GridLattice', 'smoother'), ('w_data',), '/planner_server', 'GridLattice.smoother.', 0, 10, 'double'), 'lattice_smoother_tolerance': (('planner_server', 'ros__parameters', 'GridLattice', 'smoother'), ('tolerance',), '/planner_server', 'GridLattice.smoother.', 1e-14, 1, 'double'), 'lattice_smoother_do_refinement': (('planner_server', 'ros__parameters', 'GridLattice', 'smoother'), ('do_refinement',), '/planner_server', 'GridLattice.smoother.', 0, 1, 'bool'), 'lattice_allow_reverse_expansion': (('planner_server', 'ros__parameters', 'GridLattice'), ('allow_reverse_expansion',), '/planner_server', 'GridLattice.', 0, 1, 'bool'), 'lattice_reverse_penalty': (('planner_server', 'ros__parameters', 'GridLattice'), ('reverse_penalty',), '/planner_server', 'GridLattice.', 1, 100, 'double'), 'lattice_rotation_penalty': (('planner_server', 'ros__parameters', 'GridLattice'), ('rotation_penalty',), '/planner_server', 'GridLattice.', 0, 100, 'double'), 'lattice_change_penalty': (('planner_server', 'ros__parameters', 'GridLattice'), ('change_penalty',), '/planner_server', 'GridLattice.', 0, 100, 'double'), 'lattice_non_straight_penalty': (('planner_server', 'ros__parameters', 'GridLattice'), ('non_straight_penalty',), '/planner_server', 'GridLattice.', 1, 100, 'double'), 'lattice_cost_penalty': (('planner_server', 'ros__parameters', 'GridLattice'), ('cost_penalty',), '/planner_server', 'GridLattice.', 0, 100, 'double'), 'lattice_analytic_expansion_ratio': (('planner_server', 'ros__parameters', 'GridLattice'), ('analytic_expansion_ratio',), '/planner_server', 'GridLattice.', 0.1, 100, 'double'), 'lattice_analytic_expansion_max_length': (('planner_server', 'ros__parameters', 'GridLattice'), ('analytic_expansion_max_length',), '/planner_server', 'GridLattice.', 0.1, 100, 'double'), 'lattice_tolerance': (('planner_server', 'ros__parameters', 'GridLattice'), ('tolerance',), '/planner_server', 'GridLattice.', 0, 5, 'double'), 'lattice_max_planning_time': (('planner_server', 'ros__parameters', 'GridLattice'), ('max_planning_time',), '/planner_server', 'GridLattice.', 0.05, 120, 'double'), 'lattice_cache_obstacle_heuristic': (('planner_server', 'ros__parameters', 'GridLattice'), ('cache_obstacle_heuristic',), '/planner_server', 'GridLattice.', 0, 1, 'bool')})

GEOMETRY_IDS = set(['geometry_local_footprint', 'geometry_local_robot_radius', 'geometry_local_footprint_padding', 'geometry_local_inflation_radius', 'geometry_global_footprint', 'geometry_global_robot_radius', 'geometry_global_footprint_padding', 'geometry_global_inflation_radius', 'geometry_mppi_consider_footprint'])
SPECS.update({'geometry_local_footprint': (('local_costmap', 'local_costmap', 'ros__parameters'), ('footprint',), '/local_costmap/local_costmap', '', 0, 0, 'string'), 'geometry_local_robot_radius': (('local_costmap', 'local_costmap', 'ros__parameters'), ('robot_radius',), '/local_costmap/local_costmap', '', 0.001, 3, 'double'), 'geometry_local_footprint_padding': (('local_costmap', 'local_costmap', 'ros__parameters'), ('footprint_padding',), '/local_costmap/local_costmap', '', 0, 0.3, 'double'), 'geometry_local_inflation_radius': (('local_costmap', 'local_costmap', 'ros__parameters', 'inflation_layer'), ('inflation_radius',), '/local_costmap/local_costmap', 'inflation_layer.', 0, 3, 'double'), 'geometry_global_footprint': (('global_costmap', 'global_costmap', 'ros__parameters'), ('footprint',), '/global_costmap/global_costmap', '', 0, 0, 'string'), 'geometry_global_robot_radius': (('global_costmap', 'global_costmap', 'ros__parameters'), ('robot_radius',), '/global_costmap/global_costmap', '', 0.001, 3, 'double'), 'geometry_global_footprint_padding': (('global_costmap', 'global_costmap', 'ros__parameters'), ('footprint_padding',), '/global_costmap/global_costmap', '', 0, 0.3, 'double'), 'geometry_global_inflation_radius': (('global_costmap', 'global_costmap', 'ros__parameters', 'inflation_layer'), ('inflation_radius',), '/global_costmap/global_costmap', 'inflation_layer.', 0, 3, 'double'), 'geometry_mppi_consider_footprint': (('controller_server', 'ros__parameters', 'FollowPathMPPI', 'CostCritic'), ('consider_footprint',), '/controller_server', 'FollowPathMPPI.CostCritic.', 0, 1, 'bool')})
SPECS['geometry_local_resolution'] = (
    ('local_costmap', 'local_costmap', 'ros__parameters'), ('resolution',),
    '/local_costmap/local_costmap', '', .005, .1, 'double')

SPECS.update({
    'follow_gap_gain': (CONTROL_RPP, ('follow_gap_gain',), '/controller_server', 'FollowPathRPP.', 0., 5.),
    'follow_speed_damping': (CONTROL_RPP, ('follow_speed_damping',), '/controller_server', 'FollowPathRPP.', 0., 2.),
})

ALGORITHMS = {
    'global': {
        'smac_lattice': ('Smac State Lattice（差速）', 'nav2_smac_planner/SmacPlannerLattice', 'GridLattice'),
        'smac_hybrid': ('Smac Hybrid（前进/倒车）', 'nav2_smac_planner/SmacPlannerHybrid', 'GridHybrid'),
        'smac_2d': ('Smac 2D（A*）', 'nav2_smac_planner/SmacPlanner2D', 'GridBased'),
        'navfn': ('NavFn（A* / Dijkstra）', 'nav2_navfn_planner/NavfnPlanner', 'GridNavFn'),
        'theta_star': ('Theta*', 'nav2_theta_star_planner/ThetaStarPlanner', 'GridThetaStar'),
    },
    'local': {
        'hot_dwb': ('Hot DWB 动态窗口', 'omnifleet_dwb_hot::HotDWBLocalPlanner', 'FollowPath'),
        'rpp': ('Regulated Pure Pursuit', 'omnifleet_planner::HotRegulatedPurePursuitController', 'FollowPathRPP'),
        'mppi': ('MPPI 预测控制', 'nav2_mppi_controller::MPPIController', 'FollowPathMPPI'),
    },
}
ALGORITHM_PARAMETER_NAMES = {'global_planner_algorithm': 'global', 'local_controller_algorithm': 'local'}
ALGORITHM_ROOTS = {'global': ('planner_server', 'ros__parameters'), 'local': ('controller_server', 'ros__parameters')}
SPECS['goal_stateful'] = (('controller_server', 'ros__parameters', 'general_goal_checker'), ('stateful',), '/controller_server', 'general_goal_checker.', 0, 1, 'bool')
SPECS['mppi_deadband_weight'] = (CONTROL_MPPI + ('VelocityDeadbandCritic',), ('cost_weight',), '/controller_server', 'FollowPathMPPI.VelocityDeadbandCritic.', 0, 100, 'double')
DEFAULTS = {
    'dwb_min_speed_xy': 0., 'dwb_min_speed_theta': 0., 'dwb_min_vel_x': 0.,
    'planner_tolerance': .5, 'planner_max_planning_time': 3., 'planner_downsample_costmap': False,
    'planner_max_iterations': 1000000, 'planner_use_final_orientation': True, 'navfn_tolerance': .5,
    'navfn_allow_unknown': False, 'navfn_use_astar': True, 'navfn_use_final_orientation': True,
    'theta_allow_unknown': False, 'theta_use_final_orientation': True, 'theta_how_many_corners': 8,
    'theta_w_euc_cost': 1., 'theta_w_traversal_cost': 2., 'dwb_sim_time': 1.7,
    'dwb_vx_samples': 20, 'dwb_vtheta_samples': 40, 'rpp_desired_linear_vel': .4,
    'rpp_lookahead_dist': .6, 'rpp_min_lookahead_dist': .3, 'rpp_max_lookahead_dist': .9,
    'rpp_lookahead_time': 1.5, 'rpp_rotate_to_heading_angular_vel': 1.8, 'rpp_max_angular_accel': 3.2,
    'rpp_use_regulated_linear_velocity_scaling': True, 'rpp_use_cost_regulated_linear_velocity_scaling': False,
    'rpp_cost_scaling_dist': .3, 'rpp_cost_scaling_gain': 1., 'rpp_inflation_cost_scaling_factor': 3.,
    'rpp_use_rotate_to_heading': True, 'mppi_time_steps': 56, 'mppi_model_dt': .0666667, 'mppi_batch_size': 1000,
    'mppi_iteration_count': 1, 'mppi_vx_max': .4, 'mppi_vx_min': -.35, 'mppi_wz_max': 1.2,
    'mppi_temperature': .3, 'mppi_gamma': .015,
}


DEFAULTS.update({'rpp_allow_reversing': False, 'mppi_path_forward_preference': True, 'mppi_prefer_forward_enabled': True, 'mppi_prefer_forward_weight': 5.0, 'mppi_prefer_forward_distance': 0.5, 'mppi_path_angle_enabled': True, 'mppi_use_path_orientations': False, 'mppi_goal_angle_enabled': True, 'mppi_goal_angle_distance': 0.5, 'hybrid_motion_model_for_search': 'REEDS_SHEPP', 'hybrid_minimum_turning_radius': 0.4, 'hybrid_reverse_penalty': 2.0, 'hybrid_change_penalty': 0.0, 'hybrid_non_straight_penalty': 1.2, 'hybrid_cost_penalty': 2.0, 'hybrid_angle_quantization_bins': 72, 'hybrid_analytic_expansion_ratio': 3.5, 'hybrid_analytic_expansion_max_length': 3.0, 'hybrid_tolerance': 0.25, 'hybrid_max_planning_time': 3.0, 'hybrid_allow_unknown': False, 'hybrid_smooth_path': True})

DEFAULTS.update({'mppi_path_align_offset': 20, 'mppi_path_follow_distance': 1.4, 'mppi_goal_distance': 1.4})

DEFAULTS.update({'geometry_local_footprint': '[]', 'geometry_local_robot_radius': 0.1, 'geometry_local_footprint_padding': 0.01, 'geometry_local_inflation_radius': 0.55, 'geometry_global_footprint': '[]', 'geometry_global_robot_radius': 0.1, 'geometry_global_footprint_padding': 0.01, 'geometry_global_inflation_radius': 0.55, 'geometry_mppi_consider_footprint': False})
DEFAULTS['geometry_local_resolution'] = .02

DEFAULTS.update({'follow_gap_gain': 1., 'follow_speed_damping': .5})

# Conservative receipt: these new planner settings are loaded on Nav2 restart.
RESTART_ONLY = {'hybrid_angle_quantization_bins', 'hybrid_smooth_path', 'hybrid_reverse_penalty', 'hybrid_analytic_expansion_max_length', 'hybrid_minimum_turning_radius', 'hybrid_tolerance', 'hybrid_analytic_expansion_ratio', 'hybrid_max_planning_time', 'hybrid_allow_unknown', 'hybrid_cost_penalty', 'hybrid_motion_model_for_search', 'hybrid_non_straight_penalty', 'hybrid_change_penalty'}
RESTART_ONLY.update(GEOMETRY_IDS - {'geometry_local_inflation_radius', 'geometry_global_inflation_radius'})
RESTART_ONLY.add('geometry_local_resolution')
RESTART_ONLY.update({'lattice_smoother_tolerance', 'lattice_analytic_expansion_max_length', 'lattice_rotation_penalty', 'lattice_analytic_expansion_ratio', 'lattice_smoother_do_refinement', 'lattice_max_planning_time', 'lattice_cache_obstacle_heuristic', 'lattice_cost_penalty', 'lattice_smoother_max_iterations', 'lattice_reverse_penalty', 'lattice_change_penalty', 'lattice_smoother_w_smooth', 'lattice_allow_reverse_expansion', 'lattice_filepath', 'lattice_non_straight_penalty', 'lattice_smoother_w_data', 'lattice_tolerance', 'lattice_smooth_path'})

def algorithm_path(kind, algorithm_id):
    return ALGORITHM_ROOTS[kind] + (ALGORITHMS[kind][algorithm_id][2], 'plugin')


def selected_algorithms(path=SELECTED_FILE):
    selected = {'global': 'smac_2d', 'local': 'hot_dwb'}
    try:
        stored = json.loads(path.read_text(encoding='utf-8'))
        for kind in selected:
            if stored.get(kind) in ALGORITHMS[kind]:
                selected[kind] = stored[kind]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return selected


def save_selected_algorithms(changes, path=SELECTED_FILE, backups=BACKUPS):
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = selected_algorithms(path)
    for name, kind in ALGORITHM_PARAMETER_NAMES.items():
        if name in changes:
            selected[kind] = changes[name]
    old = path.read_bytes() if path.exists() else b''
    new = (json.dumps(selected, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    backup = None
    if old != new:
        backups.mkdir(parents=True, exist_ok=True)
        if old:
            backup = backups / f'nav2-selected-algorithms.{time.time_ns()}.json'
            backup.write_bytes(old)
        fd, temp = tempfile.mkstemp(prefix='.nav2-selection-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(new)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    if path.read_bytes() != new:
        raise OSError('算法选择文件写入后回读不一致')
    return selected, str(backup) if backup else None


def descend(tree, path):
    for key in path:
        tree = tree[key]
    return tree


def spec_type(spec):
    return spec[6] if len(spec) > 6 else 'double'


def typed_value(value, spec):
    kind = spec_type(spec)
    if kind == 'bool':
        return bool(value)
    if kind == 'int':
        return int(value)
    if kind == 'string':
        return str(value)
    return float(value)


def validate_value(key, value, spec):
    kind = spec_type(spec)
    if key in ('geometry_local_footprint', 'geometry_global_footprint'):
        if not isinstance(value, str):
            raise ValueError('footprint 必须是二维坐标数组字符串')
        points = json.loads(value)
        if points != []:
            if not isinstance(points, list) or len(points) < 3 or any(not isinstance(p, list) or len(p) != 2 or
                    any(type(v) not in (int, float) or not math.isfinite(v) for v in p) for p in points):
                raise ValueError('footprint 必须是 [] 或至少三个有限二维坐标点')
            area = sum(a[0]*b[1] - a[1]*b[0] for a,b in zip(points, points[1:]+points[:1]))
            if abs(area) < 1e-10:
                raise ValueError('footprint 轮廓不能退化成点或直线；圆形模型请填 []')
    if key == 'hybrid_motion_model_for_search' and value not in ('DUBIN','REEDS_SHEPP'):
        raise ValueError('搜索运动模型只能是 DUBIN 或 REEDS_SHEPP')
    if key == 'hybrid_angle_quantization_bins' and (not isinstance(value,int) or value % 2):
        raise ValueError('朝向离散数量必须为偶数')
    if kind == 'bool' and not isinstance(value, bool):
        raise ValueError('参数类型错误')
    if kind == 'int' and (isinstance(value, bool) or not isinstance(value, int)):
        raise ValueError('参数类型错误')
    if kind == 'double' and (isinstance(value, bool) or not isinstance(value, (int, float))):
        raise ValueError('参数类型错误')
    if kind == 'string' and (not isinstance(value, str) or not value):
        raise ValueError('参数类型错误')
    if kind != 'string' and not math.isfinite(value):
        raise ValueError('参数必须是有限值')
    if kind != 'string' and not spec[4] <= value <= spec[5]:
        raise ValueError(f'{key} 必须在 {spec[4]} 到 {spec[5]} 之间')


def algorithm_state(path=YAML_FILE):
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    selected = selected_algorithms()
    state = {}
    for kind, options in ALGORITHMS.items():
        loaded = []
        for key, (label, plugin, instance) in options.items():
            try:
                loaded_plugin = descend(data, algorithm_path(kind, key))
            except (KeyError, TypeError):
                loaded_plugin = None
            aliases = {
                'omnifleet_planner::CostAwareSmac2D':'nav2_smac_planner/SmacPlanner2D',
                'omnifleet_planner::ExactGoalSmacLattice':'nav2_smac_planner/SmacPlannerLattice',
                'omnifleet_planner::PoseRotationShim':'nav2_mppi_controller::MPPIController',
            }
            if aliases.get(loaded_plugin,loaded_plugin) == plugin:
                loaded.append(key)
        current = selected[kind] if selected[kind] in loaded else (loaded[0] if loaded else None)
        state[kind] = {'current': current,
                       'plugin': options[current][1] if current else None,
                       'loaded_ids': loaded,
                       'options': [{'id': key, 'label': label, 'plugin': plugin, 'instance': instance}
                                   for key, (label, plugin, instance) in options.items()]}
    if 'smac_lattice' in state['global']['loaded_ids']:
        lattice = descend(data, ('planner_server', 'ros__parameters', 'GridLattice'))
        try:
            metadata = json.loads(Path(lattice['lattice_filepath']).read_text())['lattice_metadata']
            state['global']['lattice_metadata'] = {key: metadata.get(key) for key in
                ('motion_model', 'grid_resolution', 'turning_radius', 'num_of_headings', 'number_of_trajectories')}
            state['global']['lattice_metadata']['filepath'] = lattice['lattice_filepath']
        except (OSError, ValueError, KeyError) as error:
            state['global']['lattice_metadata'] = {'error': str(error)}
    return state


DEFAULTS.update({'goal_stateful': False, 'mppi_deadband_weight': 1.0})

def read_saved_value(data, key, spec):
    try:
        return typed_value(descend(data, spec[0] + (spec[1][0],)), spec)
    except (KeyError, TypeError):
        if key in DEFAULTS:
            return DEFAULTS[key]
        raise


def saved_values(path=YAML_FILE):
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    return {**{key: {leaf: read_saved_value(data, key, spec) if index == 0 else typed_value(descend(data, spec[0] + (leaf,)), spec)
                   for index, leaf in enumerate(spec[1])}
            for key, spec in SPECS.items()}, **{key: {leaf: map_heights()[leaf]} for key, leaf in HEIGHT_KEYS.items()}, **mola_sampling.values()}


def edited_yaml(text, changes):
    """Replace existing scalar spans while preserving comments and formatting."""
    tree = yaml.compose(text)
    edits = []
    for key, value in changes.items():
        if key not in SPECS:
            raise ValueError('算法选择或缺失参数需要结构化 YAML 更新')
        spec = SPECS[key]
        kind = spec_type(spec)
        validate_value(key, value, spec)
        for leaf in spec[1]:
            node = tree
            for segment in spec[0] + (leaf,):
                if not isinstance(node, yaml.MappingNode):
                    raise ValueError('YAML 层级不是映射')
                matches = [v for k, v in node.value if k.value == segment]
                if len(matches) != 1:
                    raise ValueError(f'YAML 路径缺失或重复: {segment}')
                node = matches[0]
            if not isinstance(node, yaml.ScalarNode):
                raise ValueError('参数不是标量')
            if key in ('geometry_local_footprint', 'geometry_global_footprint') and node.value == value:
                continue
            replacement = str(value).lower() if kind == 'bool' else str(value) if kind in ('int', 'string') else repr(float(value))
            if key in ('geometry_local_footprint', 'geometry_global_footprint'):
                replacement = json.dumps(value, ensure_ascii=False)
            edits.append((node.start_mark.index, node.end_mark.index, replacement))
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    parsed = yaml.safe_load(text)
    for key, value in changes.items():
        for leaf in SPECS[key][1]:
            actual = descend(parsed, SPECS[key][0] + (leaf,))
            if actual != typed_value(value, SPECS[key]):
                raise ValueError('YAML 参数回读校验失败')
    return text


def rewritten_yaml(text, changes):
    """Apply algorithm selections and missing profile keys, then validate the whole YAML."""
    data = yaml.safe_load(text)
    for key, value in changes.items():
        if key in ALGORITHM_PARAMETER_NAMES:
            raise ValueError('算法选择由 selector 话题处理，不写入单个插件类型')
        if key not in SPECS:
            raise ValueError('不支持的参数')
        spec = SPECS[key]
        validate_value(key, value, spec)
        parent = descend(data, spec[0])
        for leaf in spec[1]:
            parent[leaf] = typed_value(value, spec)
    result = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    checked = yaml.safe_load(result)
    for key, value in changes.items():
        if key in ALGORITHM_PARAMETER_NAMES:
            raise ValueError('算法选择由 selector 话题处理，不写入单个插件类型')
        else:
            for leaf in SPECS[key][1]:
                if descend(checked, SPECS[key][0] + (leaf,)) != typed_value(value, SPECS[key]):
                    raise ValueError('YAML 参数回读校验失败')
    return result


def apply_config_changes(text, changes):
    if any(key in ALGORITHM_PARAMETER_NAMES for key in changes):
        raise ValueError('算法选择不能作为 YAML 数值变更写入')
    try:
        data = yaml.safe_load(text)
        for key, spec in SPECS.items():
            if key not in changes:
                continue
            for leaf in spec[1]:
                descend(data, spec[0] + (leaf,))
        return edited_yaml(text, changes)
    except (KeyError, TypeError, ValueError):
        return rewritten_yaml(text, changes)


def save_changes(changes, path=YAML_FILE, backups=BACKUPS):
    target = path.resolve(strict=True)  # write the source behind the installed symlink
    old = target.read_bytes()
    yaml_changes = {key: value for key, value in changes.items() if key in SPECS}
    algorithm_changes = {key: value for key, value in changes.items() if key in ALGORITHM_PARAMETER_NAMES}
    for key, value in algorithm_changes.items():
        kind = ALGORITHM_PARAMETER_NAMES[key]
        if value not in ALGORITHMS[kind]:
            raise ValueError('不支持的算法选择')
    new = apply_config_changes(old.decode('utf-8'), yaml_changes).encode('utf-8') if yaml_changes else old
    if set(yaml_changes) & {'dwb_min_speed_xy', 'dwb_min_speed_theta', 'dwb_min_vel_x', 'linear_speed', 'angular_speed'}:
        control = descend(yaml.safe_load(new), CONTROL)
        if control.get('min_speed_xy', 0.) > control['max_speed_xy']:
            raise ValueError('DWB 最低平移速度不能超过最大平移速度')
        if control.get('min_speed_theta', 0.) > control['max_vel_theta']:
            raise ValueError('DWB 最低角速度不能超过最大角速度')
        if control.get('min_vel_x', 0.) > control['max_vel_x']:
            raise ValueError('DWB 前后速度下界不能超过前进速度上限')
    if set(yaml_changes) & {'rpp_approach_min_speed','rpp_curve_min_speed','rpp_desired_linear_vel','rpp_min_lookahead_dist','rpp_max_lookahead_dist','rpp_velocity_scaled_lookahead'}:
        rpp = descend(yaml.safe_load(new), CONTROL_RPP)
        if rpp['min_lookahead_dist'] > rpp['max_lookahead_dist']:
            raise ValueError('最小前视距离不能大于最大前视距离')
        for key in ('min_approach_linear_velocity','regulated_linear_scaling_min_speed'):
            if rpp[key] > rpp['desired_linear_vel']:
                raise ValueError('减速后的最低速度不能高于RPP期望最大线速度')
    checked = yaml.safe_load(new)
    if set(yaml_changes) & {'rpp_allow_reversing', 'rpp_use_rotate_to_heading'}:
        rpp = descend(checked, CONTROL_RPP)
        if rpp.get('allow_reversing', False) and rpp.get('use_rotate_to_heading', True):
            raise ValueError('RPP允许倒车与启用航向对齐不能同时开启；请先关闭另一项')
    desired_selection = selected_algorithms()
    for key, value in algorithm_changes.items():
        desired_selection[ALGORITHM_PARAMETER_NAMES[key]] = value
    mppi = descend(checked, CONTROL_MPPI)
    if desired_selection['local'] == 'mppi' and (set(yaml_changes) & {'mppi_use_path_orientations'} or algorithm_changes):
        if mppi.get('PathAlignCritic', {}).get('use_path_orientations', False) and desired_selection['global'] not in ('smac_hybrid', 'smac_lattice'):
            raise ValueError('当前二维规划器不提供车体方向路径；请先关闭遵循路径中的车体朝向')
    backup = None
    if new != old and set(changes) & GEOMETRY_IDS:
        collision_model.capture_body(yaml.safe_load(old), target)
    if new != old:
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / f'nav2_t2.{time.time_ns()}.yaml'
        backup.write_bytes(old)
        fd, temp = tempfile.mkstemp(prefix='.nav2-save-', dir=target.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(new)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temp, target.stat().st_mode & 0o777)
            os.replace(temp, target)
            directory_fd = os.open(target.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    if target.read_bytes() != new:
        raise OSError('文件写入后回读不一致')
    selection = None
    selection_backup = None
    if algorithm_changes:
        selection, selection_backup = save_selected_algorithms(algorithm_changes, backups=backups)
    return {'path': str(target), 'backup': str(backup) if backup else None,
            'sha256': hashlib.sha256(new).hexdigest(), 'saved': saved_values(target),
            'algorithms': algorithm_state(target), 'selection_backup': selection_backup,
            'selection': selection, 'collision_model': collision_model.state(target)}


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.callback_groups import ReentrantCallbackGroup
    from rclpy.executors import MultiThreadedExecutor
    from rcl_interfaces.msg import Parameter, ParameterValue, SetParametersResult
    from rcl_interfaces.srv import GetParameters, SetParameters, SetParametersAtomically
    from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
    from std_srvs.srv import Trigger
    from std_msgs.msg import String
    from mola_msgs.srv import MolaRuntimeParamGet, MolaRuntimeParamSet
    from action_msgs.msg import GoalStatusArray
    from geometry_msgs.msg import Twist
    from nav2_msgs.srv import ClearEntireCostmap
    from nav_msgs.msg import OccupancyGrid

    class Store(Node):
        def __init__(self):
            # MOLA's runtime services remain root-scoped in the native launcher.
            # Node-specific rules take precedence over fleet-wide remapping.
            super().__init__('omnifleet_t2_nav2_parameter_store', cli_args=[
                '--ros-args',
                '-r', 'omnifleet_t2_nav2_parameter_store:/mola_runtime_param_get:=/mola_runtime_param_get',
                '-r', 'omnifleet_t2_nav2_parameter_store:/mola_runtime_param_set:=/mola_runtime_param_set',
            ])
            self.clients_group = ReentrantCallbackGroup()
            self.height_get = self.create_client(MolaRuntimeParamGet, '/mola_runtime_param_get', callback_group=self.clients_group)
            self.height_set = self.create_client(MolaRuntimeParamSet, '/mola_runtime_param_set', callback_group=self.clients_group)
            self.navigation_active = {}
            self.last_motion = 0.0
            self.collision_navigation = None
            self.collision_navigation_at = 0.0
            self.create_subscription(String, '/navigation/status', self.observe_collision_navigation,
                                     10, callback_group=self.clients_group)
            self.height_map_received = {}
            for scope in height_linkage.SCOPES:
                self.create_subscription(OccupancyGrid, f'/{scope}_costmap/costmap',
                    lambda msg, scope=scope: self.height_map_received.update({scope: time.monotonic()}) if msg.data else None,
                    1, callback_group=self.clients_group)
            for topic in (robot_topic('/navigate_to_pose/_action/status'),
                          robot_topic('/navigate_through_poses/_action/status')):
                self.create_subscription(GoalStatusArray, topic,
                    lambda msg, topic=topic: self.navigation_active.update({topic: any(s.status in (1, 2, 3) for s in msg.status_list)}),
                    QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL),
                    callback_group=self.clients_group)
            for motion_topic in ('/cmd_vel', '/navigation/nav_cmd_vel', '/motor_command_sent'):
                self.create_subscription(Twist, motion_topic, self.observe_motion, 1, callback_group=self.clients_group)
            self.clear_costmaps = [self.create_client(ClearEntireCostmap,
                f'/{scope}_costmap/clear_entirely_{scope}_costmap', callback_group=self.clients_group) for scope in ('local', 'global')]
            self.invalidate_map_waypoints = self.create_client(Trigger,
                '/omnifleet_t2/waypoints/invalidate_map', callback_group=self.clients_group)
            self.create_service(Trigger, 'omnifleet_t2/nav2/reset_map', self.reset_map)
            self.nav_clients = {}
            for node in {spec[2] for spec in SPECS.values()}:
                self.nav_clients[node] = (
                    self.create_client(SetParametersAtomically, node + '/set_parameters_atomically', callback_group=self.clients_group),
                    self.create_client(GetParameters, node + '/get_parameters', callback_group=self.clients_group),
                )
            selector_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                                      durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.planner_selector_pub = self.create_publisher(String, '/planner_selector', selector_qos)
            self.controller_selector_pub = self.create_publisher(String, '/controller_selector', selector_qos)
            self.selector_timer = self.create_timer(1.0, self.publish_selectors)
            self.bag_process = None
            self.bag_path = None
            self.bag_lock = threading.Lock()
            # 录包服务只暴露固定话题；面板不能传入任意命令或任意话题。
            self.bag_topics = [
                # Sensor input chain: raw -> radius-filtered -> MOLA pose/TF.
                robot_topic('/rslidar_points'),
                robot_topic('/rslidar_points_filtered'),
                robot_topic('/tf'),
                robot_topic('/tf_static'),
                robot_topic('/lidar_odometry/pose'),
                robot_topic('/plan'),
                # Controller chain: planner output -> controller input -> local path.
                robot_topic('/received_global_plan'),
                robot_topic('/transformed_global_plan'),
                robot_topic('/controller_server/local_plan'),
                robot_topic('/navigation/nav_cmd_vel'),
                robot_topic('/lidar_odometry/nav_odom'),
                robot_topic('/local_costmap/costmap'),
                robot_topic('/global_costmap/costmap'),
                robot_topic('/diagnostics'),
            ]
            self.create_service(Trigger, 'omnifleet_t2/nav2/start_bag_record', self.start_bag_record)
            self.create_service(Trigger, 'omnifleet_t2/nav2/stop_bag_record', self.stop_bag_record)
            self.create_service(Trigger, 'omnifleet_t2/nav2/read_saved', self.read)
            self.create_service(SetParameters, 'omnifleet_t2/nav2/save_parameters', self.save)
            self.get_logger().info(f'永久参数文件: {YAML_FILE.resolve()}')

        def start_bag_record(self, request, response):
            with self.bag_lock:
                if self.bag_process is not None and self.bag_process.poll() is None:
                    response.success = False
                    response.message = '已经在录制：' + str(self.bag_path)
                    return response
                bag_root = Path.home() / 'omnifleet_data/recordings/bags/panel_bags'
                bag_root.mkdir(parents=True, exist_ok=True)
                self.bag_path = bag_root / time.strftime('motion_trace_%Y%m%d_%H%M%S')
                log_path = self.bag_path.with_suffix('.record.log')
                log = log_path.open('w', buffering=1)
                command = ['ros2', 'bag', 'record', '-o', str(self.bag_path), *self.bag_topics]
                try:
                    self.bag_process = subprocess.Popen(
                        command, stdout=log, stderr=subprocess.STDOUT,
                        start_new_session=True
                    )
                except Exception as error:
                    log.close()
                    response.success = False
                    response.message = '启动录包失败：' + str(error)
                    return response
                response.success = True
                response.message = '已开始录制：' + str(self.bag_path)
                self.get_logger().info(response.message)
                return response

        def stop_bag_record(self, request, response):
            with self.bag_lock:
                process = self.bag_process
                path = self.bag_path
                if process is None or process.poll() is not None:
                    response.success = False
                    response.message = '当前没有正在录制的 bag'
                    return response
                try:
                    process.send_signal(signal.SIGINT)
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=5)
                finally:
                    self.bag_process = None
                response.success = True
                response.message = '录制已停止：' + str(path)
                self.get_logger().info(response.message)
                return response

        def destroy_node(self):
            if self.bag_process is not None and self.bag_process.poll() is None:
                try:
                    self.bag_process.send_signal(signal.SIGINT)
                    self.bag_process.wait(timeout=10)
                except Exception:
                    self.bag_process.kill()
            return super().destroy_node()

        def publish_selectors(self):
            try:
                selected = selected_algorithms()
                self.planner_selector_pub.publish(String(data=ALGORITHMS['global'][selected['global']][2]))
                self.controller_selector_pub.publish(String(data=ALGORITHMS['local'][selected['local']][2]))
            except Exception as error:
                self.get_logger().warning(f'算法选择发布失败: {error}')

        def observe_motion(self, msg):
            if abs(msg.linear.x) + abs(msg.linear.y) + abs(msg.angular.z) > 0.001:
                self.last_motion = time.monotonic()

        def reset_map(self, request, response):
            try:
                if any(self.navigation_active.values()) or time.monotonic() - self.last_motion < 2.0:
                    raise ValueError('请先停止导航和底盘运动，再清空地图')
                def get_parameters():
                    return yaml.safe_load(self.request(self.height_get, MolaRuntimeParamGet.Request()).parameters)
                def set_parameters(values):
                    reply = self.request(self.height_set, MolaRuntimeParamSet.Request(parameters=yaml.safe_dump(values)))
                    if not reply.success:
                        raise ValueError(reply.error_message)
                if self.collision_navigation is not False or time.monotonic() - self.collision_navigation_at > 2:
                    raise ValueError('导航状态未确认空闲，不能清空地图')
                def clear_waypoints():
                    cleared = self.request(self.invalidate_map_waypoints, Trigger.Request())
                    if not cleared.success:
                        raise ValueError(cleared.message)
                reset_mola_map(get_parameters, set_parameters, before_reset=clear_waypoints)
                warnings = []
                for client in self.clear_costmaps:
                    if client.service_is_ready():
                        try:
                            self.request(client, ClearEntireCostmap.Request())
                        except Exception as error:
                            warnings.append(f'代价地图刷新未确认：{error}')
                response.success = True
                response.message = 'MOLA 已重置并启用建图；新地图将随点云输入更新。'
                response.message += '旧航点和路线预览已清空；已保存的地图文件保留，请重新设置航点。'
                if warnings:
                    response.message += ' '.join(warnings)
            except Exception as error:
                response.success = False
                response.message = str(error)
            return response

        def observe_collision_navigation(self, message):
            try:
                value = json.loads(message.data)
                if isinstance(value, dict) and isinstance(value.get('navigation_active'), bool):
                    self.collision_navigation = value['navigation_active']
                    self.collision_navigation_at = time.monotonic()
            except (ValueError, TypeError):
                pass

        def read(self, request, response):
            try:
                saved = saved_values()
                response.message = json.dumps({'path': str(YAML_FILE.resolve()), 'saved': saved, 'algorithms': algorithm_state(), 'parameter_links': self.link_catalog(), 'navigation_strategy': navigation_strategy(), 'collision_model': collision_model.state(YAML_FILE)}, ensure_ascii=False)
                response.success = True
            except Exception as error:
                response.success = False
                response.message = str(error)
            return response

        def link_catalog(self):
            return parameter_links.catalog(SPECS, YAML_FILE, HEIGHT_FILE, SELECTED_FILE)

        def request(self, client, request, timeout=3.):
            if not client.wait_for_service(timeout_sec=1.):
                raise TimeoutError(f'节点参数服务暂不可用：{client.srv_name}')
            future = client.call_async(request)
            ready = threading.Event()
            future.add_done_callback(lambda _: ready.set())
            if not ready.wait(timeout):
                client.remove_pending_request(future)
                raise TimeoutError('运行时参数接口超时')
            return future.result()

        def save(self, request, response):
            if any(p.name == '__collision_model' for p in request.parameters):
                try:
                    if len(request.parameters) != 1 or request.parameters[0].value.type != 4:
                        raise ValueError('碰撞模型必须单独提交字符串选择')
                    receipt = collision_model.save_mode(request.parameters[0].value.string_value,
                        YAML_FILE, BACKUPS, navigation_active=self.collision_navigation,
                        state_age=time.monotonic() - self.collision_navigation_at,
                        motion_age=time.monotonic() - self.last_motion)
                    receipt.update(saved=saved_values(), algorithms=algorithm_state())
                    response.results = [SetParametersResult(successful=True, reason=json.dumps(receipt, ensure_ascii=False))]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error))]
                return response
            if any(p.name in ('__navigation_strategy', '__navigation_strategy_status') for p in request.parameters):
                try:
                    if len(request.parameters) != 1 or request.parameters[0].value.type != 4:
                        raise ValueError('导航策略请求格式不正确')
                    parameter = request.parameters[0]
                    result = ({'strategy': navigation_strategy(), 'applies_to': 'next_task'}
                              if parameter.name == '__navigation_strategy_status'
                              else save_navigation_strategy(parameter.value.string_value))
                    response.results = [SetParametersResult(successful=True, reason=json.dumps(result, ensure_ascii=False))]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error))]
                return response
            if any(p.name in ('__stack_command', '__stack_restart', '__stack_status', '__saved_maps') for p in request.parameters):
                try:
                    if len(request.parameters) != 1 or request.parameters[0].value.type != 4:
                        raise ValueError('导航栈请求格式不正确')
                    p = request.parameters[0]
                    result = navigation_restart.handle(p.name, p.value.string_value)
                    response.results = [SetParametersResult(successful=True, reason=json.dumps(result, ensure_ascii=False))]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error))]
                return response

            if any(p.name in ('__open_config', '__open_docs') for p in request.parameters):
                try:
                    if len(request.parameters) != 1 or request.parameters[0].value.type != 4:
                        raise ValueError('链接请求格式不正确')
                    parameter = request.parameters[0]
                    target = json.loads(parameter.value.string_value)
                    opened = parameter_links.open_target(self.link_catalog(), target['id'],
                        target.get('index', 0), docs=parameter.name == '__open_docs')
                    response.results = [SetParametersResult(successful=True, reason=opened)]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error))]
                return response

            if any(p.name in mola_sampling.KEYS for p in request.parameters):
                try:
                    changes = {}
                    for p in request.parameters:
                        if p.name not in mola_sampling.KEYS or p.value.type != 2 or p.name in changes:
                            raise ValueError('MOLA 采样点数必须单独提交且不可重复，类型为整数')
                        changes[p.name] = p.value.integer_value
                    receipt = mola_sampling.save(changes, BACKUPS)
                    receipt.update(saved=saved_values(), algorithms=algorithm_state())
                    response.results = [SetParametersResult(successful=True, reason=json.dumps(receipt, ensure_ascii=False)) for _ in request.parameters]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error)) for _ in request.parameters]
                return response

            if any(p.name in HEIGHT_KEYS for p in request.parameters):
                try:
                    values = map_heights()
                    for p in request.parameters:
                        if p.name not in HEIGHT_KEYS or p.value.type != 3:
                            raise ValueError('地图高度必须单独提交浮点参数')
                        value = p.value.double_value
                        if not math.isfinite(value) or not -10 <= value <= 10:
                            raise ValueError('地图高度必须在 -10 到 10 m 内')
                        values[HEIGHT_KEYS[p.name]] = value
                    if values['slice_z_min'] >= values['slice_z_max']:
                        raise ValueError('高度下限必须小于上限')
                    if any(self.navigation_active.values()) or time.monotonic() - self.last_motion < 2.0:
                        raise ValueError('请先停止导航并等待车辆停稳 2 秒，再修改共用高度范围')
                    def read_mola():
                        modules = yaml.safe_load(self.request(self.height_get, MolaRuntimeParamGet.Request()).parameters)
                        module = next((k for k in modules if k == 'lidar_odom' or k.endswith(':lidar_odom')), None)
                        if module is None:
                            raise ValueError('MOLA 高度接口不可用')
                        return modules[module]
                    def write_mola(values):
                        modules = yaml.safe_load(self.request(self.height_get, MolaRuntimeParamGet.Request()).parameters)
                        module = next(k for k in modules if k == 'lidar_odom' or k.endswith(':lidar_odom'))
                        reply = self.request(self.height_set, MolaRuntimeParamSet.Request(parameters=yaml.safe_dump({module: values})))
                        if not reply.success:
                            raise ValueError(reply.error_message)
                    def read_nav(scope):
                        getter = self.nav_clients[f'/{scope}_costmap/{scope}_costmap'][1]
                        keys = (*height_linkage.NAV_KEYS, height_linkage.CAPABILITY)
                        reply = self.request(getter, GetParameters.Request(names=list(keys)))
                        return {key: value.integer_value if value.type == 2 else value.double_value
                                for key, value in zip(keys, reply.values) if value.type in (2, 3)}
                    def write_nav(scope, values):
                        setter = self.nav_clients[f'/{scope}_costmap/{scope}_costmap'][0]
                        params = [Parameter(name=k, value=ParameterValue(type=3, double_value=v)) for k, v in values.items()]
                        reply = self.request(setter, SetParametersAtomically.Request(parameters=params))
                        if not reply.result.successful:
                            raise ValueError(scope + ': ' + reply.result.reason)
                    def clear_nav(scope):
                        client = self.clear_costmaps[height_linkage.SCOPES.index(scope)]
                        self.request(client, ClearEntireCostmap.Request())
                        # Receipt is only sent after a new map arrives following the clear response.
                        cleared = time.monotonic()
                        deadline = cleared + 4.0
                        while self.height_map_received.get(scope, 0) <= cleared:
                            if time.monotonic() >= deadline:
                                raise TimeoutError(scope + ' 旧代价已清理，但未收到新代价地图')
                            time.sleep(.05)
                    runtime = height_linkage.apply_linked(values, read_mola, write_mola, read_nav,
                        write_nav, clear_nav, lambda values: height_linkage.persist_heights(values, YAML_FILE, HEIGHT_FILE, BACKUPS))
                    receipt = {'saved': saved_values(), 'algorithms': algorithm_state(),
                               'runtime': runtime, 'runtime_confirmed': True}
                    response.results = [SetParametersResult(successful=True, reason=json.dumps(receipt, ensure_ascii=False)) for _ in request.parameters]
                except Exception as error:
                    response.results = [SetParametersResult(successful=False, reason=str(error)) for _ in request.parameters]
                return response
            try:
                changes = {}
                for param in request.parameters:
                    if param.name in changes:
                        raise ValueError('参数不能重复')
                    if param.name in ALGORITHM_PARAMETER_NAMES:
                        if param.value.type != 4:
                            raise ValueError('算法选择必须是字符串')
                        value = param.value.string_value
                        kind = ALGORITHM_PARAMETER_NAMES[param.name]
                        if value not in ALGORITHMS[kind]:
                            raise ValueError('不支持的算法选择')
                        changes[param.name] = value
                    elif param.name in SPECS:
                        kind = spec_type(SPECS[param.name])
                        expected = {'bool': 1, 'int': 2, 'double': 3, 'string': 4}[kind]
                        if param.value.type != expected:
                            raise ValueError(f'{param.name} 参数类型不匹配')
                        changes[param.name] = (param.value.bool_value if kind == 'bool' else
                                               param.value.integer_value if kind == 'int' else
                                               param.value.string_value if kind == 'string' else
                                               param.value.double_value)
                    else:
                        raise ValueError('不支持的参数')
                if not changes:
                    raise ValueError('没有要保存的参数')
                if changes.get('global_planner_algorithm') == 'smac_hybrid':
                    _, getter = self.nav_clients['/planner_server']
                    loaded = self.request(getter, GetParameters.Request(names=['planner_plugins']))
                    if not loaded.values or 'GridHybrid' not in loaded.values[0].string_array_value:
                        raise ValueError('Smac Hybrid已配置，但当前导航栈未加载；请先停车并重启导航栈')
                receipt = save_changes(changes)
            except Exception as error:
                response.results = [SetParametersResult(successful=False, reason=str(error)) for _ in request.parameters]
                return response
            grouped = {}
            for key, value in changes.items():
                if key in ALGORITHM_PARAMETER_NAMES:
                    continue
                if key in RESTART_ONLY:
                    continue
                spec = SPECS[key]
                grouped.setdefault(spec[2], {}).update({spec[3] + leaf: typed_value(value, spec) for leaf in spec[1]})
            runtime = {key: '永久保存成功；该参数需重启导航栈后生效' for key in changes if key in RESTART_ONLY}
            has_algorithm_changes = any(key in ALGORITHM_PARAMETER_NAMES for key in changes)
            for node, values in grouped.items():
                try:
                    setter, getter = self.nav_clients[node]
                    params = []
                    # RPP consumes coupled booleans in request order. Disable
                    # the conflicting mode before enabling its replacement.
                    for name, value in sorted(values.items(), key=lambda item: 0 if item[1] is False else 1):
                        if isinstance(value, bool):
                            param_value = ParameterValue(type=1, bool_value=value)
                        elif isinstance(value, int):
                            param_value = ParameterValue(type=2, integer_value=value)
                        elif isinstance(value, str):
                            param_value = ParameterValue(type=4, string_value=value)
                        else:
                            param_value = ParameterValue(type=3, double_value=value)
                        params.append(Parameter(name=name, value=param_value))
                    reply = self.request(setter, SetParametersAtomically.Request(parameters=params))
                    if not reply.result.successful:
                        raise ValueError(reply.result.reason)
                    result = self.request(getter, GetParameters.Request(names=list(values)))
                    def mismatch(parameter, value):
                        if isinstance(value, bool):
                            return parameter.type != 1 or parameter.bool_value != value
                        if isinstance(value, int):
                            return parameter.type != 2 or parameter.integer_value != value
                        if isinstance(value, str):
                            return parameter.type != 4 or parameter.string_value != value
                        return parameter.type != 3 or abs(parameter.double_value - value) > 1e-9
                    if len(result.values) != len(values) or any(mismatch(p, v) for p, v in zip(result.values, values.values())):
                        raise ValueError('运行时回读未匹配')
                    runtime[node] = '已应用并回读确认'
                except Exception as error:
                    runtime[node] = f'永久保存成功；当前实例未确认：{error}。下次启动读取新值'
            for key in changes:
                if key in ALGORITHM_PARAMETER_NAMES:
                    runtime[key] = '已写入永久选择并发布 selector 话题；等待行为树读取选择，尚未验证行驶执行'
            receipt['runtime'] = runtime
            receipt['runtime_confirmed'] = all(value == '已应用并回读确认' for value in runtime.values())
            self.get_logger().info(json.dumps({'changes': changes, **receipt}, ensure_ascii=False))
            response.results = [SetParametersResult(successful=True, reason=json.dumps(receipt, ensure_ascii=False)) for _ in request.parameters]
            return response

    rclpy.init()
    node = Store()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
