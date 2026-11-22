import json,threading,time
from http.client import HTTPConnection
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
from rosidl_runtime_py.utilities import get_message as ros_message,get_service as ros_service,get_action
from rclpy.serialization import serialize_message,deserialize_message
_client_lock=threading.RLock()

def get_service(name):
    if '/action/' in name:
        for suffix,attribute in (('_SendGoal','SendGoalService'),('_GetResult','GetResultService')):
            if name.endswith(suffix):return getattr(get_action(name[:-len(suffix)]).Impl,attribute)
    return ros_service(name)

def get_message(name):
    if '/action/' in name and name.endswith('_FeedbackMessage'):
        return get_action(name[:-len('_FeedbackMessage')]).Impl.FeedbackMessage
    return ros_message(name)

def qos(latched=False):
    return QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE if latched else ReliabilityPolicy.BEST_EFFORT,
                      durability=DurabilityPolicy.TRANSIENT_LOCAL if latched else DurabilityPolicy.VOLATILE)

def pub_qos(latched=False):
    profile=qos(latched);profile.reliability=ReliabilityPolicy.RELIABLE;return profile

def http(port,path,body=b'',headers=None,timeout=4):
    conn=HTTPConnection('127.0.0.1',port,timeout=timeout)
    try:
        conn.request('POST' if body or headers else 'GET',path,body=body,headers=headers or {})
        response=conn.getresponse();data=response.read()
        if response.status!=200:raise RuntimeError(data.decode(errors='replace'))
        return data
    finally:conn.close()

def call_ros(node,clients,name,typename,body,timeout=15):
    with _client_lock:
        if name not in clients:
            kind=get_service(typename);clients[name]=(kind,node.create_client(kind,name))
    kind,client=clients[name]
    if not client.wait_for_service(timeout_sec=1):raise RuntimeError('service unavailable: '+name)
    request=deserialize_message(body,kind.Request)
    future=client.call_async(request);event=threading.Event();future.add_done_callback(lambda _:event.set())
    if not event.wait(timeout):
        client.remove_pending_request(future);raise RuntimeError('service timeout: '+name)
    return serialize_message(future.result())

def error_response(response,error):
    if hasattr(response,'success'):response.success=False
    if hasattr(response,'accepted'):response.accepted=False
    if hasattr(response,'return_code'):response.return_code=1
    if hasattr(response,'message'):response.message=str(error)
    return response

def input_types(robot):
    names={'cmd_vel':'geometry_msgs/msg/Twist','goal_pose':'geometry_msgs/msg/PoseStamped',
           'initialpose':'geometry_msgs/msg/PoseWithCovarianceStamped','clicked_point':'geometry_msgs/msg/PointStamped',
           'planner_selector':'std_msgs/msg/String','controller_selector':'std_msgs/msg/String','navigation/estop':'std_msgs/msg/Bool'}
    for name in ('next_name','rename','navigate_to'):names['omnifleet_t2/waypoints/'+name]='std_msgs/msg/String'
    for name in ('start','stop','undo','clear'):names['omnifleet_t2/waypoints/'+name]='std_msgs/msg/Empty'
    names['omnifleet_t2/waypoints/add_pose']='geometry_msgs/msg/PoseStamped'
    return {'/'+key:value for key,value in names.items()}
