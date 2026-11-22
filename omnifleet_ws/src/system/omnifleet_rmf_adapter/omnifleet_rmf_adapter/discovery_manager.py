"""Own expiring LAN-discovered connections, one ROS process per verified domain."""
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import time

from .discovery import Registry, PORT
from fleet_beacon import settings


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(path)


class DiscoveryManager:
    def __init__(self, config, data, runner):
        self.config, self.data, self.runner = Path(config), Path(data), Path(runner)
        self.directory = self.data/'run/discovery'
        self.directory.mkdir(parents=True,exist_ok=True)
        self.registry, self.children = Registry(), {}

    def stop(self, robot):
        child, signature = self.children.pop(robot)
        if child.poll() is None:
            child.send_signal(signal.SIGINT)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill();child.wait()
        if not signature.get('onboard_local'):
            subprocess.run(['sudo', '-n', 'systemctl', 'stop',
                            f'omnifleet-onboard-peer@{robot}.service'], check=False)
        (self.directory/(robot+'.router.yaml')).unlink(missing_ok=True)
        (self.directory/(robot+'.json')).unlink(missing_ok=True)
        (self.directory/(robot+'.fastdds.xml')).unlink(missing_ok=True)
        print('disconnected',robot,flush=True)

    def tick(self, now):
        profiles, conflicts = self.registry.active(now)
        try:
            local = settings()
        except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError):
            local = None
        if local:
            name = local['robot_id']
            peer = profiles.get(name)
            if peer and peer['instance_id'] != local['instance_id']:
                conflicts.append(name)
            profiles[name] = {**local, 'host':'127.0.0.1', 'onboard_local':True,
                              'local_namespace':local['observed_namespace']}
        configured = json.loads(self.config.read_text())
        central_domain = configured['central']['domain_id']
        for robot in list(profiles):
            if profiles[robot]['domain_id'] == central_domain:
                conflicts.append(robot);del profiles[robot]
        save(self.data/'discovery.json',{'schema':1,'updated_monotonic':now,'robots':profiles,'conflicts':conflicts})
        for robot in list(self.children):
            if profiles.get(robot) != self.children[robot][1] or not configured['robots'].get(robot,{}).get('enabled',False):
                self.stop(robot)
        for robot, profile in profiles.items():
            if not configured['robots'].get(robot,{}).get('enabled',False):
                continue  # Central executor enrolls new identities before launching a ROS client.
            if robot in self.children:
                if self.children[robot][0].poll() is None:
                    continue
                self.stop(robot)
            session = self.directory/(robot+'.fastdds.xml')
            shutil.copyfile(self.config.parent/'fastdds-client.xml', session)
            if not profile.get('onboard_local'):
                router = json.loads((self.config.parent/'fastdds-router-template.yaml').read_text())
                router['participants'][0]['domain'] = profile['domain_id']
                router['participants'][1]['connection-addresses'][0].update(
                    ip=profile['host'], port=profile['discovery_port'])
                router['xml']['raw'] = (router['xml']['raw']
                    .replace('__DDS_HOST__', profile['host'])
                    .replace('__DDS_BULK_PORT__', str(profile['discovery_port'] + 1)))
                router_file = self.directory/(robot+'.router.yaml')
                save(router_file, router)
                result = subprocess.run(['sudo', '-n', 'systemctl', 'start',
                                         f'omnifleet-onboard-peer@{robot}.service'], check=False)
                if result.returncode:
                    router_file.unlink(missing_ok=True)
                    session.unlink(missing_ok=True)
                    continue
            runtime = self.directory/(robot+'.json')
            save(runtime,{**profile,'fastdds_config':str(session),
                          'control_topic':'/navigation/fleet/local_status','compressed_maps':False})
            env={**os.environ,'OMNIFLEET_DISCOVERY_PROFILE':str(runtime)}
            child=subprocess.Popen(['/bin/bash',str(self.runner),robot],env=env)
            self.children[robot]=(child,profile)
            print('discovered',robot,'domain',profile['domain_id'],'endpoint',profile['host'],flush=True)

    def run(self):
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as receiver:
            receiver.bind(('0.0.0.0',PORT));receiver.settimeout(.2)
            next_tick=0.
            while True:
                try:
                    packet, address = receiver.recvfrom(8192)
                    self.registry.observe(json.loads(packet), address[0], time.monotonic())
                except (socket.timeout,ValueError,KeyError,TypeError):
                    pass
                if time.monotonic() >= next_tick:
                    self.tick(time.monotonic());next_tick=time.monotonic()+1


def main():
    data=Path(os.environ['OMNIFLEET_DATA'])
    manager=DiscoveryManager(os.environ['OMNIFLEET_CONFIG'],data,
        Path(os.environ['OMNIFLEET_CONFIG']).resolve().parents[1]/'scripts/run.bash')
    def interrupted(*args):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,interrupted)
    try:
        manager.run()
    except KeyboardInterrupt:
        pass
    finally:
        for robot in list(manager.children):
            manager.stop(robot)
        save(data/'discovery.json',{'schema':1,'updated_monotonic':time.monotonic(),'robots':{},'conflicts':[]})


if __name__ == '__main__':
    main()
