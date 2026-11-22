"""Dispatch the existing on-board permanent parameter service across ROS domains."""
import json
import math
import time
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from rcl_interfaces.msg import Parameter, ParameterValue
from rcl_interfaces.srv import SetParameters
from std_srvs.srv import Trigger


FIELDS = [
    {'id':'geometry_local_inflation_radius','label':'障碍膨胀半径','type':'double','unit':'m','min':0.,'max':3.,'step':.01},
    {'id':'costmap_scaling','label':'膨胀代价衰减系数','type':'double','min':.01,'max':20.,'step':.1},
    {'id':'geometry_local_footprint','label':'车体轮廓 footprint','type':'string'},
    {'id':'geometry_local_robot_radius','label':'圆形车体半径（空轮廓时使用）','type':'double','unit':'m','min':.001,'max':3.,'step':.001},
    {'id':'geometry_local_footprint_padding','label':'额外车体余量','type':'double','unit':'m','min':0.,'max':.3,'step':.01},
    {'id':'geometry_mppi_consider_footprint','label':'MPPI 完整车体碰撞检查','type':'bool'},
]
SPECS = {field['id']:field for field in FIELDS}
SCHEMA = json.loads((Path(get_package_share_directory('omnifleet_rmf_adapter'))/'config/navigation-schema.json').read_text())
for field in SCHEMA['fields']:
    if field['id'] not in SPECS:
        field={**field,'type':{'boolean':'bool','number':'double'}.get(field['type'],field['type'])}
        SPECS[field['id']]=field
for kind,key in (('global','global_planner_algorithm'),('local','local_controller_algorithm')):
    SPECS[key]={'id':key,'type':'string','choices':list(SCHEMA['algorithms'][kind])}
for key,choices in {'__navigation_strategy':['sequential','through_poses'],'__navigation_strategy_status':[''],
                    '__stack_command':None,'__stack_restart':None,'__stack_status':['']}.items():
    SPECS[key]={'id':key,'type':'string','choices':choices}
BINDINGS = {'costmap_scaling':('local_scaling','global_scaling')}
BINDINGS.update(costmap_radius=('local_radius','global_radius'),costmap_padding=('local_padding','global_padding'))
for suffix in ('footprint','robot_radius','footprint_padding','inflation_radius'):
    BINDINGS['geometry_local_'+suffix]=('geometry_local_'+suffix,'geometry_global_'+suffix)
SAVED_KEYS = set(SPECS) | {'local_radius','global_radius','local_padding','global_padding','geometry_global_footprint','geometry_global_robot_radius',
    'geometry_global_footprint_padding','geometry_global_inflation_radius','local_scaling','global_scaling'}


def validate_changes(changes):
    if not isinstance(changes,dict) or not changes:raise ValueError('没有要保存的参数')
    if '__collision_model' in changes:
        if len(changes)!=1 or changes['__collision_model'] not in ('point','body'):
            raise ValueError('碰撞模型预设需单独保存，支持 point 或 body')
        return changes
    for key,value in changes.items():
        if key not in SPECS:raise ValueError('不属于远离障碍与碰撞模型的参数：'+key)
        field=SPECS[key];kind=field['type']
        if kind=='bool':valid=type(value) is bool
        elif kind=='string':valid=isinstance(value,str) and len(value)<=4096 and (not field.get('choices') or value in field['choices'])
        elif kind=='integer':valid=type(value) is int and field['min']<=value<=field['max']
        else:valid=type(value) in (int,float) and math.isfinite(value) and field['min']<=value<=field['max']
        if not valid:raise ValueError('参数类型或范围无效：'+key)
    return changes


def compact_receipt(receipt):
    result={key:receipt[key] for key in ('path','backup','sha256','runtime','runtime_confirmed','message','algorithms','restart_required','service_result','navigation_strategy') if key in receipt}
    if 'saved' in receipt:
        result['saved']={key:value for key,value in receipt['saved'].items() if key in SAVED_KEYS}
        local=receipt['saved'].get('local_scaling');global_=receipt['saved'].get('global_scaling')
        if local is not None and local==global_:result['saved']['costmap_scaling']=local
        for alias,keys in (('costmap_radius',('local_radius','global_radius')),('costmap_padding',('local_padding','global_padding'))):
            values=[receipt['saved'].get(key) for key in keys]
            if values[0] is not None and values[0]==values[1]:result['saved'][alias]=values[0]
    if 'collision_model' in receipt:
        result['collision_model']={key:value for key,value in receipt['collision_model'].items()
            if key in ('mode','restore_available','message','restart_required')}
    return result


