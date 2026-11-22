import time
from unittest.mock import Mock
import pytest
import rmf_adapter as rmf
from test_missions import fleet
from test_rmf_traffic_bridge import attach


@pytest.mark.parametrize('x,expected_pause,expected_checkpoint', [(0.,False,0),(.8,False,0),(.98,False,1),(1.2,False,1)])
def test_wait_next_is_obeyed_at_next_checkpoint_not_at_segment_start(fleet,x,expected_pause,expected_checkpoint):
    traffic=attach(fleet);traffic.enroll=Mock();traffic.last_idle=time.monotonic()
    traffic.owner.get_node_names_and_namespaces=lambda:[('rmf_traffic_blockade_node','/')]
    handle=Mock();handle.moving_from.return_value=rmf.easy_traffic_light.MovingInstruction.WaitAtNextCheckpoint
    traffic.members={'a':{'handle':handle,'state':'MOVING'}}
    traffic.routes={'a':{'job':'test','path':[[0.,0.,0.],[1.,0.,0.],[2.,0.,0.]],'index':0}}
    fleet.owner.jobs['a']={'id':'test','phase':'EXECUTING'}
    fleet.states['a']['samples']['pose']['value']['x']=x
    fleet.states['a']['samples']['control']['value']['velocity']=[.05,0.]
    traffic.pause=Mock();traffic.tick(fleet.states)
    assert traffic.pause.called==expected_pause
    assert handle.moving_from.call_args.args[0]==expected_checkpoint
