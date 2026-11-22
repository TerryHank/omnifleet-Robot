from concurrent.futures import Future
from types import SimpleNamespace as NS
import json
from omnifleet_rmf_adapter.control_client import NavigationClient


def client():
    calls=[]
    def call(kind,request):
        f=Future();calls.append((kind,getattr(request,'data',None),f));return f
    c=NS(motion_enabled=True,arm_pending=False,epoch=None,goal_handle=None,inflight=None,pending=None,
         generation=0,manual_until=0.,arm_service_future=None,release_future=None,release_requested=False,queued_arm=None,
         enable=NS(service_is_ready=lambda:True,call_async=lambda r:call('enable',r)),
         acquire=NS(service_is_ready=lambda:True,call_async=lambda r:call('acquire',r)),
         renew=lambda:None,event=lambda *a,**k:None,stopped=lambda:True)
    c.arm=lambda r:NavigationClient.arm(c,r)
    c.progress=lambda:NavigationClient.progress_release(c)
    c.cancel=lambda:NavigationClient.cancel(c,'stop',disarm=True)
    return c,calls


def success(f,epoch=None):
    f.set_result(NS(success=True,message=json.dumps({'epoch':epoch}) if epoch else ''))


def test_old_enable_callback_cannot_revoke_a_new_lease():
    c,calls=client();c.arm('old');old=calls[-1][2]
    c.cancel();c.arm('new');c.progress()
    assert [(k,v) for k,v,_ in calls]==[('enable',True)]
    success(old);c.progress()
    assert [(k,v) for k,v,_ in calls]==[('enable',True),('enable',False)]
    success(calls[-1][2]);c.progress()
    assert [(k,v) for k,v,_ in calls][-1]==('enable',True)
    success(calls[-1][2]);success(calls[-1][2],'new-epoch')
    assert c.epoch=='new-epoch'


def test_old_acquire_finishes_before_release_and_new_arm():
    c,calls=client();c.arm('old');success(calls[-1][2]);old=calls[-1][2]
    c.cancel();c.arm('new');c.progress()
    assert len(calls)==2
    success(old,'old-epoch');assert c.epoch is None
    c.progress();assert calls[-1][:2]==('enable',False)
    success(calls[-1][2]);c.progress();success(calls[-1][2]);success(calls[-1][2],'new-epoch')
    assert c.epoch=='new-epoch'


def test_second_stop_drops_a_waiting_arm_request():
    c,calls=client();c.arm('old');c.cancel();c.arm('new');c.cancel()
    success(calls[0][2]);c.progress();success(calls[-1][2]);c.progress()
    assert c.epoch is None and c.queued_arm is None
    assert [v for k,v,_ in calls if k=='enable']==[True,False]


def test_failed_release_is_not_followed_by_new_acquire():
    c,calls=client();c.cancel();c.arm('new');c.progress()
    calls[-1][2].set_result(NS(success=False))
    c.progress();assert calls[-1][:2]==('enable',False)
    success(calls[-1][2]);c.progress();assert calls[-1][:2]==('enable',True)
