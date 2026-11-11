import math
from types import SimpleNamespace

import pytest

from omnifleet_localization.occupancy_grid_saver import save_occupancy_grid


def _message(data):
    yaw = 0.5
    return SimpleNamespace(
        info=SimpleNamespace(
            width=2,
            height=2,
            resolution=0.05,
            origin=SimpleNamespace(
                position=SimpleNamespace(x=-1.25, y=2.5),
                orientation=SimpleNamespace(
                    x=0.0,
                    y=0.0,
                    z=math.sin(yaw / 2.0),
                    w=math.cos(yaw / 2.0),
                ),
            ),
        ),
        data=data,
    )


def test_saves_flipped_pgm_and_nav2_yaml(tmp_path):
    pgm_path, yaml_path = save_occupancy_grid(
        _message([0, 100, -1, 50]), tmp_path
    )

    pgm = pgm_path.read_bytes()
    header, pixels = pgm.rsplit(b"\n", 1)
    assert header.endswith(b"2 2\n255")
    assert pixels == bytes([205, 205, 254, 0])

    yaml = yaml_path.read_text(encoding="utf-8")
    assert "image: map.pgm" in yaml
    assert "mode: trinary" in yaml
    assert "resolution: 0.05" in yaml
    assert "origin: [-1.25, 2.5, 0.5]" in yaml
    assert "occupied_thresh: 0.65" in yaml
    assert "free_thresh: 0.25" in yaml


def test_rejects_wrong_cell_count(tmp_path):
    with pytest.raises(ValueError, match="expected 4"):
        save_occupancy_grid(_message([0, 100, -1]), tmp_path)
