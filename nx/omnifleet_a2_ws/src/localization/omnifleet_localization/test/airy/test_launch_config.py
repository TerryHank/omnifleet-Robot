import ast
import math
from pathlib import Path

import pytest
import yaml


PACKAGE_ROOT = Path(__file__).parents[2]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[1]


def _rpy_matrix(roll, pitch, yaw):
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _determinant(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def test_airy_config_matches_the_robot_network_contract():
    config = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "airy" / "airy.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert config["common"] == {
        "msg_source": 1,
        "send_packet_ros": False,
        "send_point_cloud_ros": True,
    }
    lidar = config["lidar"][0]
    assert lidar["driver"]["lidar_type"] == "RSAIRY"
    assert lidar["driver"]["msop_port"] == 6699
    assert lidar["driver"]["difop_port"] == 7788
    assert lidar["driver"]["imu_port"] == 6688
    assert lidar["driver"]["socket_recv_buf"] == 10485760
    assert lidar["driver"]["use_lidar_clock"] is False
    assert lidar["ros"]["ros_frame_id"] == "rslidar"
    assert lidar["ros"]["ros_send_point_cloud_topic"] == "/rslidar_points"
    assert lidar["ros"]["ros_send_imu_data_topic"] == "/rslidar_imu_data"


def test_airy_launch_starts_only_the_driver_and_static_extrinsic():
    launch_path = PACKAGE_ROOT / "launch" / "airy_gateway.launch.py"
    source = launch_path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(launch_path))
    assert 'package="rslidar_sdk"' in source
    assert 'executable="rslidar_sdk_node"' in source
    assert 'name="robosense_airy_driver"' not in source
    assert '("param_handle:__node", "robosense_airy_driver")' in source
    assert '"base_to_airy"' in source
    assert "rviz" not in source.lower()


def test_airy_extrinsic_uses_ros_rep103_axes():
    description_root = WORKSPACE_ROOT / "vehicle" / "omnifleet_description"
    config = yaml.safe_load(
        (description_root / "config" / "extrinsics.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert config["frame_convention"]["rslidar"] == (
        "ros_rep103__x_forward_y_left_z_up"
    )
    translation = config["base_to_airy"]["translation_m"]
    assert translation == pytest.approx([-0.041, 0.0, 0.15])
    roll, pitch, yaw = config["base_to_airy"]["rotation_rpy_rad"]
    assert roll == pytest.approx(0.0, abs=1.0e-12)
    assert pitch == pytest.approx(0.0, abs=1.0e-12)
    assert yaw == pytest.approx(0.0, abs=1.0e-12)
    rotation = _rpy_matrix(roll, pitch, yaw)
    assert _determinant(rotation) == pytest.approx(1.0, abs=1.0e-12)
    assert rotation[2][2] == pytest.approx(1.0, abs=1.0e-12)
