from snapshot_fallback import build_fallback
from answer_safety import sanitize_answer
def test_fallback_is_actionable_but_never_invents_parameter_button():
 text,fields=build_fallback({'fleet':{'frame_id':'fleet_map','shared_map':{'source_robot':'robot_113','alignment_valid':True},'robots':{'robot_104':{'nav_ready':True,'velocity':[0,0],'shared_map_ready':True}}},'recent_errors':[]},120,'model_analysis_timeout')
 assert '模型没有在 120 秒内完成' in text
 assert 'robot_104' in text and '公共地图' in text
 assert fields['model_fallback'] is True and fields['parameter_actions']==[]
 assert '请缩短问题后重试' not in text
def test_missing_fleet_data_is_explicit():
 text,_=build_fallback({},120,'model_reasoning_timeout')
 assert '不能判断两车地图是否一致' in text and '当前快照没有足够' in text
def test_static_lock_removes_unlock_instruction():
 answer='处理步骤\n1. 请先打开运动使能，再发送导航。\n2. 请确认运动锁已开启。\n3. 查看地图。'
 result=sanitize_answer(answer,{'fleet':{'motion_enabled':False}})
 assert '打开运动使能' not in result and '运动锁已开启' not in result and '当前运动锁保持关闭' in result
def test_unlocked_snapshot_is_not_rewritten():
 answer='处理步骤\n1. 请打开运动使能。'
 assert sanitize_answer(answer,{'fleet':{'motion_enabled':True}})==answer
