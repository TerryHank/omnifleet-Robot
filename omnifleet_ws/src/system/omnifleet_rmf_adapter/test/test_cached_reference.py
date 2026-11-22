import json
from types import SimpleNamespace as NS
from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
from rclpy.serialization import serialize_message
from omnifleet_rmf_adapter.map_hub import MapHub

def test_restart_keeps_valid_static_reference_cache_when_reference_robot_is_offline(tmp_path):
    published={}
    def create(kind,topic,qos):
        published[topic]=[];return NS(publish=lambda m:published[topic].append(m))
    node=NS(create_publisher=create,get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    config={'central':{'reference_robot':'a','assignments':{r:{'namespace':'/'+r,'robot_name':r} for r in ('a','b')}},'robots':{r:{'enabled':True} for r in ('a','b')}}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a-epoch','b':'b-epoch'},'transforms':{'a':[0.,0.,0.],'b':[0.,0.,0.]}}))
    (tmp_path/'map_hub_status.json').write_text(json.dumps({'last_known_poses':{'a':[5.,5.,0.]}}))
    states={}
    for r in ('a','b'):
        folder=tmp_path/'vehicle-cache'/r;folder.mkdir(parents=True)
        grid=OccupancyGrid();grid.header.frame_id='map';grid.info.width=grid.info.height=100;grid.info.resolution=.1;grid.info.origin.orientation.w=1.;grid.data=[0]*10000
        (folder/'map.cdr').write_bytes(serialize_message(grid))
        states[r]={'online':r=='b','fresh':{'map':r=='b'},'samples':{'map':{'value':{}},'navigation':{'value':{'localization_epoch':r+'-epoch'}}}}
    states['b']['samples']['pose']={'value':{'x':2.,'y':2.,'yaw':0.}}
    hub=MapHub(node,config,tmp_path);hub.tick(states)
    assert set(hub.maps)=={'a','b'} and 'b' in hub.valid_robots
    assert published['/fleet/map'] and hub.state['reference_map_fresh'] is False
    receipt=json.loads((tmp_path/'vehicle-cache/b/map_transfer.json').read_text())
    assert receipt['alignment_valid'] and receipt['shared_payload_sha256']
    assert receipt['occupied_cells']>0
