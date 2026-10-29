import argparse
import json
import os
from pathlib import Path
import sys
import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('role')
    parser.add_argument('--config', required=True)
    parser.add_argument('--data', required=True)
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text())
    if args.role not in ('schedule', 'dispatcher', 'blockade', 'central', 'foxglove', 'discovery') and args.role not in config['robots']:
        parser.error('role must be a central service or a configured vehicle connection')
    robot = config['robots'].get(args.role)
    if robot is not None:
        runtime = os.environ.get('OMNIFLEET_DISCOVERY_PROFILE')
        if not runtime:
            parser.error('Vehicle connections require a fresh discovery profile')
        discovered = json.loads(Path(runtime).read_text())
        if discovered['robot_id'] != args.role:
            parser.error('Discovery identity does not match requested vehicle')
        robot = {**robot, **discovered}
    profile = robot if robot is not None else config['central']
    if robot is not None and (not robot['enabled'] or robot['domain_id'] is None):
        parser.error(f'{args.role} is disabled pending runtime verification')
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(('ZENOH_', 'CYCLONEDDS_', 'FASTRTPS_', 'FASTDDS_')) or key == 'LD_PRELOAD':
            env.pop(key)
    env.update(ROS_DOMAIN_ID=str(profile['domain_id']), RMW_IMPLEMENTATION=profile['rmw'],
               ROS_LOCALHOST_ONLY='0' if robot is not None else '1',
               OMNIFLEET_CONFIG=str(config_path), OMNIFLEET_DATA=str(Path(args.data).resolve()))
    if args.role == 'central':
        vendor = Path(args.data).resolve().parent / 'install/omnifleet_rmf_adapter_vendor'
        env['PYTHONPATH'] = str(vendor) + os.pathsep + env.get('PYTHONPATH', '')
    if robot is not None:
        env['ZENOH_SESSION_CONFIG_URI'] = str(config_path.parent / robot['zenoh_config'])
        env['OMNIFLEET_ROBOT_ID'] = args.role
        if 'zenoh_qos' in robot:
            session_path=Path(env['ZENOH_SESSION_CONFIG_URI'])
            session=json.loads(session_path.read_text())
            session['qos']=robot['zenoh_qos']
            session_path.write_text(json.dumps(session,indent=2)+'\n')
    else:
        env['ZENOH_SESSION_CONFIG_URI'] = str((config_path.parent / profile['zenoh_config']).resolve())
    if args.role == 'foxglove':
        from ament_index_python.packages import get_package_prefix
        bridge=yaml.safe_load((config_path.parent/'foxglove.yaml').read_text())
        bridge['/**']['ros__parameters']['topic_whitelist'][-1]='^/[A-Za-z][A-Za-z0-9_]*/(map|robot_description|missions/preview_path|navigation/peer_map|rmf/connection_status|global_costmap/costmap|local_costmap/costmap)$'
        output=Path(args.data).resolve()/'run/foxglove-central.yaml';output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(yaml.safe_dump(bridge))
        command=[str(Path(get_package_prefix('foxglove_bridge'))/'lib/foxglove_bridge/foxglove_bridge'),'--ros-args','--params-file',str(output)]
    elif args.role in ('schedule', 'dispatcher', 'blockade'):
        from ament_index_python.packages import get_package_prefix
        package, executable = {
            'schedule': ('rmf_traffic_ros2', 'rmf_traffic_schedule'),
            'dispatcher': ('rmf_task_ros2', 'rmf_task_dispatcher'),
            'blockade': ('rmf_traffic_ros2', 'rmf_traffic_blockade'),
        }[args.role]
        command = [str(Path(get_package_prefix(package)) / 'lib' / package / executable)]
    else:
        module = 'discovery_manager' if args.role == 'discovery' else 'client' if robot is not None else 'central'
        command = [sys.executable, '-m', 'omnifleet_rmf_adapter.' + module]
    print(f'{args.role}: domain={profile["domain_id"]} rmw={profile["rmw"]} control=operator_gated', flush=True)
    os.execvpe(command[0], command, env)


if __name__ == '__main__':
    main()
