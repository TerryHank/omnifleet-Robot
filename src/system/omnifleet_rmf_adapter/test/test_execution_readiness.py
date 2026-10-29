import pytest
from test_missions import fleet,save,start

def executing(fleet):
    save(fleet,'a',[[2.,0.,0.]])
    start(fleet,'a');fleet.tick(5)
    assert fleet.owner.jobs['a']['phase']=='EXECUTING'

def test_delayed_lifecycle_poll_does_not_cancel_native_execution(fleet):
    executing(fleet)
    fleet.states['a']['samples']['navigation']['value']['local_ready']=False
    fleet.tick(3)
    assert fleet.owner.jobs['a']['phase']=='EXECUTING'
    assert not any(p[0]=='disarm' for p in fleet.sent)

@pytest.mark.parametrize('condition',['disconnect','estop','epoch'])
def test_actual_connection_estop_or_epoch_failure_still_stops_execution(fleet,condition):
    executing(fleet)
    if condition=='disconnect':fleet.states['a']['online']=False
    if condition=='estop':fleet.states['a']['samples']['control']['value']['estop']=True
    if condition=='epoch':fleet.states['a']['samples']['navigation']['value']['localization_epoch']='new'
    fleet.tick(3)
    assert fleet.owner.jobs['a']['phase']!='EXECUTING'
    assert any(p[0]=='disarm' for p in fleet.sent)
