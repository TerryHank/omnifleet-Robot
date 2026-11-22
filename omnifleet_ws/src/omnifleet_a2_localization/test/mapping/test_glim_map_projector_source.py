from pathlib import Path

import numpy as np
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

from omnifleet_a2_localization.glim_map_projector import GlimMapProjector


PROJECTOR = Path(__file__).parents[2] / "omnifleet_a2_localization" / "glim_map_projector.py"
BACKEND_LAUNCH = (
    Path(__file__).parents[2] / "launch" / "backends" / "glim_cuda_backend.launch.py"
)


def test_projection_has_no_neighbor_or_multi_frame_evidence_filter():
    source = PROJECTOR.read_text(encoding="utf-8")
    for removed in (
        "OccupancyEvidence",
        "occupancy_evidence",
        "hit_history",
        "quality_hit_required",
        "strong_hit_required",
        "persistent_hit_required",
        "hit_spatial_tolerance_cells",
        "obstacle_support_cells",
        "bridge_small_obstacle_gaps",
        "clip_ray_at_guards",
        "candidate_ttl",
    ):
        assert removed not in source


def test_bootstrap_uses_only_the_latest_raw_airy_frame():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("input_topic", "/glim_ros/map")' in source
    assert '"bootstrap_input_topic", "/rslidar_points"' in source
    assert 'declare_parameter("bootstrap_max_rate_hz", 0.5)' in source
    assert 'declare_parameter("bootstrap_raytrace_max_range", 6.0)' in source
    assert "aligned_points" not in source
    assert "accumulate" not in source
    callback = source.split("def on_bootstrap_cloud", 1)[1].split(
        "@staticmethod", 1
    )[0]
    assert "self.current_occupied_cells = observed_occupied" in callback
    assert "self.free_cells = observed_free - self.occupied_cells" in callback
    assert "self.occupied_cells.update" not in callback
    assert "self.free_cells.update" not in callback
    assert "difference_update" not in callback
    assert "depth=1" in source


def test_bootstrap_rate_limits_failed_tf_attempts():
    source = PROJECTOR.read_text(encoding="utf-8")
    callback = source.split("def on_bootstrap_cloud", 1)[1].split(
        "@staticmethod", 1
    )[0]
    assert "last_bootstrap_accept" not in source
    assert callback.index("self.last_bootstrap_attempt = now") < callback.index(
        "self.lookup_frame_transform"
    )


def test_official_map_keeps_only_current_frame_free_space():
    source = PROJECTOR.read_text(encoding="utf-8")
    global_callback = source.split("def try_apply_global_map", 1)[1].split(
        "def on_bootstrap_cloud", 1
    )[0]
    assert "self.official_map_active = True" in global_callback
    assert "self.official_occupied_cells = occupied_cells" in global_callback
    assert "当前单帧继续提供可见自由区" in global_callback


def test_mapping_launch_enables_bounded_bootstrap_input():
    source = BACKEND_LAUNCH.read_text(encoding="utf-8")
    assert '"bootstrap_input_topic": "/rslidar_points"' in source
    assert '"bootstrap_max_rate_hz": 0.10' in source
    assert '"bootstrap_raytrace_max_range"' in source
    assert '"tf_latest_tolerance_sec": 0.10' in source
    assert '"/glim_ros/aligned_points"' not in source


def test_single_frame_ray_cells_include_origin_and_endpoint():
    cells = GlimMapProjector.ray_cells((0, 0), (3, 1))
    assert cells[0] == (0, 0)
    assert cells[-1] == (3, 1)
    assert len(cells) == 4


def test_global_map_uses_depth_one_and_skips_unchanged_content():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert "depth=1" in source
    callback = source.split("def try_apply_global_map", 1)[1].split(
        "def quaternion_matrix", 1
    )[0]
    assert "occupied_cells == self.official_occupied_cells" in callback


def test_xyz_decode_does_not_request_intensity():
    message = point_cloud2.create_cloud_xyz32(
        Header(frame_id="map"),
        [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)],
    )
    xyz = GlimMapProjector.decode(message)
    np.testing.assert_allclose(xyz, [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def test_height_is_classified_relative_to_robot_base():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("ground_relative_min", -0.03)' in source
    assert 'declare_parameter("obstacle_relative_min", 0.06)' in source
    masks = source.split("def height_masks", 1)[1].split("def publish_map", 1)[0]
    assert "delta @ map_from_base[:, 2] - self.ground_z_offset" in masks


def test_cloud_pose_lookup_uses_the_cloud_stamp():
    source = PROJECTOR.read_text(encoding="utf-8")
    lookup = source.split("def lookup_frame_transform", 1)[1].split(
        "def lookup_bootstrap_transform", 1
    )[0]
    assert "Time.from_msg(msg.header.stamp)" in lookup
    assert "timeout=Duration(seconds=0.02)" in lookup


def test_cloud_pose_lookup_has_only_a_bounded_latest_tf_fallback():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("tf_latest_tolerance_sec", 0.02)' in source
    lookup = source.split("def lookup_frame_transform", 1)[1].split(
        "def lookup_bootstrap_transform", 1
    )[0]
    assert lookup.index("stamp,") < lookup.index("Time(),")
    assert "skew_ns <= self.tf_latest_tolerance_ns" in lookup
    assert "0.0 <= tf_latest_tolerance <= 0.1" in source


def test_global_snapshot_replaces_direct_cell_state():
    source = PROJECTOR.read_text(encoding="utf-8")
    callback = source.split("def try_apply_global_map", 1)[1].split(
        "def quaternion_matrix", 1
    )[0]
    assert "self.official_occupied_cells = occupied_cells" in callback
    assert "self.free_cells.difference_update(self.occupied_cells)" in callback
    assert "self.pending_global_map = None" in callback
    assert 'self.publish_map(msg, "正式GLIM障碍+当前可见自由区")' in callback


def test_occupancy_grid_uses_native_map_plane():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("resolution", 0.08)' in source
    assert 'map_frame = "map"' in source
    assert "output.info.origin.position.z = 0.0" in source
    assert "lookup_robot_ground_z" not in source


def test_tf_can_arrive_while_exact_stamp_lookup_waits():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert "MultiThreadedExecutor(num_threads=2)" in source
    assert "while rclpy.ok():" in source
    assert "executor.spin_once(timeout_sec=0.2)" in source
    assert "executor.spin()" not in source
