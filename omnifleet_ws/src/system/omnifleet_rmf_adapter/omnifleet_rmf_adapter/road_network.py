"""Shared-map road network, routed by Open-RMF's graph planner."""
import datetime
import json
import math

import rmf_adapter as rmf
from rmf_adapter import geometry, vehicletraits


class RoadNetwork:
    def __init__(self,data,config):
        self.file=data/'road-network.json'
        self.config=config
        self.data=json.loads(self.file.read_text()) if self.file.exists() else {'revision':0,'nodes':[],'edges':[]}
        if not self.data.get('named_waypoints'):
            catalog=data/'squads-and-regions.json'
            legacy=json.loads(catalog.read_text()) if catalog.exists() else {}
            for entry in legacy.get('regions',{}).values():
                pose=entry.get('arrival')
                if not pose:continue
                node=next((n for n in self.data['nodes'] if math.dist(n['xy'],pose[:2])<.01),None)
                label=entry['name'].removesuffix('区')+'点' if entry['name'].endswith('区') else entry['name']
                if node is None:
                    node={'id':entry['id'],'name':label,'xy':pose[:2]}
                    self.data['nodes'].append(node)
                if node.get('name',entry['name'])==entry['name']:node['name']=label
                node.setdefault('yaw',pose[2])
            self.data.update(named_waypoints=True,revision=self.data['revision']+1)
            temporary=self.file.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.data,ensure_ascii=False))
            temporary.replace(self.file)
        self.reset_graph()

    def reset_graph(self):
        self.planners={}
        self.graph=rmf.graph.Graph()
        self.nodes={node['id']:i for i,node in enumerate(self.data['nodes'])}
        for node in self.data['nodes']:
            self.graph.add_waypoint('fleet_map',node['xy'])
        for a,b in self.data['edges']:
            self.graph.add_bidir_lane(self.nodes[a],self.nodes[b])

    def save(self,packet):
        if packet.get('revision')!=self.data['revision']:raise ValueError('路网已更新，请重新打开编辑')
        nodes,edges=packet.get('nodes'),packet.get('edges')
        if not isinstance(nodes,list) or not isinstance(edges,list):raise ValueError('路点或连线格式无效')
        validated={}
        for node in nodes:
            name=node.get('id') if isinstance(node,dict) else None
            xy=node.get('xy') if name else None
            if (not isinstance(name,str) or not name.strip() or name in validated or not isinstance(xy,list)
                    or len(xy)!=2 or not all(type(v) in (float,int) and math.isfinite(v) for v in xy)):
                raise ValueError('每个路点需要唯一名称和有效地图坐标')
            label=node.get('name',name)
            yaw=node.get('yaw',0.)
            if not isinstance(label,str) or not 1<=len(label.strip())<=40:
                raise ValueError('路点名称须为 1–40 字')
            if type(yaw) not in (int,float) or not math.isfinite(yaw):raise ValueError('路点朝向无效')
            validated[name]={'id':name,'name':label.strip(),'xy':xy,'yaw':math.atan2(math.sin(yaw),math.cos(yaw))}
        lanes=[]
        for edge in edges:
            if not isinstance(edge,list) or len(edge)!=2 or any(not isinstance(k,str) or k not in validated for k in edge):
                raise ValueError('连线端点不存在')
            a,b=edge
            if math.dist(validated[a]['xy'],validated[b]['xy'])<.01:raise ValueError('连线两端重合')
            pair=sorted(edge)
            if pair not in lanes:lanes.append(pair)
        updated={**self.data,'revision':self.data['revision']+1,'nodes':list(validated.values()),'edges':lanes}
        temporary=self.file.with_suffix('.tmp')
        temporary.write_text(json.dumps(updated,ensure_ascii=False))
        temporary.replace(self.file)
        self.data=updated
        self.reset_graph()
        return {'phase':'saved','message':f'已保存 {len(nodes)} 个路点、{len(lanes)} 条双向路段'}

    def route(self,robot,start,goal,returning=False):
        if not self.data['edges']:raise ValueError('请先规划路网，保存路点并连接路段')
        nodes=self.data['nodes']
        connected={name for edge in self.data['edges'] for name in edge}
        def nearest(p):return min((self.nodes[name] for name in sorted(connected)),key=lambda i:math.dist(nodes[i]['xy'],p[:2]))
        first,last=nearest(start),nearest(goal)
        if not returning and math.dist(nodes[last]['xy'],goal[:2])>.01:
            raise ValueError('目标到达点尚未连接路网')
        if first==last:
            indices=[first]
        else:
            if robot not in self.planners:
                traits={'footprint_radius':.39,'linear_velocity':.5,'linear_acceleration':.5,'angular_velocity':.8,'angular_acceleration':.8,**self.config['robots'][robot].get('rmf_traits',{})}
                profile=vehicletraits.Profile(geometry.make_final_convex_circle(traits['footprint_radius']))
                vehicle=vehicletraits.VehicleTraits(vehicletraits.Limits(traits['linear_velocity'],traits['linear_acceleration']),
                    vehicletraits.Limits(traits['angular_velocity'],traits['angular_acceleration']),profile)
                self.planners[robot]=rmf.plan.Planner(rmf.plan.Configuration(self.graph,vehicle))
            result=self.planners[robot].get_plan_waypoints(
                rmf.plan.Start(datetime.datetime.now(),first,start[2]),rmf.plan.Goal(last))
            indices=[first]
            for point in result:
                # RMF can merge collinear lanes into a single plan waypoint.
                for index in point.approach_lanes:
                    node=self.graph.get_lane(index).exit.waypoint_index
                    if indices[-1]!=node:indices.append(node)
                if point.graph_index is not None and indices[-1]!=point.graph_index:indices.append(point.graph_index)
            if indices[-1]!=last:raise ValueError('路网不连通，无法到达目标')
        names=[nodes[i].get('name',nodes[i]['id']) for i in indices]
        points=[{'name':nodes[i].get('name',nodes[i]['id']),'pose':[*nodes[i]['xy'],goal[2]]} for i in indices]
        if returning and math.dist(points[-1]['pose'][:2],goal[:2])>.01:
            points.append({'name':'出发位置','pose':list(goal)})
        for point,nxt in zip(points,points[1:]):
            x,y,_=point['pose'];nx,ny,_=nxt['pose']
            point['pose'][2]=math.atan2(ny-y,nx-x)
        length=sum(math.dist(a[:2],b[:2]) for a,b in zip([start]+[p['pose'] for p in points], [p['pose'] for p in points]))
        if len(points)>1 and math.dist(start[:2],points[0]['pose'][:2])<.06:points.pop(0)
        return names,points,length

    def itinerary(self,robot,start,destinations,returning=False):
        names,points,total=[],[],0.
        for destination in destinations:
            leg,via,distance=self.route(robot,start,destination['pose'],returning)
            names.extend(leg[1:] if names and names[-1]==leg[0] else leg)
            if points and via and math.dist(points[-1]['pose'][:2],via[0]['pose'][:2])<.01:
                via=via[1:]
            points.extend(via)
            total+=distance
            start=destination['pose']
        return names,points,total
