from pathlib import Path
from types import SimpleNamespace as NS
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from target_sparse_depth_node import TargetSparseDepthNode


def receiver():
    output=[]
    node=NS(depths=[],color_info=NS(header=NS(frame_id='rgb'),width=1920),depth_info=None,
        transform=None,native_subscriptions=None,minimum=.2,maximum=3.5,range_pub=None,
        get_clock=lambda:NS(now=lambda:NS(nanoseconds=100_000_000_000)),
        publisher=NS(publish=lambda m:output.append(json.loads(m.data))))
    calls=[]
    def subscribe():node.native_subscriptions=[];calls.append(True)
    node.subscribe_native=subscribe
    return node,output,calls


def test_measured_foreground_is_forwarded_without_duplicate_native_subscription():
    node,output,calls=receiver()
    message=NS(data=json.dumps(dict(source_stamp=10.,foreground_depth_ready=True,
        tracks=[dict(track_id=7,bbox=[100,100,40,60],foreground=dict(
            depth_stamp=10.,depth_m=.92,rgb_xyz_m=[0.,0.,.92],sampled_count=165))])))
    TargetSparseDepthNode.on_target(node,message)
    assert calls==[] and output[0]['calibration_ready']
    assert output[0]['detections'][0]['depth_m']==.92
    assert output[0]['detections'][0]['sampled_count']==165


def test_legacy_input_keeps_native_query_path_but_subscribes_once():
    node,output,calls=receiver()
    message=NS(data=json.dumps(dict(source_stamp=10.,tracks=[dict(track_id=7,bbox=[100,100,40,60])])))
    TargetSparseDepthNode.on_target(node,message)
    TargetSparseDepthNode.on_target(node,message)
    assert calls==[True] and output[0]['detections'][0]['depth_m'] is None


def test_range_age_uses_measured_depth_timestamp_not_newer_rgb_timestamp():
    node,_,_=receiver();ranges=[]
    node.range_pub=NS(publish=ranges.append)
    message=NS(data=json.dumps(dict(source_stamp=10.,tracks=[dict(track_id=7,
        foreground=dict(depth_stamp=9.95,depth_m=.92,rgb_xyz_m=[0.,0.,.92],sampled_count=165))])))
    TargetSparseDepthNode.on_target(node,message)
    assert ranges[0].header.stamp.sec==9
    assert ranges[0].header.stamp.nanosec==950_000_000
