"""Own expiring LAN-discovered connections, one ROS process per verified domain."""
import hmac
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

from .discovery import Registry, RELAY_PORT


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
        (self.directory/(robot+'.json')).unlink(missing_ok=True)
        (self.directory/(robot+'.zenoh.json5')).unlink(missing_ok=True)
        print('disconnected',robot,flush=True)

    def tick(self, now):
        profiles, conflicts = self.registry.active(now)
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
            session = self.directory/(robot+'.zenoh.json5')
            save(session,{'mode':'client','connect':{'endpoints':[f'tcp/{profile["host"]}:{profile["zenoh_port"]}'],
                'timeout_ms':5000,'exit_on_failure':True},'listen':{'endpoints':[]},
                'queries_default_timeout':600000,
                'transport':{'shared_memory':{'enabled':False}},
                'scouting':{'multicast':{'enabled':False},'gossip':{'enabled':False}}})
            runtime = self.directory/(robot+'.json')
            save(runtime,{**profile,'zenoh_config':str(session)})
            env={**os.environ,'OMNIFLEET_DISCOVERY_PROFILE':str(runtime)}
            child=subprocess.Popen(['/bin/bash',str(self.runner),robot],env=env)
            self.children[robot]=(child,profile)
            print('discovered',robot,'domain',profile['domain_id'],'endpoint',profile['host'],flush=True)

    def run(self, token):
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as receiver:
            receiver.bind(('0.0.0.0',RELAY_PORT));receiver.settimeout(.2)
            next_tick=0.
            while True:
                try:
                    packet=json.loads(receiver.recv(8192))
                    if isinstance(packet,dict) and isinstance(packet.get('relay_token'),str) and hmac.compare_digest(packet['relay_token'],token):
                        self.registry.observe(packet['beacon'],packet['source_ip'],time.monotonic())
                except (socket.timeout,ValueError,KeyError,TypeError):
                    pass
                if time.monotonic() >= next_tick:
                    self.tick(time.monotonic());next_tick=time.monotonic()+1


def main():
    data=Path(os.environ['OMNIFLEET_DATA'])
    manager=DiscoveryManager(os.environ['OMNIFLEET_CONFIG'],data,
        Path(os.environ['OMNIFLEET_CONFIG']).resolve().parents[1]/'scripts/run.bash')
    token=(data/'run/discovery-relay-token').read_text().strip()
    def interrupted(*args):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,interrupted)
    try:
        manager.run(token)
    except KeyboardInterrupt:
        pass
    finally:
        for robot in list(manager.children):
            manager.stop(robot)
        save(data/'discovery.json',{'schema':1,'updated_monotonic':time.monotonic(),'robots':{},'conflicts':[]})


if __name__ == '__main__':
    main()
