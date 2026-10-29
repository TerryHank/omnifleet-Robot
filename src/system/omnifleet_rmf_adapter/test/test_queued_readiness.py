import pytest
from test_missions import fleet,save,start


@pytest.mark.parametrize('ticks,phase',[(0,'ARMING'),(2,'PLANNING')])
def test_accepted_goal_waits_through_transient_readiness_loss_then_executes_once(fleet,ticks,phase):
    save(fleet,'a',[[2.,0.,0.]])
    start(fleet,'a');fleet.tick(ticks)
    assert fleet.owner.jobs['a']['phase']==phase
    fleet.states['a']['samples']['navigation']['value']['local_ready']=False
    fleet.tick(4)
    assert fleet.owner.jobs['a']['phase']==phase
    assert fleet.owner.jobs['a']['waiting_ready']
    assert not any(p[0]=='disarm' for p in fleet.sent)
    assert not any(p[0]=='navigate' for p in fleet.sent)
    fleet.states['a']['samples']['navigation']['value']['local_ready']=True
    fleet.tick(5)
    assert fleet.owner.jobs['a']['phase']=='EXECUTING'
    assert len([p for p in fleet.sent if p[0]=='navigate'])==1


@pytest.mark.parametrize('condition',['disconnect','estop','epoch'])
def test_real_invalidity_still_cancels_waiting_goal(fleet,condition):
    save(fleet,'a',[[2.,0.,0.]]);start(fleet,'a');fleet.tick(2)
    fleet.states['a']['samples']['navigation']['value']['local_ready']=False
    fleet.tick()
    if condition=='disconnect':fleet.states['a']['online']=False
    if condition=='estop':fleet.states['a']['samples']['control']['value']['estop']=True
    if condition=='epoch':fleet.states['a']['samples']['navigation']['value']['localization_epoch']='new'
    fleet.tick(3)
    assert fleet.owner.jobs['a']['phase']!='PLANNING'
    assert any(p[0]=='disarm' for p in fleet.sent)


def test_replacement_is_not_lost_when_readiness_dips_while_old_goal_stops(fleet):
    fleet.owner.command({'op':'single_goal','robot_id':'a','point':[2.,0.,0.]},fleet.states);fleet.tick(5)
    fleet.owner.command({'op':'single_goal','robot_id':'a','point':[3.,0.,0.]},fleet.states)
    fleet.states['a']['samples']['navigation']['value']['local_ready']=False
    fleet.tick(3)
    job=fleet.owner.jobs['a']
    assert job['phase']=='ARMING' and job['points'][0]['pose']==[3.,0.,0.]
    fleet.states['a']['samples']['navigation']['value']['local_ready']=True;fleet.tick(5)
    assert fleet.owner.jobs['a']['phase']=='EXECUTING'
    assert len([p for p in fleet.sent if p[0]=='navigate'])==2
