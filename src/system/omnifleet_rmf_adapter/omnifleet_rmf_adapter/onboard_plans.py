"""Read-only path requests to each vehicle's selected Nav2 planner."""
from concurrent.futures import Future
import json
import time
import uuid
from pathlib import Path
from .map_hub import compose


class OnboardPlans:
    def __init__(self,data,maps,send):
        self.data,self.maps,self.send=Path(data),maps,send;self.pending={}

    def request(self,robot,targets,states):
        identifier='plan-'+uuid.uuid4().hex;future=Future()
        epoch=states[robot]['samples']['navigation']['value']['localization_epoch']
        self.pending[identifier]={'robot':robot,'future':future,'epoch':epoch,'targets':targets,
            'transform':list(self.maps.alignment[robot]),'deadline':time.monotonic()+30.}
        self.send('plan',identifier,robot_id=robot,poses=[p['pose'] for p in targets],localization_epoch=epoch)
        return future

    def close(self):
        for identifier,request in self.pending.items():
            self.send('cancel_plan',identifier,robot_id=request['robot']);request['future'].cancel()
            (self.data/'run'/'plans'/request['robot']/(identifier+'.json')).unlink(missing_ok=True)
        self.pending.clear()

    def tick(self,states):
        for identifier,request in list(self.pending.items()):
            robot=request['robot'];future=request['future'];state=states.get(robot,{})
            filename=self.data/'run'/'plans'/robot/(identifier+'.json')
            nav=state.get('samples',{}).get('navigation',{}).get('value',{})
            event=state.get('samples',{}).get('fleet_client',{}).get('value',{}).get('history',{}).get(identifier,{})
            error=None
            if not state.get('online') or nav.get('localization_epoch')!=request['epoch'] or self.maps.alignment.get(robot)!=request['transform']:
                error='车端规划期间连接或地图会话变化'
            elif time.monotonic()>request['deadline']:error='车端路径计算回执超时'
            elif event.get('phase')=='plan_failed':error=event.get('message','车端规划失败')
            if not future.cancelled() and not error and event.get('phase')=='planned' and filename.exists():
                try:
                    result=json.loads(filename.read_text())
                    if result['epoch']!=request['epoch'] or not result['path']:raise ValueError('车端路径无效')
                    future.set_result({'path':[compose(request['transform'],p) for p in result['path']],
                        'targets':request['targets'],'planner_id':result['planner_id'],'planning_source':'onboard_nav2'})
                except (OSError,ValueError,KeyError) as exception:error=str(exception)
            if error and not future.done():future.set_exception(ValueError(error))
            if future.done():
                if future.cancelled() or error:self.send('cancel_plan',identifier,robot_id=robot)
                filename.unlink(missing_ok=True);self.pending.pop(identifier)
