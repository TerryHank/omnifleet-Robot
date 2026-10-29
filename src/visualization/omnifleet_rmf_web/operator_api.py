"""RMF Web access to the existing OmniFleet operator contract and cached ROS data."""
import asyncio,base64,hashlib,json,math,os,struct,subprocess,time,urllib.error,urllib.request,zlib
from pathlib import Path
from fastapi import APIRouter,HTTPException,Request
from nav_msgs.msg import OccupancyGrid
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from rosidl_runtime_py.convert import message_to_ordereddict
from fastapi.responses import Response
import xml.etree.ElementTree as ET
import numpy as np

router=APIRouter(prefix='/omnifleet/operator',tags=['OmniFleet operator'])
WS=Path(__file__).resolve().parents[3]
DATA=WS/'data'
CENTRAL=os.environ.get('OMNIFLEET_OPERATOR_CENTRAL','http://127.0.0.1:8081')
HTTP=urllib.request.build_opener(urllib.request.ProxyHandler({}))
image_cache={}

def central(route,body=None,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['X-OmniFleet-Token']=token
    request=urllib.request.Request(CENTRAL+route,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    try:
        with HTTP.open(request,timeout=5) as response:return json.load(response)
    except urllib.error.HTTPError as error:raise HTTPException(error.code,'中央拒绝该请求') from None
    except (OSError,ValueError):raise HTTPException(503,'中央调度暂不可用') from None

@router.get('/state')
async def state():return await asyncio.to_thread(central,'/state')

@router.post('/command')
async def command(request:Request):
    if request.headers.get('origin') not in (None,'http://localhost:3000','http://127.0.0.1:3000','http://localhost:8080','http://127.0.0.1:8080'):raise HTTPException(403,'origin not allowed')
    payload=await request.body()
    if not 0<len(payload)<=16384:raise HTTPException(400,'请求长度无效')
    try:packet=json.loads(payload)
    except ValueError:raise HTTPException(400,'请求格式无效') from None
    return await asyncio.to_thread(central,'/command',packet,request.headers.get('X-OmniFleet-Token'))

@router.get('/schema')
async def schema():
    value=json.loads((WS/'src/system/omnifleet_rmf_adapter/config/navigation-schema.json').read_text())
    from omnifleet_rmf_adapter.permanent_parameters import FIELDS
    known={f['id'] for f in value['fields']}
    value['fields'].extend({**f,'group':'车体与障碍','help':'沿用单车永久参数服务；几何修改可能需要重启导航栈'} for f in FIELDS if f['id'] not in known)
    return value

def resolve_robot(identifier,snapshot):
    if identifier in snapshot['assignments']:return identifier
    for robot,assignment in snapshot['assignments'].items():
        if identifier==assignment['robot_name']:return robot
    raise HTTPException(404,'车辆身份已变化，请刷新')

def png(width,height,pixels):
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    scan=b''.join(b'\0'+pixels[y*width*4:(y+1)*width*4] for y in range(height))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')

def read_map(robot,layer,snapshot):
    robot=resolve_robot(robot,snapshot)
    files={'map':'map.cdr','shared':'shared_map_out.cdr','peer':'peer_map_out.cdr','global':'global_costmap.cdr','local':'local_costmap.cdr','fleet_costmap':'shared_costmap.cdr'}
    if layer not in files:raise HTTPException(404,'地图图层无效')
    path=DATA/'shared_costmap.cdr' if layer=='fleet_costmap' else DATA/'vehicle-cache'/robot/files[layer]
    if not path.is_file():raise HTTPException(404,'等待本车地图数据')
    stamp=path.stat().st_mtime_ns;key=(robot,layer)
    cached=image_cache.get(key)
    if not cached or cached[0]!=stamp:
        payload=path.read_bytes();grid=deserialize_message(payload,OccupancyGrid);w,h=grid.info.width,grid.info.height
        cells=np.asarray(grid.data,dtype=np.int16).reshape(h,w);rgba=np.zeros((h,w,4),dtype=np.uint8)
        if layer in ('peer','global','local','fleet_costmap'):
            visible=cells>0;rgba[visible,:3]=[245,101,75];rgba[:,:,3]=np.where(visible,np.minimum(220,cells*2.2),0).astype(np.uint8)
        else:
            rgba[cells>=0]=[157,193,213,160];rgba[cells>=65]=[13,40,65,255]
        pixels=np.flipud(rgba).tobytes()
        q=grid.info.origin.orientation;p=grid.info.origin.position
        value={'width':w,'height':h,'resolution':grid.info.resolution,'origin':[p.x,p.y,math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))],
               'frame_id':grid.header.frame_id,'hash':hashlib.sha256(payload).hexdigest(),
               'png':'data:image/png;base64,'+base64.b64encode(png(w,h,pixels)).decode()}
        image_cache[key]=(stamp,value);cached=image_cache[key]
    transform=[0.,0.,0.] if cached[1]['frame_id']=='fleet_map' else snapshot['maps']['transforms'].get(robot)
    return {**cached[1],'transform':transform or [0.,0.,0.],'aligned':transform is not None,'age_seconds':max(0.,time.time()-stamp/1e9),'robot':robot,'layer':layer}

