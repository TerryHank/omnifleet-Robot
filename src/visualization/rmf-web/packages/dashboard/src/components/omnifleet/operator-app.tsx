import React from 'react';
import { command, enqueueCommand, FleetState, localPoints, Pose, request, sample } from './api';
import { FleetMap } from './map';
import { PermanentParameters } from './permanent';
import { Diagnostics, Telemetry } from './telemetry';
import './operator.css';
import { ManualQueue } from './manual-queue';
import { TrafficPanel } from './traffic';
import { FormationPanel } from './formation';
import { RmfPanel } from './rmf';

const orderKey = 'omnifleet.web.vehicleOrder';
const labels: Record<string, string> = { accepted: '请求已接收', saved: '已保存', cleared: '已清除', rejected: '请求未通过', failed: '请求失败', queued: '等待处理', renamed: '名称已保存', reassigned: '调度前缀已生效', registering: '正在重新配准', execution_configured: '调度许可已保存', RMF_PAUSED: '等待 RMF 交通恢复', SCHEDULED: '等待计划时间', ARMING: '申请控制权', YIELDING: '等待路权', CANCEL_UNCONFIRMED: '停止未确认', IDLE: '空闲', PLANNING: '规划中', WAITING: '等待放行', EXECUTING: '执行中', COMPLETED: '已完成', STOPPING: '正在停止', STOPPED: '已停止', FAILED: '任务失败', INVALIDATED: '地图会话已变化', BLOCKED: '路线受阻' };
export function OperatorApp({ initialPage = 'dispatch' }: { initialPage?: string }) {
  const [state, setState] = React.useState<FleetState | null>(null), [connected, setConnected] = React.useState(false);
  const [page, setPage] = React.useState(initialPage === 'tasks' ? 'dispatch' : initialPage), [selected, setSelected] = React.useState('');
  const [order, setOrder] = React.useState<string[]>([]), [mode, setMode] = React.useState(initialPage === 'tasks' ? 'routes' : 'follow');
  const [distance, setDistance] = React.useState('1'), [receipt, setReceipt] = React.useState('等待中央实时状态…');
  const [prefixes, setPrefixes] = React.useState<Record<string, string>>({}), [drafts, setDrafts] = React.useState<Record<string, string>>({});
  const [busy, setBusy] = React.useState(false), [speed, setSpeed] = React.useState(.15);
  const [mapPath, setMapPath] = React.useState('');
  const [parameterQuery, setParameterQuery] = React.useState('');
  const dragging = React.useRef(''), holding = React.useRef<number | null>(null), stateRef = React.useRef(state); stateRef.current = state;
  const pendingOrder = React.useRef<{ order: string[]; revision: number; sent: number } | null>(null), orderInitialized = React.useRef(false);
  const manualTarget = React.useRef('');
  const manualFailure = React.useRef('');
  const manualRequests = React.useRef(new Map<string, { robot: string; velocity: [number, number] }>());
  const manualQueue = React.useRef<ManualQueue | null>(null);
  if (!manualQueue.current) manualQueue.current = new ManualQueue(async (item) => {
    const snapshot = stateRef.current;
    if (!snapshot?.assignments[item.robot]) throw new Error('操控目标不可用');
    const id = await enqueueCommand(snapshot, 'web_manual', { robot_id: snapshot.assignments[item.robot].robot_name, velocity: item.velocity });
    manualRequests.current.set(id, item);
  }, (error, item) => {
    manualFailure.current = '遥控发送失败：' + error.message; setReceipt(manualFailure.current);
    if (holding.current !== null) { clearInterval(holding.current); holding.current = null; }
    if (item.velocity.some((v) => v !== 0)) manualQueue.current?.submit(item.robot, [0, 0]);
  });

  React.useEffect(() => { setPage(initialPage === 'tasks' ? 'dispatch' : initialPage); if (initialPage === 'tasks') setMode('routes'); }, [initialPage]);
  React.useEffect(() => {
    let live = true, timer: ReturnType<typeof setTimeout>;
    const refresh = async () => {
      try {
        const next: FleetState = await request('/state');
        if (!live) return;
        setState(next); setConnected(true);
        const robots = Object.keys(next.assignments);
        const traffic = next.missions.traffic || {};
        if (!orderInitialized.current) {
          orderInitialized.current = true;
          let saved: string[] = [];
          try { const value = JSON.parse(localStorage.getItem(orderKey) || '[]'); if (Array.isArray(value)) saved = value.filter((r) => typeof r === 'string'); } catch { /* No saved order. */ }
          if (!traffic.order_configured && saved.length && !next.missions.follow.active && !next.missions.formation?.active) {
            const restored = Array.from(new Set([...saved.filter((r) => robots.includes(r)), ...robots]));
            pendingOrder.current = { order: restored, revision: traffic.order_revision || 0, sent: Date.now() };
            void command('dispatch_order', { order: restored.map((r) => next.assignments[r].robot_name), order_revision: traffic.order_revision || 0 }).catch((error) => { pendingOrder.current = null; setReceipt(error.message); });
          }
        }
        if (pendingOrder.current && ((traffic.order_revision || 0) > pendingOrder.current.revision || Date.now()-pendingOrder.current.sent > 15000)) pendingOrder.current = null;
        setSelected((r) => robots.includes(r) ? r : robots[0]);
        setOrder((previous) => {
          let saved: string[] = [];
          try { saved = JSON.parse(localStorage.getItem(orderKey) || '[]'); } catch { /* First visit has no order. */ }
          const base = pendingOrder.current?.order || traffic.order || (previous.length ? previous : saved.length ? saved : next.missions.follow.order || robots);
          return [...base.filter((r: string) => robots.includes(r)), ...robots.filter((r) => !base.includes(r))];
        });
      } catch (error) { if (live) { setConnected(false); setReceipt((error as Error).message); } }
      finally { if (live) timer = setTimeout(() => void refresh(), 300); }
    };
    void refresh(); return () => { live = false; clearTimeout(timer); };
  }, []);
  const act = async (op: string, fields: Record<string, unknown> = {}) => {
    setBusy(true);
    try { const result = await command(op, fields); setReceipt(result.message || labels[result.phase] || `已收到回执：${result.phase}`); return result; }
    catch (error) { setReceipt((error as Error).message); return null; }
    finally { setBusy(false); }
  };
  const reorder = (robot: string, to: number) => {
    if (!state || !connected || busy || pendingOrder.current || state.missions.follow.active || state.missions.formation?.active) return;
    const next = order.filter((r) => r !== robot); next.splice(to, 0, robot); setOrder(next); localStorage.setItem(orderKey, JSON.stringify(next));
    pendingOrder.current = { order: next, revision: state.missions.traffic?.order_revision || 0, sent: Date.now() };
    void act('dispatch_order', { order: next.map(name), order_revision: pendingOrder.current.revision }).then((result) => { if (!result) pendingOrder.current = null; });
  };
  const release = React.useCallback(() => {
    if (holding.current === null) return;
    clearInterval(holding.current); holding.current = null;
    if (manualTarget.current) manualQueue.current?.submit(manualTarget.current, [0, 0]);
  }, []);
  React.useEffect(() => {
    window.addEventListener('blur', release); document.addEventListener('visibilitychange', release);
    return () => { release(); window.removeEventListener('blur', release); document.removeEventListener('visibilitychange', release); };
  }, [release]);

  React.useEffect(() => { release(); }, [selected, order[0], mode, state?.missions.formation?.active, state?.missions.formation?.saved?.leader]);
  React.useEffect(() => { if (!connected) release(); }, [connected, release]);
  React.useEffect(() => {
    if (!state) return;
    if (state.operator_stopped) release();
    for (const [id, item] of Array.from(manualRequests.current)) {
      const result = state.commands[id];
      if (!result) continue;
      manualRequests.current.delete(id);
      const label = state.assignments[item.robot]?.robot_name || item.robot;
      if (['rejected', 'failed'].includes(result.phase)) { release(); manualFailure.current = label + ' 无法操控：' + result.message; setReceipt(manualFailure.current); }
      else if (!manualFailure.current) setReceipt(label + '：' + (result.message || result.phase) + ' · 指令 ' + item.velocity[0].toFixed(2) + ' m/s / ' + item.velocity[1].toFixed(2) + ' rad/s');
    }
  }, [state, release]);
  const hold = (event: React.PointerEvent, v: number, w: number) => {
    if (!state || holding.current !== null) return;
    if (state.operator_stopped) { setReceipt('调度处于软件停止状态，请先点击“释放停止”'); return; }
    if (!Number.isFinite(v) || !Number.isFinite(w) || Math.abs(v) > .3 || Math.abs(w) > 1.5) { setReceipt('遥控速度超出本车遥控接口范围'); return; }
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
    const target = state.missions.formation?.active ? state.missions.formation.saved.leader : mode === 'follow' ? order[0] : selected;
    manualTarget.current = target; manualFailure.current = '';
    const send = () => manualQueue.current?.submit(target, [v, w]);
    send(); holding.current = window.setInterval(send, 100);
  };
  if (!state || !selected) return <main className="of-app"><div className="of-panel of-empty"><h1>正在连接本机调度服务</h1><p>{receipt}</p><button onClick={() => window.location.reload()}>重新连接</button></div></main>;
  const follow = state.missions.follow, formation = state.missions.formation || {}, target = formation.active ? formation.saved.leader : mode === 'follow' ? order[0] : selected;
  const name = (robot: string) => state.assignments[robot]?.robot_name || robot;
  const robot = state.robots[selected], nav = sample(state, selected, 'navigation'), control = sample(state, selected, 'control');
  const waypointRobot = formation.active ? target : selected;
  const route = state.missions.routes[waypointRobot];
  const text = drafts[waypointRobot] ?? (route?.points || []).map((p: any) => [p.pose[0], p.pose[1], p.pose[2] * 180 / Math.PI].map((v: number) => +v.toFixed(4)).join(', ')).join('\n');
  const setText = (value: string) => setDrafts({ ...drafts, [waypointRobot]: value });
  const importPoints = () => {
    const catalog = sample(state, waypointRobot, 'waypoints');
    if (!catalog || catalog.frame_id !== 'map') { setReceipt('尚未收到本车 map 航点'); return; }
    setText(catalog.waypoints.map((p: any) => [p.x, p.y, p.yaw_deg].join(', ')).join('\n')); setReceipt('已导入车端航点，请保存');
  };
  const permit = async () => {
    for (const r of order) if (!state.execution_enabled[r]) await command('execution_permission', { robot_id: name(r), enabled: true });
    const until = Date.now() + 5000;
    while (Date.now() < until) { const latest: FleetState = await request('/state'); if (order.every((r) => latest.execution_enabled[r])) return; await new Promise((resolve) => setTimeout(resolve, 150)); }
    throw new Error('执行许可尚未收到本车回读，请查看车辆连接状态');
  };
  const switchMode = async (next: string) => {
    release(); setMode(next);
    if (next === 'follow') { try { await permit(); } catch (error) { setReceipt((error as Error).message); } }
  };
  const goal = async (pose: Pose, multi: boolean, estimate = false) => {
    await act(estimate ? 'web_estimate' : 'web_goal', { robot_id: name(target), pose, multi });
  };
  const startFormation = () => { release(); void (async () => { try { await permit(); await act('formation_start', { order: order.map(name) }); } catch (error) { setReceipt((error as Error).message); } })(); };
  const service = (id: string) => void act('web_service', { robot_id: name(selected), service: id });
  return <main className="of-app">
    <div className="of-statusbar"><span><i className={connected ? 'of-dot' : 'of-dot offline'} />{connected ? '本机调度在线' : '连接中断 · 当前为缓存状态'}</span><span>共享地图 {state.maps.alignment_valid ? '已配准' : '等待配准'} · {Object.values(state.robots).filter((r: any) => r.online).length}/{Object.keys(state.assignments).length} 台在线</span><span className="of-status-time">{new Date().toLocaleTimeString('zh-CN', { hour12: false })}</span></div>
    {state.operator_stopped && <div className="of-stop-banner" role="alert"><strong>调度处于软件停止状态</strong><span>方向操控和导航已暂停。释放停止不会自动续跑旧任务。</span><button onClick={() => void act('web_stop', { stopped: false })}>释放停止并恢复操控</button></div>}
    <nav className="of-tabs" aria-label="机器人功能"><div>{[['dispatch', '实时调度'], ['parameters', '永久导航参数'], ['telemetry', '实时数据 / 话题'], ['diagnostics', '智能诊断'], ['maintenance', '地图与运维']].map(([id, label]) => <button key={id} aria-selected={page === id} onClick={() => { release(); setPage(id); }}>{label}</button>)}</div><label>当前车辆<select aria-label="当前车辆" value={selected} onChange={(e) => { release(); setSelected(e.target.value); }}>{order.map((r) => <option value={r} key={r}>{name(r)}</option>)}</select></label></nav>
    {page === 'parameters' ? <PermanentParameters key={selected} state={state} robot={selected} onResult={setReceipt} initialQuery={parameterQuery} /> : page === 'telemetry' ? <Telemetry key={selected} state={state} robot={selected} /> : page === 'diagnostics' ? <Diagnostics key={selected} state={state} robot={selected} onResult={setReceipt} onParameter={(id) => { setParameterQuery(id); setPage('parameters'); }} /> : page === 'maintenance' ? <section className="of-panel"><div className="of-section-title"><h2>地图与导航运维</h2><span>{name(selected)}</span></div><div className="of-maintenance-grid">
      <article><h3>共享地图与同伴地图</h3><p>{state.maps.alignment_valid ? '当前地图配准有效' : '正在等待有效配准'}</p><button disabled={busy} onClick={() => void act('align_maps')}>重新配准</button><pre>{JSON.stringify({ transforms: state.maps.transforms, peers: state.maps.peer_occupied_cells, registration: state.registration }, null, 2)}</pre></article>
      <article><h3>清除旧动态障碍</h3><p>调用本车代价地图服务；后续真实传感器数据会继续更新。</p><button disabled={busy} onClick={() => service('clear_local')}>清除局部代价</button><button disabled={busy} onClick={() => service('clear_global')}>清除全局代价</button></article>
      <article><h3>导航数据录制</h3><p>在所选车辆上录制，并读取开始 / 结束回执。</p><button disabled={busy} onClick={() => service('start_bag')}>开始录包</button><button disabled={busy} onClick={() => service('stop_bag')}>停止录包并保存</button></article>
      <article><h3>地图保存与加载</h3><input aria-label="本车地图文件路径" placeholder="车端地图文件路径（不含扩展名）" value={mapPath} onChange={(e) => setMapPath(e.target.value)} /><div><button disabled={busy || !mapPath.trim()} onClick={() => void act('web_service', { robot_id: name(selected), service: 'save_map', map_path: mapPath })}>保存地图与航点</button><button disabled={busy || !mapPath.trim()} onClick={() => { if (window.confirm('加载地图会切换本车定位会话，继续？')) void act('web_service', { robot_id: name(selected), service: 'load_map', map_path: mapPath }); }}>加载地图与航点</button></div><p>重置会使当前定位会话和旧航点失效。</p><button className="danger" disabled={busy} onClick={() => { if (window.confirm('确认重置所选车辆的当前地图？')) service('reset_map'); }}>重置本车地图</button></article>
    </div></section> : <div className="of-workspace"><aside>
      <section className="of-panel"><div className="of-section-title"><h2>车辆</h2><span>{order.length} 台 · 拖动排序</span></div><ol className="of-vehicles" aria-label="车辆及领车顺序">{order.map((r, index) => {
        const vehicle = state.robots[r], n = sample(state, r, 'navigation'), c = sample(state, r, 'control');
        return <li key={r} draggable={!follow.active} data-testid={`vehicle-${r}`} className={selected === r ? 'selected' : ''} onDragStart={() => { dragging.current = r; }} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); if (dragging.current && !follow.active) reorder(dragging.current, index); dragging.current = ''; }}>
          <button className="of-drag" aria-label={`拖动排序 ${name(r)}`} title="拖动排序" onClick={() => setSelected(r)}>⠿</button><div className="of-vehicle-main"><div className="of-prefix"><input aria-label={`车辆前缀 ${name(r)}`} value={prefixes[r] ?? name(r)} onChange={(e) => setPrefixes({ ...prefixes, [r]: e.target.value })} onKeyDown={(e) => { if (e.key === 'Enter') void act('robot_reassign', { connection_id: r, prefix: prefixes[r] ?? name(r) }); }} /><button disabled={busy || follow.active} onClick={() => void act('robot_reassign', { connection_id: r, prefix: prefixes[r] ?? name(r) })}>应用前缀</button></div><div className="of-vehicle-meta"><span className={vehicle?.online ? 'online' : 'offline-text'}>{vehicle?.online ? '● 在线' : '● 离线'}</span><span>{index === 0 ? '领车' : `跟随 ${name(order[index - 1])}`}</span><span>{n?.local_ready ? '导航就绪' : n?.readiness_reason || '等待导航'}</span></div><small>{state.assignments[r].namespace} · {sample(state, r, 'voltage')?.toFixed?.(2) ?? '—'} V · {c?.velocity?.[0]?.toFixed(2) ?? '—'} m/s</small></div><div className="of-order-buttons"><button aria-label={`${name(r)} 上移`} disabled={!index || follow.active} onClick={() => reorder(r, index - 1)}>↑</button><button aria-label={`${name(r)} 下移`} disabled={index === order.length - 1 || follow.active} onClick={() => reorder(r, index + 1)}>↓</button></div>
        </li>;
      })}</ol><div className="of-toolbar"><span>已选领车：<strong data-testid="selected-leader">{name(order[0])}</strong></span><button disabled={busy} onClick={() => void act('align_maps')}>配准地图</button></div></section>
      <FormationPanel state={state} order={order} busy={busy} act={act} start={startFormation} />
      <section className="of-panel"><div className="of-segment"><button aria-selected={mode === 'follow'} onClick={() => void switchMode('follow')}>跟随领车</button><button aria-selected={mode === 'routes'} onClick={() => void switchMode('routes')}>各车航点</button></div>
        {mode === 'follow' ? <div className="of-section-body"><h3>实时前车跟随</h3><p className="of-muted">按列表顺序逐车跟随。地图发点和下方遥控指向领车。</p><label>跟车间距<input aria-label="跟车间距" type="number" min="0" step="any" value={distance} onChange={(e) => setDistance(e.target.value)} /> 米</label><div className="of-toolbar"><button className="primary" disabled={busy || !connected || !!state.missions.traffic?.zones?.length} onClick={() => { void (async () => { try { await permit(); await act('follow_start', { order: order.map(name), distance: distance.trim() ? Number(distance) : null }); } catch (error) { setReceipt((error as Error).message); } })(); }}>开始跟随</button><button disabled={busy} onClick={() => void act('follow_stop')}>停止跟随</button></div><p data-testid="follow-state">当前领车：{follow.leader ? name(follow.leader) : '尚未启动'} · {labels[follow.phase] || follow.phase}</p><p>{follow.message}</p></div> : <div className="of-section-body"><h3>{name(waypointRobot)} 的多点航点</h3><p className="of-muted">地图发布位姿立即执行单点；“添加多点航点”立即加入本车队列。下方文本为本车 map 坐标（x, y, 角度）。</p><textarea aria-label="多点航点坐标" rows={5} value={text} onChange={(e) => setText(e.target.value)} placeholder="1.0, 0.0, 0&#10;2.0, 0.5, 90" /><div className="of-toolbar"><button onClick={importPoints}>导入车端航点</button><button onClick={() => { const p = sample(state, waypointRobot, 'pose'); if (p) setText((text + '\n' + [p.x, p.y, p.yaw * 180 / Math.PI].join(', ')).trim()); }}>追加当前位置</button><button disabled={busy} onClick={() => { try { void act('route_save', { robot_id: name(waypointRobot), points: localPoints(text) }).then((value) => { if (value) setDrafts((previous) => { const next = { ...previous }; delete next[waypointRobot]; return next; }); }); } catch (error) { setReceipt((error as Error).message); } }}>保存队列</button></div><div className="of-toolbar"><button disabled={busy} onClick={() => void act('route_prepare', { robot_id: name(waypointRobot) })}>规划预检</button></div><button className="primary of-full" disabled={busy} onClick={() => void act('routes_start')}>{formation.active ? '规划并执行领车航点' : '规划并执行全部车辆航点'}</button><p className="of-muted">单车执行与停止已合并到右侧调度表；没有航点的车辆会跳过。</p><button disabled={busy} onClick={() => void act('routes_stop')}>停止全部航点导航</button></div>}
        <div className="of-toolbar of-section-body"><button onClick={() => void act('route_clear', { robot_id: name(target) })}>清除 {name(target)} 航点</button><button onClick={() => void act('routes_clear')}>清除全部航点</button></div>
      </section>
      <section className="of-panel"><div className="of-section-title"><h2>操控 · {name(target)}</h2><label>线速度<input aria-label="遥控线速度" type="number" min="0" max=".3" step=".01" value={speed} onChange={(e) => setSpeed(Number(e.target.value))} /> m/s</label></div><div className="of-dpad">{[[1, 0, '前进', '↑'], [0, 1, '左转', '←'], [0, 0, '停止操控', '■'], [0, -1, '右转', '→'], [-1, 0, '后退', '↓']].map(([v, w, label, icon], i) => <button key={i} aria-label={String(label)} className={`direction-${i}`} disabled={i !== 2 && (!connected || !!state.operator_stopped)} onPointerDown={(e) => hold(e, Number(v) * speed, Number(w) * .6)} onPointerUp={release} onPointerCancel={release} onLostPointerCapture={release}>{icon}</button>)}</div><p className="of-muted of-center">{state.operator_stopped ? '软件停止保持中，请先释放停止。' : '按住运动，松开停止；失焦时停止。'}</p></section>
    </aside><div className="of-main-column"><FleetMap state={state} target={target} onGoal={(p, multi, estimate) => void goal(p, multi, estimate)} onResult={setReceipt} />
      <TrafficPanel state={state} robot={selected} busy={busy || !connected} act={act}><RmfPanel state={state} busy={busy} act={act} onResult={setReceipt} embedded /></TrafficPanel>
      <div className="of-grid-two"><section className="of-panel of-device"><h3>导航状态 · {name(selected)}</h3><p>{nav?.message || nav?.readiness_reason || '等待读取'}</p><small>{control?.control_mode} · {nav?.selected_controller} · {robot?.domain_id !== undefined ? `ROS Domain ${robot.domain_id}` : ''}</small></section><section className="of-panel of-device"><h3>门 / 电梯 / 信标</h3><p className="of-muted">暂无已接入设备数据</p><a href="/rmf/map">查看 RMF 原生设备页面 ↗</a></section></div>
    </div></div>}
    <div className="of-operation-receipt" role="status"><span>操作回执</span><p>{receipt}</p><button className="danger" onClick={() => { release(); void act('web_stop', { stopped: true }); }}>全部停止</button><button onClick={() => void act('web_stop', { stopped: false })}>释放停止</button></div>
  </main>;
}
