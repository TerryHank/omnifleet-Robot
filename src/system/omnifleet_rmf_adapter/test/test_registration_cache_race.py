from queue import Queue
from types import SimpleNamespace as NS

from omnifleet_rmf_adapter.central import CentralObserver


def test_committed_alignment_wins_over_lagging_published_map_status(tmp_path):
    calls=[]
    maps=NS(reference=None,names={'link_a':'/alpha','link_b':'/beta'},valid_robots=set(),state={'alignment_valid':False})
    def current_transforms(states):
        maps.valid_robots=set(maps.names)
    maps.transforms=current_transforms
    observer=NS(snapshots=lambda:{},initialized_clients=set(),ui=NS(inbox=Queue()),ui_results={},
        maps=maps,registration=None,data=tmp_path,robot_ids=[],operator=NS(receipt=None,stopped=False),plans=NS(tick=lambda _:None),
        config={'robots':{},'central':{'assignments':{}}},schedule_response=0.,permanent_parameters=NS(tick=lambda *a:None),
        auto_registration=NS(due=lambda states,names,valid,running,now:calls.append(valid)),
        missions=NS(tick=lambda states:None,snapshot=lambda:{'prechecks':{}}),
        decorated_states=lambda:{},display_names=NS(snapshot=lambda:{}),identities=NS(revision=0))
    observer.execution_permissions=lambda states:CentralObserver.execution_permissions(observer,states)
    CentralObserver.control_cycle(observer)
    assert calls==[True]
