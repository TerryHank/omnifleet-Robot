import ast
from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]


def test_fast_livo_uses_mola_grid_with_visual_fusion_disabled():
    source = (ROOT / 'launch/fast_livo2_airy.launch.py').read_text()
    ast.parse(source)
    assert "package='omnifleet_mola_grid'" in source
    assert "'/fast_livo2'" in source
    params = yaml.safe_load((ROOT / 'config/fast_livo2_airy_lio.yaml').read_text())['/**']['ros__parameters']
    assert params['common']['img_en'] == 0
    assert params['preprocess']['lidar_type'] == 7
    assert params['pcd_save']['pcd_save_en'] is False
    assert params['uav']['gravity_align_en'] is True


def test_rtabmap_uses_native_nodes_and_grid_without_production_tf_or_database_deletion():
    source = (ROOT / 'launch/rtabmap_airy.launch.py').read_text()
    ast.parse(source)
    assert "get_package_share_directory('omnifleet_bringup')" in source
    assert 'mola' not in source
    assert "default_value='rtabmap_trial'" in source
    assert "'-d'" not in source
    native = (ROOT.parents[1] / 'system/omnifleet_bringup/launch/rtabmap_lidar_grid.launch.py').read_text()
    ast.parse(native)
    assert "package='rtabmap_odom'" in native and "package='rtabmap_slam'" in native
    assert "'publish_tf':False" in native
    assert "'Grid/Sensor':'0'" in native and "'Grid/3D':'false'" in native