@router.get('/maps/{robot}/{layer}')
async def map_image(robot:str,layer:str):
    snapshot=await asyncio.to_thread(central,'/state')
    return await asyncio.to_thread(read_map,robot,layer,snapshot)

@router.get('/inspect/{robot}')
async def inspect(robot:str,topic:str):
    snapshot=await asyncio.to_thread(central,'/state');robot=resolve_robot(robot,snapshot)
    if not topic.startswith('/') or len(topic)>300 or '..' in topic:raise HTTPException(400,'话题名称无效')
    path=DATA/'vehicle-cache'/robot/'web'/(topic.strip('/').replace('/','__')+'.json')
    if not path.is_file():raise HTTPException(404,'尚未收到该话题消息')
    data=json.loads(path.read_text());data['age_seconds']=max(0.,time.monotonic()-data.pop('sample_monotonic'))
    return data

@router.get('/scene/{robot}')
async def scene(robot:str):
    snapshot=await asyncio.to_thread(central,'/state');robot=resolve_robot(robot,snapshot)
    transforms=[]
    for key in ('tf_static','tf'):
        path=DATA/'vehicle-cache'/robot/(key+'.cdr')
        if path.is_file():transforms.extend(message_to_ordereddict(deserialize_message(path.read_bytes(),TFMessage))['transforms'])
    description=snapshot['robots'][robot].get('samples',{}).get('robot_description',{}).get('value','')
    return {'transforms':transforms,'description':description,'alignment':snapshot['maps']['transforms'].get(robot)}

@router.get('/diagnostic/{robot}/{identifier}')
async def diagnostic(robot:str,identifier:str):
    import re
    snapshot=await asyncio.to_thread(central,'/state');robot=resolve_robot(robot,snapshot)
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,160}',identifier):raise HTTPException(400,'请求编号无效')
    path=DATA/'vehicle-cache'/robot/'web'/('diagnostic-'+identifier+'.json')
    if not path.is_file():raise HTTPException(404,'该请求的诊断结果尚未返回')
    return json.loads(path.read_text())

def model_asset(robot,uri,snapshot):
    robot=resolve_robot(robot,snapshot)
    description=snapshot['robots'][robot].get('samples',{}).get('robot_description',{}).get('value','')
    allowed={m.attrib.get('filename') for m in ET.fromstring(description).iter('mesh')}
    if uri not in allowed:raise HTTPException(403,'资源不属于该车模型')
    cache=DATA/'rmf_web/model-assets';cache.mkdir(exist_ok=True)
    path=cache/hashlib.sha256((robot+'|'+uri).encode()).hexdigest()
    if not path.exists():
        config=json.loads((WS/'src/system/omnifleet_rmf_adapter/config/framework.json').read_text())
        script='''from pathlib import Path
import sys
from ament_index_python.packages import get_package_share_directory
uri=URI
if uri.startswith('package://'):
 package,relative=uri[10:].split('/',1);base=Path(get_package_share_directory(package));target=(base/relative).resolve()
 assert target.is_relative_to(base.resolve())
elif uri.startswith('file://'):target=Path(uri[7:])
else:target=Path(uri)
assert target.is_file() and target.stat().st_size<=16000000
sys.stdout.buffer.write(target.read_bytes())
'''.replace('URI',repr(uri))
        process=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5',config['robots'][robot]['host'],
          'source /home/iecme/omnifleet_ws/src/system/workspace_support/robot_fleet_env.bash; python3 -'],input=script.encode(),capture_output=True,timeout=20)
        if process.returncode:raise HTTPException(502,'本车模型资源暂时不可读取')
        temporary=path.with_suffix('.tmp');temporary.write_bytes(process.stdout);temporary.replace(path)
    return path.read_bytes()

@router.get('/asset/{robot}')
async def asset(robot:str,uri:str):
    snapshot=await asyncio.to_thread(central,'/state')
    return Response(await asyncio.to_thread(model_asset,robot,uri,snapshot),media_type='application/octet-stream',headers={'Cache-Control':'private,max-age=3600'})
