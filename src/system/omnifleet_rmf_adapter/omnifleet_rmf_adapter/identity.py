"""Authoritative public vehicle IDs and real ROS namespace assignments."""
import json
from pathlib import Path
import re


class FleetIdentities:
    def __init__(self, config, path):
        self.config, self.path = config, Path(path)
        self.assignments = config['central']['assignments']
        self.revision = config['central'].get('identity_revision', 0)
        for robot, assignment in self.assignments.items():
            if assignment['namespace'] != '/' + self.target(robot, assignment['robot_name']):
                raise ValueError('调度 ID 必须与实际 namespace 前缀一致')

    def target(self, connection, prefix):
        if connection not in self.assignments:
            raise ValueError('接入车辆不存在')
        if not isinstance(prefix, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}', prefix):
            raise ValueError('前缀必须以英文字母开头，只能包含英文字母、数字和下划线，最多 40 字符')
        if prefix in {'fleet', 'omnifleet', 'map', 'tf', 'tf_static'}:
            raise ValueError('该前缀由系统保留')
        if any(robot != connection and a['robot_name'] == prefix for robot, a in self.assignments.items()):
            raise ValueError('该前缀已被其他车辆使用')
        return prefix

    def command(self, packet):
        if packet.get('identity_revision', 0) != self.revision:
            raise ValueError('车辆 ID 已更新，请刷新调度状态后重试')
        result = dict(packet)
        lookup = {a['robot_name']: robot for robot, a in self.assignments.items()}
        if 'robot_id' in result:
            if result['robot_id'] not in lookup:
                raise ValueError('调度 ID 不存在，请使用当前已分配的前缀')
            result['robot_id'] = lookup[result['robot_id']]
        if 'order' in result:
            if not isinstance(result['order'], list) or any(not isinstance(r, str) or r not in lookup for r in result['order']):
                raise ValueError('跟随列表包含未分配的调度 ID')
            result['order'] = [lookup[r] for r in result['order']]
        return result

    def commit(self, connection, prefix):
        prefix = self.target(connection, prefix)
        stored = json.loads(self.path.read_text(encoding='utf-8'))
        if stored['central'].get('identity_revision', 0) != self.revision or any(
            (a['robot_name'], a['namespace']) != (stored['central']['assignments'][r]['robot_name'], stored['central']['assignments'][r]['namespace'])
            for r, a in self.assignments.items()
        ):
            raise RuntimeError('身份配置已被其他操作修改，请重新加载调度端')
        stored['central']['assignments'][connection].update(robot_name=prefix, namespace='/' + prefix)
        stored['central']['identity_revision'] = self.revision + 1
        temporary = self.path.with_suffix('.json.tmp')
        try:
            temporary.write_text(json.dumps(stored, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            temporary.replace(self.path)
        except OSError as error:
            raise RuntimeError('前缀保存失败：' + str(error)) from error
        self.revision += 1
        self.assignments[connection].update(robot_name=prefix, namespace='/' + prefix)
        self.config['central']['identity_revision'] = self.revision
