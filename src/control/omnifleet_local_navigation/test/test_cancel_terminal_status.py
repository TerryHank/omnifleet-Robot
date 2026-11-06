"""A matching server terminal state closes cancellation even if Result RPC is lost."""
import ast,time
from pathlib import Path
from types import MethodType,SimpleNamespace as NS

SOURCE=Path(__file__).parents[1]/'omnifleet_local_navigation/route_execution.py'
tree=ast.parse(SOURCE.read_text())
selected=[method for cls in tree.body if isinstance(cls,ast.ClassDef) and cls.name=='ContinuousRoute'
          for method in cls.body if isinstance(method,ast.FunctionDef)
          and method.name in ('_retire_cancelled','observe_action_status','cancel')]
methods={"time":time};exec(compile(ast.Module(body=selected,type_ignores=[]),'route_cancel_methods','exec'),methods)


def rig(cancel_code=0,canceling=True):
    route=NS(requests={})
    for name,value in methods.items():
        if callable(value):setattr(route,name,MethodType(value,route))
    calls=[]
    response=NS(return_code=cancel_code)
    future=NS(result=lambda:response,add_done_callback=lambda fn:fn(NS(result=lambda:response)))
    client=object()
    handle=NS(goal_id=NS(uuid=[7]*16),cancel_goal_async=lambda:(calls.append(True) or future))
    entry=dict(handle=handle,client=client,cancel=canceling,cancel_sent=False)
    route.requests['owned']=entry
    return route,client,entry,calls


def status(identity=7,value=5):
    return NS(status_list=[NS(goal_info=NS(goal_id=NS(uuid=[identity]*16)),status=value)])


def test_matching_cancelled_goal_closes_lost_result_rpc():
    route,client,entry,_=rig()
    route.observe_action_status(client,status())
    assert route.requests=={}


def test_unrelated_server_goal_or_executing_status_cannot_close_request():
    route,client,entry,_=rig()
    route.observe_action_status(object(),status())
    route.observe_action_status(client,status(8))
    route.observe_action_status(client,status(value=2))
    assert route.requests['owned'] is entry


def test_terminal_normal_result_is_retained_until_cancel_requested():
    route,client,entry,calls=rig(canceling=False)
    route.observe_action_status(client,status(value=4))
    assert route.requests['owned'] is entry
    route.cancel(entry)
    assert not route.requests and not calls


def test_cancel_service_goal_terminated_reply_is_authoritative():
    route,client,entry,calls=rig(cancel_code=3)
    route.cancel(entry)
    assert not route.requests and calls==[True]


def test_cancel_accepted_reply_still_waits_for_terminal_confirmation():
    route,client,entry,calls=rig(cancel_code=0)
    route.cancel(entry)
    assert route.requests and calls==[True]
    route.observe_action_status(client,status())
    assert not route.requests


def test_unknown_pending_acceptance_cannot_be_retired_by_other_goal_status():
    route,client,entry,_=rig()
    entry['handle']=None
    route.observe_action_status(client,status())
    route.cancel(entry)
    assert route.requests['owned'] is entry
