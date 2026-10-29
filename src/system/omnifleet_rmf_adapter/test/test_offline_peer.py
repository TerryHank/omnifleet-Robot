import json
from types import SimpleNamespace as NS

from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
from omnifleet_rmf_adapter.map_hub import MapHub


def test_reference_offline_keeps_other_robot_coordinates_and_last_body(tmp_path):
    config={'central':{'reference_robot':'b','assignments':{r:{'namespace':'/'+r,'robot_name':r} for r in ('a','b')}},'robots':{r:{'enabled':True} for r in ('a','b')}}
    node=NS(create_publisher=lambda *a:NS(publish=lambda m:None),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    hub=MapHub(node,config,tmp_path)
    states={r:{'online':True,'fresh':{'map':True},'samples':{'navigation':{'value':{'localization_epoch':r}},
        'pose':{'value':{'x':x,'y':2.,'yaw':0.}}}} for r,x in [('a',2.),('b',5.)]}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a','b':'b'},'transforms':{'a':[0.,0.,0.],'b':[0.,0.,0.]}}))
    for r in ('a','b'):
        folder=tmp_path/'vehicle-cache'/r;folder.mkdir(parents=True)
        grid=OccupancyGrid();grid.info.width=grid.info.height=100;grid.info.resolution=.1;grid.info.origin.orientation.w=1.;grid.data=[0]*10000
        hub.maps[r]=grid
    hub.tick(states)
    before=hub.state['peer_occupied_cells']['a']
    states['b'].update(online=False,fresh={'map':False});hub.last_map_publish=0.;hub.tick(states)
    assert hub.valid_robots == {'a'}
    assert hub.state['held_offline_robots'] == ['b']
    assert hub.state['peer_occupied_cells']['a'] > before > 0
    receipt=json.loads((tmp_path/'vehicle-cache/a/map_transfer.json').read_text())
    assert receipt['alignment_valid'] and not receipt['reference_map_fresh']
    restored=MapHub(node,config,tmp_path)
    assert restored.held_peers['b'] == [5.,2.,0.]
    states['b']['samples']['navigation']['value']['localization_epoch']='rebooted'
    hub.transforms(states)
    assert not hub.valid_robots


def test_reference_payload_expiry_retains_the_observed_epoch_and_reboot_invalidates(tmp_path):
    config={'central':{'reference_robot':'b','assignments':{r:{'namespace':'/'+r,'robot_name':r} for r in ('a','b')}},'robots':{r:{'enabled':True} for r in ('a','b')}}
    node=NS(create_publisher=lambda *a:NS(publish=lambda m:None),get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    hub=MapHub(node,config,tmp_path)
    states={r:{'online':True,'fresh':{'map':True},'samples':{'navigation':{'value':{'localization_epoch':r}},
        'pose':{'value':{'x':x,'y':2.,'yaw':0.}}}} for r,x in [('a',2.),('b',5.)]}
    (tmp_path/'fleet_alignment.json').write_text(json.dumps({'validated':True,'epochs':{'a':'a','b':'b'},'transforms':{'a':[0.,0.,0.],'b':[0.,0.,0.]}}))
    for r in ('a','b'):
        folder=tmp_path/'vehicle-cache'/r;folder.mkdir(parents=True)
        grid=OccupancyGrid();grid.info.width=grid.info.height=100;grid.info.resolution=.1;grid.info.origin.orientation.w=1.;grid.data=[0]*10000
        hub.maps[r]=grid
    hub.tick(states)
    anchor=states.pop('b')
    hub.last_map_publish=0.;hub.tick(states)
    assert hub.valid_robots == {'a'} and hub.reference_epoch == 'b'
    restored=MapHub(node,config,tmp_path)
    restored.transforms(states)
    assert restored.valid_robots == {'a'}
    states['b']=anchor
    states['b']['samples']['navigation']['value']['localization_epoch']='b-rebooted'
    hub.last_map_publish=0.;hub.tick(states)
    assert not hub.valid_robots.intersection({'a'})
    states.pop('b')
    hub.transforms(states)
    assert not hub.valid_robots
    restored=MapHub(node,config,tmp_path)
    restored.transforms(states)
    assert not restored.valid_robots
