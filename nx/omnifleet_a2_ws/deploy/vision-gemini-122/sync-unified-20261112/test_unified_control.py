"""Exercise the actual native controller in an isolated, motion-disabled ROS domain."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

os.environ.update(ROS_DOMAIN_ID='84', RMW_IMPLEMENTATION='rmw_fastrtps_cpp', ROS_LOCALHOST_ONLY='1')
import rclpy
from ai_msgs.msg import PerceptionTargets, Target, Roi, Attribute
from std_msgs.msg import String, Empty, Header
from geometry_msgs.msg import Twist

workspace=Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/sync-unified-20261112/source'
log=workspace.parent/'unified-native-test.log'
stream=log.open('w')
process=subprocess.Popen([str(workspace/'build/body_tracking/body_tracking'),'--ros-args',
    '-r','__ns:=/unified_test','--params-file',str(workspace/'src/perception/omnifleet_person_follow/config/body_tracking_104.yaml'),
    '-p','enable_motion:=false','-p','follow_distance:=1.5',
    '-p','ai_msg_sub_topic_name:=/unified_test/targets',
    '-r','body_tracking_cmd:=/unified_test/cmd','-r','body_tracking_state:=/unified_test/state',
    '-r','/cmd_vel:=/unified_test/disabled_velocity',
    '-r','/vision/body_tracking/cancel:=/unified_test/cancel','--log-level','error'],stdout=stream,stderr=subprocess.STDOUT)
try:
    rclpy.init();node=rclpy.create_node('unified_native_test')
    states=[];commands=[];physical=[]
    node.create_subscription(String,'/unified_test/state',lambda m:states.append(json.loads(m.data)),10)
    node.create_subscription(Twist,'/unified_test/cmd',lambda m:commands.append((m.linear.x,m.angular.z)),10)
    node.create_subscription(Twist,'/unified_test/disabled_velocity',lambda m:physical.append(m),10)
    publisher=node.create_publisher(PerceptionTargets,'/unified_test/targets',10)
    cancel=node.create_publisher(Empty,'/unified_test/cancel',10)
    end=time.monotonic()+8
    while publisher.get_subscription_count()==0 and time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
    assert publisher.get_subscription_count(), 'controller discovery'

    def frame(code,body=True):
        message=PerceptionTargets(header=Header(stamp=node.get_clock().now().to_msg(),frame_id='camera'))
        if body:
            roi=Roi(type='body',confidence=1.);roi.rect.x_offset=800;roi.rect.y_offset=200;roi.rect.width=320;roi.rect.height=700
            message.targets.append(Target(type='person',track_id=11,rois=[roi],attributes=[
                Attribute(type='range_base_m',value=1.5,confidence=1.),
                Attribute(type='range_age_s',value=0.,confidence=1.),
                Attribute(type='bearing_rad',value=0.,confidence=1.)]))
        if code is None:
            message.targets.append(Target(type='hand_observation',attributes=[Attribute(type='hand_gesture_observation',value=0.,confidence=1.)]))
        else:
            roi=Roi(type='hand',confidence=1.);roi.rect.x_offset=930;roi.rect.y_offset=300;roi.rect.width=70;roi.rect.height=120
            message.targets.append(Target(type='hand',track_id=11,rois=[roi],attributes=[
                Attribute(type='gesture',value=float(code),confidence=1.),Attribute(type='body_track_id',value=11.,confidence=1.)]))
        return message

    results=[]
    def check(name,code,active,motion=None,body=True):
        start=len(commands)
        for _ in range(9):
            publisher.publish(frame(code,body));until=time.monotonic()+.08
            while time.monotonic()<until:rclpy.spin_once(node,timeout_sec=.01)
        assert states, (name,'no status')
        state=states[-1]
        assert state.get('operator_mode')=='unified',(name,state)
        assert state.get('follow_active') is active,(name,state)
        assert state.get('motion_enabled') is False,(name,state)
        if motion is not None:
            assert commands,(name,'no preview')
            x,z=commands[-1]
            assert abs(z)<1e-8,(name,'unexpected rotation',commands[-1])
            assert (x>0 if motion==1 else x<0 if motion==-1 else abs(x)<1e-8),(name,commands[-1])
        results.append(dict(test=name,follow_active=active,last_command=commands[-1] if commands else None))
        print('PASS',results[-1],flush=True)

    check('idle 1 forward',101,False,1)
    check('idle 2 reverse',102,False,-1)
    check('hand lowered stops',None,False,0)
    check('OK enters follow',11,True)
    check('following ignores 1',101,True,0)
    check('following ignores 2',102,True,0)
    check('missing target does not enable digits',101,True,0,False)
    check('palm exits follow',5,False,0)
    check('idle 2 works after palm',102,False,-1)
    check('idle palm stops',5,False,0)
    assert not physical,'motion-disabled controller published physical velocity'
    (log.parent/'unified-native-test.json').write_text(json.dumps(results,indent=2))
    print('ALL_UNIFIED_TESTS_PASS',flush=True)
finally:
    process.send_signal(signal.SIGINT)
    try:process.wait(timeout=8)
    except subprocess.TimeoutExpired:process.kill();process.wait()
    stream.close()
