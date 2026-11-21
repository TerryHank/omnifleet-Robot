from pathlib import Path

import yaml


PACKAGE_ROOT = Path(__file__).parents[1]


def test_mv_dt01snu_rgbd_configuration_contract():
    config = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "mv_dt01snu_rgbd.yaml").read_text(
            encoding="utf-8"
        )
    )
    params = config["mvs_camera_node"]["ros__parameters"]

    assert params["serial_number"] == "DB0993529"
    assert params["camera_working_mode"] == "DepthMode"
    assert params["rgbd_capture_strategy"] == "batched"
    assert params["color_frames_per_cycle"] == 1
    assert params["depth_frames_per_cycle"] == 1
    assert params["color_image_mode"] == "Color"
    assert params["depth_image_mode"] == "Depth"
    assert params["color_exposure_mode"] == "DynamicMode"
    assert params["rgbd_align_coord"] == "TransformDepthToRGBCoordinate"
    assert params["depth_scale"] == 0.001
    assert params["depth_min"] == 0.2
    assert params["depth_max"] == 3.5
    assert params["color_frame_id"] == "camera_color_optical_frame"
    assert params["depth_frame_id"] == "camera_color_optical_frame"
    assert params["color_image_topic"] == "/tof/color/image_raw"
    assert (
        params["depth_image_topic"]
        == "/tof/aligned_depth_to_color/image_raw"
    )
    assert params["pointcloud_topic"] == "/tof/points"
    assert params["colorized_pointcloud_topic"] == "/tof/points_colorized"
    assert params["rgbd_max_pair_delta_ms"] == 750
    assert params["camera_fx"] > 0.0
    assert params["camera_fy"] > 0.0


def test_rgbd_launch_uses_the_rgbd_configuration():
    launch_source = (
        PACKAGE_ROOT / "launch" / "mvs_rgbd.launch.py"
    ).read_text(encoding="utf-8")

    assert "mv_dt01snu_rgbd.yaml" in launch_source
    assert 'executable="mvs_camera_node"' in launch_source
    assert "SetEnvironmentVariable" not in launch_source
    assert 'SetEnvironmentVariable("LD_LIBRARY_PATH"' not in launch_source
    assert "additional_env=" in launch_source


def test_camera_launch_does_not_leak_vendor_libraries_to_other_nodes():
    launch_source = (
        PACKAGE_ROOT / "launch" / "mvs_camera.launch.py"
    ).read_text(encoding="utf-8")

    assert "SetEnvironmentVariable" not in launch_source
    assert 'SetEnvironmentVariable("LD_LIBRARY_PATH"' not in launch_source
    assert "additional_env=" in launch_source


def test_rgbd_driver_publishes_compact_millimeter_depth():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    assert "TYPE_16UC1" in source
    assert "TYPE_32FC1" not in source


def test_mv_dt01snu_color_exposure_mode_is_applied_explicitly():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    assert '"color_exposure_mode", ""' in source
    assert 'log_enum_entries("ColorExposureModeSelector")' in source
    assert (
        'set_enum_by_string("ColorExposureModeSelector", '
        "color_exposure_mode_, true)"
    ) in source


def test_rgbd_pointcloud_restores_organized_dimensions_after_resize():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    resize = source.index("modifier.resize(points.size());")
    assert source.index("cloud.height = height;", resize) > resize
    assert source.index("cloud.width = width;", resize) > resize
    assert source.index(
        "cloud.row_step = cloud.point_step * cloud.width;", resize
    ) > resize


def test_geometry_and_colorized_clouds_are_separate():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    assert '"colorized_pointcloud_topic", "/tof/points_colorized"' in source
    assert "color_pair_valid &&" in source
    assert "colorized_pointcloud_pub_" in source
    assert "point.r = 0U;" in source
    assert "color_pair_available_ = false;" in source
    assert "intrinsics, color_pair_valid);" in source


def test_capture_threads_do_not_publish_after_ros_shutdown():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    alternating_guard = (
        "if (!rclcpp::ok() || !running_.load()) {\n"
        "        continue;\n"
        "      }\n"
        "      publish_alternating_rgbd_pair"
    )
    continuous_guard = (
        "if (rclcpp::ok() && running_.load()) {\n"
        "          publish_frame(frame);\n"
        "        }"
    )
    assert alternating_guard in source
    assert continuous_guard in source
    assert source.count(
        "if (!rclcpp::ok() || !running_.load()) {\n"
        "          MV_CC_FreeImageBuffer(handle_, &frame);\n"
        "          break;\n"
        "        }"
    ) >= 2


def test_cleanup_is_idempotent_and_releases_worker_before_sdk():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    cleanup = source[source.index("  void cleanup()") :]
    assert "cleanup_started_.exchange(true)" in cleanup
    assert cleanup.index("worker_.join();") < cleanup.index("MV_CC_CloseDevice")
    assert cleanup.index("MV_CC_CloseDevice") < cleanup.index("MV_CC_DestroyHandle")
    assert cleanup.index("MV_CC_DestroyHandle") < cleanup.index("MV_CC_Finalize")


def test_jetson_state_is_explicitly_released_without_static_destructor_race():
    vpi = (PACKAGE_ROOT / "src" / "rgbd_vpi.cpp").read_text(encoding="utf-8")
    cuda = (PACKAGE_ROOT / "src" / "rgbd_cuda.cu").read_text(encoding="utf-8")

    assert "static VpiState * instance = new VpiState();" in vpi
    assert "static CudaBuffers * instance = new CudaBuffers();" in cuda
    assert "shutdown_vpi_vic();" in (
        PACKAGE_ROOT / "src" / "mvs_camera_node.cpp"
    ).read_text(encoding="utf-8")
    assert "shutdown_cuda_rgbd();" in (
        PACKAGE_ROOT / "src" / "mvs_camera_node.cpp"
    ).read_text(encoding="utf-8")


def test_main_does_not_shutdown_an_already_stopped_ros_context():
    source = (PACKAGE_ROOT / "src" / "mvs_camera_node.cpp").read_text(
        encoding="utf-8"
    )

    main = source[source.index("int main(int argc") :]
    assert main.count("if (rclcpp::ok())") == 2
    assert main.count("rclcpp::shutdown();") == 2
