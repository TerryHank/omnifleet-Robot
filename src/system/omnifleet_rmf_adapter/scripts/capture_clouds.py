import base64
import json
from omnifleet_rmf_adapter.state import connection_states
from omnifleet_rmf_adapter.cloud_quality import scan_quality
import os
from pathlib import Path
import subprocess
import sys
import time
import math

config_path = Path(os.environ['OMNIFLEET_CONFIG'])
settings = json.loads(config_path.read_text())
if len(sys.argv) == 1:
    selected=json.loads(os.environ['OMNIFLEET_REGISTRATION_ROBOTS']) if os.environ.get('OMNIFLEET_REGISTRATION_ROBOTS') else list(settings['robots'])
    for robot, profile in settings['robots'].items():
        if profile['enabled'] and robot in selected:
            result=subprocess.run([sys.executable, __file__, robot], timeout=180)
            if result.returncode:raise SystemExit(result.returncode)
else:
    robot = sys.argv[1]
    config = settings['robots'][robot]
    runtime=Path(os.environ['OMNIFLEET_DATA'])/'run/discovery'/(robot+'.json')
    if runtime.exists():config={**config,**json.loads(runtime.read_text())}
    os.environ.update(ROS_DOMAIN_ID=str(config['domain_id']), RMW_IMPLEMENTATION=config['rmw'], ROS_LOCALHOST_ONLY='0',
                      ZENOH_SESSION_CONFIG_URI=str(config_path.parent/config['zenoh_config']))
    import rclpy
    from rclpy.serialization import deserialize_message, serialize_message
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import PointCloud2
    from std_srvs.srv import Trigger
    rclpy.init()
    node = rclpy.create_node('current_cloud_alignment_capture_'+robot)
    client=node.create_client(Trigger,config['observed_namespace']+'/fleet/alignment_map_snapshot')
    end = time.monotonic()+12
    data=Path(os.environ['OMNIFLEET_DATA'])
    def stationary():
        report=json.loads((data/'connection_status.json').read_text())
        assert 0<=time.time()-report['wall_time_seconds']<3.
        state=connection_states(report)[robot]
        control=state['samples']['control']['value']
        assert state['online'] and all(state['fresh'].get(k) for k in ('pose','navigation','control'))
        # MANUAL is a selected mode, including a released joystick with zero speed.
        assert not control.get('nav_active') and not state['samples']['navigation']['value'].get('navigation_active'), robot+': navigation is active'
        velocity=control.get('velocity',[])
        # The fresh wheel velocity is the direct stationary evidence. The
        # derived stopped_seconds counter can reset while MOLA exports a map.
        assert len(velocity)==2 and all(math.isfinite(v) and abs(v)<.01 for v in velocity), robot+': wheels are moving or feedback is invalid'
        return state
    while True:
        try:
            before=stationary();break
        except AssertionError:
            assert time.monotonic()<end, robot+': vehicle state did not become fresh and stationary'
            rclpy.spin_once(node,timeout_sec=.1)
    assert client.wait_for_service(timeout_sec=10.),robot+': alignment map snapshot service unavailable'
    future=client.call_async(Trigger.Request())
    rclpy.spin_until_future_complete(node,future,timeout_sec=150.)
    assert future.done() and future.exception() is None,robot+': alignment map snapshot timed out'
    response=future.result();assert response.success,robot+': '+response.message
    payload=json.loads(response.message)
    raw=base64.b64decode(payload['cloud_cdr_base64'],validate=True)
    cloud=deserialize_message(raw,PointCloud2)
    assert cloud.width and cloud.row_step==len(cloud.data),robot+': invalid alignment map snapshot'
    quality=scan_quality(cloud)
    after=stationary()
    assert before['samples']['navigation']['value']['localization_epoch']==after['samples']['navigation']['value']['localization_epoch']
    a,b=before['samples']['pose']['value'],after['samples']['pose']['value']
    assert sum((a[k]-b[k])**2 for k in ('x','y'))<.0025
    assert abs(math.atan2(math.sin(a['yaw']-b['yaw']),math.cos(a['yaw']-b['yaw'])))<.03
    suffix='-keyframe' if payload.get('kind')=='current_mola_keyframes' else ''
    p = data/'alignment'/(robot+suffix+'-cloud.cdr')
    p.write_bytes(raw)
    (p.parent/(robot+suffix+'-capture.json')).write_text(json.dumps({'pose':b,'epoch':after['samples']['navigation']['value']['localization_epoch'],
        'capture_kind':payload.get('kind'),'quality':quality,'merged_points':cloud.width,'voxel_m':payload.get('voxel_m')}))
    print(robot,cloud.header.frame_id,'snapshot points',cloud.width,flush=True)
    # Nearby vehicles can share the current scan even when their accumulated
    # maps cover different rooms. Never reuse an earlier raw-scan capture.
    raw_path=data/'alignment'/(robot+'-cloud.cdr')
    raw_meta=data/'alignment'/(robot+'-capture.json')
    raw_path.unlink(missing_ok=True);raw_meta.unlink(missing_ok=True)
    scans=[]
    subscription=node.create_subscription(PointCloud2,config['observed_namespace']+'/fleet/alignment_points',scans.append,qos_profile_sensor_data)
    deadline=time.monotonic()+6.
    while not scans and time.monotonic()<deadline:rclpy.spin_once(node,timeout_sec=.1)
    if scans:
        latest=scans[-1];after=stationary();b=after['samples']['pose']['value']
        assert before['samples']['navigation']['value']['localization_epoch']==after['samples']['navigation']['value']['localization_epoch']
        assert sum((a[k]-b[k])**2 for k in ('x','y'))<.0025
        assert abs(math.atan2(math.sin(a['yaw']-b['yaw']),math.cos(a['yaw']-b['yaw'])))<.03
        assert latest.header.frame_id=='rslidar'
        raw_path.write_bytes(serialize_message(latest))
        raw_meta.write_text(json.dumps({'pose':b,'epoch':after['samples']['navigation']['value']['localization_epoch'],
                                      'capture_kind':'current_raw_lidar','quality':scan_quality(latest)}))
        print(robot,'fresh raw scan points',latest.width,flush=True)
    node.destroy_node();rclpy.shutdown()
