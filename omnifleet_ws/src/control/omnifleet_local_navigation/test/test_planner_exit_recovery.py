import array
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from omnifleet_local_navigation.clearance_recovery import (
    ClearanceEscape, global_recovery_checks, recovery_config,
)


def objectify(value):
    return NS(**{k: objectify(v) for k, v in value.items()}) if isinstance(value, dict) else value


def test_exit_uses_initial_overlap_only_and_reads_live_global_grid():
    def grid():
        return objectify(dict(data=array.array('b', [0]) * 1600, info=dict(
            width=40, height=40, resolution=.05, origin=dict(
                position=dict(x=-1., y=-1.), orientation=dict(x=0., y=0., z=0., w=1.)))))

    pose = [0., 0., 0.]
    config = dict(length=.5, width=.37, padding=.05)
    current = grid()
    # Lethal cell at the front edge of the starting footprint.
    current.data[20 * 40 + 24] = 100
    start_blocked, path_blocked = global_recovery_checks(lambda: current, pose, config, {})
    assert start_blocked(pose)
    assert not path_blocked(pose)
    assert path_blocked([.02, 0., 0.])

    escape = ClearanceEscape(pose, [], [], config, .01, 0., 'epoch',
                             start_blocked=start_blocked, path_blocked=path_blocked)
    assert escape.direction == -1
    assert not start_blocked(escape.path[-1])
    assert escape.certified(pose, [-.1, 0.], [], [])
    assert escape.command(0., pose, [], [], [0., 0.], True, 'epoch')[0] < 0.

    # A new global-only cell behind the robot appears mid-recovery.
    current = grid()
    current.data[20 * 40 + 24] = 100
    current.data[20 * 40 + 13] = 100
    assert not path_blocked(pose)
    assert not escape.certified(pose, [-.1, 0.], [], [])
    assert escape.command(.1, pose, [], [], [0., 0.], True, 'epoch') == [0., 0.]


def test_recorded_global_local_map_mismatch():
    scenes = json.loads((Path(__file__).parent / 'data/recorded-global-exit.json').read_text())
    rejected = completed = 0
    for scene in scenes:
        grid = objectify(scene['global_grid'])
        grid.data = array.array('b', grid.data)
        pose, config = scene['pose'], scene['config']
        start_blocked, path_blocked = global_recovery_checks(lambda: grid, pose, config, {})
        if not start_blocked(pose):
            continue
        args = (pose, scene['obstacles'], scene['unknown'],
                recovery_config(config, scene['local_parameters']), scene['resolution'], 0., 'epoch')
        if scene['time'] == 1792635990.8:
            # The earlier endpoint-only check found a path that deepened overlap.
            old = ClearanceEscape(*args, start_blocked=start_blocked)
            assert any(path_blocked(p) for p in old.path)
            with pytest.raises(ValueError, match='不加深现有重叠'):
                ClearanceEscape(*args, start_blocked=start_blocked, path_blocked=path_blocked)
            rejected += 1
            continue
        escape = ClearanceEscape(*args, start_blocked=start_blocked, path_blocked=path_blocked)
        assert all(not path_blocked(p) for p in escape.path)
        assert not start_blocked(escape.path[-1])
        velocity = [escape.direction * escape.speed, escape.direction * escape.speed * escape.curvature]
        for i, p in enumerate(escape.path):
            command = escape.command(i * .01 / escape.speed, p, scene['obstacles'], scene['unknown'],
                                     velocity, True, 'epoch')
            assert escape.state != 'failed', escape.reason
        assert escape.state == 'stopping', escape.reason
        assert command == [0., 0.]
        completed += 1
    assert (rejected, completed) == (1, 1)
