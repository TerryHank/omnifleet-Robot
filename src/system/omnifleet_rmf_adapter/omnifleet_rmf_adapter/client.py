"""Subscriptions and graph introspection only; no vehicle command endpoints."""
from collections import Counter
import json
import hashlib
import math
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
import time

import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.action.graph import get_action_names_and_types
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy
from rclpy.serialization import serialize_message, deserialize_message
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry, OccupancyGrid
from tf2_msgs.msg import TFMessage
from std_msgs.msg import Bool, Float32, String
from tf2_ros import Buffer, TransformException
from rclpy.time import Time


STATUS_FIELDS = (
    'task_id', 'source', 'phase', 'navigation_active', 'local_ready', 'traffic_paused', 'traffic_suspended',
    'readiness_reason', 'control_mode', 'manual_active', 'local_override', 'fleet_enabled',
    'fleet_hold', 'estop', 'contact', 'safety_reason', 'control_gate_ready', 'tf_age_ms',
    'localization_status', 'fleet_control_available', 'message',
    'localization_epoch','fleet_lease_fresh','fleet_lease_sequence','fleet_lease_task_id','fleet_lease_revision',
    'velocity','velocity_age','nav_active','stopped_seconds',
    'navigation_parameter_source','selected_planner','selected_controller',
    'follow_stream', 'formation_stream', 'manual_command_age', 'fleet_rx', 'last_fleet_failure',
)


