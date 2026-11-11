from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "robot_doctor"
loader = SourceFileLoader("robot_doctor", str(SCRIPT))
spec = spec_from_loader(loader.name, loader)
doctor = module_from_spec(spec)
loader.exec_module(doctor)


def test_cli_defaults_match_production_modes():
    args = doctor.parse_args([])
    assert args.scope == "base"
    assert args.terrain_mode == "2d"
    assert args.local_obstacle_mode == "obstacle"
    assert args.timeout == 15.0


def test_all_cold_switch_combinations_are_accepted():
    for terrain in ("2d", "2_5d"):
        for local in ("obstacle", "voxel", "stvl"):
            args = doctor.parse_args(
                ["--scope", "nav", "--terrain-mode", terrain,
                 "--local-obstacle-mode", local]
            )
            assert args.terrain_mode == terrain
            assert args.local_obstacle_mode == local


def test_doctor_is_read_only():
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden = (
        "ros2 topic pub",
        "systemctl start",
        "systemctl stop",
        "systemctl restart",
        "ros2 lifecycle set",
        "ros2 action send_goal",
    )
    assert not any(token in source for token in forbidden)


def test_real_production_contract_is_encoded():
    source = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "omnifleet-a2-chassis.service",
        "omnifleet-a2-airy.service",
        "/rslidar_points",
        "/rslidar_imu_data",
        "/glim_ros/points_corrected",
        "/glim_ros/map",
        "/omnifleet_a2/terrain/grid_map",
        '"/cmd_vel"',
        "omnifleet_a2_driver",
    ):
        assert token in source
    assert "velocity_smoother" not in source
    assert "collision_monitor" not in source
    assert "omnifleet_command_mux" not in source
    assert '["static_layer", "obstacle_layer", "inflation_layer"]' in source
    assert '["static_layer", "traversability_layer", "inflation_layer"]' in source
