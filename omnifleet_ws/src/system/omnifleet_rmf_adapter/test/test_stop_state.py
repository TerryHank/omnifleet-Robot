import json
from test_operator_controls import controls
from std_msgs.msg import Bool
from omnifleet_rmf_adapter.operator_controls import OperatorControls

def test_stop_state_survives_central_restart_without_resuming_a_job(controls):
    f=controls;f.operator.pause(Bool(data=True))
    assert json.loads((f.owner.data/'operator-stop.json').read_text())=={'stopped':True}
    restored=OperatorControls(f.owner)
    assert restored.stopped and not f.owner.missions.follow['active']
    restored.pause(Bool(data=False))
    assert not OperatorControls(f.owner).stopped

def test_web_manual_reports_latched_stop_without_sending_motion(controls):
    import pytest
    f=controls;f.operator.pause(Bool(data=True));f.sent.clear()
    with pytest.raises(ValueError,match='调度已停止'):
        f.operator.web_command({'op':'web_manual','id':'probe','robot_id':'connection','velocity':[.15,0.]},f.states)
    assert not f.sent
