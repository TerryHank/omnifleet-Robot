from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


def test_r2_odometry_uses_configurable_frames_and_does_not_own_tf_by_default():
    source = (PACKAGE / "src" / "base_node_R2.cpp").read_text(encoding="utf-8")

    assert 'declare_parameter<std::string>("odom_frame","odom")' in source
    assert (
        'declare_parameter<std::string>("base_footprint_frame","base_link")'
        in source
    )
    assert 'declare_parameter<bool>("pub_odom_tf",false)' in source
    assert "odom.header.frame_id = odom_frame_" in source
    assert "odom.child_frame_id = base_footprint_frame_" in source
    assert "t.header.frame_id = odom_frame_" in source
    assert "t.child_frame_id = base_footprint_frame_" in source
