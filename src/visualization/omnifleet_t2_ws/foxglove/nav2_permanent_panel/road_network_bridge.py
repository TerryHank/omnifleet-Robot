"""Foxglove route-graph preview backed by the official Nav2 Route Server."""
import json
import hashlib
import math
from pathlib import Path
import signal
import subprocess
import threading
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import ComputePathToPose, ComputeRoute
from nav2_msgs.srv import SetRouteGraph
from nav_msgs.msg import Path as NavPath
from rclpy.qos import DurabilityPolicy, QoSProfile
from rcl_interfaces.msg import SetParametersResult
from rcl_interfaces.srv import SetParameters
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker, MarkerArray

GRAPH_ROOT = Path('/home/iecme/omnifleet_a2_data/missions/road_networks')
CURRENT_WAYPOINTS = Path('/home/iecme/omnifleet_a2_data/missions/waypoints.json')
ALGORITHMS = Path('/home/iecme/.local/share/omnifleet_t2/nav2-selected-algorithms.json')


def waypoint_signature(saved):
    records = dict(frame_id=saved.get('frame_id', 'map'),
                   poses=[p['pose'] for p in saved['waypoints']])
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def path_length(path):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def road_pairs(count):
    segments = list(zip(range(count), range(1, count)))
    if count > 2:
        segments.append((count - 1, 0))
    return [pair for a, b in segments for pair in ((a, b), (b, a))]


def write_graph(path, graph):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.geojson.tmp')
    temporary.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf8')
    temporary.replace(path)


def graph_catalog(root=GRAPH_ROOT, waypoints_path=CURRENT_WAYPOINTS):
    raw = waypoints_path.read_bytes()
    saved = json.loads(raw)
    frame = saved.get('frame_id', 'map')
    nodes = [dict(id=i, name=point.get('name', str(i)),
                  x=point['pose']['position']['x'], y=point['pose']['position']['y'])
             for i, point in enumerate(saved['waypoints'], 1)]
    if not nodes:
        return []
    edges = []
    paths_saved = False
    path = root / 'current_map_waypoints' / 'road_network.geojson'
    if path.is_file():
        graph = json.loads(path.read_text(encoding='utf8'))
        if (graph.get('path_geometry_version') == 1 and
                graph.get('source', {}).get('waypoint_signature') == waypoint_signature(saved)):
            paths_saved = True
            for feature in graph['features']:
                props = feature['properties']
                if 'startid' in props:
                    points = feature['geometry']['coordinates'][0]
                    edges.append(dict(id=props['id'], start=props['startid'], end=props['endid'],
                                      path=points, length_m=path_length(points)))
    expected = {(a + 1, b + 1) for a, b in road_pairs(len(nodes))}
    paths_saved = paths_saved and {(e['start'], e['end']) for e in edges} == expected
    return [dict(id='current_map_waypoints', name=f'当前地图 · {len(nodes)}个航点',
                 frame=frame, nodes=nodes, edges=edges, filepath=str(path),
                 paths_saved=paths_saved, closed_loop=paths_saved and len(nodes) > 1)]


def wait(future, timeout=10.):
    ready = threading.Event()
    future.add_done_callback(lambda _: ready.set())
    if not ready.wait(timeout):
        raise TimeoutError('路网规划接口响应超时')
    return future.result()