class RobotObserver(Node):
    def create_timer(self,period,callback,*args,**kwargs):
        def measured():
            started=time.monotonic()
            try:return callback()
            finally:
                elapsed=time.monotonic()-started
                timings=getattr(self,'callback_timings',{})
                name=callback.__qualname__;old=timings.get(name,{})
                timings[name]={'last':elapsed,'maximum':max(elapsed,old.get('maximum',0.)),'at':started}
                self.callback_timings=timings
                if hasattr(self,'samples'):self.record('callback_timings',dict(timings))
        return super().create_timer(period,measured,*args,**kwargs)

    def __init__(self):
        self.robot_id = os.environ['OMNIFLEET_ROBOT_ID']
        super().__init__('omnifleet_rmf_observer_' + self.robot_id)
        self.steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        config = json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text())
        self.profile = config['robots'][self.robot_id]
        runtime = os.environ.get('OMNIFLEET_DISCOVERY_PROFILE')
        if runtime:
            self.profile = {**self.profile, **json.loads(Path(runtime).read_text())}
        self.socket_path = Path(os.environ['OMNIFLEET_DATA']) / 'run/state.sock'
        self.ipc = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.ipc.setblocking(False)
        self.samples = {}
        self.cache = Path(os.environ['OMNIFLEET_DATA']) / 'vehicle-cache' / self.robot_id
        self.cache.mkdir(parents=True, exist_ok=True)
        self.pose_buffer=Buffer();self.pose_frame='map';self.pose_base='base_link'
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.map_state_mtime=None
        self.map_process=subprocess.Popen([sys.executable,'-m','omnifleet_rmf_adapter.map_relay'])
        self.create_timer(.1,self.read_map_state,clock=self.steady_clock)
        self.counts = Counter()
        self.graph = {}
        self.read_only=True
        prefix = self.profile['observed_namespace']
        self.create_subscription(String, prefix + '/navigation/status',
                                 lambda m: self.status('navigation', m), qos_profile_sensor_data)
        self.create_subscription(String, prefix + '/navigation/local_status',
                                 lambda m: self.status('control', m), qos_profile_sensor_data)
        self.create_subscription(String, prefix + '/omnifleet_t2/waypoints/catalog', self.catalog, latched)
        self.create_subscription(Odometry, prefix + self.profile['pose_topic'], self.pose, QoSProfile(depth=1))
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(String, prefix + '/robot_description', lambda m: self.record('robot_description', m.data), latched)
        self.create_subscription(TFMessage, prefix + '/tf', lambda m: self.cache_tf('tf', m), qos_profile_sensor_data)
        self.create_subscription(TFMessage, prefix + '/tf_static', lambda m: self.cache_tf('tf_static', m), latched)
        self.create_subscription(Float32, prefix + '/voltage',
                                 lambda m: self.record('voltage', m.data) if math.isfinite(m.data) else None,
                                 qos_profile_sensor_data)
        for field in ('estop', 'contact'):
            self.create_subscription(Bool, prefix + '/navigation/' + field,
                                     lambda m, f=field: self.record(f, m.data), qos_profile_sensor_data)
        self.create_timer(5.0, self.discover,clock=self.steady_clock)
        self.emit_timer=self.create_timer(1.0, self.emit,clock=self.steady_clock)

    def read_map_state(self):
        if self.map_process.poll() is not None:
            self.get_logger().warning('Map relay exited; restarting its existing connection')
            self.map_process=subprocess.Popen([sys.executable,'-m','omnifleet_rmf_adapter.map_relay'])
        path=self.cache/'map_relay_state.json'
        if not path.exists():return
        modified=path.stat().st_mtime_ns
        if modified==self.map_state_mtime:return
        for key,(stamp,value) in json.loads(path.read_text()).items():
            if stamp!=self.samples.get(key,(0,None))[0]:
                self.samples[key]=(stamp,value);self.counts[key]+=1
        self.map_state_mtime=modified

    def close_map_process(self):
        if self.map_process.poll() is None:
            self.map_process.send_signal(signal.SIGINT)
            try:self.map_process.wait(timeout=3)
            except subprocess.TimeoutExpired:self.map_process.kill();self.map_process.wait()

    def record(self, key, value):
        self.samples[key] = (time.monotonic(), value)
        self.counts[key] += 1

    def catalog(self, message):
        try:
            value = json.loads(message.data)
            self.record('waypoints', {'frame_id':value.get('frame_id','map'), 'waypoints':value.get('waypoints',[])[:100],
                                      'pass_radius':value.get('pass_radius')})
        except (ValueError, TypeError):
            self.get_logger().warning('Invalid waypoint catalogue')

    def cache_tf(self, key, message):
        for transform in message.transforms:
            if transform.header.frame_id == 'fleet_map':
                continue  # Never echo the imported central alignment back into the hub.
            if key=='tf_static':self.pose_buffer.set_transform_static(transform,'robot-observer')
            else:self.pose_buffer.set_transform(transform,'robot-observer')
            if transform.child_frame_id.rsplit('/',1)[-1]=='base_link':self.pose_base=transform.child_frame_id
        try:
            transform=self.pose_buffer.lookup_transform(self.pose_frame,self.pose_base,Time())
            stamp=transform.header.stamp.sec+transform.header.stamp.nanosec*1e-9
            previous=self.samples.get('pose',(0,{}))[1].get('stamp_seconds',0.)
            if self.samples.get('pose',(0,{}))[1].get('source')!='control_tf' and (stamp>previous or self.samples.get('pose',(0,{}))[1].get('source')!='tf'):
                p,q=transform.transform.translation,transform.transform.rotation
                self.record('pose',{'x':p.x,'y':p.y,'yaw':math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z)),
                    'frame_id':self.pose_frame,'stamp_seconds':stamp,'source':'tf'})
        except TransformException:
            pass

    def cache_message(self, key, message):
        if not message.info.width or len(message.data) != message.info.width * message.info.height:
            return
        self.cache_pending[key] = message
        if key=='map':self.local_grid = message

    def transfer_maps(self):
        import copy
        metadata = self.cache/'map_transfer.json'
        if not metadata.exists():return
        receipt = json.loads(metadata.read_text())
        nav = self.samples.get('navigation',(0,{}))[1]
        valid = (receipt.get('alignment_valid') and 0 <= time.monotonic()-receipt['sent_monotonic'] < 2
                 and receipt.get('epoch') == nav.get('localization_epoch'))
        stamp = self.get_clock().now().to_msg()
        if valid:
            payloads={name:(self.cache/(name+'_map_out.cdr')).read_bytes() for name in ('peer','shared')}
            if any(hashlib.sha256(value).hexdigest()!=receipt.get(name+'_payload_sha256') for name,value in payloads.items()):return
            published=getattr(self,'published_map_payloads',{})
            for name,publisher in [('peer_map_out',self.peer_output),('shared_map_out',self.shared_output)]:
                kind=name.split('_')[0];digest=receipt[kind+'_payload_sha256']
                if published.get(kind)==digest:continue
                message = deserialize_message(payloads[name.split('_')[0]],OccupancyGrid)
                message.header.stamp = stamp
                publisher.publish(message)
                published[kind]=digest
            self.published_map_payloads=published
            pose=receipt['transform']
            t=TransformStamped();t.header.frame_id='fleet_map';t.header.stamp=stamp;t.child_frame_id='map'
            t.transform.translation.x,t.transform.translation.y=pose[:2]
            t.transform.rotation.z,t.transform.rotation.w=math.sin(pose[2]/2),math.cos(pose[2]/2)
            self.fleet_tf.publish(TFMessage(transforms=[t]))
        elif self.local_grid is not None:
            cleared=copy.deepcopy(self.local_grid);cleared.header.stamp=stamp
            cleared.data=[-1]*len(cleared.data);self.peer_output.publish(cleared)
            self.published_map_payloads={}
        state={'source_robot':receipt['reference_robot'],'alignment_valid':bool(valid),
               'shared_source_fresh':bool(receipt.get('reference_map_fresh')),
               'localization_epoch':nav.get('localization_epoch'),'occupied_cells':receipt['occupied_cells'] if valid else 0,
               'transport_age':time.monotonic()-receipt['sent_monotonic']}
        state['shared_payload_verified']=bool(valid)
        state['shared_cells_sha256']=receipt.get('shared_cells_sha256') if valid else None
        self.shared_status.publish(String(data=json.dumps(state)))
        self.record('map_transfer',state)

    def flush_cache(self):
        for key, message in list(self.cache_pending.items()):
            target = self.cache / (key + '.cdr')
            temporary = target.with_suffix('.tmp')
            temporary.write_bytes(serialize_message(message))
            temporary.replace(target)
            self.record(key, {'bytes': target.stat().st_size})
            del self.cache_pending[key]

    def status(self, key, message):
        try:
            payload = json.loads(message.data)
            if payload.get('robot_id') != self.robot_id:
                self.record('identity_error', {'received_robot':payload.get('robot_id')})
                return
            if key=='control':
                pose=payload.get('local_pose');stamp=payload.get('pose_stamp_ns',0)/1e9
                previous=self.samples.get('pose',(0,{}))[1]
                if isinstance(pose,list) and len(pose)==3 and all(type(v) in (int,float) and math.isfinite(v) for v in pose) and (stamp>previous.get('stamp_seconds',0.) or previous.get('source')!='control_tf'):
                    self.record('pose',{'x':pose[0],'y':pose[1],'yaw':pose[2],'frame_id':'map','stamp_seconds':stamp,'source':'control_tf'})
            self.record(key, {k: payload[k] for k in STATUS_FIELDS if k in payload})
        except (ValueError, TypeError):
            self.get_logger().warning('Invalid JSON status on ' + key)

    def pose(self, message):
        if self.samples.get('pose',(0,{}))[1].get('source') in ('tf','control_tf'):return
        p = message.pose.pose
        values = (p.position.x, p.position.y, p.orientation.x, p.orientation.y,
                  p.orientation.z, p.orientation.w)
        if not all(math.isfinite(v) for v in values):
            return
        q = p.orientation
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        stamp=message.header.stamp.sec+message.header.stamp.nanosec*1e-9
        if stamp<=self.samples.get('pose',(0,{}))[1].get('stamp_seconds',0.):return
        self.pose_frame=message.header.frame_id
        self.record('pose', {'x': p.position.x, 'y': p.position.y, 'yaw': yaw,
                             'frame_id': message.header.frame_id,
                             'stamp_seconds':stamp,'source':'odometry'})

    def discover(self):
        prefix = self.profile['observed_namespace'] + '/navigation/'
        self.graph = {
            'topics':dict(self.get_topic_names_and_types()),
            'topic_count': len(self.get_topic_names_and_types()),
            'actions': dict(get_action_names_and_types(self)),
            'navigation_services': {k: v for k, v in self.get_service_names_and_types() if k.startswith(prefix)},
        }

    def emit(self):
        now = time.monotonic()
        payload = {
            'schema': 1, 'robot_id': self.robot_id, 'domain_id': self.profile['domain_id'],
            'observed_namespace': self.profile['observed_namespace'],
            'sample_monotonic': now, 'read_only': self.read_only,
            'samples': {k: {'age_seconds': now - t, 'value': v} for k, (t, v) in self.samples.items()},
            'message_counts': dict(self.counts), 'graph': self.graph,
            'battery_soc': None,
        }
        try:
            self.ipc.sendto(json.dumps(payload, allow_nan=False).encode(), str(self.socket_path))
        except (FileNotFoundError, ConnectionRefusedError, BlockingIOError):
            pass


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    from .control_client import NavigationClient
    node = NavigationClient()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.close_map_process()
        node.ipc.close()
        node.commands.close();node.command_path.unlink(missing_ok=True)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
