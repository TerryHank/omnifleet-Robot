import json
from types import SimpleNamespace as NS
from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
from omnifleet_rmf_adapter.map_hub import MapHub, peer_grid


def test_neighbour_body_is_retained_when_footprints_overlap(tmp_path):
    config={'central':{'reference_robot':'b','assignments':{r:{'namespace':'/'+r,'robot_name':r} for r in ('a','b')}},'robots':{r:{'enabled':True} for r in ('a','b')}}
    node=NS(create_publisher=lambda *a:NS(publish=lambda m:None),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    hub=MapHub(node,config,tmp_path)
    footprint=[[-.25,-.185],[-.25,.185],[.25,.185],[.25,-.185]]
    states={r:{'online':True,'fresh':{'map':True},'samples':{'navigation':{'value':{'localization_epoch':r}},
        'formation_profile':{'value':{'footprint':footprint,'padding':.02}},
        'pose':{'value':{'x':x,'y':2.,'yaw':0.}}}} for r,x in [('a',2.),('b',2.4)]}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a','b':'b'},'transforms':{'a':[0.,0.,0.],'b':[0.,0.,0.]}}))
    for r in ('a','b'):
        (tmp_path/'vehicle-cache'/r).mkdir(parents=True)
        grid=OccupancyGrid();grid.info.width=grid.info.height=100;grid.info.resolution=.1;grid.info.origin.orientation.w=1.;grid.data=[0]*10000
        hub.maps[r]=grid
    hub.tick(states)
    expected=peer_grid(hub.maps['a'],[([2.4,2.,0.],0.,[-.27,.27,-.205,.205])])
    assert list(hub.peer_maps['a'].data)==list(expected.data)
    assert hub.peer_maps['a'].data[20*100+22]==100
    assert hub.peer_maps['a'].data[20*100+18]==-1
