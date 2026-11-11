"""One verified height change across MOLA and both independent Nav2 point filters."""
import json
import math
import os
from pathlib import Path
import tempfile
import time
import yaml

SCOPES = ('local', 'global')
NAV_KEYS = ('obstacle_layer.min_obstacle_height', 'obstacle_layer.max_obstacle_height',
            'obstacle_layer.lidar.min_obstacle_height', 'obstacle_layer.lidar.max_obstacle_height')
CAPABILITY = 'obstacle_layer.height_filter_revision'


def apply_linked(values, read_mola, write_mola, read_nav, write_nav, clear_nav, persist):
    low, high = values['slice_z_min'], values['slice_z_max']
    if not all(math.isfinite(v) and -10 <= v <= 10 for v in (low, high)) or low >= high:
        raise ValueError('高度上下限必须是有限数值，且下限小于上限')
    desired = dict(zip(NAV_KEYS, (low, high, low, high)))
    old_mola = read_mola()
    old_nav = {scope: read_nav(scope) for scope in SCOPES}
    if not all(k in old_mola for k in values):
        raise ValueError('MOLA 未提供高度热修改接口')
    for scope, actual in old_nav.items():
        if actual.get(CAPABILITY) != 1:
            raise ValueError(f'{scope} 代价地图尚未加载高度实时过滤修复；本次未修改参数')
        if not all(k in actual for k in NAV_KEYS):
            raise ValueError(f'{scope} 代价地图缺少高度参数；本次未修改参数')
    changed = []
    try:
        changed.append('MOLA')
        write_mola(values)
        for scope in SCOPES:
            changed.append(scope)
            write_nav(scope, desired)
        actual_mola = read_mola()
        if any(abs(actual_mola[k] - v) > 1e-8 for k, v in values.items()):
            raise ValueError('MOLA 高度回读不一致')
        for scope in SCOPES:
            actual = read_nav(scope)
            if any(abs(actual[k] - v) > 1e-8 for k, v in desired.items()):
                raise ValueError(f'{scope} 代价地图高度回读不一致')
        for scope in SCOPES:
            clear_nav(scope)  # Clear only costmaps; never invoke MOLA reset_state.
        persist(values)
    except Exception as error:
        failures = []
        for target in reversed(changed):
            try:
                if target == 'MOLA':
                    write_mola({k: old_mola[k] for k in values})
                    actual = read_mola()
                    if any(abs(actual[k] - old_mola[k]) > 1e-8 for k in values):
                        raise RuntimeError('回退后高度回读不一致')
                else:
                    write_nav(target, {k: old_nav[target][k] for k in NAV_KEYS})
                    actual = read_nav(target)
                    if any(abs(actual[k] - old_nav[target][k]) > 1e-8 for k in NAV_KEYS):
                        raise RuntimeError('回退后高度回读不一致')
                    clear_nav(target)
            except Exception as rollback_error:
                failures.append(target + ': ' + str(rollback_error))
        suffix = '；回退未完全成功：' + '；'.join(failures) if failures else '；已回退运行参数，未保存新值'
        raise RuntimeError(str(error) + suffix) from error
    return {'MOLA': '高度已回读确认', 'local': '过滤高度已回读，旧代价已清理并收到新地图',
            'global': '过滤高度已回读，旧代价已清理并收到新地图'}


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.height-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def persist_heights(values, yaml_file, height_file, backups):
    target = Path(yaml_file).resolve(strict=True)
    height_file = Path(height_file)
    old_yaml = target.read_bytes()
    old_height = height_file.read_bytes() if height_file.exists() else None
    data = yaml.safe_load(old_yaml)
    for scope in SCOPES:
        layer = data[scope + '_costmap'][scope + '_costmap']['ros__parameters']['obstacle_layer']
        for target_layer in (layer, layer['lidar']):
            target_layer['min_obstacle_height'] = values['slice_z_min']
            target_layer['max_obstacle_height'] = values['slice_z_max']
    folder = Path(backups) / ('linked-heights-' + str(time.time_ns()))
    folder.mkdir(parents=True)
    (folder / 'nav2.yaml').write_bytes(old_yaml)
    if old_height is not None:
        (folder / 'map-height.json').write_bytes(old_height)
    new_yaml = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).encode()
    new_height = json.dumps(values).encode()
    try:
        atomic_write(target, new_yaml)
        atomic_write(height_file, new_height)
        if target.read_bytes() != new_yaml or height_file.read_bytes() != new_height:
            raise OSError('永久配置回读不一致')
    except Exception:
        atomic_write(target, old_yaml)
        if old_height is not None:
            atomic_write(height_file, old_height)
        elif height_file.exists():
            height_file.unlink()
        raise
