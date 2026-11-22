#!/usr/bin/env python3
"""Set the verified CPU policy on one critical thread in this service cgroup."""
import os
import sys
import time
from pathlib import Path


service, name, priority, cpus = sys.argv[1:]
cpus = {int(cpu) for cpu in cpus.split(',')}
priority = int(priority)
group = Path('/sys/fs/cgroup/system.slice') / (service + '.service') / 'cgroup.threads'
is_scan = name == 'worker_lidar[0]'
deadline = time.monotonic() + (35 if is_scan else 15)

while time.monotonic() < deadline:
    try:
        tids = group.read_text().split()
    except OSError:
        tids = []
    matches = []
    for tid in tids:
        task = Path('/proc') / tid
        try:
            if (task / 'comm').read_text().strip() != name:
                continue
            if not is_scan and not any(
                row == 'Tgid:\t' + tid for row in (task / 'status').read_text().splitlines()
            ):
                continue
            matches.append(int(tid))
        except OSError:
            continue
    if matches and (is_scan or len(matches) == 1):
        scheduled = False
        for tid in matches:
            try:
                old_cpus = os.sched_getaffinity(tid)
                os.sched_setaffinity(tid, cpus)
                os.sched_setscheduler(tid, os.SCHED_RR, os.sched_param(priority))
            except ProcessLookupError:
                continue
            except PermissionError as error:
                os.sched_setaffinity(tid, old_cpus)
                print(f'{service}: default scheduling retained: {error}', file=sys.stderr)
                sys.exit(0)
            print(f'{service}: {name} TID {tid} RR {priority}, CPUs {sorted(cpus)}', flush=True)
            scheduled = True
        if scheduled:
            break
    time.sleep(.2)
else:
    print(f'{service}: {name} did not appear; default scheduling retained', file=sys.stderr)
