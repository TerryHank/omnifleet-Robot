"""Saved formation squads and named regions in the simulation's shared map."""
import json
import math
import uuid


def contains(vertices, x, y):
    inside = False
    for (ax, ay), (bx, by) in zip(vertices, vertices[1:]+vertices[:1]):
        cross = (x-ax)*(by-ay)-(y-ay)*(bx-ax)
        if abs(cross)<1e-9 and min(ax,bx)<=x<=max(ax,bx) and min(ay,by)<=y<=max(ay,by):
            return True
        if (ay>y)!=(by>y) and x<ax+(bx-ax)*(y-ay)/(by-ay):
            inside = not inside
    return inside


def coordinate(value, length):
    if not isinstance(value,list) or len(value)!=length or any(type(v) not in (int,float) or not math.isfinite(v) for v in value):
        raise ValueError('地图坐标无效')
    return value


class Catalog:
    def __init__(self, data):
        self.path = data/'squads-and-regions.json'
        self.data = json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {
            'squads':{}, 'regions':{}}
        for entry in self.data['squads'].values():
            entry.setdefault('mode','formation')

    def save(self, packet, robots):
        kind = 'squads' if packet['op']=='squad_save' else 'regions'
        entries = self.data[kind]
        identifier = packet.get('entry_id') or uuid.uuid4().hex
        if not isinstance(identifier,str): raise ValueError('条目编号无效')
        previous = entries.get(identifier)
        if packet.get('entry_id') and (not previous or previous['revision']!=packet.get('revision')):
            raise ValueError('条目已更新，请重新打开编辑')
        name = packet.get('name','')
        if not isinstance(name,str) or not 1<=len(name.strip())<=40:
            raise ValueError('请输入 1–40 字的名称')
        entry = {'id':identifier, 'name':name.strip(), 'revision':previous['revision']+1 if previous else 1}
        if kind=='squads':
            order,shape,spacing=packet.get('order'),packet.get('shape'),packet.get('spacing')
            if not isinstance(order,list) or len(order)<2 or len(set(order))!=len(order) or any(robot not in robots for robot in order):
                raise ValueError('请选择至少两辆不同车辆')
            mode=packet.get('mode','formation')
            if mode not in ('follow','formation'):raise ValueError('请选择小队类型')
            if mode=='follow':shape=None
            elif shape not in ('current','column','line','wedge','rectangle','custom'):
                raise ValueError('请选择队形')
            if type(spacing) not in (int,float) or not math.isfinite(spacing) or spacing<=0:
                raise ValueError('间距须为大于零的米数')
            entry.update(order=order, leader=order[0], mode=mode, shape=shape, spacing=spacing)
            if shape=='custom':
                entry['cell_offsets']=custom_offsets(packet.get('cell_offsets'),len(order))
        else:
            vertices=packet.get('vertices')
            if not isinstance(vertices,list) or not 3<=len(vertices)<=32:
                raise ValueError('区域须包含 3–32 个边界点')
            vertices=[coordinate(point,2) for point in vertices]
            area=abs(sum(ax*by-bx*ay for (ax,ay),(bx,by) in zip(vertices,vertices[1:]+vertices[:1])))/2
            if area<.01:raise ValueError('区域边界的面积过小')
            arrival=packet.get('arrival')
            if arrival is not None:
                arrival=coordinate(arrival,3)
                if not contains(vertices,*arrival[:2]):raise ValueError('到达点须在区域内')
            entry.update(vertices=vertices, arrival=arrival, frame_id='fleet_map')
        self._write({**self.data, kind:{**entries, identifier:entry}})
        return {'phase':'saved','message':entry['name']+'已保存','entry':entry}

    def delete_squad(self, packet):
        identifier = packet.get('entry_id')
        entries = self.data['squads']
        entry = entries.get(identifier) if isinstance(identifier, str) else None
        if not entry or entry['revision'] != packet.get('revision'):
            raise ValueError('小队已变更，请刷新后重试')
        self._write({**self.data, 'squads':{key: value for key, value in entries.items() if key != identifier}})
        return {'phase':'deleted','message':entry['name']+'已删除'}

    def _write(self, updated):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(updated,ensure_ascii=False),encoding='utf-8')
        temporary.replace(self.path)
        self.data = updated

    def snapshot(self, positions):
        regions=[]
        for entry in self.data['regions'].values():
            occupants=[robot for robot,pose in positions.items() if contains(entry['vertices'],*pose[:2])]
            regions.append({**entry,'occupants':occupants})
        return {'squads':list(self.data['squads'].values()),'regions':regions}


def custom_offsets(value,count):
    if not isinstance(value,list) or len(value)!=count:
        raise ValueError('请为每辆车设置位置')
    slots=[coordinate(point,2) for point in value]
    if len({tuple(point) for point in slots})!=count:
        raise ValueError('两辆车不能占用同一格')
    x,y=slots[0]
    return [[a-x,b-y] for a,b in slots]
