"""Deterministic read-only answer when the model stream misses its deadline."""
import math

def _fmt(value,unit=''):
    if isinstance(value,(int,float)) and math.isfinite(value):return f'{value:g}{unit}'
    return '未采到'

def build_fallback(snapshot,timeout_seconds=120,error_code='model_timeout'):
    if snapshot.get('diagnosis_scope',{}).get('mode')=='local':
        robot=snapshot.get('parameter_owner','本车');local=snapshot.get('local_navigation',{})
        events=snapshot.get('causal_evidence',{}).get('events',[])
        stops=[e for e in events if '停止路线' in e.get('message','') or 'stale localization' in e.get('message','')]
        facts=[f'- 本次只检查 {robot} 本地任务，其他车辆和共享地图不是启动前提。',
               f'- 当前本地模块就绪：{local.get("local_ready","未采到")}；已保存事件 {len(events)} 条。']
        if stops:facts.append('- 已记录的停止事件 '+stops[-1]['id']+'：'+stops[-1]['message'][:300])
        lines=['发现的问题',f'- 模型在 {timeout_seconds:g} 秒内未完成；以下仅为事件证据，不是完整模型结论。',
               '', '判断依据',*facts,'','处理步骤','1. 按已保存请求编号和事件时间核对定位输入、TF发布及消费时间。',
               '2. 不因模型超时放宽导航判据或更改参数；模型恢复后可使用同一证据继续分析。',
               '', '还需确认','- 模型完整因果分析尚未完成；参数按钮不提供。']
        return '\n'.join(lines),{'model_fallback':True,'model_error_code':error_code,'parameter_ids':[],'parameter_actions':[]}
    fleet=snapshot.get('fleet') if isinstance(snapshot.get('fleet'),dict) else {}
    robots=fleet.get('robots') if isinstance(fleet.get('robots'),dict) else {}
    lines=['发现的问题',f'- 已确认：模型没有在 {timeout_seconds:g} 秒内完成，下面先给出实时数据检查结果。',
           '- 未确认：模型没有完成完整因果分析，不能仅凭这份兜底结果修改参数。','', '判断依据']
    if robots:
        for robot,state in robots.items():
            if not isinstance(state,dict):continue
            velocity=state.get('velocity') if isinstance(state.get('velocity'),list) else []
            lines.append(f"- {robot}：导航{'就绪' if state.get('nav_ready') else '未就绪或未采到'}，速度 {_fmt(velocity[0] if velocity else None,' m/s')}，公共地图{'有效' if state.get('shared_map_ready') else '未确认'}。")
    shared=fleet.get('shared_map') if isinstance(fleet.get('shared_map'),dict) else {}
    if shared:lines.append(f"- 公共地图来源 {shared.get('source_robot','未采到')}，对齐状态{'有效' if shared.get('alignment_valid') else '未确认'}；地图坐标为 {fleet.get('frame_id','未采到')}。")
    else:lines.append('- 当前快照没有足够的车队地图状态，不能判断两车地图是否一致。')
    lines.append(f'- 最近错误记录：{len(snapshot.get("recent_errors") or [])} 条；这只能说明采集窗口内读到的记录，不能代表更早或之后没有错误。')
    lines += ['', '处理步骤', '1. 先按上面“判断依据”核对当前状态，不要因为模型超时直接改参数或解除安全锁。',
              '2. 如果仍需模型分析，把问题缩短为一个现象和一个目标后重试；实时快照兜底结果不会替代完整模型结论。',
              '3. 如果连续超时，保留本次时间和请求编号，检查模型服务响应时间；车辆控制不受本诊断请求影响。', '',
              '还需确认', '- 模型没有完成完整分析，参数按钮本次不提供；需要模型成功返回并引用实时证据后才能给出参数定位。']
    return '\n'.join(lines),{'model_fallback':True,'model_error_code':error_code,'parameter_ids':[],'parameter_actions':[]}
