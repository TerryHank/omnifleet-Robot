import React from 'react';
import { FleetState, localPoints } from './api';

const phases: Record<string,string> = { QUEUED:'等待分配', ASSIGNED:'已分配', EXECUTING:'执行中', COMPLETED:'已完成', STOPPED:'已停止', FAILED:'失败', INVALIDATED:'已失效' };
const trafficStates: Record<string,string> = { REGISTERING:'注册中', IDLE:'空闲', NEGOTIATING:'交通协商中', READY:'已放行', MOVING:'行进中', WAITING:'让行等待', ARRIVED:'已到达' };
export function RmfPanel({ state, busy, act, onResult, embedded = false }: { state: FleetState; busy: boolean; act:(op:string,fields?:Record<string,unknown>)=>Promise<any>; onResult:(message:string)=>void; embedded?: boolean }) {
  const [text,setText] = React.useState('');
  const status=state.rmf, tasks=status?.dispatch?.tasks || [], robots=status?.traffic?.robots || {};
  const name=(robot:string)=>state.assignments[robot]?.robot_name || robot || '等待分配';
  const submit=()=>{try{const points=localPoints(text);if(!points.length)throw Error('请填写共享地图航点');void act('rmf_submit_task',{points,kind:points.length===1?'single':'route'});}catch(error){onResult((error as Error).message)}};
  const body = <><p className="of-muted">自动分配按空闲和预计完成时间选车；指定车辆任务仍保持指定。各车继续使用本车 Nav2。</p>
    <div className="of-toolbar">{Object.entries(robots).map(([r,v]:any)=><span key={r} data-testid={`rmf-member-${r}`}>{name(r)}：{v.registered?'已注册':'注册中'} · {trafficStates[v.state] || '等待状态'}</span>)}</div>
    <details><summary>提交自动分配单点 / 多点任务</summary><p>共享地图坐标，每行填写横坐标、纵坐标、朝向角度。</p><textarea aria-label="RMF自动分配航点" rows={3} value={text} onChange={e=>setText(e.target.value)} placeholder="1.0, 0.0, 0&#10;2.0, 0.5, 90" /><button disabled={busy} onClick={submit}>由 RMF 自动分配任务</button></details>
    <div className="of-table-scroll"><table><thead><tr><th>RMF 任务编号</th><th>车辆</th><th>任务状态</th><th>反馈</th></tr></thead><tbody>{tasks.map((task:any)=><tr key={task.request_id} data-testid={`rmf-task-${task.request_id}`}><td>{task.task_id || '等待任务编号'}</td><td>{name(task.robot)}</td><td>{phases[task.phase] || task.phase}</td><td>{task.message}</td></tr>)}{!tasks.length&&<tr><td colSpan={4} className="of-center of-muted">暂无 RMF 任务</td></tr>}</tbody></table></div></>;
  if (embedded) return <div role="region" aria-label="Open-RMF调度" className="of-rmf-embedded"><details className="of-section-body"><summary>Open-RMF 自动分配与任务记录 · {tasks.length} 项</summary>{body}</details></div>;
  return <section className="of-panel" aria-label="Open-RMF调度"><div className="of-section-title"><h2>Open-RMF 调度</h2><span>{Object.values(robots).filter((r:any)=>r.registered).length} 台已注册 · {tasks.length} 个任务</span></div><div className="of-section-body">{body}</div></section>;
}
