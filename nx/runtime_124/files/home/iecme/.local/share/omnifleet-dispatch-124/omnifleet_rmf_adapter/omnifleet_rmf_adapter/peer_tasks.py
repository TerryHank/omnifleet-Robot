"""Exchange task summaries while the originating dispatcher keeps task ownership."""

import json
from pathlib import Path


TOPIC = '/fleet/dispatch_tasks'


def export_tasks(origin, missions, rmf_tasks):
    entries = {}
    for robot, job in missions.get('jobs', {}).items():
        identifier = job.get('id')
        if isinstance(identifier, str) and identifier:
            entries[identifier] = {
                'id': identifier, 'robot_id': robot, 'phase': job.get('phase'),
                'title': job.get('route_name') or job.get('name') or identifier,
            }
    for task in rmf_tasks:
        identifier = task.get('id') or task.get('task_id') or task.get('request_id')
        if isinstance(identifier, str) and identifier:
            entries.setdefault(identifier, {
                'id': identifier, 'robot_id': task.get('robot_id'),
                'phase': task.get('phase') or task.get('status'),
                'title': task.get('name') or task.get('category') or identifier,
            })
    return {'schema': 1, 'dispatcher': origin, 'tasks': list(entries.values())}


def receive_tasks(text, origin):
    value = json.loads(text)
    if not isinstance(value, dict) or value.get('schema') != 1 or value.get('dispatcher') != origin:
        return None
    tasks = value.get('tasks')
    if not isinstance(tasks, list):
        return None
    return [{'id': f"{origin}:{task['id']}", 'source_task_id': task['id'],
             'dispatcher': origin, 'robot_id': task.get('robot_id'),
             'title': task.get('title'), 'phase': task.get('phase')}
            for task in tasks if isinstance(task, dict) and isinstance(task.get('id'), str)]


def store(path, packet):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(packet, ensure_ascii=False))
    temporary.replace(path)
