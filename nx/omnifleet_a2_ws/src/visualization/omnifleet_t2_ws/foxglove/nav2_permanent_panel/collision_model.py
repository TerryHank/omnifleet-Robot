"""Persist a reversible Nav2 collision model for the next navigation startup."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import yaml


def profile_path(path):
    return path.resolve().parent / 'nav2-collision-body.json'


def model_paths(data):
    paths = []
    for scope in ('local', 'global'):
        root = (scope + '_costmap', scope + '_costmap', 'ros__parameters')
        paths.extend((root + ('footprint',), root + ('robot_radius',),
                      root + ('footprint_padding',), root + ('inflation_layer', 'inflation_radius')))
    for name, settings in data['controller_server']['ros__parameters'].items():
        if not isinstance(settings, dict):
            continue
        for critic in ('CostCritic', 'ObstaclesCritic'):
            if critic in settings.get('critics', []):
                paths.append(('controller_server', 'ros__parameters', name, critic, 'consider_footprint'))
    return paths


def parent_at(data, path):
    for key in path[:-1]:
        data = data[key]
    return data


def point_geometry(data):
    for scope in ('local', 'global'):
        params = data[scope + '_costmap'][scope + '_costmap']['ros__parameters']
        if params.get('footprint', '[]') not in ('', '[]') or params.get('robot_radius', 1) > .01:
            return False
    return True


POINT_VALUES = {'footprint': '[]', 'robot_radius': .01, 'footprint_padding': 0.,
                'inflation_radius': .01, 'consider_footprint': False}


def capture_body(data, path):
    profile = profile_path(Path(path))
    if profile.exists() or point_geometry(data):
        return
    body = [{'path': list(p), 'present': p[-1] in parent_at(data, p),
             'value': copy.deepcopy(parent_at(data, p).get(p[-1]))} for p in model_paths(data)]
    atomic_write(profile, (json.dumps({'version': 1, 'body': body}, ensure_ascii=False, indent=2) + '\n').encode())


def state(path):
    data = yaml.safe_load(Path(path).read_text())
    profile = profile_path(Path(path))
    is_point = all(parent_at(data, p).get(p[-1]) == POINT_VALUES[p[-1]] for p in model_paths(data)
                   if p[-1] != 'inflation_radius' and (p[0] != 'controller_server' or p[2] == 'FollowPathMPPI'))
    mode = 'point' if is_point else 'body'
    if not is_point and profile.exists():
        body = json.loads(profile.read_text())['body']
        matches = all((item['path'][-1] in parent_at(data, item['path'])) == item['present'] and
                      parent_at(data, item['path']).get(item['path'][-1]) == item['value'] for item in body if item['path'][-1] != 'inflation_radius')
        if not matches:
            mode = 'custom'
    return {'mode': mode, 'restore_available': profile.exists(), 'applies_to': 'next_restart'}


def atomic_write(path, content):
    fd, temporary = tempfile.mkstemp(prefix='.collision-model-', dir=path.parent)
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


def save_mode(mode, path, backups, *, navigation_active, state_age, motion_age):
    if mode not in ('body', 'point'):
        raise ValueError('碰撞模型只能选择 body 或 point')
    path = Path(path).resolve(strict=True)
    original = path.read_bytes()
    data = yaml.safe_load(original)
    paths = model_paths(data)
    profile = profile_path(path)
    if mode == 'point':
        if not profile.exists():
            if point_geometry(data):
                raise ValueError('当前已是小半径模型，但缺少原车体备份，不能建立可恢复的切换')
            capture_body(data, path)
        for p in paths:
            parent_at(data, p)[p[-1]] = {'footprint': '[]', 'robot_radius': .01,
                                       'footprint_padding': 0., 'inflation_radius': .01,
                                       'consider_footprint': False}[p[-1]]
    elif profile.exists():
        saved = json.loads(profile.read_text())
        if saved.get('version') != 1 or {tuple(x['path']) for x in saved['body']} != set(paths):
            raise ValueError('车体备份与当前控制器配置不匹配，请检查配置后恢复')
        for item in saved['body']:
            p = tuple(item['path'])
            if item['present']:
                parent_at(data, p)[p[-1]] = item['value']
            else:
                parent_at(data, p).pop(p[-1], None)
    elif point_geometry(data):
        raise ValueError('缺少原车体备份，不能恢复实际车体模型')
    new = original if yaml.safe_load(original) == data else yaml.safe_dump(data, allow_unicode=True, sort_keys=False).encode()
    backup = None
    if new != original:
        backups = Path(backups)
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / ('nav2-collision-model.' + str(time.time_ns()) + '.yaml')
        backup.write_bytes(original)
        if path.read_bytes() != original:
            raise ValueError('配置已被其他操作修改，请重新读取后再切换')
        atomic_write(path, new)
    if path.read_bytes() != new:
        raise OSError('碰撞模型写入后回读不一致')
    return {'collision_model': state(path), 'path': str(path),
            'backup': str(backup) if backup else None, 'sha256': hashlib.sha256(new).hexdigest(),
            'runtime_confirmed': False, 'applies_to': 'next_restart',
            'message': '已永久保存；需点击“重启导航栈”后生效，当前运行模型尚未切换'}
