import React from 'react';
import { command, FleetState, request, sample } from './api';

export function useTopics(state: FleetState, robot: string, topics: string[], enabled = true) {
  const [values, setValues] = React.useState<Record<string, any>>({});
  const key = topics.join('|');
  React.useEffect(() => {
    if (!enabled || !topics.length) { setValues({}); return; }
    let live = true;
    const watch = () => { void command('web_watch', { robot_id: state.assignments[robot].robot_name, topics }, false).catch(() => undefined); };
    const read = async () => {
      const entries = await Promise.all(topics.map(async (topic) => {
        try { return [topic, await request(`/inspect/${encodeURIComponent(robot)}?topic=${encodeURIComponent(topic)}`)]; }
        catch (error) { return [topic, { error: (error as Error).message }]; }
      }));
      if (live) setValues(Object.fromEntries(entries));
    };
    watch(); void read(); const timer = setInterval(() => void read(), 450), renew = setInterval(watch, 3500);
    return () => { live = false; clearInterval(timer); clearInterval(renew); };
  }, [robot, key, enabled, state.identity_revision]);
  return values;
}
function Chart({ title, data, unit }: { title: string; data: number[][]; unit: string }) {
  const colors = ['var(--of-vehicle-0)', 'var(--of-vehicle-1)', 'var(--of-vehicle-3)'];
  const all = data.flat().filter(Number.isFinite), min = Math.min(0, ...all), max = Math.max(.05, ...all), range = max - min || 1;
  return <div className="of-chart"><h3>{title}<small>{unit}</small></h3><svg viewBox="0 0 320 100" aria-label={title}>
    {[0, 25, 50, 75, 100].map((y) => <line key={y} x1="0" y1={y} x2="320" y2={y} stroke="var(--of-grid)" />)}
    {data.map((series, index) => <polyline key={index} fill="none" stroke={colors[index % 3]} strokeWidth="1.6" points={series.map((value, n) => `${n / Math.max(1, series.length - 1) * 320},${94 - (value - min) / range * 86}`).join(' ')} />)}
  </svg><small>{min.toFixed(2)} ～ {max.toFixed(2)}</small></div>;
}
export function Telemetry({ state, robot }: { state: FleetState; robot: string }) {
  const topics: Record<string, string[]> = state.robots[robot]?.graph?.topics || {};
  const [raw, setRaw] = React.useState('/wheel/odom');
  const cameras = Object.keys(topics).filter((name) => topics[name].includes('sensor_msgs/msg/CompressedImage'));
  const [camera, setCamera] = React.useState('');
  const imus = Object.keys(topics).filter((name) => topics[name].includes('sensor_msgs/msg/Imu')).slice(0, 2);
  const watched = Array.from(new Set([raw, camera, ...imus, '/joint_states', '/rosout', '/navigation/nav_cmd_vel'].filter((name) => topics[name])));
  const values = useTopics(state, robot, watched);
  const [history, setHistory] = React.useState<any[]>([]);
  React.useEffect(() => { setHistory([]); }, [robot]);
  React.useEffect(() => {
    const control = sample(state, robot, 'control');
    const imu = values[imus[0]]?.value;
    setHistory((rows) => [...rows.slice(-89), { v: control?.velocity?.[0] || 0, w: control?.velocity?.[1] || 0, voltage: sample(state, robot, 'voltage'), imu, imus: Object.fromEntries(imus.map((topic) => [topic, values[topic]?.value])) }]);
  }, [state]);
  const exportState = () => {
    const { token, ...safe } = state;
    const url = URL.createObjectURL(new Blob([JSON.stringify(safe, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'omnifleet-status.json'; link.click(); URL.revokeObjectURL(url);
  };
  return <section className="of-panel"><div className="of-section-title"><h2>实时数据与话题</h2><button onClick={exportState}>导出状态</button></div><div className="of-toolbar"><label>相机<select aria-label="相机话题" value={camera} onChange={(e) => setCamera(e.target.value)}><option value="">不订阅图像</option>{cameras.map((name) => <option key={name}>{name}</option>)}</select></label><small>{cameras.length ? '选择后按需接收本车图像' : '本车暂无已发布图像话题'}</small></div>{values[camera]?.value?.image && <img className="of-camera" src={values[camera].value.image} alt="本车实时相机" />}<div className="of-chart-grid">
    <Chart title="轮速反馈 · 线速度" unit="m/s" data={[history.map((p) => p.v)]} /><Chart title="轮速反馈 · 角速度" unit="rad/s" data={[history.map((p) => p.w)]} /><Chart title="电池电压" unit="V" data={[history.map((p) => p.voltage ?? 0)]} />
    {imus.map((topic) => <React.Fragment key={topic}><Chart title={topic + ' · 线加速度 XYZ'} unit="m/s²" data={['x', 'y', 'z'].map((axis) => history.map((p) => p.imus?.[topic]?.linear_acceleration?.[axis] || 0))} /><Chart title={topic + ' · 角速度 XYZ'} unit="rad/s" data={['x', 'y', 'z'].map((axis) => history.map((p) => p.imus?.[topic]?.angular_velocity?.[axis] || 0))} /></React.Fragment>)}
  </div><div className="of-toolbar"><label>原始话题<select aria-label="原始话题" value={raw} onChange={(e) => setRaw(e.target.value)}>{Object.keys(topics).sort().map((name) => <option key={name}>{name}</option>)}</select></label><span>{topics[raw]?.join(', ')} · {values[raw]?.age_seconds?.toFixed(1) || '—'} 秒</span></div><pre className="of-raw">{JSON.stringify(values[raw]?.value || values[raw]?.error || '等待话题消息', null, 2)}</pre>
    <details><summary>关节 / 履带反馈</summary><pre>{JSON.stringify(values['/joint_states']?.value || '该车暂无 joint_states', null, 2)}</pre></details>
    <details><summary>最新 ROS 日志</summary><pre>{JSON.stringify(values['/rosout']?.value || '等待新日志', null, 2)}</pre></details>
    <details><summary>导航接口与话题图</summary><pre>{JSON.stringify(state.robots[robot]?.graph, null, 2)}</pre></details>
  </section>;
}
export function Diagnostics({ state, robot, onResult, onParameter }: { state: FleetState; robot: string; onResult: (message: string) => void; onParameter: (id: string) => void }) {
  const [question, setQuestion] = React.useState(''), [engine, setEngine] = React.useState('dsh'), [model, setModel] = React.useState('MiniMax-M3');
  const [answer, setAnswer] = React.useState('输入问题，读取本车诊断结果。'), [busy, setBusy] = React.useState(false);
  const [details, setDetails] = React.useState<any>(null);
  const models = useTopics(state, robot, ['/omnifleet_t2/diagnostics/models']);
  let catalog: any = {};
  try { catalog = JSON.parse(models['/omnifleet_t2/diagnostics/models']?.value?.data || '{}'); } catch { /* Wait for a complete model catalogue. */ }
  const names = Array.from(new Set<string>([model, ...(catalog.models || []).map((m: any) => typeof m === 'string' ? m : m.id || m.name).filter(Boolean)]));
  const ask = async () => {
    setBusy(true); setAnswer('正在由本车采集诊断信息…');
    try {
      const result = await command('web_diagnostic', { robot_id: state.assignments[robot].robot_name, question, engine, model });
      const value = await request(`/diagnostic/${encodeURIComponent(robot)}/${encodeURIComponent(result.request_id)}`);
      setDetails(value); setAnswer(typeof value.answer === 'string' ? value.answer : JSON.stringify(value, null, 2)); onResult('本车诊断已返回');
    } catch (error) { setAnswer((error as Error).message); onResult((error as Error).message); }
    finally { setBusy(false); }
  };
  return <section className="of-panel"><div className="of-section-title"><h2>智能诊断</h2><span>{state.assignments[robot]?.robot_name} · 只读分析</span></div><div className="of-toolbar"><label>引擎<select aria-label="诊断引擎" value={engine} onChange={(e) => setEngine(e.target.value)}><option value="dsh">DSH</option><option value="phyagentos">PhyAgentOS</option></select></label><label>模型<select aria-label="诊断模型" value={model} onChange={(e) => setModel(e.target.value)}>{names.map((name) => <option key={name}>{name}</option>)}</select></label></div><textarea aria-label="诊断问题" placeholder="例如：为什么发布航点后没有移动？" maxLength={4000} value={question} onChange={(e) => setQuestion(e.target.value)} /><button className="primary" disabled={busy || !question.trim()} onClick={() => void ask()}>{busy ? '诊断中…' : '开始诊断'}</button><pre className="of-diagnostic" role="status">{answer}</pre><div className="of-toolbar">{(details?.parameter_actions || []).filter((action: any) => ['inspect', 'adjust'].includes(action.intent)).slice(0, 6).map((action: any) => <button key={action.id} onClick={() => onParameter(action.id)}>定位参数 {details.parameter_labels?.[action.id] || action.id}</button>)}</div>{details?.timings && <details><summary>诊断耗时与证据</summary><pre>{JSON.stringify({ timings: details.timings, causal_chain: details.causal_chain }, null, 2)}</pre></details>}</section>;
}
