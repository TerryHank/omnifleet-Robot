import json,time
from pathlib import Path
import rclpy
from rclpy.qos import qos_profile_sensor_data,QoSProfile,DurabilityPolicy,ReliabilityPolicy
from nav_msgs.msg import Odometry
from action_msgs.msg import GoalStatusArray

def check_stationary():
    rclpy.init();n=rclpy.create_node('configuration_switch_stationary_guard')
    wheel=[];active=[];subs=[]
    ns='/'+__import__('os').environ['OMNIFLEET_ROBOT_ID']
    subs.append(n.create_subscription(Odometry,ns+'/odom',lambda m:wheel.append(m),qos_profile_sensor_data))
    q=QoSProfile(depth=10,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
    for action in ['navigate_to_pose','navigate_through_poses','follow_waypoints']:
        subs.append(n.create_subscription(GoalStatusArray,ns+'/'+action+'/_action/status',lambda m:active.extend(s.status for s in m.status_list if s.status in [1,2,3]),q))
    end=time.monotonic()+3
    while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.05)
    stationary=len(wheel)>=10 and all(abs(m.twist.twist.linear.x)<.005 and abs(m.twist.twist.angular.z)<.005 for m in wheel)
    n.destroy_node();rclpy.shutdown()
    result={'stationary':stationary,'wheel_samples':len(wheel),'active_goals':active}
    assert stationary and not active,'Switch refused: '+json.dumps(result)
    return result

def wait_for_fused():
    rclpy.init();n=rclpy.create_node('configuration_switch_fusion_ready');messages=[]
    ns='/'+__import__('os').environ['OMNIFLEET_ROBOT_ID']
    sub=n.create_subscription(Odometry,ns+'/localization/fused_odom',messages.append,qos_profile_sensor_data)
    end=time.monotonic()+30
    while not messages and time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.1)
    n.destroy_node();rclpy.shutdown()
    assert messages,'Smoother did not produce localization; Nav2 was left stopped'

if __name__=='__main__':
    print(json.dumps(check_stationary()))
