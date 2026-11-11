from pathlib import Path


PROJECTOR = Path(__file__).parents[2] / "omnifleet_localization" / "glim_map_projector.py"


def test_airy_scans_are_accumulated_before_one_evidence_update():
    source = PROJECTOR.read_text(encoding="utf-8")
    callback = source.split("def on_aligned_cloud", 1)[1].split(
        "def quaternion_matrix", 1
    )[0]
    assert "self.pending_scans.append" in callback
    assert "self.process_scan_window(msg, now)" in callback
    window = source.split("def process_scan_window", 1)[1].split(
        "def publish_map", 1
    )[0]
    assert "strong_cells=strong_observations" in window
    assert "quality_cells=quality_observations" in window


def test_default_policy_is_conservative_and_data_derived():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("resolution", 0.025)' in source
    assert 'declare_parameter("ray_angular_resolution_deg", 0.4)' in source
    assert 'declare_parameter("wall_stop_margin", 0.075)' in source
    assert 'declare_parameter("wall_guard_cells", 2)' in source
    assert 'declare_parameter("free_expansion_radius", 0.0)' in source
    assert 'declare_parameter("quality_hit_required", 5)' in source
    assert 'declare_parameter("quality_hit_window", 10)' in source
    assert 'declare_parameter("strong_hit_required", 3)' in source
    assert 'declare_parameter("persistent_hit_required", 8)' in source


def test_single_candidates_do_not_become_wall_guards():
    source = PROJECTOR.read_text(encoding="utf-8")
    window = source.split("def process_scan_window", 1)[1].split(
        "def publish_map", 1
    )[0]
    assert "active_wall_guards" in window
    assert "active_confirmed | strong_observations" in window
    assert "occupied | self.evidence" not in window


def test_aligned_intensity_and_structure_are_used_for_obstacle_quality():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'field_names=("x", "y", "z", "intensity")' in source
    assert "obstacle_support_cells(" in source
    assert 'declare_parameter("quality_intensity_min", 1.0)' in source
    assert 'declare_parameter("vertical_structure_min_span", 0.20)' in source
    assert 'declare_parameter("free_confirmation_scans", 3)' in source


def test_height_is_classified_relative_to_robot_ground():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("ground_relative_min", -0.03)' in source
    assert 'declare_parameter("ground_relative_max", 0.03)' in source
    assert 'declare_parameter("obstacle_relative_min", 0.06)' in source
    assert 'declare_parameter("obstacle_relative_max", 1.80)' in source
    masks = source.split("def height_masks", 1)[1].split(
        "def process_scan_window", 1
    )[0]
    assert "base_z - self.ground_z_offset" in masks


def test_cloud_pose_lookup_never_falls_back_to_latest_tf():
    source = PROJECTOR.read_text(encoding="utf-8")
    lookup = source.split("def lookup_frame_transform", 1)[1].split(
        "def lookup_robot_ground_z", 1
    )[0]
    assert "Time.from_msg(msg.header.stamp)" in lookup
    assert "Time()" not in lookup


def test_tf_can_arrive_while_exact_stamp_lookup_waits():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert "MultiThreadedExecutor(num_threads=2)" in source
    assert "executor.spin()" in source
    assert "timeout=Duration(seconds=0.35)" in source


def test_grid_is_rendered_at_a_fixed_robot_ground_plane():
    source = PROJECTOR.read_text(encoding="utf-8")
    assert 'declare_parameter("ground_z_offset_from_base", 0.0)' in source
    assert "self.fixed_ground_z = None" in source
    assert "ground_z = self.lookup_robot_ground_z(map_frame)" in source
    assert "output.info.origin.position.z = ground_z" in source
