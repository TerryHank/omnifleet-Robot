"""Ordered operator tasks executed by the central ROS executor."""
import json
import time
import uuid


class TaskQueue:
    def __init__(self, central):
        self.central = central
        self.path = central.data / 'task-queue.json'
        self.rows = json.loads(self.path.read_text(encoding='utf8')) if self.path.exists() else []
        for row in self.rows:
            if row['phase'] == 'EXECUTING':
                row.update(phase='STOPPED', message='调度服务已重启')
            elif row['phase'] == 'QUEUED':
                row['phase'] = 'READY'
        self.active = None

    def save(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.rows, ensure_ascii=False), encoding='utf8')
        temporary.replace(self.path)

    def command(self, packet, states):
        op = packet['op']
        if op == 'queue_new':
            row = {'id':uuid.uuid4().hex, 'phase':'DRAFT', 'revision':0, 'spec':{}}
            self.rows.append(row)
        elif op == 'queue_start':
            for item in self.rows:
                if item['phase'] == 'READY':
                    item['phase'] = 'QUEUED'
            self.save()
            return {'phase':'accepted', 'message':'已提交待执行任务'}
        else:
            new_task = op == 'queue_save' and packet.get('entry_id') is None
            if new_task:
                row = {'id':uuid.uuid4().hex, 'phase':'DRAFT', 'revision':0, 'spec':{}}
            else:
                row = next((r for r in self.rows if r['id'] == packet.get('entry_id')), None)
                if not row or row['revision'] != packet.get('revision'):
                    raise ValueError('任务已更新，请重新编辑')
            if op == 'queue_stop' and row is self.active:
                if row['spec']['kind'] == 'road':
                    self.central.missions.command({'op':'dispatch_stop'}, states)
                else:
                    self.central.missions.command({'op':'route_stop','robot_id':row['spec']['robot']}, states)
                self.finish(row, 'STOPPED', '操作者停止任务')
            elif row is self.active:
                raise ValueError('请先停止正在执行的任务')
            elif op == 'queue_delete':
                self.rows.remove(row)
            elif op == 'queue_move':
                target = next((r for r in self.rows if r['id'] == packet.get('target_id')), None)
                side = packet.get('side')
                if target is None or target is row or side not in ('before','after'):
                    raise ValueError('任务顺序已变化，请重新拖动')
                self.rows.remove(row)
                self.rows.insert(self.rows.index(target)+(side == 'after'), row)
            elif op == 'queue_save':
                name = packet.get('name','')
                if not isinstance(name,str) or len(name.strip()) > 80:
                    raise ValueError('任务名称最多 80 字')
                if packet.get('kind') == 'road':
                    ids = packet.get('nodes')
                    if not isinstance(ids,list) or not 1 <= len(ids) <= 100 or packet.get('mode') not in ('nearest','all'):
                        raise ValueError('请选择有效的路点和分配方式')
                    self.points(ids)
                    spec = {'kind':'road', 'nodes':ids, 'mode':packet['mode']}
                elif packet.get('kind') == 'corridor':
                    zones = self.central.missions.traffic.saved['zones']
                    if packet.get('side') not in ('a','b') or packet.get('robot_id') not in self.central.robot_ids or not any(z['id']==packet.get('corridor') for z in zones):
                        raise ValueError('请选择车辆、通道及入口')
                    spec = {'kind':'corridor','robot':packet['robot_id'],'corridor':packet['corridor'],'side':packet['side']}
                else:
                    raise ValueError('未知任务类型')
                phase = 'QUEUED' if row['phase']=='QUEUED' else 'READY'
                row.update(name=name.strip(),spec=spec,phase=phase,message='',revision=row['revision']+1)
                if new_task:
                    self.rows.append(row)
                for key in ('started','finished','run_id'):
                    row.pop(key,None)
            else:
                raise ValueError('任务无法执行此操作')
        self.save()
        return {'phase':'accepted','entry_id':row['id'],'message':'任务列表已更新'}

    def points(self, ids):
        graph = self.central.missions.roads.data
        connected = {v for edge in graph['edges'] for v in edge}
        nodes = {n['id']:n for n in graph['nodes']}
        if any(not isinstance(i,str) or i not in connected for i in ids):
            raise ValueError('路线包含已删除或未连接的路点')
        return [{'name':nodes[i].get('name',i),'pose':[*nodes[i]['xy'],nodes[i].get('yaw',0.)]} for i in ids]

    def finish(self, row, phase, message):
        row.update(phase=phase,message=message,finished=time.time(),revision=row['revision']+1)
        self.active = None
        if phase != 'COMPLETED':
            for item in self.rows:
                if item['phase']=='QUEUED':
                    item['phase']='READY'
        self.save()

    def tick(self, states):
        missions = self.central.missions
        goal = missions.goal_dispatch.state
        row = self.active
        if row:
            if row['spec']['kind']=='road':
                if goal.get('id') != row['run_id']:
                    self.finish(row,'STOPPED','目标任务已被替换')
                    return
                if goal['active']:
                    row['message']=goal['message']
                    return
                self.finish(row,goal['phase'],goal['message'])
            else:
                record = self.central.rmf_dispatch.pending.get(row['run_id'],{})
                row['message']=record.get('message','等待 RMF 回执')
                if record.get('phase') in ('COMPLETED','FAILED','INVALIDATED','STOPPED'):
                    self.finish(row,record['phase'],row['message'])
            return
        row = next((r for r in self.rows if r['phase']=='QUEUED'),None)
        if not row or goal['active']:
            return
        spec = row['spec']
        try:
            if spec['kind']=='road':
                if self.central.operator.stopped:
                    raise ValueError('调度操控处于停止状态')
                request={'op':'dispatch_goal','points':self.points(spec['nodes']),'mode':spec['mode']}
                result=missions.command(request,states)
                run_id=missions.goal_dispatch.state['id']
            else:
                result=missions.command({'op':'traffic_call','action':'pass','corridor':spec['corridor'],
                                         'side':spec['side'],'robot_id':spec['robot']},states)
                run_id=result['rmf_request_id']
        except (ValueError,RuntimeError,KeyError,TypeError) as error:
            self.finish(row,'FAILED',str(error))
            return
        row.update(phase='EXECUTING',started=time.time(),run_id=run_id,message=result['message'],revision=row['revision']+1)
        self.active=row
        self.save()
