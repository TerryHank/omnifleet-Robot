import appConfig from '../../app-config';

export const operatorUrl = `${appConfig.rmfServerUrl}/omnifleet/operator`;
export type Pose = [number, number, number];
export interface Assignment { namespace: string; robot_name: string; }
export interface FleetState {
  ready: boolean; token: string; identity_revision: number;
  assignments: Record<string, Assignment>; robots: Record<string, any>;
  maps: any; missions: any; commands: Record<string, any>;
  execution_enabled: Record<string, boolean>; registration: any;
  operator_stopped?: boolean;
  rmf?: any;
}
export async function request(path: string, options?: RequestInit) {
  const response = await fetch(`${operatorUrl}${path}`, { cache: 'no-store', ...options });
  const value = await response.json();
  if (!response.ok) throw new Error(value.detail || value.error || `接口响应 ${response.status}`);
  return value;
}
export async function command(op: string, fields: Record<string, unknown> = {}, wait = true) {
  const state: FleetState = await request('/state');
  const id = `web-${crypto.randomUUID()}`;
  await request('/command', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-OmniFleet-Token': state.token },
    body: JSON.stringify({ op, id, identity_revision: state.identity_revision, ...fields }) });
  if (!wait) return { phase: 'sent', request_id: id };
  const end = Date.now() + (op === 'web_diagnostic' ? 180000 : 65000);
  while (Date.now() < end) {
    const snapshot: FleetState = await request('/state');
    const result = snapshot.commands[id];
    if (result && !['forwarding', 'queued', 'pending', 'PRECHECKING', 'PREPARING'].includes(result.phase)) {
      if (['rejected', 'failed', 'FAILED', 'INVALIDATED'].includes(result.phase)) throw new Error(result.message || '本车拒绝了请求');
      return result;
    }
    await new Promise((resolve) => setTimeout(resolve, 180));
  }
  throw new Error('未收到最终回执，请读取当前任务状态；请求不会自动重发');
}
export async function enqueueCommand(state: FleetState, op: string, fields: Record<string, unknown>) {
  const id = `web-${crypto.randomUUID()}`;
  await request('/command', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-OmniFleet-Token': state.token },
    body: JSON.stringify({ op, id, identity_revision: state.identity_revision, ...fields }) });
  return id;
}
export const sample = (state: FleetState | null, robot: string, key: string) => state?.robots[robot]?.samples?.[key]?.value;
export function compose(a: Pose, b: Pose): Pose {
  return [a[0] + Math.cos(a[2]) * b[0] - Math.sin(a[2]) * b[1], a[1] + Math.sin(a[2]) * b[0] + Math.cos(a[2]) * b[1], a[2] + b[2]];
}
export function inverse(a: Pose): Pose { return [-Math.cos(a[2]) * a[0] - Math.sin(a[2]) * a[1], Math.sin(a[2]) * a[0] - Math.cos(a[2]) * a[1], -a[2]]; }
export function localPoints(text: string) {
  return text.split('\n').filter((line) => line.trim()).map((line, index) => {
    const values = line.split(/[,，\s]+/).filter(Boolean).map(Number);
    if (values.length !== 3 || !values.every(Number.isFinite)) throw new Error(`第 ${index + 1} 行需填写 x, y, 朝向角度`);
    return { name: `航点${index + 1}`, pose: [values[0], values[1], values[2] * Math.PI / 180] };
  });
}
export function parameterBatches(changes: Record<string, unknown>) {
  const remaining = { ...changes }, batches: Record<string, unknown>[] = [];
  for (const names of [['mola_map_points', 'mola_icp_points'], ['map_z_min', 'map_z_max'], ['pwm_compensation_m1', 'pwm_compensation_m2'], ['global_planner_algorithm'], ['local_controller_algorithm'], ...Object.keys(changes).filter((key) => key.startsWith('__')).map((key) => [key])]) {
    const batch: Record<string, unknown> = {};
    for (const name of names) if (name in remaining) { batch[name] = remaining[name]; delete remaining[name]; }
    if (Object.keys(batch).length) batches.push(batch);
  }
  if (Object.keys(remaining).length) batches.push(remaining);
  return batches;
}
