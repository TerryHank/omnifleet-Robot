"""Persistent display names shared by the operator UI and map labels."""
import json
from pathlib import Path


class RobotNames:
    def __init__(self, config, data):
        self.assignments = config['central']['assignments']
        self.path = Path(data) / 'robot_names.json'
        saved = json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
        self.names = {}
        for robot, name in saved.get('names', {}).items():
            if robot in self.assignments:
                name = self.validate(name)
                if name:
                    self.names[robot] = name
        for robot, assignment in self.assignments.items():
            assignment['display_name'] = self.names.get(robot, self.default(robot))

    @staticmethod
    def default(robot):
        return '车辆 ' + robot.removeprefix('robot_')

    @staticmethod
    def validate(name):
        if not isinstance(name, str):
            raise ValueError('Vehicle name must be text')
        name = name.strip()
        if len(name) > 40 or any(ord(char) < 32 or ord(char) == 127 for char in name):
            raise ValueError('Vehicle name must contain at most 40 characters without control characters')
        return name

    def rename(self, robot, name):
        if robot not in self.assignments:
            raise ValueError('Vehicle is not assigned by the central configuration')
        name = self.validate(name)
        updated = dict(self.names)
        if name:
            updated[robot] = name
        else:
            updated.pop(robot, None)
        temporary = self.path.with_suffix('.json.tmp')
        try:
            temporary.write_text(json.dumps({'schema': 1, 'names': updated}, ensure_ascii=False) + '\n', encoding='utf-8')
            temporary.replace(self.path)
        except OSError as error:
            raise RuntimeError('Could not save vehicle name: ' + str(error)) from error
        self.names = updated
        label = name or self.default(robot)
        self.assignments[robot]['display_name'] = label
        return {'phase': 'renamed', 'robot_id': robot, 'display_name': label}

    def snapshot(self):
        return dict(self.names)
