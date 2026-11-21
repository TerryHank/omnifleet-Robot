import json
from types import SimpleNamespace as NS
from builtin_interfaces.msg import Time
from nav_msgs.msg import OccupancyGrid
from rclpy.serialization import serialize_message
from omnifleet_rmf_adapter.map_hub import MapHub
from omnifleet_rmf_adapter.client import RobotObserver


def test_costmap_cache_does_not_replace_local_map_used_to_clear_peers():
    grid=OccupancyGrid();grid.info.width=grid.info.height=1;grid.data=[0]
    original=object();node=NS(cache_pending={},local_grid=original)
    RobotObserver.cache_message(node,'global_costmap',grid)
    assert node.local_grid is original and node.cache_pending['global_costmap'] is grid


def test_real_cost_values_and_frame_are_relayed_with_dynamic_prefix(tmp_path):
    published={}
    def publisher(kind,topic,qos):
        published[topic]=[];return NS(publish=lambda m:published[topic].append(m))
    node=NS(create_publisher=publisher,get_clock=lambda:NS(now=lambda:NS(to_msg=lambda:Time())))
    config={'central':{'reference_robot':'transport_a','assignments':{'transport_a':{'namespace':'/new_prefix','robot_name':'new_prefix'}}},'robots':{'transport_a':{'enabled':True}}}
    hub=MapHub(node,config,tmp_path)
    cache=tmp_path/'vehicle-cache/transport_a';cache.mkdir(parents=True)
    grid=OccupancyGrid();grid.header.frame_id='odom';grid.info.width=3;grid.info.height=1;grid.info.resolution=.1;grid.data=[0,76,100]
    (cache/'local_costmap.cdr').write_bytes(serialize_message(grid))
    state={'transport_a':{'online':True,'fresh':{'local_costmap':True},'samples':{'local_costmap':{'value':{}},'navigation':{'value':{'localization_epoch':'e'}}}}}
    hub.tick(state)
    result=published['/new_prefix/local_costmap/costmap'][0]
    assert result.header.frame_id=='new_prefix/odom' and list(result.data)==[0,76,100]
    assert not hub.maps
