import queue
from types import SimpleNamespace as NS
from omnifleet_rmf_adapter.central import CentralObserver


def test_fast_central_restart_disarms_preexisting_goals_before_renewing_heartbeats(tmp_path):
    sent=[]
    mission=NS(tick=lambda states:None,snapshot=lambda:{'prechecks':{}})
    node=NS(snapshots=lambda:{'a':{'transport_connected':True}},initialized_clients=set(),session_id='new-process',
        send_command=lambda op,*a,**k:sent.append(op) or True,ui=NS(inbox=queue.Queue()),ui_results={},
        auto_registration=NS(due=lambda *a:False),maps=NS(reference=None,names={'a':'/a'},state={},transforms=lambda _: {},valid_robots=set()),registration=None,
        missions=mission,data=tmp_path,config={'robots':{'a':{'motion_enabled':False}},'central':{'assignments':{'a':{}}}},
        display_names=NS(snapshot=lambda:{}),permanent_parameters=NS(tick=lambda *a:None),
        identities=NS(revision=0,command=lambda packet:packet),operator=NS(receipt=None,stopped=False),plans=NS(tick=lambda _:None),
        robot_ids=['a'],decorated_states=lambda:{},schedule_response=0.)
    node.execution_permissions=lambda states:CentralObserver.execution_permissions(node,states)
    CentralObserver.control_cycle(node)
    assert sent==['disarm','ping']
    CentralObserver.control_cycle(node)
    assert sent==['disarm','ping','ping']
