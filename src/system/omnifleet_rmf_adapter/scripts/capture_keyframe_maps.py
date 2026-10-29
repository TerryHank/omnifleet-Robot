"""Capture current-session accumulated maps through each independent ROS domain."""
import base64,json,math,os,subprocess,sys,time
from pathlib import Path
from omnifleet_rmf_adapter.state import connection_states
from omnifleet_rmf_adapter.registration import registration_pair
config_path=Path(os.environ['OMNIFLEET_CONFIG']);settings=json.loads(config_path.read_text());data=Path(os.environ['OMNIFLEET_DATA'])
if len(sys.argv)==1:
    members=set(registration_pair(settings)) if os.environ.get('OMNIFLEET_REGISTRATION_SOURCE') else set(settings['robots'])
    for robot,profile in settings['robots'].items():
        if profile['enabled'] and robot in members:
            result=subprocess.run([sys.executable,__file__,robot],timeout=65.)
            if result.returncode:raise SystemExit(result.returncode)
else:
    robot=sys.argv[1];profile=settings['robots'][robot]
    runtime=data/'run/discovery'/(robot+'.json')
    if runtime.exists():profile={**profile,**json.loads(runtime.read_text())}
    os.environ.update(ROS_DOMAIN_ID=str(profile['domain_id']),RMW_IMPLEMENTATION=profile['rmw'],ROS_LOCALHOST_ONLY='0',ZENOH_SESSION_CONFIG_URI=str(config_path.parent/profile['zenoh_config']))
    import rclpy
    from std_srvs.srv import Trigger
    from rclpy.serialization import deserialize_message
    from sensor_msgs.msg import PointCloud2
    def stationary():
        report=json.loads((data/'connection_status.json').read_text());assert 0<=time.time()-report['wall_time_seconds']<3.
        state=connection_states(report)[robot];control=state['samples']['control']['value'];nav=state['samples']['navigation']['value']
        assert state['online'] and all(state['fresh'].get(k) for k in ('map','pose','navigation','control'))
        assert not nav.get('navigation_active') and not control.get('nav_active'), robot+': navigation is active'
        assert control.get('stopped_seconds',0)>.3, robot+': fresh stopped-wheel feedback is required'
        velocity=control.get('velocity',[])
        assert len(velocity)==2 and all(math.isfinite(v) and abs(v)<.01 for v in velocity), robot+': wheels are moving or feedback is invalid'
        return state
    before=stationary();rclpy.init();node=rclpy.create_node('keyframe_alignment_capture_'+robot)
    client=node.create_client(Trigger,profile['observed_namespace']+'/fleet/alignment_map_snapshot')
    assert client.wait_for_service(timeout_sec=5.),'Keyframe map snapshot service is unavailable'
    future=client.call_async(Trigger.Request());rclpy.spin_until_future_complete(node,future,timeout_sec=50.)
    assert future.done(),'Keyframe map export timed out';response=future.result();assert response.success,response.message
    payload=json.loads(response.message);after=stationary()
    epoch=before['samples']['navigation']['value']['localization_epoch']
    assert epoch==after['samples']['navigation']['value']['localization_epoch']==payload['epoch']
    a,b=before['samples']['pose']['value'],after['samples']['pose']['value']
    assert math.dist([a['x'],a['y']],[b['x'],b['y']])<.05
    assert abs(math.atan2(math.sin(a['yaw']-b['yaw']),math.cos(a['yaw']-b['yaw'])))<.03
    cloud=base64.b64decode(payload.pop('cloud_cdr_base64'),validate=True);message=deserialize_message(cloud,PointCloud2)
    assert message.header.frame_id=='map' and message.width*message.height==payload['points'] and payload['points']>80
    folder=data/'alignment';(folder/(robot+'-keyframe-cloud.cdr')).write_bytes(cloud)
    (folder/(robot+'-keyframe-capture.json')).write_text(json.dumps({**payload,'pose':b}))
    print(robot+': captured current keyframe map, '+str(payload['points'])+' points',flush=True)
    os._exit(0)
