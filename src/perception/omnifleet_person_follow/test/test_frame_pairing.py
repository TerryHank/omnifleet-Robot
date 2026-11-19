from collections import OrderedDict
import threading
from types import SimpleNamespace as NS
import numpy as np
from omnifleet_person_follow.node import PersonFollowNode
from omnifleet_person_follow.core import FollowManager


def frame(n, depth=False):
    return NS(header=NS(stamp=NS(sec=1,nanosec=n),frame_id='camera'),
              encoding='16UC1' if depth else 'bgr8',width=12,height=12,step=24,is_bigendian=False,
              data=np.full((12,12),1000,np.uint16).tobytes())


def test_rgb_never_waits_for_depth_and_only_equal_stamps_fuse():
    node = PersonFollowNode.__new__(PersonFollowNode)
    node.tros = None
    node.lock, node.event = threading.RLock(), threading.Event()
    node.fusion_cache, node.depths, node.positions = OrderedDict(), OrderedDict(), {}
    node.latest, node.dropped, node.rgb_received = None, 0, 0
    node.fused_pairs = 0
    node.depth_query_calls,node.depth_query_ms,node.depth_query_result = 0,0.,None
    node.manager = FollowManager(state='TRACKING',track_id=7)
    node.minimum,node.maximum,node.global_frame = .2,1.5,'map'
    node.info = NS(width=12,height=12,k=[100,0,6,0,100,6,0,0,1])
    node.depth_k = np.array(node.info.k).reshape(3,3)
    node.depth_to_rgb,node.native_depth_size = np.eye(4),(12,12)
    node.tf = NS(lookup_transform=lambda *args:NS(transform=NS(
        rotation=NS(x=0.,y=0.,z=0.,w=1.),translation=NS(x=0.,y=0.,z=0.))))
    rgb1, rgb2 = frame(1), frame(2)
    node.on_image(rgb1)
    assert node.latest is rgb1
    node.on_image(rgb2)
    assert node.latest is rgb2 and node.dropped == 1
    tracks=[dict(id=7,bbox=[0,0,12,12],mask=np.ones((12,12),bool))]
    node.fusion_cache[node.key(rgb1)] = tracks,(12,12,3),rgb1.header
    d1, d2 = frame(1,True), frame(2,True)
    node.on_depth(d2)
    assert not node.positions
    node.on_depth(d1)
    np.testing.assert_allclose(node.positions[7]['xyz'],[-.005,-.005,1.],atol=1e-10)
    assert node.fused_pairs == 1 and node.positions[7]['depth_key'] == (1,1)
    assert node.depth_query_calls == 1
    assert node.depth_query_result['grid_size'] == 16
    assert node.depth_query_result['inspected_pixels'] <= 256
    node.manager.state = 'PAUSED'
    rgb3 = frame(3)
    node.fusion_cache[node.key(rgb3)] = tracks,(12,12,3),rgb3.header
    node.on_depth(frame(3,True))
    assert node.depth_query_calls == 1
    node.manager.state,node.manager.track_id = 'IDLE',None
    rgb4 = frame(4)
    node.fusion_cache[node.key(rgb4)] = tracks,(12,12,3),rgb4.header
    node.on_depth(frame(4,True))
    assert node.depth_query_calls == 1


def test_lost_candidate_depth_is_sparse_rate_limited_and_does_not_change_identity(monkeypatch):
    node = PersonFollowNode.__new__(PersonFollowNode)
    node.tros = None
    node.lock = threading.RLock()
    node.fusion_cache, node.depths, node.positions = OrderedDict(), OrderedDict(), {}
    node.fused_pairs = 0
    node.depth_query_calls, node.depth_query_ms, node.depth_query_result = 0, 0., None
    node.manager = FollowManager(state='LOST', track_id=7)
    node.minimum, node.maximum, node.global_frame = .2, 1.5, 'map'
    node.info = NS(width=12,height=12,k=[100,0,6,0,100,6,0,0,1])
    node.depth_k = np.array(node.info.k).reshape(3,3)
    node.depth_to_rgb, node.native_depth_size = np.eye(4),(12,12)
    node.tf = NS(lookup_transform=lambda *args:NS(transform=NS(
        rotation=NS(x=0.,y=0.,z=0.,w=1.),translation=NS(x=0.,y=0.,z=0.))))
    clock = [10.]
    monkeypatch.setattr('omnifleet_person_follow.node.time.monotonic',lambda:clock[0])
    candidate = dict(id=8,bbox=[0,0,12,12],mask=np.ones((12,12),bool),confidence=.9)
    for index in [1,2]:
        rgb = frame(index)
        node.fusion_cache[node.key(rgb)] = [candidate],(12,12,3),rgb.header
        node.on_depth(frame(index,True))
        clock[0] += .02
    assert node.depth_query_calls == node.candidate_depth_queries == 1
    assert node.depth_query_result['inspected_pixels'] <= 256
    assert 'world' in node.positions[8] and node.manager.track_id == 7
