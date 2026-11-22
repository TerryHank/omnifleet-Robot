"""Save and load simulation occupancy maps in the shared Gazebo frame."""
import hashlib
import json
from pathlib import Path
import time
import uuid

from rclpy.serialization import deserialize_message, serialize_message
from nav_msgs.msg import OccupancyGrid


class MapLibrary:
    def __init__(self,data):
        self.data=Path(data)
        self.folder=self.data/'saved-maps';self.folder.mkdir(exist_ok=True)

    def save(self,packet,maps):
        grid=maps.merged_map
        name=packet.get('name','').strip()
        if not 1<=len(name)<=60:raise ValueError('地图名称须为 1–60 字')
        if grid is None:raise ValueError('共享地图尚未就绪')
        key=uuid.uuid4().hex
        (self.folder/(key+'.cdr')).write_bytes(serialize_message(grid))
        info={'id':key,'name':name,'saved_at':time.time(),'width':grid.info.width,'height':grid.info.height,
              'resolution':grid.info.resolution,'reference':maps.reference,'epoch':maps.reference_epoch}
        (self.folder/(key+'.json')).write_text(json.dumps(info,ensure_ascii=False))
        return {'phase':'saved','message':'地图已保存：'+name,'map_id':key}

    def load(self,packet,maps):
        key=packet.get('map_id')
        if key=='live':
            maps.saved_grid=None;maps.loaded_map_id=None
            return {'phase':'loaded','message':'已显示实时共享地图'}
        key=self.entry(key)
        info=json.loads((self.folder/(key+'.json')).read_text())
        if (info['reference'],info['epoch'])!=(maps.reference,maps.reference_epoch):
            raise ValueError('地图属于其他定位坐标系')
        maps.saved_grid=deserialize_message((self.folder/(key+'.cdr')).read_bytes(), OccupancyGrid)
        maps.saved_epoch=maps.reference_epoch
        maps.loaded_map_id=key
        return {'phase':'loaded','message':'已显示地图：'+info['name'],'map_id':key}

    def entry(self,key):
        if not isinstance(key,str) or len(key)!=32 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('请选择已保存地图')
        if not (self.folder/(key+'.json')).is_file():raise ValueError('已保存地图不存在')
        return key

    def delete(self,packet,maps):
        key=self.entry(packet.get('map_id'))
        (self.folder/(key+'.json')).unlink()
        (self.folder/(key+'.cdr')).unlink(missing_ok=True)
        if getattr(maps,'loaded_map_id',None)==key:
            maps.saved_grid=None;maps.loaded_map_id=None
        return {'phase':'deleted','message':'地图存档已删除'}

    def snapshot(self):
        maps=[json.loads(p.read_text()) for p in self.folder.glob('*.json')]
        for info in maps:info['path']=str(self.folder/(info['id']+'.cdr'))
        return sorted(maps,key=lambda m:m['saved_at'],reverse=True)
