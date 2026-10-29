import React from 'react';
import { command, FleetState, parameterBatches, request, sample } from './api';

interface Props { state: FleetState; robot: string; onResult: (message: string) => void; initialQuery?: string; }
export function PermanentParameters({ state, robot, onResult, initialQuery = '' }: Props) {
  const [schema, setSchema] = React.useState<any>(null);
  const [query, setQuery] = React.useState(initialQuery);
  const [drafts, setDrafts] = React.useState<Record<string, any>>({});
  const [busy, setBusy] = React.useState(false);
  const [stack, setStack] = React.useState('');
  const [strategy, setStrategy] = React.useState('');
  const [feedback, setFeedback] = React.useState('');
  const receipt = sample(state, robot, 'navigation_parameters');
  const saved = receipt?.saved || {};
  const scalar = (id: string) => saved[id] ? Object.values(saved[id])[0] : undefined;
  React.useEffect(() => { request('/schema').then(setSchema).catch((error) => setFeedback(error.message)); }, []);
  const run = async (changes?: Record<string, any>, all = false) => {
    setBusy(true); setFeedback('等待本车永久参数服务回执…');
    const messages: string[] = []; let completed = true;
    try {
      const targets = all ? Object.keys(state.assignments) : [robot];
      for (const target of targets) {
       for (const batch of changes ? parameterBatches(changes) : [undefined]) {
        try { const result = await command(changes ? 'nav_parameters_save' : 'nav_parameters_read', { robot_id: state.assignments[target].robot_name, ...(batch ? { changes: batch } : {}) });
        messages.push(`${state.assignments[target].robot_name}：${result.service_result?.message || result.message || (changes ? result.runtime_confirmed ? '已永久保存并确认运行值' : '已永久保存，请查看运行回执' : '已读取永久参数')}`);
        if (result.service_result?.command) setStack(result.service_result.command);
        if (result.service_result?.strategy) setStrategy(result.service_result.strategy);
        if (batch?.__stack_restart && result.service_result) {
          let status = result.service_result; const deadline = Date.now() + 120000;
          while (['queued', 'stopping', 'starting', 'waiting'].includes(status.phase)) {
            if (Date.now() > deadline) throw new Error('尚未确认导航栈启动结果，请读取启动配置查看状态');
            setFeedback(status.message || status.phase); await new Promise((resolve) => setTimeout(resolve, 2500));
            status = (await command('nav_parameters_save', { robot_id: state.assignments[target].robot_name, changes: { __stack_status: '' } })).service_result;
          }
          if (status.phase === 'failed') throw new Error(status.message || '导航栈启动失败');
          messages.push(status.message || status.phase);
        }
        if (result.runtime && !result.runtime_confirmed) messages.push(...Object.values(result.runtime).map(String));
        } catch (error) { completed = false; messages.push(`${state.assignments[target].robot_name}：${(error as Error).message}`); break; }
       }
      }
      if (changes && completed) setDrafts((current) => Object.fromEntries(Object.entries(current).filter(([key, value]) => !(key in changes) || value !== changes[key])));
    } catch (error) { messages.push((error as Error).message); }
    finally { setFeedback(messages.join('\n')); onResult(messages.join('；')); setBusy(false); }
  };
  React.useEffect(() => { setDrafts({}); void (async () => { await run(); await run({ __navigation_strategy_status: '' }); await run({ __stack_status: '' }); })(); }, [robot]); // All three are reads; none starts navigation.
  const startupMode = async (mode: string) => {
    let value = stack.replace(/\s+startup_mode:=(?:"[^"]*"|'[^']*'|\S+)/g, '').trim();
    if (mode === 'mapping') value = value.replace(/\s+map_path:=(?:"[^"]*"|'[^']*'|\S+)/g, '').trim();
    value += ' startup_mode:=' + mode; setStack(value); await run({ __stack_command: value });
  };
  const groups: Record<string, any[]> = {};
  for (const field of schema?.fields || []) {
    const text = `${field.id} ${field.label} ${field.path} ${field.help}`.toLowerCase();
    if (query && !text.includes(query.toLowerCase())) continue;
    const algorithm = receipt?.algorithms?.[field.kind]?.current;
    if (!query && field.algorithm && algorithm && field.algorithm !== algorithm) continue;
    (groups[field.group || '其他参数'] ||= []).push(field);
  }
  return <section className="of-panel of-parameters">
    <div className="of-section-title"><h2>永久导航参数</h2><span>{state.assignments[robot]?.robot_name} · 车端保存 / 运行回读</span></div>
    <div className="of-toolbar">
      <input aria-label="搜索永久参数" placeholder="搜索参数、含义或 ROS 路径…" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button disabled={busy} onClick={() => void run()}>读取本车</button>
      <button className="primary" disabled={busy || !Object.keys(drafts).length} onClick={() => void run(drafts)}>保存并应用</button>
      <button disabled={busy || !Object.keys(drafts).length} onClick={() => void run(drafts, true)}>同步修改到全部车辆</button>
    </div>
    <p className="of-muted">最高速度、跟随增益及导航策略使用车辆自身配置。需要重启的参数会显示实际回执。</p>
    <div className="of-grid-two">
      {['global', 'local'].map((kind) => <label key={kind}>{kind === 'global' ? '全局规划器' : '局部控制器'}
        <select aria-label={kind === 'global' ? '全局规划器' : '局部控制器'} value={drafts[`${kind === 'global' ? 'global_planner' : 'local_controller'}_algorithm`] ?? receipt?.algorithms?.[kind]?.current ?? ''}
          onChange={(e) => setDrafts({ ...drafts, [`${kind === 'global' ? 'global_planner' : 'local_controller'}_algorithm`]: e.target.value })}>
          <option value="" disabled>等待读取</option>{Object.entries(schema?.algorithms?.[kind] || {}).map(([id, profile]: any) => <option key={id} value={id}>{profile.label}</option>)}
        </select></label>)}
    </div>
    <div className="of-toolbar"><span>多点策略</span><button aria-pressed={strategy === 'sequential'} disabled={busy} onClick={() => void run({ __navigation_strategy: 'sequential' })}>逐点到达</button><button aria-pressed={strategy === 'through_poses'} disabled={busy} onClick={() => void run({ __navigation_strategy: 'through_poses' })}>连续途经</button><span className="of-muted">{strategy}</span></div>
    {Object.entries(groups).map(([name, fields]) => <details key={name} open={!!query || name === '速度与平顺' || name === '路线跟踪'}><summary>{name}<span>{fields.length} 项</span></summary><div className="of-fields">{fields.map((field) => {
      const value = field.id in drafts ? drafts[field.id] : scalar(field.id);
      return <label key={field.id} title={`${field.help}\n${field.path}`}><span>{field.label} <small>{field.unit}</small></span>
        {['boolean', 'bool'].includes(field.type) ? <input type="checkbox" aria-label={field.id} checked={Boolean(value)} onChange={(e) => setDrafts({ ...drafts, [field.id]: e.target.checked })} /> :
          <input type={field.type === 'string' ? 'text' : 'number'} aria-label={field.id} min={field.min} max={field.max} step={field.step || 'any'} value={value === undefined ? '' : String(value)} placeholder="等待读取"
            onChange={(e) => setDrafts({ ...drafts, [field.id]: field.type === 'string' ? e.target.value : e.target.value === '' ? '' : Number(e.target.value) })} />}
        <small>{field.help}</small><code>{field.path}</code></label>;
    })}</div></details>)}
    <details><summary>碰撞模型、建图与导航栈</summary><div className="of-toolbar"><button disabled={busy} onClick={() => void run({ __collision_model: 'point' })}>近似点模型（1 cm）</button><button disabled={busy} onClick={() => void run({ __collision_model: 'body' })}>实际车体模型</button><span>{receipt?.collision_model?.mode}</span></div>
      <div className="of-toolbar"><span>下次启动模式</span><button disabled={busy || !stack.includes('mola_nav2_unified.launch.py')} onClick={() => void startupMode('mapping')}>边建图边导航</button><button disabled={busy || !stack.includes('mola_nav2_unified.launch.py')} onClick={() => void startupMode('saved_map')}>加载已有地图导航</button></div>
      <label>车端导航启动命令<textarea aria-label="导航启动命令" value={stack} onChange={(e) => setStack(e.target.value)} placeholder="先读取启动配置" /></label>
      <div className="of-toolbar"><button disabled={busy} onClick={() => void run({ __stack_status: '' })}>读取启动配置</button><button disabled={busy || !stack.trim()} onClick={() => void run({ __stack_command: stack })}>保存启动命令</button><button className="danger" disabled={busy || !stack.trim()} onClick={() => { if (window.confirm('重启导航栈会重建定位会话。车端将按已有流程备份地图。继续？')) void run({ __stack_restart: stack }); }}>重启导航栈</button></div>
    </details>
    <pre role="status" className="of-receipt">{feedback}</pre>
  </section>;
}
