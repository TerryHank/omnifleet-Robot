import React from 'react';
import { FleetState, Pose } from './api';
import { SharedCostmapSettings } from './shared-costmap';

const phases: Record<string, string> = { IDLE: '空闲', SCHEDULED: '等待计划时间', ARMING: '申请租约', PLANNING: '规划中', YIELDING: '等待路权', RMF_PAUSED: '等待 RMF 放行', EXECUTING: '执行中', STOPPING: '确认停止', STOPPED: '已停止', COMPLETED: '完成', FAILED: '失败', INVALIDATED: '会话失效', BLOCKED: '受阻', CANCEL_UNCONFIRMED: '停止未确认' };
const poseText = (p?: Pose) => p ? `${p[0].toFixed(2)}, ${p[1].toFixed(2)}, ${(p[2] * 180 / Math.PI).toFixed(0)}°` : '—';
const localTime = (stamp: number) => stamp ? new Date(stamp * 1000 - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16) : '';
const taskTitle = (state: FleetState, robot: string) => {
  const { formation, follow, jobs, routes } = state.missions;
  if (formation?.active && formation.saved?.order?.includes(robot)) return '编队';
  if (follow?.active && follow.order?.includes(robot)) return '领车跟随';
  const source = jobs?.[robot]?.source;
  return ({ single: '单点导航', route: '多点导航', formation: '编队', follow: '领车跟随' } as Record<string, string>)[source]
    || (routes?.[robot]?.points?.length ? '多点导航' : '—');
};
interface Props { state: FleetState; robot: string; busy: boolean; act: (op: string, fields?: Record<string, unknown>) => Promise<any>; children?: React.ReactNode; }

export function TrafficPanel({ state, robot, busy, act, children }: Props) {
  const traffic = state.missions.traffic || {};
  const name = (r: string) => state.assignments[r]?.robot_name || r;
  const [time, setTime] = React.useState('');
  React.useEffect(() => { setTime(localTime(traffic.settings?.[robot]?.not_before || 0)); }, [robot]);
  const order: string[] = traffic.order || state.missions.follow.order || Object.keys(state.assignments);
  const index = order.indexOf(robot), priority = index < 0 ? 0 : order.length-index;
  const jobs = state.missions.jobs || {}, rmf = state.rmf;
  const registered = Object.values(rmf?.traffic?.robots || {}).filter((value: any) => value.registered).length;
  const online = Object.values(state.robots).filter((value: any) => value.online).length;
  return <section className="of-panel of-traffic" aria-label="统一调度与反馈">
    <div className="of-section-title"><h2>任务调度与反馈</h2><span>{Object.keys(jobs).length} 项任务 · {online}/{Object.keys(state.assignments).length} 台在线 · {registered} 台 RMF 已注册</span></div>
    <div className="of-dispatch-summary"><span>路权：领车最高，其后按拖动顺序；执行中不抢占</span><span>RMF 分配 {rmf?.dispatch?.connected ? '已连接' : '未连接'}</span><span>交通协商 {rmf?.traffic?.connected ? '已连接' : '未连接'}</span></div>
    <div className="of-table-scroll"><table className="of-compact-dispatch"><thead><tr>{['任务 / 车辆', '位置', '优先级', '计划 / 状态', '进度与反馈', '操作'].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>
      {(state.missions.dispatch_rows || []).map((row: any) => { const job = jobs[row.car]; return <tr key={row.car} data-testid={`dispatch-row-${row.car}`}><td><strong>{taskTitle(state, row.car)}</strong><small>{name(row.car)}</small></td><td><span>当前 {poseText(row.pose)}</span><small>起点 {poseText(row.init_pose)} → 目标 {poseText(row.target_pose)}</small></td><td><span>任务 {row.task_priority}</span><small>路权 {row.local_priority}</small></td><td><span>{row.not_before ? new Date(row.not_before * 1000).toLocaleString() : '立即'}</span><small>{phases[row.phase] || '状态待确认'}</small></td><td><span>{job ? `${job.index || 0}/${job.points?.length || 0}` : '—'}</span><small className="of-traffic-message">{job?.message || row.resources?.join(', ') || row.message || '暂无执行反馈'}</small></td><td><div className="of-row-actions"><button disabled={busy || !state.missions.routes?.[row.car]?.points?.length} onClick={() => void act('route_start', { robot_id: name(row.car) })}>执行</button><button disabled={busy} onClick={() => void act('route_stop', { robot_id: name(row.car) })}>停止</button></div></td></tr>; })}
    </tbody></table></div>
    <details className="of-section-body"><summary>设置 {name(robot)} 的计划时间</summary><p>任务标题由实际任务自动显示：单点导航、多点导航、编队、领车跟随。优先顺序请在原车辆列表中拖动调整，两个前端同步。</p><div className="of-traffic-fields">
      <label>任务标题<output aria-label="调度任务标题">{taskTitle(state, robot)}</output></label>
      <label>车辆顺序<output aria-label="调度车辆顺序">{index < 0 ? '—' : `第 ${index+1} 位${index === 0 ? '（领车）' : ''}`}</output></label>
      <label>自动优先级<output aria-label="自动调度优先级">{priority}</output></label>
      <label>最早开始时间<input aria-label="计划开始时间" type="datetime-local" value={time} onChange={(e) => setTime(e.target.value)} /></label>
      <button disabled={busy} onClick={() => void act('dispatch_settings', { robot_id: name(robot), not_before: time ? new Date(time).getTime() / 1000 : 0 })}>保存调度参数</button>
    </div></details>
    <details className="of-section-body"><summary>跟随、调度与任务历史</summary><pre>{JSON.stringify(state.missions.events || [], null, 2)}</pre></details>
    <SharedCostmapSettings state={state} busy={busy} act={act} />
    {children}
  </section>;
}
