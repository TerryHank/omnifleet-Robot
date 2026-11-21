import json
from dsh_runner import ask_dsh
from test_parameter_guidance import sample
sample['observations']={'/cmd_vel':{'vx':.005,'wz':-1.24},'/odom':{'vx':0,'wz':0},'/plan':{'poses':33,'received_seconds_ago':.76}}
sample['recent_errors']=[{'node':'controller_server','message':'Failed to make progress'},{'node':'controller_server','message':'[follow_path] [ActionServer] Aborting handle.'}]
answer=ask_dsh('这是用户截图的历史回放，用于验证建议是否有依据。机器人未移动、控制器报 Failed to make progress，请说明应该检查什么；不要把速度上限当成实际速度。',sample)
assert 'linear_speed' not in answer['parameter_ids'],answer
print(json.dumps(answer,ensure_ascii=False))
