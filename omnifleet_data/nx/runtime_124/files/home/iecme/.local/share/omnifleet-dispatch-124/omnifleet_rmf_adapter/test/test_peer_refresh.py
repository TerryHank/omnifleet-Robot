import hashlib,json
from types import SimpleNamespace as NS
from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
from omnifleet_rmf_adapter.map_hub import MapHub

def test_moving_peer_updates_after_two_tenths_without_breaking_map_transfer_hashes(tmp_path,monkeypatch):
    clock=[100.];monkeypatch.setattr('omnifleet_rmf_adapter.map_hub.time.monotonic',lambda:clock[0])
    config={'central':{'reference_robot':'a','assignments':{r:{'namespace':'/dynamic_'+r,'robot_name':'dynamic_'+r} for r in ('a','b')}},'robots':{r:{'enabled':True} for r in ('a','b')}}
    node=NS(create_publisher=lambda *a:NS(publish=lambda m:None),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    hub=MapHub(node,config,tmp_path)
    states={r:{'online':True,'fresh':{'map':True},'samples':{'navigation':{'value':{'localization_epoch':r}},'pose':{'value':{'x':x,'y':2.,'yaw':0.}}}} for r,x in [('a',5.),('b',2.)]}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a','b':'b'},'transforms':{'a':[0.,0.,0.],'b':[0.,0.,0.]}}))
    for r in ('a','b'):
        (tmp_path/'vehicle-cache'/r).mkdir(parents=True)
        grid=OccupancyGrid();grid.info.width=grid.info.height=100;grid.info.resolution=.1;grid.info.origin.orientation.w=1.;grid.data=[0]*10000;hub.maps[r]=grid
    hub.tick(states);cache=tmp_path/'vehicle-cache/b';old=(cache/'peer_map_out.cdr').read_bytes()
    states['a']['samples']['pose']['value']['x']=5.2;clock[0]+=.2;hub.tick(states)
    peer=(cache/'peer_map_out.cdr').read_bytes();assert peer!=old
    receipt=json.loads((cache/'map_transfer.json').read_text())
    assert receipt['peer_payload_sha256']==hashlib.sha256(peer).hexdigest()
    assert receipt['shared_payload_sha256']==hashlib.sha256((cache/'shared_map_out.cdr').read_bytes()).hexdigest()
