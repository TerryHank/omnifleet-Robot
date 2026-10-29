import React from 'react';
import { FleetState } from './api';

const phases: Record<string, string> = { UNSAVED: '尚未保存队形', SAVED: '队形已保存', FORMING: '跟车正在到位', HOLDING: '保持队形中', STOPPED: '编队已停止', FAILED: '编队异常停止' };
export function FormationPanel({ state, order, busy, act, start }: { state: FleetState; order: string[]; busy: boolean; act: (op: string, fields?: Record<string, unknown>) => Promise<any>; start: () => void; }) {
  const formation = state.missions.formation || {}, saved = formation.saved;
  const name = (robot: string) => state.assignments[robot]?.robot_name || robot;
  return <section className="of-panel" aria-label="保持队形编队">
    <div className="of-section-title"><h2>保持当前位置队形</h2><span>{phases[formation.phase] || '尚未保存队形'}</span></div>
    <div className="of-section-body"><p className="of-muted">按原车辆列表确定领车。各车摆好位置后点击“保持队形”，保存各车相对领车的位置和朝向；开始编队后，向领车发送单点或多点航点，跟车按保存的关系动态跟踪。</p>
      <div className="of-toolbar"><button disabled={busy} onClick={() => void act('formation_capture', { order: order.map(name) })}>保持队形</button><button className="primary" disabled={busy} onClick={start}>开始编队</button><button disabled={busy} onClick={() => void act('formation_stop')}>停止编队</button></div>
      <p data-testid="formation-state">{phases[formation.phase] || '尚未保存队形'}{saved ? ` · 领车：${name(saved.leader)}` : ''}</p><p>{formation.message}</p>
      {formation.active && <p className="of-muted">编队进行中：地图发点、地图航点编辑和遥控均指向领车 {name(saved?.leader)}。已保存队形由 WSL 动态生成各跟车目标。</p>}
      {saved && <div className="of-table-scroll"><table><thead><tr><th>车辆</th><th>角色</th><th>相对领车位置</th><th>相对朝向</th><th>当前位置偏差</th><th>当前朝向偏差</th></tr></thead><tbody>{saved.order.map((robot: string, index: number) => {
        const offset = saved.offsets[robot], error = formation.position_errors?.[robot], angle = formation.heading_errors?.[robot];
        return <tr key={robot} data-testid={`formation-row-${robot}`}><td>{name(robot)}</td><td>{index ? `跟车 ${index}` : '领车'}</td><td>{offset ? `前后 ${offset[0].toFixed(2)} 米，左右 ${offset[1].toFixed(2)} 米` : '—'}</td><td>{offset ? `${(offset[2]*180/Math.PI).toFixed(1)}°` : '—'}</td><td>{Number.isFinite(error) ? `${error.toFixed(2)} 米` : '—'}</td><td>{Number.isFinite(angle) ? `${(angle*180/Math.PI).toFixed(1)}°` : '—'}</td></tr>;
      })}</tbody></table></div>}
    </div>
  </section>;
}