class RoadNetworkBridge(Node):
    def __init__(self):
        super().__init__('omnifleet_road_network_bridge')
        group = ReentrantCallbackGroup()
        self.lifecycle = self.create_client(ChangeState, '/road_network/route_server/change_state', callback_group=group)
        self.graph = self.create_client(SetRouteGraph, '/road_network/route_server/set_route_graph', callback_group=group)
        self.route = ActionClient(self, ComputeRoute, '/road_network/compute_route', callback_group=group)
        self.planner = ActionClient(self, ComputePathToPose, '/compute_path_to_pose', callback_group=group)
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.graph_pub = self.create_publisher(MarkerArray, '/road_network/saved_graph', latched)
        self.path_pub = self.create_publisher(NavPath, '/road_network/saved_plan', latched)
        self.revision = None
        self.create_service(Trigger, '/omnifleet_t2/road_network/catalog', self.catalog)
        self.create_service(SetParameters, '/omnifleet_t2/road_network/plan', self.plan)

    def initialize(self):
        if not self.lifecycle.wait_for_service(timeout_sec=15.):
            raise TimeoutError('官方路网服务未启动')
        for state in (1, 3):
            request = ChangeState.Request()
            request.transition.id = state
            if not wait(self.lifecycle.call_async(request)).success:
                raise RuntimeError('官方路网服务激活失败')

    def catalog(self, request, response):
        try:
            graphs = graph_catalog()
            self.publish_graph(graphs)
            response.message = json.dumps({'graphs': graphs}, ensure_ascii=False)
            response.success = True
        except (OSError, ValueError, KeyError) as error:
            response.success, response.message = False, str(error)
        return response

    def publish_graph(self, graphs):
        revision = json.dumps(graphs, sort_keys=True)
        if revision == self.revision:
            return
        self.revision = revision
        markers = [Marker(action=Marker.DELETEALL)]
        if graphs:
            graph = graphs[0]
            header = NavPath().header
            header.frame_id, header.stamp = graph['frame'], self.get_clock().now().to_msg()
            for edge in graph['edges']:
                marker = Marker(header=header, ns='saved_edges', id=edge['id'], type=Marker.LINE_STRIP)
                marker.pose.orientation.w = 1.
                marker.scale.x = .035
                marker.color.r, marker.color.g, marker.color.b, marker.color.a = .65, .7, .76, 1.
                marker.points = [Point(x=float(p[0]), y=float(p[1]), z=.03) for p in edge['path']]
                markers.append(marker)
            for node in graph['nodes']:
                marker = Marker(header=header, ns='waypoint_names', id=node['id'], type=Marker.TEXT_VIEW_FACING)
                marker.pose.position = Point(x=float(node['x']), y=float(node['y']), z=.15)
                marker.pose.orientation.w = 1.
                marker.scale.z, marker.color.a, marker.color.r, marker.color.g = .16, 1., 1., 1.
                marker.text = node['name']
                markers.append(marker)
        self.graph_pub.publish(MarkerArray(markers=markers))
        empty = NavPath()
        empty.header.frame_id = graphs[0]['frame'] if graphs else 'map'
        self.path_pub.publish(empty)

    def generate(self, request, response):
        try:
            saved = json.loads(CURRENT_WAYPOINTS.read_text())
            graph = graph_catalog()[0]
            planner_ids = dict(smac_2d='GridBased', smac_hybrid='GridHybrid',
                               smac_lattice='GridLattice', navfn='GridNavFn', theta_star='GridThetaStar')
            planner_id = planner_ids[json.loads(ALGORITHMS.read_text())['global']]
            if not self.planner.wait_for_server(timeout_sec=3.):
                raise RuntimeError('当前全局规划器未就绪')
            features = [dict(type='Feature', properties=dict(id=n['id'], frame=graph['frame'], metadata=dict(name=n['name'])),
                             geometry=dict(type='Point', coordinates=[n['x'], n['y']])) for n in graph['nodes']]
            count = 0
            for start, end in road_pairs(len(saved['waypoints'])):
                    goal = ComputePathToPose.Goal(use_start=True, planner_id=planner_id)
                    for target, index in ((goal.start, start), (goal.goal, end)):
                        record = saved['waypoints'][index]['pose']
                        target.header.frame_id = graph['frame']
                        target.header.stamp = self.get_clock().now().to_msg()
                        for key, value in record['position'].items():
                            setattr(target.pose.position, key, float(value))
                        for key, value in record['orientation'].items():
                            setattr(target.pose.orientation, key, float(value))
                    handle = wait(self.planner.send_goal_async(goal))
                    if not handle.accepted:
                        raise RuntimeError('全局规划请求未被接受')
                    try:
                        wrapped = wait(handle.get_result_async(), timeout=20.)
                    except TimeoutError:
                        handle.cancel_goal_async()
                        raise
                    if wrapped.status != 4 or not wrapped.result.path.poses:
                        raise RuntimeError(f'航点{start+1} → 航点{end+1} 全局规划失败，未覆盖已保存路网')
                    poses = wrapped.result.path.poses
                    points = [[p.pose.position.x, p.pose.position.y] for p in poses]
                    count += 1
                    features.append(dict(type='Feature',
                        properties=dict(id=len(graph['nodes'])+count, startid=start+1, endid=end+1,
                                        cost=path_length(points), overridable=False),
                        geometry=dict(type='MultiLineString', coordinates=[points]),
                        path_poses=[[p.pose.position.x, p.pose.position.y, p.pose.position.z,
                                     p.pose.orientation.x, p.pose.orientation.y,
                                     p.pose.orientation.z, p.pose.orientation.w] for p in poses]))
            document = dict(type='FeatureCollection', name=graph['id'], frame_id=graph['frame'],
                path_geometry_version=1, closed_loop=len(graph['nodes']) > 1, features=features,
                source=dict(waypoint_signature=waypoint_signature(saved), planner_id=planner_id,
                            generated_at=time.time()))
            # Commit one complete graph; individual failed requests leave the last saved graph intact.
            write_graph(Path(graph['filepath']), document)
            self.publish_graph(graph_catalog())
            response.success = True
            response.message = json.dumps(dict(edge_count=count, planner_id=planner_id,
                                               filepath=graph['filepath'], closed_loop=document['closed_loop']), ensure_ascii=False)
        except (OSError, ValueError, KeyError, IndexError, RuntimeError, TimeoutError) as error:
            response.success, response.message = False, str(error)
        return response

    def plan(self, request, response):
        try:
            values = {p.name: p.value.string_value if p.value.type == 4 else p.value.integer_value
                      for p in request.parameters}
            if values.get('operation') == 'generate':
                generated = self.generate(None, Trigger.Response())
                response.results = [SetParametersResult(successful=generated.success, reason=generated.message)
                                    for _ in request.parameters]
                return response
            graph = next(g for g in graph_catalog() if g['id'] == values['graph_id'])
            if not graph['paths_saved']:
                raise RuntimeError('当前航点尚未保存全局路径，请点击“生成并保存全局路线”')
            if values.get('operation') == 'loop':
                start = values['start_id']
                ids = list(range(start, len(graph['nodes']) + 1)) + list(range(1, start + 1))
                if len(graph['nodes']) == 1:
                    ids = [start]
                by_pair = {(e['start'], e['end']):e['id'] for e in graph['edges']}
                edge_ids = [by_pair[(a, b)] for a, b in zip(ids, ids[1:])]
            else:
                if not wait(self.graph.call_async(SetRouteGraph.Request(graph_filepath=graph['filepath']))).success:
                    raise RuntimeError('路网文件加载失败')
                if not self.route.wait_for_server(timeout_sec=3.):
                    raise TimeoutError('官方路网规划接口尚未就绪')
                goal = ComputeRoute.Goal(start_id=values['start_id'], goal_id=values['goal_id'],
                                         use_start=True, use_poses=False)
                handle = wait(self.route.send_goal_async(goal))
                if not handle.accepted:
                    raise RuntimeError('路网规划请求被拒绝')
                wrapped = wait(handle.get_result_async())
                if wrapped.status != 4:
                    raise RuntimeError('未找到可用路网路线，状态=' + str(wrapped.status))
                result = wrapped.result
                ids = [n.nodeid for n in result.route.nodes]
                edge_ids = [edge.edgeid for edge in result.route.edges]
            lookup = {n['id']: n for n in graph['nodes']}
            document = json.loads(Path(graph['filepath']).read_text(encoding='utf8'))
            features = {f['properties']['id']: f for f in document['features'] if 'path_poses' in f}
            path = NavPath()
            path.header.frame_id, path.header.stamp = graph['frame'], self.get_clock().now().to_msg()
            for edge_id in edge_ids:
                for p in features[edge_id]['path_poses']:
                    pose = PoseStamped(header=path.header)
                    pose.pose.position = Point(x=p[0], y=p[1], z=p[2])
                    pose.pose.orientation.x, pose.pose.orientation.y = p[3], p[4]
                    pose.pose.orientation.z, pose.pose.orientation.w = p[5], p[6]
                    path.poses.append(pose)
            if not path.poses and ids:
                pose = PoseStamped(header=path.header)
                pose.pose.position = Point(x=float(lookup[ids[0]]['x']), y=float(lookup[ids[0]]['y']))
                pose.pose.orientation.w = 1.
                path.poses.append(pose)
            points = [[p.pose.position.x, p.pose.position.y] for p in path.poses]
            length = path_length(points)
            self.path_pub.publish(path)
            receipt = dict(graph_id=graph['id'], nodes=ids, node_names=[lookup[i]['name'] for i in ids],
                           length_m=length, path=points, closed_loop=values.get('operation') == 'loop')
            response.results = [SetParametersResult(successful=True, reason=json.dumps(receipt, ensure_ascii=False))
                                for _ in request.parameters]
        except (OSError, ValueError, KeyError, StopIteration, RuntimeError, TimeoutError) as error:
            response.results = [SetParametersResult(successful=False, reason=str(error) or '路网不存在')
                                for _ in request.parameters]
        return response


def main():
    server = subprocess.Popen(['/opt/ros/humble/lib/nav2_route/route_server', '--ros-args',
                               '-r', '__ns:=/road_network'], start_new_session=True)
    rclpy.init()
    node = RoadNetworkBridge()
    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(node)
    worker = threading.Thread(target=executor.spin, daemon=True)
    worker.start()
    try:
        node.initialize()
        node.get_logger().info('路网规划预览服务已就绪')
        while rclpy.ok():
            if server.poll() is not None:
                raise RuntimeError('官方路网服务已退出')
            time.sleep(.5)
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()
        if server.poll() is None:
            server.send_signal(signal.SIGINT)
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == '__main__':
    main()
