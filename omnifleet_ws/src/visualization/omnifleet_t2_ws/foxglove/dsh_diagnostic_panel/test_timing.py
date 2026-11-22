import io,json,time,subprocess
import pytest
import dsh_runner as runner
from diagnostic_payload import compact_snapshot

def sample():
 return {'parameter_details':{'active':{'applicable':True,'node':'/controller','ros_parameters':['A.weight'],'label':'重复标签'},'inactive':{'applicable':False,'node':'/controller','ros_parameters':['B.weight']}},'parameter_catalog':{'active':'标签','inactive':'无关'},'parameter_evidence_paths':{'active':['/live_parameters/~1controller/A.weight'],'inactive':['/live_parameters/~1controller/B.weight']},'live_parameters':{'/controller':{'A.weight':5,'B.weight':10,'extra':True}},'saved_parameters':{'active':{'weight':5},'inactive':{'weight':10}},'foxglove':{'topic_names':['duplicate']}}

def test_compaction_keeps_active_values_and_paths():
 s=sample();compact,metrics=compact_snapshot(s)
 assert 'inactive' not in compact['parameter_details']
 assert compact['live_parameters']['/controller']=={'A.weight':5,'extra':True}
 assert compact['parameter_evidence_paths']['active']==s['parameter_evidence_paths']['active']
 assert 'foxglove' not in compact and 'inactive' in s['parameter_details']
 assert metrics['snapshot_bytes_after']<metrics['snapshot_bytes_before']

@pytest.mark.parametrize('generating',[True,False])
def test_timeout_has_stage_and_never_exposes_prompt(monkeypatch,generating):
 events=[{'stage':'request_start','time':time.time(),'attempt':1},{'stage':'response_headers','time':time.time()+.01,'attempt':1}]
 if generating:events.append({'stage':'first_model_token','time':time.time()+.02,'attempt':1})
 class Process:
  pid=1;returncode=0
  stdout=io.BytesIO(b'');stderr=io.BytesIO(b''.join(b'DSH_TIMING '+json.dumps(e).encode()+b'\n' for e in events))
  def wait(self,timeout):
   if timeout==.01:time.sleep(.05);raise subprocess.TimeoutExpired(['secret prompt'],timeout)
 monkeypatch.setattr(runner.subprocess,'Popen',lambda *a,**kw:Process())
 monkeypatch.setattr(runner.os,'killpg',lambda *a:None)
 with pytest.raises(runner.DiagnosticTimeout) as error:runner.ask_dsh('private question',sample(),timeout=.01)
 assert error.value.code==('model_analysis_timeout' if generating else 'model_response_timeout')
 assert 'private' not in str(error.value) and 'secret' not in str(error.value)
 assert 'model_connect_seconds' in error.value.timings
