from snapshot_fallback import build_fallback
from diagnostic_node import timeout_completion
from dsh_runner import DiagnosticTimeout
from dsh_runner import MODEL_TIMEOUT_SECONDS
def test_diagnostic_deadline_is_bounded():
 assert MODEL_TIMEOUT_SECONDS==120
def test_timeout_is_terminal_complete_snapshot_only():
 snapshot={'captured_at_unix':1,'fleet':{'frame_id':'fleet_map','shared_map':{'source_robot':'robot_113','alignment_valid':True},'robots':{'robot_104':{'nav_ready':True,'velocity':[0,0],'shared_map_ready':True}}},'recent_errors':[]}
 error=DiagnosticTimeout('old text','model_analysis_timeout',{'model_elapsed_seconds':120.2})
 result=timeout_completion(snapshot,error,{'model_elapsed_seconds':120.2})
 assert result['status']=='complete' and result['model_fallback'] is True
 assert result['parameter_actions']==[] and '请缩短问题后重试' not in result['answer']
 assert result['timings']['fallback']=='snapshot_only'
def test_non_timeout_error_is_not_converted():
 assert not isinstance(RuntimeError('x'),DiagnosticTimeout)
