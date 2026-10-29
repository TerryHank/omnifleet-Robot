import json,struct,time
from concurrent.futures import Future
from types import SimpleNamespace as NS
import pytest
from sensor_msgs.msg import JointState,PointCloud2,PointField,CompressedImage
from std_msgs.msg import String
from omnifleet_rmf_adapter.web_client import WebClient

def make(tmp_path):
    published=[];records=[];destroyed=[];clients={}
    def client(cls,path):
        service=NS(calls=[],future=Future(),service_is_ready=lambda:True,remove_pending_request=lambda _:None)
        service.call_async=lambda request:(service.calls.append(request) or service.future)
        clients[path]=service;return service
    node=NS(cache=tmp_path,create_client=client,create_publisher=lambda *a:NS(publish=published.append),
        create_subscription=lambda *a:object(),create_timer=lambda *a:None,record=lambda k,v:records.append((k,v)),
        get_topic_names_and_types=lambda:[('/joint_states',['sensor_msgs/msg/JointState'])],destroy_subscription=destroyed.append)
    return WebClient(node),clients,published,records,destroyed

def test_map_save_uses_the_existing_waypoint_sidecar_service(tmp_path):
    client,services,_,records,_=make(tmp_path)
    client.request({'id':'save','op':'web_service','service':'save_map','map_path':'/data/test-map'})
    service=services['/omnifleet_t2/waypoints/map_save']
    assert service.calls[0].map_path=='/data/test-map'
    service.future.set_result(NS(success=True,error_message=''));client.tick()
    assert records[-1][1]['save']['phase']=='completed'

def test_native_map_load_failure_is_reported_without_false_success(tmp_path):
    client,services,_,records,_=make(tmp_path)
    client.request({'id':'load','op':'web_service','service':'load_map','map_path':'/missing'})
    services['/omnifleet_t2/waypoints/map_load'].future.set_result(NS(success=False,error_message='native map missing'))
    client.tick();assert records[-1][1]['load']['phase']=='failed' and 'native map missing' in records[-1][1]['load']['message']

def test_watch_expires_and_unsubscribes_after_the_browser_leaves(tmp_path,monkeypatch):
    client,_,_,_,destroyed=make(tmp_path);clock=[time.monotonic()]
    monkeypatch.setattr('omnifleet_rmf_adapter.web_client.time.monotonic',lambda:clock[0])
    client.request({'id':'watch','op':'web_watch','topics':['/joint_states']});assert '/joint_states' in client.watches
    clock[0]+=9.;client.tick();assert not client.watches and len(destroyed)==1

def test_joint_arrays_remain_arrays_in_raw_topic_data(tmp_path):
    client,*_=make(tmp_path);message=JointState();message.name=['left','right'];message.position=[1.,2.]
    client.store('/joint_states',message)
    assert json.loads((tmp_path/'web/joint_states.json').read_text())['value']['position']==[1.,2.]

def test_camera_compressed_frame_is_encoded_without_starting_any_hardware(tmp_path):
    client,*_=make(tmp_path);message=CompressedImage();message.format='jpeg';message.data=b'jpeg-test'
    client.store('/camera/compressed',message)
    assert json.loads((tmp_path/'web/camera__compressed.json').read_text())['value']['image'].startswith('data:image/jpeg;base64,')

def test_point_cloud_preserves_frame_and_coordinate_order(tmp_path):
    client,*_=make(tmp_path);message=PointCloud2();message.header.frame_id='lidar';message.width=2;message.height=1;message.point_step=12;message.row_step=24
    message.fields=[PointField(name=k,offset=i*4,datatype=7,count=1) for i,k in enumerate(('x','y','z'))]
    message.data=struct.pack('<ffffff',1.,2.,3.,4.,5.,6.)
    client.store('/points',message);value=json.loads((tmp_path/'web/points.json').read_text())['value']
    assert value['frame_id']=='lidar' and value['points']==[[1.,2.,3.],[4.,5.,6.]]

def test_diagnostic_answer_is_correlated_and_full_content_stays_out_of_ipc(tmp_path):
    client,_,_,records,_=make(tmp_path)
    client.reply({'request_id':'diag','phase':'forwarding'});client.answer(String(data=json.dumps({'request_id':'diag','status':'complete','answer':'read-only result'})))
    assert records[-1][1]['diag']['phase']=='completed' and 'answer' not in records[-1][1]['diag']
    assert 'read-only result' in (tmp_path/'web/omnifleet_t2__diagnostics__answer.json').read_text()

def test_unknown_raw_message_type_reports_failure_instead_of_crashing_client(tmp_path,monkeypatch):
    client,_,_,records,_=make(tmp_path)
    monkeypatch.setattr('omnifleet_rmf_adapter.web_client.get_message',lambda _:(_ for _ in ()).throw(ImportError('message definition missing')))
    client.request({'id':'unsupported','op':'web_watch','topics':['/joint_states']})
    assert records[-1][1]['unsupported']['phase']=='failed'


def test_diagnostic_progress_is_not_final_and_terminal_result_is_never_throttled(tmp_path):
    client,_,_,records,_=make(tmp_path);client.reply({'request_id':'diag','phase':'forwarding'})
    client.answer(String(data=json.dumps({'request_id':'diag','status':'collecting','answer':'collecting'})))
    assert records[-1][1]['diag']['phase']=='forwarding'
    client.answer(String(data=json.dumps({'request_id':'diag','status':'complete','answer':'final'})))
    assert records[-1][1]['diag']['phase']=='completed'
    assert json.loads((tmp_path/'web/diagnostic-diag.json').read_text())['answer']=='final'

def test_long_diagnostic_survives_visualization_watch_receipts(tmp_path):
    client,_,_,records,_=make(tmp_path);client.reply({'request_id':'slow','phase':'forwarding'})
    for index in range(40):client.reply({'request_id':'watch-'+str(index),'phase':'completed'})
    client.answer(String(data=json.dumps({'request_id':'slow','status':'complete','answer':'final'})))
    assert records[-1][1]['slow']['phase']=='completed'

def test_visualization_cache_is_bound_to_the_vehicle_map_epoch(tmp_path):
    client,*_=make(tmp_path);client.node.samples={'navigation':(time.monotonic(),{'localization_epoch':'current-map'})}
    client.store('/example',String(data='static path metadata'))
    assert json.loads((tmp_path/'web/example.json').read_text())['localization_epoch']=='current-map'
