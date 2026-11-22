#!/usr/bin/env python3
"""Stop manual OmniFleet MOLA/Nav2 trees; preserve systemd services."""
import os
from pathlib import Path
import signal
import sys
import time


def snapshot():
    result = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            args = (entry / 'cmdline').read_bytes().decode(errors='replace').split('\0')
            stat = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            cgroup = (entry / 'cgroup').read_text()
            protected = any(part.endswith('.service') and not part.startswith('user@')
                            for part in cgroup.replace('\n', '/').split('/'))
            result[int(entry.name)] = (int(stat[1]), stat[19], stat[0], args, protected)
        except (OSError, ValueError, IndexError):
            continue
    return result


def application(args):
    names = [Path(arg).name for arg in args[:3]]
    if 'ros2' in names and 'launch' in args:
        i = args.index('launch')
        return i + 1 < len(args) and args[i + 1] in {
            'omnifleet_t2_mola_experiments', 'omnifleet_planner',
            'mola_lidar_odometry', 'nav2_bringup',
        }
    if args and args[0].startswith('/opt/ros/humble/lib/nav2_'):
        return True
    if args and args[0].startswith('/home/iecme/omnifleet_ws/mola_3_2_ws/') and names[0] == 'mola-cli':
        return True
    if 'omnifleet_t2_experiment_imu_adapter' in ' '.join(args) and names[0] == 'airy_imu_adapter_node':
        return True
    return any(name in {'base_link_rslidar_tf.py', 'fresh_pointcloud_filter.py'} for name in names[:2])


processes = snapshot()
targets = {pid for pid, item in processes.items()
           if not item[4] and application(item[3]) and pid != os.getpid()}
while True:
    children = {pid for pid, item in processes.items()
                if item[0] in targets and not item[4] and pid != os.getpid()}
    if children <= targets:
        break
    targets |= children

for pid in sorted(targets):
    print(f"应用进程 {pid}: {' '.join(processes[pid][3]).strip()}", flush=True)
if '--dry-run' in sys.argv:
    print(f'预览：共 {len(targets)} 个应用进程；所有 systemd 服务均排除。')
    sys.exit(0)


def alive():
    current = snapshot()
    return {pid for pid in targets if pid in current
            and current[pid][1] == processes[pid][1]
            and current[pid][2] != 'Z' and not current[pid][4]}


for sig, grace in [(signal.SIGINT, 8), (signal.SIGTERM, 3), (signal.SIGKILL, 2)]:
    pending = alive()
    if not pending:
        break
    for pid in pending:
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline and alive():
        time.sleep(0.2)
remaining = alive()
print(f'仍存活的应用进程：{sorted(remaining)}' if remaining else
      '应用层节点已清除；雷达、底盘、相机、描述/静态 TF、Foxglove、航点和永久参数服务保持原状态。', flush=True)
sys.exit(1 if remaining else 0)