class ParameterClient:
    def __init__(self,node):
        self.node=node
        prefix=node.profile['observed_namespace']+'/omnifleet_t2/nav2/'
        self.reader=node.create_client(Trigger,prefix+'read_saved')
        self.writer=node.create_client(SetParameters,prefix+'save_parameters')
        self.pending=None;self.snapshot={}
        node.create_timer(.2,self.tick)

    def request(self,packet):
        identifier=packet['id']
        try:
            if self.pending:raise ValueError('该车参数服务请求正在处理，请等待回执')
            read=packet['op']=='nav_parameters_read'
            client=self.reader if read else self.writer
            if not client.service_is_ready():raise ValueError('本车永久导航参数服务尚未连接')
            request=Trigger.Request() if read else SetParameters.Request()
            if not read:
                for key,value in validate_changes(packet.get('changes')).items():
                    names=BINDINGS.get(key,(key,))
                    saved=self.snapshot.get('saved',{})
                    if all(name in saved and next(iter(saved[name].values()))==value for name in names):continue
                    if key=='__collision_model' or SPECS[key]['type']=='string':parameter=ParameterValue(type=4,string_value=value)
                    elif SPECS[key]['type']=='bool':parameter=ParameterValue(type=1,bool_value=value)
                    elif SPECS[key]['type']=='integer':parameter=ParameterValue(type=2,integer_value=value)
                    else:parameter=ParameterValue(type=3,double_value=float(value))
                    for name in names:request.parameters.append(Parameter(name=name,value=parameter))
                if not request.parameters:
                    self.finish(identifier,'saved',runtime={},runtime_confirmed=False,message='本车永久配置已一致，未改变运行参数')
                    return
            self.pending={'id':identifier,'read':read,'service':not read and any(k.startswith('__') and k!='__collision_model' for k in packet['changes']),
                          'future':client.call_async(request),'client':client,'deadline':time.monotonic()+45.}
        except (ValueError,TypeError) as error:self.finish(identifier,'rejected',message=str(error))

    def finish(self,identifier,phase,**receipt):
        self.snapshot.pop('service_result',None)
        self.snapshot.update(compact_receipt(receipt))
        self.node.record('navigation_parameters',{**self.snapshot,'request_id':identifier,'phase':phase,
            'message':receipt.get('message','已读取永久参数' if phase=='read' else '已写入本车永久参数')})

    def tick(self):
        pending=self.pending
        if not pending:return
        if not pending['future'].done():
            if time.monotonic()<=pending['deadline']:return
            pending['client'].remove_pending_request(pending['future']);self.pending=None
            self.finish(pending['id'],'failed',message='永久参数服务回执超时，保存结果未确认；请重新读取')
            return
        self.pending=None
        try:
            response=pending['future'].result()
            if pending['read']:
                if not response.success:raise ValueError(response.message)
                receipt=json.loads(response.message)
            else:
                if not response.results or any(not item.successful for item in response.results):
                    raise ValueError('; '.join(item.reason for item in response.results) or '保存未确认')
                receipt=json.loads(response.results[0].reason)
            if pending['service']:self.finish(pending['id'],'completed',service_result=receipt,message=receipt.get('message','已收到本车服务回执'))
            else:self.finish(pending['id'],'read' if pending['read'] else 'saved',**receipt)
        except Exception as error:self.finish(pending['id'],'failed',message=str(error))


class ParameterCommands:
    def __init__(self,send):self.send=send;self.pending={}

    def request(self,packet,states):
        robot=packet.get('robot_id')
        if robot not in states or not states[robot].get('transport_connected'):raise ValueError('车辆接入未连接')
        if packet['op']=='nav_parameters_save':validate_changes(packet.get('changes'))
        if any(p['robot']==robot for p in self.pending.values()):raise ValueError('该车参数请求尚未完成')
        identifier=packet['id']
        if not self.send(packet['op'],identifier,robot_id=robot,changes=packet.get('changes')):
            raise ValueError('车辆参数接入端不可用')
        self.pending[identifier]={'robot':robot,'deadline':time.monotonic()+50.}
        return {'phase':'forwarding','message':'已发送至本车永久参数服务，等待保存或读取回执'}

    def tick(self,states,results):
        for identifier,pending in list(self.pending.items()):
            sample=states.get(pending['robot'],{}).get('samples',{}).get('navigation_parameters',{}).get('value',{})
            if sample.get('request_id')==identifier:
                results[identifier]={k:v for k,v in sample.items() if k not in ('saved','algorithms')};self.pending.pop(identifier)
            elif time.monotonic()>pending['deadline']:
                results[identifier]={'phase':'failed','message':'接入端回执超时，保存结果未确认；请重新读取'}
                self.pending.pop(identifier)
