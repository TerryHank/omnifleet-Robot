"""Remove unsafe unlock/start advice when the live snapshot is motion-locked."""
import re

def sanitize_answer(answer,snapshot):
    fleet=snapshot.get('fleet') if isinstance(snapshot,dict) else None
    if not isinstance(fleet,dict) or fleet.get('motion_enabled') is not False:return answer
    # Keep the model's evidence, but replace an operational unlock/start line
    # with the deterministic state observed by the ROS snapshot.
    pattern=re.compile(r'[^。\n]*(?:(?:运动锁|运动使能|运动许可)[^。\n]*(?:开启|打开|解除|取消)|(?:开启|打开|解除|取消)[^。\n]*(?:运动锁|运动使能|运动许可|发车))[^。\n]*。')
    return pattern.sub('当前运动锁保持关闭，本次不执行运动操作。',answer)
