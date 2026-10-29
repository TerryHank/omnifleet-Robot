import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from omnifleet_rmf_adapter.central import CentralObserver
from omnifleet_rmf_adapter.control_client import NavigationClient
from omnifleet_rmf_adapter.identity import FleetIdentities
from omnifleet_rmf_adapter.missions import Missions


def node_fixture(tmp_path):
    config={'central':{'identity_revision':3,'assignments':{'link_a':{'robot_name':'alpha','namespace':'/alpha'}}},
            'robots':{'link_a':{'enabled':True,'motion_enabled':False,'domain_id':181}}}
    path=tmp_path/'config.json';path.write_text(json.dumps(config))
    sent=[];actions=[]
    mission=NS(formation=NS(active=False),follow={'active':False,'order':['link_a','link_b']},
        command=lambda request,states:actions.append(request),stop=lambda *args:actions.append(args),client=Missions.client)
    node=NS(config=config,identities=FleetIdentities(config,path),maps=NS(names={'link_a':'/alpha'}),missions=mission,
            send_command=lambda *a,**k:sent.append((a,k)))
    return node,path,sent,actions


def test_enable_is_persisted_without_arming_or_moving_even_before_vehicle_ready(tmp_path):
    node,path,sent,actions=node_fixture(tmp_path)
    result=CentralObserver.set_execution_permission(node,{'robot_id':'link_a','enabled':True,'id':'enable'}, {})
    assert result['enabled'] is True and result['robot_id']=='alpha'
    stored=json.loads(path.read_text())
    assert stored['robots']['link_a']['motion_enabled'] is True
    assert stored['central']['identity_revision']==3 and stored['robots']['link_a']['domain_id']==181
    assert sent==actions==[]
    requested,observed,effective=CentralObserver.execution_permissions(node,{})
    assert requested['link_a'] and not observed['link_a'] and not effective['link_a']
    state={'online':True,'fresh':{'fleet_client':True},'samples':{'fleet_client':{'value':{'motion_enabled':True}}}}
    assert CentralObserver.execution_permissions(node,{'link_a':state})[2]['link_a']
    state['fresh']['fleet_client']=False
    assert not CentralObserver.execution_permissions(node,{'link_a':state})[2]['link_a']


def test_revocation_closes_config_and_stops_related_follow_and_vehicle_job(tmp_path):
    node,path,sent,actions=node_fixture(tmp_path)
    node.missions.follow['active']=True
    CentralObserver.set_execution_permission(node,{'robot_id':'link_a','enabled':False,'id':'off'}, {})
    assert json.loads(path.read_text())['robots']['link_a']['motion_enabled'] is False
    assert actions[0]=={'op':'follow_stop'} and actions[1][0]=='link_a'
    assert sent==[(('disarm','off'),{'robot_id':'link_a'})]


@pytest.mark.parametrize('value',('yes',1,None))
def test_nonboolean_permission_is_rejected(tmp_path,value):
    node,path,sent,actions=node_fixture(tmp_path);before=path.read_bytes()
    with pytest.raises(ValueError):CentralObserver.set_execution_permission(node,{'robot_id':'link_a','enabled':value,'id':'bad'}, {})
    assert path.read_bytes()==before and not sent


def test_config_write_failure_does_not_enable_runtime_or_send_commands(tmp_path,monkeypatch):
    node,path,sent,actions=node_fixture(tmp_path);before=path.read_bytes()
    def fail(*args):raise OSError('write failed')
    monkeypatch.setattr(Path,'replace',fail)
    with pytest.raises(RuntimeError):CentralObserver.set_execution_permission(node,{'robot_id':'link_a','enabled':True,'id':'bad'}, {})
    assert not node.config['robots']['link_a']['motion_enabled'] and path.read_bytes()==before
    assert sent==actions==[]


def test_client_enables_without_control_calls_and_revokes_live_lease_on_config_change(tmp_path):
    node,path,_,_=node_fixture(tmp_path);calls=[];records=[];cancelled=[]
    client=NS(permission_path=path,permission_mtime=None,permission_error=None,robot_id='link_a',motion_enabled=False,
        generation=0,pending=None,arm_pending=False,goal_handle=None,inflight=None,epoch=None,
        control={},events={},stopped=lambda:True,record=lambda *args:records.append(args),
        enable=NS(service_is_ready=lambda:True,call_async=lambda req:calls.append(req.data)))
    client.event=lambda *a,**k:NavigationClient.event(client,*a,**k)
    client.cancel=lambda *a,**k:NavigationClient.cancel(client,*a,**k)
    data=json.loads(path.read_text());data['robots']['link_a']['motion_enabled']=True;path.write_text(json.dumps(data))
    NavigationClient.refresh_execution_permission(client)
    assert client.motion_enabled and client.control['motion_enabled'] and calls==[] and client.epoch is None
    client.epoch='lease';client.goal_handle=NS(cancel_goal_async=lambda:cancelled.append(True))
    data['robots']['link_a']['motion_enabled']=False;path.write_text(json.dumps(data));client.permission_mtime=None
    NavigationClient.refresh_execution_permission(client)
    assert not client.motion_enabled and client.epoch is None and cancelled==[True] and calls==[False]
    assert client.generation==1


def test_unreadable_configuration_revokes_permission(tmp_path):
    _,path,_,_=node_fixture(tmp_path);revoked=[]
    client=NS(permission_path=path,permission_mtime=None,permission_error=None,robot_id='link_a',motion_enabled=True,
              control={},record=lambda *a:None,cancel=lambda *a,**k:revoked.append((a,k)))
    path.write_text('{')
    NavigationClient.refresh_execution_permission(client)
    assert not client.motion_enabled and client.permission_error and revoked
