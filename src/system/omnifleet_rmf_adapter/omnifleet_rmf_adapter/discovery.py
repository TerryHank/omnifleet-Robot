"""LAN beacon validation and expiring identities; independent of ROS."""
import ipaddress
import re


PORT = 7446
RELAY_PORT = 7448
TTL = 6.0


def beacon_profile(beacon, source_ip):
    address = ipaddress.IPv4Address(source_ip)
    if address.is_loopback or address.is_multicast or address.is_unspecified or address.is_reserved:
        raise ValueError('Invalid beacon source')
    if not isinstance(beacon, dict) or beacon.get('protocol') != 'omnifleet-discovery' or beacon.get('version') != 1:
        raise ValueError('Unsupported beacon')
    robot = beacon.get('robot_id')
    if not isinstance(robot, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}', robot) or robot in {'fleet','omnifleet','map','tf','tf_static'}:
        raise ValueError('Invalid vehicle identity')
    domain, port = beacon.get('domain_id'), beacon.get('zenoh_port')
    if type(domain) is not int or not 0 <= domain <= 232 or type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Invalid ROS domain or Zenoh port')
    if beacon.get('rmw') != 'rmw_zenoh_cpp':
        raise ValueError('Unsupported vehicle middleware')
    for key in ('instance_id', 'boot_id'):
        if not isinstance(beacon.get(key), str) or not re.fullmatch(r'[a-f0-9-]{16,64}', beacon[key]):
            raise ValueError('Invalid machine or boot identity')
    prefix, pose = beacon.get('observed_namespace', ''), beacon.get('pose_topic')
    if not isinstance(prefix, str) or not re.fullmatch(r'(?:/[A-Za-z][A-Za-z0-9_]*)*', prefix):
        raise ValueError('Invalid namespace')
    if not isinstance(pose, str) or not re.fullmatch(r'(?:/[A-Za-z][A-Za-z0-9_]*)+', pose):
        raise ValueError('Invalid pose topic')
    return {k: beacon[k] for k in ('robot_id','domain_id','rmw','instance_id','boot_id','pose_topic')} | {
        'host': str(address), 'zenoh_port': port, 'observed_namespace': prefix,
        'local_namespace': prefix,
        'interface_priority': 1 if beacon.get('interface_priority') == 1 else 0,
    }


class Registry:
    def __init__(self):
        self.candidates = {}

    def observe(self, beacon, source_ip, now):
        profile = beacon_profile(beacon, source_ip)
        self.candidates[(profile['robot_id'], profile['instance_id'], source_ip)] = (now, profile)

    def active(self, now):
        self.candidates = {key: value for key, value in self.candidates.items() if 0 <= now-value[0] < TTL}
        groups = {}
        for seen, profile in self.candidates.values():
            groups.setdefault(profile['robot_id'], []).append(profile)
        result, conflicts = {}, set()
        for robot, profiles in groups.items():
            if len({p['instance_id'] for p in profiles}) != 1 or len({p['boot_id'] for p in profiles}) != 1:
                conflicts.add(robot)
            else:
                lan_profiles = [p for p in profiles if p.get('interface_priority') == 1]
                if lan_profiles:result[robot] = lan_profiles[0]  # Only vehicle-advertised physical LAN interfaces.
        domains = {}
        for robot, profile in result.items():
            domains.setdefault(profile['domain_id'], []).append(robot)
        for robots in domains.values():
            if len(robots) > 1:
                conflicts.update(robots)
        return {r:p for r,p in result.items() if r not in conflicts}, sorted(conflicts)


def new_vehicle(profile, assignments):
    robot = profile['robot_id']
    name = robot
    used = {a['robot_name'] for a in assignments.values()}
    index = 2
    while name in used:
        name = robot[:35] + '_' + str(index)
        index += 1
    return {
        'enabled': True, 'motion_enabled': False,
        **{k:profile[k] for k in ('domain_id','rmw','pose_topic','local_namespace','observed_namespace')},
        'map_transform_validated': False, 'fleet_lease_contract_validated': False,
    }, {'robot_name':name, 'namespace':'/'+name}
