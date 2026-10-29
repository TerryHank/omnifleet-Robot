"""Central namespacing and visualization; never publishes vehicle commands."""
from array import array
import copy
import hashlib
import json
import math
import re
import time
import numpy as np
from pathlib import Path

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from rclpy.serialization import deserialize_message
from rclpy.serialization import serialize_message
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage
from visualization_msgs.msg import Marker, MarkerArray
from .shared_costmap import SharedCostmap, inflate
from .map_merge import merge_grids


def compose(a, b):
    c, s = math.cos(a[2]), math.sin(a[2])
    return [a[0]+c*b[0]-s*b[1], a[1]+s*b[0]+c*b[1], a[2]+b[2]]


def inverse(p):
    c, s = math.cos(p[2]), math.sin(p[2])
    return [-c*p[0]-s*p[1], s*p[0]-c*p[1], -p[2]]


def namespaces(config):
    result = {}
    for robot, profile in config['robots'].items():
        if not profile['enabled']:
            continue
        namespace = config['central']['assignments'][robot]['namespace']
        if not re.fullmatch(r'/[A-Za-z][A-Za-z0-9_]*', namespace) or namespace in result.values() or namespace in {'/fleet','/omnifleet','/map','/tf','/tf_static'}:
            raise ValueError('Each central vehicle namespace must be a unique single segment')
        result[robot] = namespace
    return result


def prefix_frame(namespace, frame):
    return namespace.strip('/') + '/' + frame.lstrip('/') if frame else ''


def reported_peer_bounds(state):
    saved=state.get('samples',{}).get('navigation_parameters',{}).get('value',{}).get('saved',{})
    try:
        profile=state.get('samples',{}).get('formation_profile',{}).get('value',{})
        points=json.loads(saved['geometry_local_footprint']['footprint']) if 'geometry_local_footprint' in saved else profile.get('footprint',[])
        padding=float(saved['geometry_local_footprint_padding']['footprint_padding']) if 'geometry_local_footprint_padding' in saved else float(profile.get('padding',0.))
        if len(points)<3 or padding<0 or not math.isfinite(padding):return None
        if not all(len(p)==2 and all(math.isfinite(v) for v in p) for p in points):return None
        return [min(p[0] for p in points)-padding,max(p[0] for p in points)+padding,
                min(p[1] for p in points)-padding,max(p[1] for p in points)+padding]
    except (ValueError,TypeError):return None


def peer_grid(source, peers):
    result = copy.deepcopy(source)
    result.data = array('b', [-1]) * (source.info.width * source.info.height)
    q, p = source.info.origin.orientation, source.info.origin.position
    origin = [p.x, p.y, math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))]
    resolution = source.info.resolution
    for peer in peers:
        pose,radius=peer[:2]
        x,y,yaw=compose(inverse(origin),pose)
        bounds=peer[2] if len(peer)>2 else None
        if bounds is not None:
            xmin,xmax,ymin,ymax=bounds;c,z=math.cos(yaw),math.sin(yaw)
            corners=[(x+c*px-z*py,y+z*px+c*py) for px in (xmin,xmax) for py in (ymin,ymax)]
            left=math.floor(min(p[0] for p in corners)/resolution)
            right=math.floor(max(p[0] for p in corners)/resolution)
            bottom=math.floor(min(p[1] for p in corners)/resolution)
            top=math.floor(max(p[1] for p in corners)/resolution)
            # Exact rectangle/cell overlap on the body axes. World-axis overlap
            # is already bounded above; include every cell touching the padded body.
            half=resolution*.5*(abs(c)+abs(z))
            for row in range(max(0,bottom),min(source.info.height,top+1)):
                for col in range(max(0,left),min(source.info.width,right+1)):
                    dx,dy=(col+.5)*resolution-x,(row+.5)*resolution-y
                    bx,by=c*dx+z*dy,-z*dx+c*dy
                    if xmin-half<=bx<=xmax+half and ymin-half<=by<=ymax+half:
                        result.data[row*source.info.width+col]=100
            continue
        cx, cy = math.floor(x/resolution), math.floor(y/resolution)
        span = math.ceil(radius/resolution + .71)
        for row in range(max(0, cy-span), min(source.info.height, cy+span+1)):
            for col in range(max(0, cx-span), min(source.info.width, cx+span+1)):
                if math.hypot((col+.5)*resolution-x, (row+.5)*resolution-y) <= radius+resolution*.71:
                    result.data[row*source.info.width+col] = 100
    return result


