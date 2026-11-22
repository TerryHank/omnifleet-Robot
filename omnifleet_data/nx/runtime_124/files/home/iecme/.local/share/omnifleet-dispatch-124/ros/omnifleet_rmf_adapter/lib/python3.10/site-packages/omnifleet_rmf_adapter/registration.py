"""Stationary data capture and geometric registration; never arms either vehicle."""
import json
import fcntl
import math
import os
from pathlib import Path
import subprocess
import sys
import time


def stationary(state, seconds=2.):
    samples=state.get('samples',{})
    nav=samples.get('navigation',{}).get('value',{})
    control=samples.get('control',{}).get('value',{})
    velocity=control.get('velocity',[])
    return bool(state.get('online') and all(state.get('fresh',{}).get(k) for k in ('map','pose','navigation','control'))
                and nav.get('local_ready') and nav.get('localization_epoch')
                and not nav.get('navigation_active') and not control.get('nav_active')
                and control.get('stopped_seconds',0)>=seconds and control.get('velocity_age',99)<.5
                and len(velocity)==2 and all(type(v) in (int,float) and math.isfinite(v) and abs(v)<.01 for v in velocity))


def registration_members(states, robots, reference, valid=()):
    """Offline or already aligned peers do not block a newly discovered member."""
    if reference not in robots or not stationary(states.get(reference,{})):return []
    pending=[r for r in robots if r!=reference and r not in valid and stationary(states.get(r,{}))]
    return [reference]+pending if pending else []


class AutoRegistration:
    def __init__(self, retry_seconds=300.):
        self.candidate = None
        self.ready_since = 0.
        self.attempted = None
        self.last_attempt = 0.
        self.retry_seconds = retry_seconds

    def due(self, states, robots, alignment_valid, running, now):
        epochs = []
        for robot in sorted(robots):
            state = states.get(robot, {})
            samples = state.get('samples', {})
            nav = samples.get('navigation', {}).get('value', {})
            if not stationary(state):
                self.candidate = None
                return False
            epochs.append((robot, nav['localization_epoch']))
        if len(epochs) < 2:
            self.candidate=None
            return False
        key = tuple(epochs)
        if key != self.candidate:
            self.candidate, self.ready_since = key, now
        if alignment_valid or running or now-self.ready_since < 5.:
            return False
        if key == self.attempted and now-self.last_attempt < self.retry_seconds:
            return False
        self.attempted = key
        self.last_attempt = now
        return True


def registration_pair(config):
    robots = [r for r, p in config['robots'].items() if p['enabled']]
    reference = config['central']['reference_robot']
    source=os.environ.get('OMNIFLEET_REGISTRATION_SOURCE')
    if source:
        if source not in robots or source==reference or reference not in robots:
            raise ValueError('Registration pair must belong to the enabled fleet and assigned reference')
        return source,reference
    if len(robots) != 2 or reference not in robots:
        raise ValueError('Map registration requires two enabled vehicles and an assigned reference')
    return next(r for r in robots if r != reference), reference


def commit_alignment(data, result, robots):
    from .state import connection_states
    report = json.loads((data/'connection_status.json').read_text())
    if not 0 <= time.time()-report['wall_time_seconds'] < 3.:
        raise ValueError('Central state expired before registration commit')
    states = connection_states(report)
    epochs = {}
    for robot in robots:
        state = states[robot]
        nav = state['samples']['navigation']['value']
        if not stationary(state,.3):
            raise ValueError('Vehicles must remain stationary and fresh until registration commit')
        epochs[robot] = nav.get('localization_epoch')
    if not result.get('validated') or result['epochs'] != epochs or set(result['transforms']) != set(robots):
        raise ValueError('Registration is unvalidated or localization sessions changed during matching')
    # Preserve other validated members only while their own and the anchor's
    # localization epochs still match. A new arrival must not evict its peers.
    reference=result.get('reference_robot')
    previous=data/'fleet_alignment.json'
    if reference and previous.exists():
        try:saved=json.loads(previous.read_text())
        except ValueError:saved={}
        if saved.get('validated') and saved.get('epochs',{}).get(reference)==epochs.get(reference):
            result={**result,'epochs':dict(result['epochs']),'transforms':dict(result['transforms'])}
            for robot,transform in saved.get('transforms',{}).items():
                if robot in result['transforms']:continue
                epoch=states.get(robot,{}).get('samples',{}).get('navigation',{}).get('value',{}).get('localization_epoch')
                if epoch and saved.get('epochs',{}).get(robot)==epoch:
                    result['epochs'][robot]=epoch;result['transforms'][robot]=transform
    temporary=data/'fleet_alignment.tmp'
    temporary.write_text(json.dumps(result,indent=2));temporary.replace(data/'fleet_alignment.json')



