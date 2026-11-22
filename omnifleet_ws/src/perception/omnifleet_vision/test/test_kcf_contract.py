from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


def test_safe_defaults_and_omnifleet_topics():
    config = (PACKAGE / "config" / "kcf_follower.yaml").read_text()
    assert "enable_motion: false" in config
    assert "cmd_vel_topic: /cmd_vel_vision" in config
    assert "tracker_color_topic: /camera/color/image_raw" in config
    assert "aligned_color_topic: /camera/color/image_raw" in config
    assert "depth_topic: /camera/depth/image_raw" in config
    assert "max_pair_delta: 0.8" in config
    assert "tracking_timeout: 0.5" in config
    assert "depth_timeout: 0.5" in config
    assert "control_rate: 10.0" in config
    assert "tracking_scale: 0.4" in config
    assert "minimum_linear_speed: 0.40" in config
    assert "max_linear_speed: 0.40" in config
    assert "linear_deadband: 0.15" in config


def test_node_parameterizes_topics_and_depth_encodings():
    source = (PACKAGE / "src" / "kcf_follower_node.cpp").read_text()
    for parameter in (
        "tracker_color_topic",
        "aligned_color_topic",
        "depth_topic",
        "output_image_topic",
        "cmd_vel_topic",
        "enable_motion",
        "depth_scale_16u",
        "depth_scale_32f",
        "max_pair_delta",
        "tracking_timeout",
        "depth_timeout",
        "control_rate",
        "tracking_scale",
        "minimum_linear_speed",
        "max_linear_speed",
        "linear_deadband",
    ):
        assert f'"{parameter}"' in source
    assert "TYPE_16UC1" in source
    assert "TYPE_32FC1" in source
    assert 'cmd_vel_topic_ != "/cmd_vel_vision"' in source
    assert "create_wall_timer" in source
    assert "std::abs(requested_linear) > 1.0e-9" in source
    assert "std::copysign(minimum_linear_speed_" in source
    assert "all numeric control parameters must be finite" in source
    assert "gains, deadbands and speed limits must not be negative" in source
    assert "depth scales and min_depth < target_distance < max_depth must be valid" in source
    assert "tracking_scale must be in the interval (0, 1]" in source
    assert "cv::resize" in source
    assert '#include "kcftracker.h"' in source


def test_tracker_and_depth_callbacks_have_separate_jobs():
    source = (PACKAGE / "src" / "kcf_follower_node.cpp").read_text()
    tracker_callback = source.split("void tracker_color_callback", 1)[1].split(
        "void aligned_depth_callback", 1
    )[0]
    depth_callback = source.split("void aligned_depth_callback", 1)[1].split(
        "std::string tracker_color_topic_", 1
    )[0]
    assert "tracker_->update" in tracker_callback
    assert "tracker_->update" not in depth_callback
    assert "max_pair_delta_" in depth_callback
    assert "invalidate_depth_candidate" in depth_callback
    assert "publish_stop" in depth_callback


def test_tracker_sources_are_compiled():
    cmake = (PACKAGE / "CMakeLists.txt").read_text()
    assert "src/kcftracker.cpp" in cmake
    assert "src/fhog.cpp" in cmake
    assert "libopencv_core.so.4.5d" in cmake
    assert "OMNIFLEET_OPENCV_LIBRARIES" in cmake


def test_launch_exposes_headless_roi_and_motion_gate():
    launch = (PACKAGE / "launch" / "kcf_follower.launch.py").read_text()
    for argument in (
        "roi_x",
        "roi_y",
        "roi_width",
        "roi_height",
        "enable_motion",
        "use_gui",
        "tracker_color_topic",
        "aligned_color_topic",
        "max_pair_delta",
        "tracking_timeout",
        "depth_timeout",
        "control_rate",
        "tracking_scale",
        "minimum_linear_speed",
        "max_linear_speed",
        "linear_deadband",
    ):
        assert f'"{argument}"' in launch


def test_gui_roi_selection_preserves_image_coordinates_and_confirms_on_release():
    source = (PACKAGE / "src" / "kcf_follower_node.cpp").read_text()
    selector = source.split("cv::Rect select_roi", 1)[1].split(
        "static std::unique_ptr<KCFTracker>", 1
    )[0]
    assert "cv::WINDOW_AUTOSIZE" in selector
    assert "cv::WINDOW_NORMAL" not in selector
    assert "state->finished = state->result.width > 5" in source
    assert "release mouse to confirm" in source


def test_fast_camera_profile_explicitly_selects_color_only_mode():
    config = (PACKAGE / "config" / "mvs_rgb_fast.yaml").read_text()
    assert "rgbd_enabled: true" in config
    assert 'rgbd_capture_strategy: "color_only"' in config
    assert 'image_mode: "Color"' in config