class MapHub:
    def __init__(self, node, config, data):
        self.node, self.config, self.data = node, config, Path(data)
        self.names = namespaces(config)
        self.reference = config['central'].get('reference_robot')
        self.maps, self.seen = {}, {}
        self.costmaps = {}
        self.peer_maps = {}
        self.merge_signature, self.merged_map, self.merge_status = None, None, {}
        self.shared_payload, self.shared_cells_sha256 = None, None
        self.alignment = {}
        self.valid_robots = set()
        previous = self.data/'map_hub_status.json'
        previous_state = json.loads(previous.read_text()) if previous.exists() else {}
        self.held_peers = previous_state.get('last_known_poses', {})
        self.reference_epoch = previous_state.get('reference_epoch') if previous_state.get('reference_robot') == self.reference else None
        self.obstacles = {}
        self.state = {}
        self.last_map_publish = 0.
        self.latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.bulk = QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT)
        self.tf = node.create_publisher(TFMessage, '/tf', QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
        self.static_tf = node.create_publisher(TFMessage, '/tf_static', self.latched)
        self.shared = node.create_publisher(OccupancyGrid, '/fleet/map', self.bulk)
        self.shared_costmap = SharedCostmap(self.data)
        self.last_costmap_publish, self.costmap_revision = 0., None
        self.shared_costmap_publisher = node.create_publisher(OccupancyGrid, '/fleet/global_costmap/costmap', self.bulk)
        self.peer_alias = node.create_publisher(OccupancyGrid, '/fleet/peer_map', self.bulk)
        self.status = node.create_publisher(String, '/fleet/map_status', self.bulk)
        self.markers = node.create_publisher(MarkerArray, '/fleet/robots', self.bulk)
        self.publishers = {r:self.create_vehicle_publishers(ns) for r,ns in self.names.items()}

    def create_vehicle_publishers(self, namespace, created=None):
        result={}
        for key,typ,suffix in [('map',OccupancyGrid,'/map'),('peer',OccupancyGrid,'/navigation/peer_map'),
                              ('global_costmap',OccupancyGrid,'/global_costmap/costmap'),
                              ('local_costmap',OccupancyGrid,'/local_costmap/costmap'),('description',String,'/robot_description')]:
            publisher=self.node.create_publisher(typ,namespace+suffix,self.latched if key=='description' else self.bulk)
            if created is not None:created.append(publisher)
            result[key]=publisher
        return result

    def transforms(self, states):
        path = self.data/'fleet_alignment.json'
        saved = json.loads(path.read_text()) if path.exists() else {}
        epochs = {r: s.get('samples', {}).get('navigation', {}).get('value', {}).get('localization_epoch') for r, s in states.items()}
        observed_anchor_epoch = epochs.get(self.reference)
        if observed_anchor_epoch:self.reference_epoch = observed_anchor_epoch
        # Losing the reference's connection payload does not reset a fixed map.
        # Retain the last observed epoch, including any already observed change.
        anchor_epoch = observed_anchor_epoch or (
            getattr(self, 'reference_epoch', None) if not states.get(self.reference, {}).get('online') else None)
        anchor_matches = bool(saved.get('validated') and anchor_epoch
                              and saved.get('epochs', {}).get(self.reference) == anchor_epoch)
        result = {self.reference: [0., 0., 0.]} if (
            states.get(self.reference, {}).get('online') or anchor_matches) else {}
        pair_reasons = {}
        for robot in self.names:
            if robot == self.reference:continue
            pose = saved.get('transforms', {}).get(robot)
            if not saved.get('validated'):
                pair_reasons[robot] = '等待与参考车辆完成地图配准'
            elif not anchor_epoch:
                pair_reasons[robot] = '参考车辆定位会话尚未就绪'
            elif not anchor_matches:
                pair_reasons[robot] = '参考车辆定位会话已变化，等待重新配准'
            elif saved.get('epochs', {}).get(robot) != epochs.get(robot):
                pair_reasons[robot] = '本车定位会话已变化，等待重新配准'
            elif not isinstance(pose, list) or len(pose) != 3 or not all(
                    type(v) in (int, float) and math.isfinite(v) for v in pose):
                pair_reasons[robot] = '缺少有效的共享地图坐标变换'
            else:
                result[robot] = pose
        valid_robots, validation_reasons = set(), {}
        for robot in self.names:
            state = states.get(robot, {})
            if not state.get('online'):reason = '车辆离线或定位状态已过期'
            elif not epochs.get(robot):reason = '本车定位会话尚未就绪'
            elif not state.get('fresh', {}).get('map'):reason = '本车地图尚未收到或已过期'
            else:reason = pair_reasons.get(robot, '')
            if reason:validation_reasons[robot] = reason
            else:valid_robots.add(robot)
        self.valid_robots, self.validation_reasons = valid_robots, validation_reasons
        self.alignment = result
        return result

    def tick(self, states, transforms=None):
        now = time.monotonic()
        if transforms is None:transforms = self.transforms(states)
        dynamic, static = [], []
        for robot, namespace in self.names.items():
            state = states.get(robot, {})
            for key, typ in [('map', OccupancyGrid), ('global_costmap',OccupancyGrid),
                             ('local_costmap',OccupancyGrid),('tf', TFMessage), ('tf_static', TFMessage)]:
                sample = state.get('samples', {}).get(key)
                current=state.get('transport_connected') if key=='tf_static' else state.get('fresh',{}).get(key)
                cached_map=key=='map' and robot not in self.maps
                if not sample or not (current or cached_map):
                    continue
                path = self.data/'vehicle-cache'/robot/(key+'.cdr')
                if not path.exists():
                    continue
                modified = path.stat().st_mtime_ns
                if key != 'tf' and self.seen.get((robot, key)) == modified:
                    continue
                message = deserialize_message(path.read_bytes(), typ)
                self.seen[(robot, key)] = modified
                if isinstance(message,OccupancyGrid):
                    if key=='map':self.maps[robot] = message
                    else:self.costmaps[(robot,key)] = message
                    exported = copy.deepcopy(message)
                    exported.header.frame_id = prefix_frame(namespace, message.header.frame_id)
                    self.publishers[robot][key].publish(exported)
                else:
                    for transform in message.transforms:
                        transform.header.frame_id = prefix_frame(namespace, transform.header.frame_id)
                        transform.child_frame_id = prefix_frame(namespace, transform.child_frame_id)
                        (static if key == 'tf_static' else dynamic).append(transform)
            description = state.get('samples', {}).get('robot_description', {}).get('value')
            if description and self.seen.get((robot, 'description')) != description:
                self.publishers[robot]['description'].publish(String(data=description))
                self.seen[(robot, 'description')] = description
        stamp = self.node.get_clock().now().to_msg()
        for robot, pose in transforms.items():
            t = TransformStamped()
            t.header.frame_id = 'fleet_map'
            t.header.stamp = stamp
            t.child_frame_id = prefix_frame(self.names[robot], 'map')
            t.transform.translation.x, t.transform.translation.y = pose[:2]
            t.transform.rotation.z, t.transform.rotation.w = math.sin(pose[2]/2), math.cos(pose[2]/2)
            dynamic.append(t)
        if dynamic:
            self.tf.publish(TFMessage(transforms=dynamic))
        if static:
            self.static_tf.publish(TFMessage(transforms=static))
        if now-self.last_map_publish < .15:return
        self.last_map_publish=now
        reference = self.maps.get(self.reference)
        poses = {}
        for robot, transform in transforms.items():
            state = states.get(robot, {})
            p = state.get('samples', {}).get('pose', {}).get('value')
            if p and state.get('online'):
                poses[robot] = compose(transform, [p['x'], p['y'], p['yaw']])
            elif p and robot not in self.held_peers:
                self.held_peers[robot] = compose(transform, [p['x'], p['y'], p['yaw']])
        self.held_peers = {r: p for r, p in self.held_peers.items() if r in transforms}
        self.held_peers.update(poses)
        self.obstacles = {r: (p, .39 if r in poses else .64) for r, p in self.held_peers.items()}
        peer_bounds={r:reported_peer_bounds(states.get(r,{})) for r in poses}
        contributors = {self.reference: reference} if reference else {}
        contributors.update({r: self.maps[r] for r in sorted(self.valid_robots)
                             if r != self.reference and r in self.maps})
        signature = tuple((r, self.seen.get((r, 'map')), tuple(transforms.get(r, [0., 0., 0.])))
                          for r in contributors)
        if signature != self.merge_signature:
            self.merged_map, self.merge_status = merge_grids(
                contributors, {r: transforms.get(r, [0., 0., 0.]) for r in contributors}) if contributors else (None, {})
            self.merge_signature = signature
            if self.merged_map is not None:self.merged_map.header.stamp = stamp
            self.shared_payload = serialize_message(self.merged_map) if self.merged_map is not None else None
            self.shared_cells_sha256 = hashlib.sha256(memoryview(self.merged_map.data).cast('B')).hexdigest() if self.merged_map is not None else None
        shared = self.merged_map
        if shared is not None:
            shared.header.stamp = stamp
            self.shared.publish(shared)
            if now-self.last_costmap_publish >= .5 or self.costmap_revision != self.shared_costmap.saved['revision']:
                occupied = copy.deepcopy(shared)
                overlay = peer_grid(occupied, [(p,radius,peer_bounds.get(r)) for r,(p,radius) in self.obstacles.items()])
                occupied.data = array('b', np.maximum(np.asarray(occupied.data), np.asarray(overlay.data)).astype(np.int8).tobytes())
                costmap = inflate(occupied, self.shared_costmap.saved['parameters'])
                self.shared_costmap_publisher.publish(costmap)
                temporary = self.data/'shared_costmap.cdr.tmp'
                temporary.write_bytes(serialize_message(costmap))
                temporary.replace(self.data/'shared_costmap.cdr')
                self.shared_costmap.updated = True
                self.last_costmap_publish, self.costmap_revision = now, self.shared_costmap.saved['revision']
        markers = []
        for index,robot in enumerate(self.names):
            marker=Marker();marker.header.frame_id='fleet_map';marker.header.stamp=stamp
            marker.ns='fleet_labels';marker.id=index;marker.type=Marker.TEXT_VIEW_FACING
            marker.action=Marker.ADD if robot in poses else Marker.DELETE
            if robot in poses:marker.pose.position.x,marker.pose.position.y=poses[robot][:2]
            marker.pose.position.z=.55;marker.pose.orientation.w=1.
            marker.text=self.config['central']['assignments'][robot]['robot_name']
            marker.scale.z=.22;marker.color.a=1.
            marker.color.r=1. if index%2==0 else 0.;marker.color.g=.85;marker.color.b=0. if index%2==0 else 1.
            markers.append(marker)
        self.markers.publish(MarkerArray(markers=markers))
        shared_payload = self.shared_payload
        shared_cells_sha256 = self.shared_cells_sha256
        peer_cells = {}
        for robot, source in self.maps.items():
            peers = [(compose(inverse(transforms[robot]), p), radius, peer_bounds.get(r)) for r, (p, radius) in self.obstacles.items() if r != robot] if robot in self.valid_robots else []
            grid = peer_grid(source, peers)
            grid.header.frame_id = prefix_frame(self.names[robot], 'map')
            grid.header.stamp = stamp
            self.publishers[robot]['peer'].publish(grid)
            peer_cells[robot] = int(np.count_nonzero(np.asarray(grid.data) == 100))
            if robot == self.reference:
                self.peer_alias.publish(grid)
            cache = self.data/'vehicle-cache'/robot
            local = copy.deepcopy(grid)
            local.header.frame_id = 'map'
            self.peer_maps[robot] = local
            temp = cache/'peer_map_out.tmp'
            peer_payload=serialize_message(local)
            temp.write_bytes(peer_payload)
            temp.replace(cache/'peer_map_out.cdr')
            if shared_payload is not None:
                temp = cache/'shared_map_out.tmp'
                temp.write_bytes(shared_payload)
                temp.replace(cache/'shared_map_out.cdr')
            nav = states.get(robot,{}).get('samples',{}).get('navigation',{}).get('value',{})
            receipt = {'sent_monotonic':now,'epoch':nav.get('localization_epoch'),
                       'reference_robot':self.reference,'alignment_valid':robot in self.valid_robots,
                       'reference_map_fresh':bool(states.get(self.reference,{}).get('fresh',{}).get('map')),
                       'transform':transforms.get(robot),'occupied_cells':peer_cells[robot]}
            receipt['peer_payload_sha256']=hashlib.sha256(peer_payload).hexdigest()
            receipt['shared_payload_sha256']=hashlib.sha256(shared_payload).hexdigest() if shared_payload else None
            receipt['shared_cells_sha256']=shared_cells_sha256
            temp = cache/'map_transfer.tmp'
            temp.write_text(json.dumps(receipt))
            temp.replace(cache/'map_transfer.json')
        self.state = {'reference_robot': self.reference, 'reference_epoch': getattr(self, 'reference_epoch', None), 'namespaces': self.names,
                      'maps': {r: {'width': m.info.width, 'height': m.info.height, 'fresh': states.get(r, {}).get('fresh', {}).get('map', False)} for r, m in self.maps.items()},
                      'alignment_valid': len(self.valid_robots) == len(self.names), 'valid_robots':sorted(self.valid_robots),
                      'validation_reasons':self.validation_reasons,
                      'reference_map_fresh':bool(states.get(self.reference,{}).get('fresh',{}).get('map')), 'held_offline_robots':sorted(set(self.held_peers)-set(poses)), 'transforms': transforms, 'poses': poses,
                      'last_known_poses': self.held_peers, 'peer_occupied_cells': peer_cells, 'motion_enabled': False,
                      'shared_map': self.merge_status, 'shared_costmap': self.shared_costmap.snapshot()}
        self.status.publish(String(data=json.dumps(self.state)))
        temporary=self.data/'map_hub_status.tmp';temporary.write_text(json.dumps(self.state, indent=2));temporary.replace(self.data/'map_hub_status.json')