def merge_registrations(results, robots, reference):
    transforms={reference:[0.,0.,0.]};epochs={};metrics={}
    for source,result in results:
        if not result.get('validated') or set(result.get('transforms',{}))!={source,reference}:
            raise ValueError('A member alignment was not validated')
        for robot,epoch in result['epochs'].items():
            if robot in epochs and epochs[robot]!=epoch:raise ValueError('Reference localization changed between member alignments')
            epochs[robot]=epoch
        transforms[source]=result['transforms'][source];metrics[source]=result['best']
    if set(transforms)!=set(robots) or set(epochs)!=set(robots):raise ValueError('Incomplete fleet registration')
    if len(results)==1:return results[0][1]
    return {'validated':True,'transforms':transforms,'epochs':epochs,'best':metrics,'reference_robot':reference}


def run_stage(script,timeout=90):
    result=subprocess.run([sys.executable,str(script)],timeout=timeout,
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,
        env={**os.environ,'OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'1'})
    if result.stdout:print(result.stdout,end='',flush=True)
    if result.returncode:
        lines=[line.strip() for line in result.stdout.splitlines() if line.strip()]
        detail=lines[-1] if lines else 'exit status '+str(result.returncode)
        raise RuntimeError(script.name+': '+detail)


def main():
    data=Path(os.environ['OMNIFLEET_DATA'])
    scripts=Path(__file__).resolve().parents[1]/'scripts'
    folder=data/'alignment';folder.mkdir(exist_ok=True)
    lock=(folder/'registration.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    config=json.loads(Path(os.environ['OMNIFLEET_CONFIG']).read_text())
    enabled=[r for r,p in config['robots'].items() if p['enabled']]
    robots=json.loads(os.environ['OMNIFLEET_REGISTRATION_ROBOTS']) if os.environ.get('OMNIFLEET_REGISTRATION_ROBOTS') else enabled
    if not isinstance(robots,list) or len(set(robots))!=len(robots) or any(r not in enabled for r in robots):
        raise ValueError('Registration members must be distinct enabled discovered vehicles')
    reference=config['central']['reference_robot']
    if len(robots)<2 or reference not in robots:raise ValueError('Map registration needs at least two enabled vehicles and an assigned reference')
    status=data/'registration-job.json'
    def update(phase,**fields):
        temporary=status.with_suffix('.tmp');temporary.write_text(json.dumps({'phase':phase,'updated_at':time.time(),'trigger':os.environ.get('OMNIFLEET_REGISTRATION_TRIGGER','manual'),**fields}));temporary.replace(status)
    previous=data/'fleet_alignment.json'
    if previous.exists():
        (folder/('before-'+str(time.time_ns())+'.json')).write_bytes(previous.read_bytes())
    errors={}
    try:
        update('running',step='capture_clouds.py');run_stage(scripts/'capture_clouds.py',timeout=max(360,len(robots)*180))
        results=[];errors={}
        for robot in robots:
            if robot==reference:continue
            os.environ['OMNIFLEET_REGISTRATION_SOURCE']=robot
            try:
                for script in ('register_maps.py','register_clouds.py'):
                    update('running',step=script,robot_id=robot);run_stage(scripts/script,timeout=180 if script=='register_clouds.py' else 90)
                pair=json.loads((folder/'cloud-registration.json').read_text())
                if not pair.get('validated'):
                    best=pair.get('best',{});xy=best.get('planar_xy',{})
                    raise ValueError('几何校验未通过：3D双向重叠 %.1f%%/%.1f%%，RMSE %.3fm；XY双向重叠 %.1f%%/%.1f%%；候选区分度 %.3f'%(
                        100*best.get('fitness',0),100*best.get('reverse_fitness',0),best.get('inlier_rmse_m',999),
                        100*xy.get('fitness',0),100*xy.get('reverse_fitness',0),pair.get('distinct_candidate_margin',0)))
                results.append((robot,pair))
            except Exception as error:
                errors[robot]=str(error)
        if not results:raise ValueError('; '.join(r+': '+e for r,e in errors.items()))
        members=[reference]+[r for r,_ in results]
        result=merge_registrations(results,members,reference);result['reference_robot']=reference
        commit_alignment(data,result,members)
        update('partial' if errors else 'validated',metrics=result['best'],epochs=result['epochs'],members=members,errors=errors)
    except Exception as error:
        update('failed',message=str(error),errors=errors)
        raise


if __name__=='__main__':main()
