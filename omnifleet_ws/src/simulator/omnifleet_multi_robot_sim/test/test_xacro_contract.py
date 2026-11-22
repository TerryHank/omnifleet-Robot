from pathlib import Path
import shutil
import subprocess

import pytest


XACRO = Path(__file__).parents[3] / "vehicle" / "omnifleet_description" / "urdf" / "lunshi_ackermann_lite_gazebo_classic.urdf.xacro"


def test_single_robot_defaults_are_compatible():
    text = XACRO.read_text(encoding="utf-8")
    assert '<xacro:arg name="robot_namespace" default="/" />' in text
    assert '<xacro:arg name="frame_prefix" default="" />' in text
    assert '<xacro:arg name="stable_drive" default="false" />' in text
    assert '<xacro:arg name="odom_topic" default="odom" />' in text


def test_plugin_namespace_and_frames_are_parameterized():
    text = XACRO.read_text(encoding="utf-8")
    assert text.count("<namespace>$(arg robot_namespace)</namespace>") >= 4
    assert "<odometry_frame>$(arg frame_prefix)odom</odometry_frame>" in text
    assert "<robot_base_frame>$(arg frame_prefix)base_link</robot_base_frame>" in text
    assert "<frame_name>$(arg frame_prefix)camera_color_optical_frame</frame_name>" in text


def _expand_xacro(*arguments):
    executable = shutil.which("xacro")
    if executable is None:
        pytest.skip("xacro executable is not installed")
    result = subprocess.run(
        [executable, str(XACRO), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        unavailable_errors = (
            "PackageNotFoundError",
            "No package metadata was found for xacro",
            "ModuleNotFoundError",
            "No module named 'xacro'",
        )
        if any(error in result.stderr for error in unavailable_errors):
            pytest.skip(f"xacro installation is unavailable: {result.stderr.splitlines()[-1]}")
        pytest.fail(f"xacro expansion failed:\n{result.stderr}")
    return result.stdout


def test_xacro_default_expansion_keeps_single_robot_contract():
    expanded = _expand_xacro()
    assert expanded.count("<namespace>/</namespace>") >= 2
    assert "<odometry_frame>odom</odometry_frame>" in expanded
    assert "<robot_base_frame>base_link</robot_base_frame>" in expanded
    assert "<remapping>cmd_vel:=cmd_vel</remapping>" in expanded


def test_xacro_multi_robot_expansion_sets_plugin_namespaces_and_frames():
    expanded = _expand_xacro(
        "robot_namespace:=/robot1",
        "frame_prefix:=robot1/",
        "mapping_sensors:=true",
    )
    assert expanded.count("<namespace>/robot1</namespace>") >= 4
    assert "<odometry_frame>robot1/odom</odometry_frame>" in expanded
    assert "<robot_base_frame>robot1/base_link</robot_base_frame>" in expanded
    assert "<frame_name>robot1/imu_link</frame_name>" in expanded
    assert "<frame_name>robot1/camera_color_optical_frame</frame_name>" in expanded


def test_stable_drive_is_independent_from_mapping_sensors():
    expanded = _expand_xacro("stable_drive:=true", "mapping_sensors:=false")
    assert "<linear_velocity_pid_gain>10 0 0</linear_velocity_pid_gain>" in expanded
    assert "gazebo_ros_imu" not in expanded
