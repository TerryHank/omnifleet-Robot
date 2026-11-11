#!/usr/bin/env python3
"""Start Airy after boot clock settling; restart on wall-clock steps.

No ROS timestamps are rewritten. Offline operation is allowed after bounded
initial synchronization wait, then protected by the same step detector.
"""
import os,signal,subprocess,sys,time

class ClockStep:
    def __init__(self, wall, steady):self.offset=wall-steady
    def update(self, wall, steady):
        offset=wall-steady;step=offset-self.offset;self.offset=offset
        return step if abs(step)>.1 else None

def synchronized():
    try:
        p=subprocess.run(['timedatectl','show','-p','NTPSynchronized','--value'],capture_output=True,text=True,timeout=2)
        return p.returncode==0 and p.stdout.strip()=='yes'
    except subprocess.TimeoutExpired:return False

def main():
    command=sys.argv[1:]
    if command and command[0]=='--':command=command[1:]
    if not command:raise ValueError('Missing child command')
    stopped=False
    def stop(*_):
        nonlocal stopped
        stopped=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    begin=time.monotonic();stable=begin;clock=ClockStep(time.time(),begin)
    while not stopped:
        now=time.monotonic()
        if clock.update(time.time(),now) is not None:stable=now
        synced=synchronized()
        if now-stable>=5 and (synced or now-begin>=45) and time.time()>1577836800:
            print('Sensor clock guard: '+('NTP synchronized' if synced else 'offline stable clock; watching for later time steps'),flush=True);break
        time.sleep(.5)
    if stopped:return 0
    child=subprocess.Popen(command,start_new_session=True)
    clock=ClockStep(time.time(),time.monotonic())
    try:
        while not stopped and child.poll() is None:
            step=clock.update(time.time(),time.monotonic())
            if step is not None:
                print(f'Sensor clock guard: host clock stepped {step:+.6f}s; stopping driver so systemd reinitializes the shared sensor epoch',flush=True)
                return 75
            time.sleep(.05)
        return child.returncode if child.returncode is not None else 0
    finally:
        if child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()

if __name__=='__main__':sys.exit(main())
