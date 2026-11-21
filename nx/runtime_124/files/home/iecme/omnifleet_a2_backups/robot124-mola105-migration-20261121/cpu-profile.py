#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

unit, profile = sys.argv[1:]
group = Path('/sys/fs/cgroup/system.slice') / (unit+'.service') / 'cgroup.threads'
policy = {'mola': -2, 'navigation': -3, 'airy': -10, 'chassis': None, 'display': 4}
allowed = set(os.sched_getaffinity(0))
until = time.monotonic()+12

def configure(tids):
    workers = []
    matched = set()
    for tid in tids:
        p = Path('/proc') / str(tid)
        try:
            name=(p/'comm').read_text().strip()
            args=(p/'cmdline').read_bytes().split(b'\0')
            if policy[profile] is not None and os.sched_getscheduler(tid)==os.SCHED_OTHER:
                os.setpriority(os.PRIO_PROCESS,tid,policy[profile])
            if profile=='mola' and name=='worker_lidar[0]':
                workers.append(tid)
            cpus=None
            if profile=='mola' and name in ('mola_graph','mola_lc'):
                cpus={6,7}
            elif profile=='navigation' and args[0].endswith(b'/controller_server'):
                cpus={3,4}
                matched.add("controller")
            elif profile=='navigation' and args[0].endswith(b'/planner_server'):
                cpus={4,6,7}
                matched.add("planner")
            elif profile=='chassis' and any(a.endswith(b'/ackermann_driver') for a in args[:2]):
                status=(p/'status').read_text().splitlines()
                if any(row==f'Tgid:\t{tid}' for row in status):
                    cpus={5}
                    matched.add("driver")
            if cpus is not None and cpus&allowed:
                os.sched_setaffinity(tid,cpus&allowed)
        except (FileNotFoundError,ProcessLookupError,PermissionError):
            continue
    if profile=='navigation':
        return matched=={'controller','planner'}
    if profile=='chassis':
        return 'driver' in matched
    if profile!='mola':
        return True
    rt=[]
    for tid in workers:
        try:
            if os.sched_getscheduler(tid) in (os.SCHED_RR,os.SCHED_FIFO):
                rt.append(tid)
        except ProcessLookupError:
            continue
    # The donor has one lidar worker. Keep any already-real-time workers
    # off USB CPU0 on older builds without promoting their extra pools.
    targets=rt or (workers if len(workers)==1 else [])
    for tid in targets:
        try:
            os.sched_setaffinity(tid,{1,2}&allowed)
            if not rt:
                os.sched_setscheduler(tid,os.SCHED_RR,os.sched_param(1))
            print(f'{unit}: lidar TID {tid} scheduler {os.sched_getscheduler(tid)} CPUs {sorted(os.sched_getaffinity(tid))}',flush=True)
        except (ProcessLookupError,PermissionError):
            continue
    return bool(workers)

while time.monotonic()<until:
    try:
        tids=[int(line) for line in group.read_text().splitlines()]
    except FileNotFoundError:
        tids=[]
    if tids and configure(tids):
        break
    time.sleep(.2)
