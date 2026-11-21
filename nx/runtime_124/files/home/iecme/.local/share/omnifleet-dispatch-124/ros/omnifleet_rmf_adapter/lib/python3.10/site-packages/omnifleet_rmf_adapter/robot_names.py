"""Expose the authoritative dispatch name in operator views and map labels."""


class RobotNames:
    def __init__(self, config):
        self.assignments = config['central']['assignments']
        for assignment in self.assignments.values():
            assignment['display_name'] = assignment['robot_name']

    def snapshot(self):
        return {robot: assignment['robot_name'] for robot, assignment in self.assignments.items()}
