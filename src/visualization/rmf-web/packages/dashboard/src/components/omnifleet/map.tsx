import React from 'react';
import { command, compose, FleetState, Pose, request, sample } from './api';
import { Scene } from './scene';
import { useTopics } from './telemetry';

interface Props { state: FleetState; target: string; onGoal: (pose: Pose, multi: boolean, estimate?: boolean) => void; onResult: (message: string) => void; }
export function FleetMap({ state, target, onGoal, onResult }: Props) {
  const [layers, setLayers] = React.useState({ shared: true, fleet_costmap: true, map: false, peer: false, global: false, local: false });
  const [images, setImages] = React.useState<Record<string, any>>({});
  const [mode, setMode] = React.useState('pan');
  const [three, setThree] = React.useState(false);
  const [cloud, setCloud] = React.useState(false);
  const cloudAvailable = Object.values(state.robots[target]?.graph?.topics || {}).some((types: any) => types.includes('sensor_msgs/msg/PointCloud2'));
  const [view, setView] = React.useState({ x: -4, y: -3, w: 8, h: 6 });
  const [mark, setMark] = React.useState<Pose | null>(null);
  const [measure, setMeasure] = React.useState<Pose[]>([]);
  const [drag, setDrag] = React.useState<any>(null);
  const [frames, setFrames] = React.useState<any[]>([]);
  const graph = state.robots[target]?.graph?.topics || {};
  const planTopics = ['/plan', '/local_plan', '/optimal_trajectory'].filter((topic) => graph[topic]?.includes('nav_msgs/msg/Path'));
  const plans = useTopics(state, target, planTopics);
  const svg = React.useRef<SVGSVGElement>(null);
  const start = React.useRef<any>(null);
  const revision = state.identity_revision;
  const targetRef = React.useRef(target); targetRef.current = target;
  const poseOf = (robot: string): Pose | undefined => {
    const p = sample(state, robot, 'pose'), transform = state.maps.transforms?.[robot];
    return p && transform ? compose(transform, [p.x, p.y, p.yaw]) : undefined;
  };
  const fit = React.useCallback(() => {
    const poses = Object.keys(state.assignments).map(poseOf).filter(Boolean) as Pose[];
    if (!poses.length) return;
    const x = poses.reduce((sum, p) => sum + p[0], 0) / poses.length, y = poses.reduce((sum, p) => sum + p[1], 0) / poses.length;
    setView({ x: x - 4, y: -y - 3, w: 8, h: 6 });
  }, [state.maps.alignment_valid]);
  React.useEffect(() => { fit(); }, [fit]);
  React.useEffect(() => {
    let live = true;
    const load = async () => {
      const next: Record<string, any> = {};
      for (const [layer, show] of Object.entries(layers)) if (show) {
        try { next[layer] = await request(`/maps/${encodeURIComponent(target)}/${layer}`); }
        catch (error) { next[layer] = { error: (error as Error).message }; }
      }
      const scene = await request(`/scene/${encodeURIComponent(target)}`).catch(() => null);
      if (live) { setImages(next); setFrames(scene?.transforms || []); }
    };
    void load(); const timer = window.setInterval(() => void load(), 900);
    return () => { live = false; clearInterval(timer); };
  }, [target, JSON.stringify(layers), revision]);
  React.useEffect(() => { start.current = null; setMark(null); setDrag(null); }, [target, revision, mode]);
  React.useEffect(() => { const cancel = (event: KeyboardEvent) => { if (event.key === 'Escape') { start.current = null; setMark(null); setDrag(null); setMeasure([]); } }; window.addEventListener('keydown', cancel); return () => window.removeEventListener('keydown', cancel); }, []);
  const point = (event: React.PointerEvent): Pose => {
    const rect = svg.current!.getBoundingClientRect();
    const matrix = svg.current!.getScreenCTM();
    if (matrix) { const p = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse()); return [p.x, -p.y, 0]; }
    return [view.x + (event.clientX - rect.left) / rect.width * view.w, -view.y - (event.clientY - rect.top) / rect.height * view.h, 0];
  };
  const release = async (event: React.PointerEvent) => {
    if (!start.current) return;
    const initial = start.current; start.current = null;
    const current = point(event);
    if (drag) {
      const assignment = state.assignments[drag.robot];
      setDrag(null);
      try { const result = await command('route_update', { robot_id: assignment.robot_name, index: drag.index + 1, position: current.slice(0, 2), ...drag.snapshot }); onResult(result.message); }
      catch (error) { onResult((error as Error).message); }
    } else if (['goal', 'multi', 'estimate'].includes(mode)) {
      const yaw = Math.hypot(current[0] - initial.p[0], current[1] - initial.p[1]) > .05 ? Math.atan2(current[1] - initial.p[1], current[0] - initial.p[0]) : poseOf(target)?.[2] || 0;
      onGoal([initial.p[0], initial.p[1], yaw], mode === 'multi', mode === 'estimate'); setMark(null);
    }
  };
  const zoom = (factor: number) => setView((v) => ({ x: v.x + v.w * (1 - factor) / 2, y: v.y + v.h * (1 - factor) / 2, w: v.w * factor, h: v.h * factor }));
  const colors = [0, 1, 2, 3].map((i) => `var(--of-vehicle-${i})`);
  const framePose = (frame: string, seen: string[] = []): Pose | null => {
    frame = frame.replace(/^\//, '');
    if (frame === 'map') return [0, 0, 0];
    if (seen.includes(frame)) return null;
    const edge = frames.find((t) => t.child_frame_id.replace(/^\//, '') === frame);
    if (!edge) return null;
    const parent = framePose(edge.header.frame_id, [...seen, frame]);
    if (!parent) return null;
    const p = edge.transform.translation, q = edge.transform.rotation;
    return compose(parent, [p.x, p.y, Math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))]);
  };
  return <section className="of-panel of-map-panel">
    <div className="of-section-title"><h2>共享地图</h2><span>目标车辆 · {state.assignments[target]?.robot_name || '—'} <i className={state.maps.alignment_valid ? 'of-dot' : 'of-dot offline'} /></span></div>
    <div className="of-map-tools">
      {[['pan', '↖', '选择 / 平移'], ['goal', '⚑', '发布位姿（单点导航）'], ['multi', '⊕', '添加多点航点'], ['estimate', '↥', '设置初始位姿'], ['measure', '╱', '测距']].map(([id, icon, label]) => <button key={id} title={label} aria-label={label} aria-pressed={mode === id} onClick={() => { setThree(false); setMode(id); }}>{icon}</button>)}
      <button aria-label="切换三维视图" aria-pressed={three} onClick={() => setThree(!three)}>3D</button><button aria-label="显示点云" aria-pressed={three && cloud} disabled={!cloudAvailable} title={cloudAvailable ? '显示当前车辆实时点云' : '当前车辆尚未发现点云话题'} onClick={() => { setCloud(!(three && cloud)); setThree(true); }}>点云</button><button aria-label="放大" onClick={() => zoom(.75)}>＋</button><button aria-label="缩小" onClick={() => zoom(1.33)}>－</button><button onClick={fit}>重置视图</button>
      <details className="of-layer-menu"><summary>▱ 图层</summary>{Object.entries(layers).map(([key, checked]) => <label key={key}><input type="checkbox" checked={checked} onChange={(e) => setLayers({ ...layers, [key]: e.target.checked })} />{{ shared: '共享地图', fleet_costmap: 'WSL 共享代价', map: '本车地图', peer: '本车同伴占用', global: '本车全局代价', local: '本车局部代价' }[key]}</label>)}</details>
    </div>
    <div className="of-map-help">{three ? '拖动旋转 · 滚轮缩放 · 实时车体与点云' : mode === 'pan' ? '拖动地图平移；拖动航点圆环修改位置' : mode === 'measure' ? '点击两点测距' : '按住选择位置，拖动设定朝向，松开后发送'}{measure.length === 2 && ` · ${Math.hypot(measure[1][0] - measure[0][0], measure[1][1] - measure[0][1]).toFixed(2)} m`}</div>
    {three ? <Scene state={state} robot={target} image={images.shared || images.map} overlay={images.fleet_costmap} cloud={cloud} onCloudChange={setCloud} /> : <svg ref={svg} data-testid="fleet-map" aria-label="共享地图与航点编辑" role="img" viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`} preserveAspectRatio="xMidYMid meet"
      onWheel={(e) => zoom(e.deltaY > 0 ? 1.1 : .9)}
      onPointerDown={(e) => { if (e.button !== 0) return; svg.current?.setPointerCapture(e.pointerId); const p = point(e); start.current = { p, client: [e.clientX, e.clientY], view }; if (mode === 'measure') { setMeasure((m) => m.length === 1 ? [m[0], p] : [p]); start.current = null; } else if (mode !== 'pan') setMark(p); }}
      onPointerMove={(e) => { if (!start.current) return; const p = point(e); if (drag) setDrag({ ...drag, p }); else if (mode === 'pan') { const rect = svg.current!.getBoundingClientRect(); const scale = Math.min(rect.width / view.w, rect.height / view.h); setView({ ...start.current.view, x: start.current.view.x - (e.clientX - start.current.client[0]) / scale, y: start.current.view.y - (e.clientY - start.current.client[1]) / scale }); } else setMark([start.current.p[0], start.current.p[1], Math.atan2(p[1] - start.current.p[1], p[0] - start.current.p[0])]); }}
      onPointerUp={(e) => void release(e)} onPointerCancel={() => { start.current = null; setMark(null); setDrag(null); }}>
      <defs><pattern id="of-grid" width=".5" height=".5" patternUnits="userSpaceOnUse"><path d="M .5 0 L 0 0 0 .5" fill="none" stroke="var(--of-grid)" strokeWidth=".008" /></pattern></defs><rect x={view.x} y={view.y} width={view.w} height={view.h} fill="url(#of-grid)" />
      {Object.entries(images).map(([key, image]) => image.png && image.transform && <g key={key} transform={`translate(${image.transform[0]} ${-image.transform[1]}) rotate(${-image.transform[2] * 180 / Math.PI})`}><g transform={`translate(${image.origin[0]} ${-image.origin[1]}) rotate(${-image.origin[2] * 180 / Math.PI}) scale(${image.resolution})`}><image href={image.png} x="0" y={-image.height} width={image.width} height={image.height} style={{ imageRendering: 'pixelated' }} opacity={key === 'shared' || key === 'map' ? .82 : .7} /></g></g>)}
      {planTopics.map((topic, index) => { const value = plans[topic]?.value, frame = value?.header?.frame_id; if (!frame || (plans[topic].localization_epoch && plans[topic].localization_epoch !== sample(state, target, 'navigation')?.localization_epoch)) return null; const local = framePose(frame), transform = frame === 'fleet_map' ? [0, 0, 0] as Pose : local && compose(state.maps.transforms[target] || [0, 0, 0], local); if (!transform) return null; return <polyline key={topic} data-testid="native-plan" fill="none" stroke={index ? 'var(--of-local-plan)' : 'var(--of-plan)'} strokeWidth=".035" points={(value.poses || []).map((p: any) => { const point = compose(transform, [p.pose.position.x, p.pose.position.y, 0]); return `${point[0]},${-point[1]}`; }).join(' ')} />; })}
      {(state.missions.traffic?.zones || []).map((z: any) => <g key={'traffic-' + z.id} pointerEvents="none" stroke={z.state === 'BLOCKED' ? '#df5151' : z.owner ? '#ed9c32' : '#39aa88'}><line x1={z.a[0]} y1={-z.a[1]} x2={z.b[0]} y2={-z.b[1]} strokeWidth={z.width} strokeLinecap="round" opacity=".22" /><text x={z.a[0]} y={-z.a[1] - .25} fontSize=".18" stroke="none" fill="currentColor">{z.id} · {z.owner ? state.assignments[z.owner]?.robot_name : '空闲'}</text>{['wait_a', 'wait_b'].map((k) => z[k] && <circle key={k} cx={z[k][0]} cy={-z[k][1]} r=".15" strokeWidth=".03" fill="none" />)}</g>)}
      {Object.entries(state.assignments).map(([robot, assignment], index) => {
        const transform = state.maps.transforms?.[robot], route = state.missions.routes[robot];
        const points: Pose[] = transform ? (route?.points || []).map((p: any) => compose(transform, p.pose)) : [];
        const pose = poseOf(robot), color = colors[index % colors.length];
        return <g key={robot} fill={color} stroke={color}><polyline fill="none" strokeWidth=".025" strokeDasharray=".08 .04" points={points.map((p) => `${p[0]},${-p[1]}`).join(' ')} />
          {points.map((p, n) => <g key={n} data-testid={`waypoint-${assignment.robot_name}-${n + 1}`} transform={`translate(${drag?.robot === robot && drag?.index === n ? drag.p[0] : p[0]} ${-(drag?.robot === robot && drag?.index === n ? drag.p[1] : p[1])})`} style={{ cursor: 'grab' }} onPointerDown={(e) => { e.stopPropagation(); if (sample(state, robot, 'navigation')?.navigation_active) { onResult('请先停止本车导航，再修改已安排航点'); return; } svg.current?.setPointerCapture(e.pointerId); start.current = { p, view }; setDrag({ robot, index: n, p, snapshot: { localization_epoch: route.epoch, route_revision: route.revision || 0, map_transform: state.maps.transforms[robot] } }); }}><circle r=".10" fill="var(--of-marker)" strokeWidth=".025" /><text x=".15" y="-.11" fontSize=".14" stroke="none">{assignment.robot_name} · {p && route.points[n].name || `航点${n + 1}`}</text><text textAnchor="middle" y=".045" fontSize=".12" stroke="none">{n + 1}</text></g>)}
          {pose && <g pointerEvents="none" transform={`translate(${pose[0]} ${-pose[1]})`}><circle r=".26" fill={color} opacity=".10" stroke="none" /><g transform={`rotate(${-pose[2] * 180 / Math.PI})`}><rect x="-.24" y="-.17" width=".48" height=".34" rx=".04" fill="var(--of-marker)" strokeWidth=".035" /><path d="M -.04 -.09 L .16 0 L -.04 .09 Z" stroke="none" /></g><text x=".28" y="-.25" stroke="none" fontSize=".20">{assignment.robot_name}</text></g>}
        </g>;
      })}
      {mark && <g transform={`translate(${mark[0]} ${-mark[1]}) rotate(${-mark[2] * 180 / Math.PI})`} stroke="var(--of-goal)" strokeWidth=".035"><circle r=".08" fill="none" /><path d="M 0 0 L .65 0 M .5 -.09 L .65 0 .5 .09" fill="none" /></g>}
      {measure.length === 2 && <line x1={measure[0][0]} y1={-measure[0][1]} x2={measure[1][0]} y2={-measure[1][1]} stroke="white" strokeWidth=".025" />}
    </svg>}
    <footer><span><i className="of-dot" /> 实时共享地图</span><span>{state.maps.alignment_valid ? '配准有效' : '等待配准'} · {Object.values(images).find((image) => image.error)?.error || '拖动 / 滚轮缩放'}</span></footer>
  </section>;
}
