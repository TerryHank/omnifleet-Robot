import React from 'react';
import { Alert, Box, Chip, Divider, Grid, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';
import appConfig from '../app-config';
import { createMicroApp } from './micro-app';

interface Sample<T> { value: T; age_seconds: number; fresh: boolean; message_count: number; }
interface Navigation { phase?: string; task_id?: string; source?: string; navigation_active?: boolean; local_ready?: boolean; readiness_reason?: string; tf_age_ms?: number; localization_status?: string; message?: string; }
interface Control { control_mode?: string; manual_active?: boolean; local_override?: boolean; fleet_enabled?: boolean; estop?: boolean; control_gate_ready?: boolean; }
interface Pose { x: number; y: number; yaw: number; frame_id: string; stamp_seconds: number; }
interface Robot {
  robot_id: string; name: string; namespace: string; domain_id: number;
  online: boolean; transport_connected: boolean; dispatch_enabled: boolean; rmf_registered: boolean | null; battery_soc: number | null; state_source: string;
  samples: { pose: Sample<Pose> | null; navigation: Sample<Navigation> | null; control: Sample<Control> | null; voltage: Sample<number> | null; };
}
interface Dispatch { task_id: string; status: number; assignment: { is_assigned: boolean; fleet_name: string; expected_robot_name: string; }; errors: string[]; }
interface Snapshot {
  server_time_seconds: number;
  central: {
    domain_id: number | null; bridge_fresh: boolean; bridge_age_seconds: number | null; bridge_message_count: number; source_wall_time_seconds: number | null;
    schedule_connected: boolean; schedule_rpc_age_seconds: number | null;
    dispatcher_connected: boolean; dispatcher_rpc_age_seconds: number | null; dispatcher_response_count: number;
    dispatch_topic_age_seconds: number | null; dispatch_topic_message_count: number;
    dispatch: { active: Dispatch[]; finished: Dispatch[]; } | null;
    participants: { participants: unknown[]; } | null; queries: { query_ids: number[]; } | null;
  };
  robots: Robot[];
}

const yesNo = (value?: boolean) => value === undefined ? '未知' : value ? '是' : '否';
const age = (value: number | null | undefined) => value == null ? '未收到' : `${value.toFixed(2)} 秒`;
const number = (value: number | undefined, digits = 4) => value == null ? '未知' : value.toFixed(digits);
const phases: Record<string, string> = { completed: '已完成', idle: '空闲', executing: '执行中', navigating: '导航中', running: '运行中', stopped: '已停止', failed: '失败', canceled: '已取消', waiting: '等待中', paused: '已暂停' };
const modes: Record<string, string> = { LOCAL: '本地', FLEET: '车队', MANUAL: '手动', NONE: '无' };
const dispatchLabels = ['未初始化', '排队中', '已选择', '已分发', '分配失败', '分发中取消'];

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return <Grid item xs={12} sm={6} md={4}><Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="body2" sx={{ overflowWrap: 'anywhere' }}>{value}</Typography></Grid>;
}

function freshness<T>(sample: Sample<T> | null, elapsed: number) {
  const totalAge = sample ? sample.age_seconds + elapsed : null;
  return sample ? `${sample.fresh && totalAge! <= 3 ? '实时' : '已过期'} · ${age(totalAge)} · ${sample.message_count} 条` : '未收到';
}

export const LiveStatusApp = createMicroApp('104 与中央调度实时状态', () => {
  const [data, setData] = React.useState<Snapshot | null>(null);
  const [connected, setConnected] = React.useState(false);
  const [frames, setFrames] = React.useState(0);
  const [lastReceived, setLastReceived] = React.useState(0);
  const [now, setNow] = React.useState(Date.now());
  React.useEffect(() => {
    const stream = new EventSource(`${appConfig.rmfServerUrl}/omnifleet/status/stream`);
    stream.onopen = () => setConnected(true);
    stream.onmessage = (event) => {
      setData(JSON.parse(event.data));
      setFrames((count) => count + 1);
      setLastReceived(Date.now());
    };
    stream.onerror = () => setConnected(false);
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => { stream.close(); window.clearInterval(timer); };
  }, []);
  const webFresh = connected && now - lastReceived < 4000;
  const elapsed = Math.max(0, (now - lastReceived) / 1000);
  const central = data?.central;
  const dispatch = central?.dispatch;
  return (
    <Box component="div" sx={{ p: 2 }}>
      <Box component="div" sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1, mb: 1 }}>
        <Chip size="small" color={webFresh ? 'success' : 'warning'} label={webFresh ? 'Web 实时通道在线' : 'Web 数据中断／重连中'} />
        <Chip size="small" variant="outlined" label="只读监测" />
        <Typography variant="caption">接收 {frames} 帧 · 页面更新时间：{lastReceived ? new Date(lastReceived).toLocaleTimeString('zh-CN') : '等待数据'}</Typography>
      </Box>
      {!webFresh && data && <Alert severity="warning" sx={{ mb: 1 }}>Web 数据流已中断，下方为上次收到的状态，不能据此判断当前在线状态。</Alert>}
      <Paper variant="outlined" sx={{ p: 1.5, mb: 1.5 }}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>中央 RMF 调度</Typography>
        <Grid container spacing={1}>
          <Field label="中央 ROS 域" value={central?.domain_id ?? '未知'} />
          <Field label="中央状态桥" value={webFresh && central?.bridge_fresh ? '实时' : '未收到／已过期'} />
          <Field label="状态消息计数" value={central?.bridge_message_count ?? 0} />
          <Field label="调度核心活性" value={webFresh && central?.schedule_connected ? `查询正常 · ${age(central.schedule_rpc_age_seconds)}` : '未确认／已过期'} />
          <Field label="任务分发器 /get_dispatches" value={webFresh && central?.dispatcher_connected ? `查询正常 · ${age(central.dispatcher_rpc_age_seconds)}` : '未确认／已过期'} />
          <Field label="分发器响应计数" value={central?.dispatcher_response_count ?? 0} />
          <Field label="当前分发中 / 分发结束记录" value={dispatch ? `${dispatch.active.length} / ${dispatch.finished.length}` : '未收到'} />
          <Field label="交通参与者 / 调度查询数" value={`${central?.participants ? central.participants.participants.length : '未收到'} / ${central?.queries ? central.queries.query_ids.length : '未收到'}`} />
          <Field label="/dispatch_states 话题消息" value={central ? `${central.dispatch_topic_message_count} 条 · 最近 ${age(central.dispatch_topic_age_seconds)}` : '未收到'} />
        </Grid>
        <Typography variant="caption" color="text.secondary">分发器每 2 秒通过只读服务查询，以查询响应判断活性。分发结束不等于任务执行完成。</Typography>
        {dispatch && (dispatch.active.length + dispatch.finished.length > 0) && <Table size="small"><TableHead><TableRow><TableCell>任务编号</TableCell><TableCell>分发状态</TableCell><TableCell>目标车队 / 机器人</TableCell><TableCell>错误</TableCell></TableRow></TableHead><TableBody>{[...dispatch.active, ...dispatch.finished].map((task) => <TableRow key={task.task_id}><TableCell>{task.task_id}</TableCell><TableCell>{dispatchLabels[task.status] ?? `未知状态 ${task.status}`}</TableCell><TableCell>{task.assignment.is_assigned ? `${task.assignment.fleet_name} / ${task.assignment.expected_robot_name}` : '未分配'}</TableCell><TableCell>{task.errors.join('；') || '无'}</TableCell></TableRow>)}</TableBody></Table>}
      </Paper>
      {data?.robots.map((robot) => {
        const { pose, navigation, control, voltage } = robot.samples;
        const nav = navigation?.value;
        const ctrl = control?.value;
        return <Paper key={robot.robot_id} variant="outlined" sx={{ p: 1.5, mb: 1.5 }}>
          <Box component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="subtitle1">{robot.name}</Typography>
            <Chip size="small" color={webFresh && robot.online ? 'success' : 'warning'} label={webFresh && robot.online ? '状态在线' : '状态过期／未连接'} />
          </Box>
          <Grid container spacing={1}>
            <Field label="车辆 ROS 域 / 中央命名空间" value={`${robot.domain_id} / ${robot.namespace}`} />
            <Field label="车辆状态来源" value={robot.state_source === 'dedicated_read_only_observer' ? '104 专用只读采集器' : '中央状态桥'} />
            <Field label="导航阶段 / 当前任务" value={`${nav?.phase ? phases[nav.phase] ?? nav.phase : '未知'} / ${nav?.task_id || '无'}`} />
            <Field label="导航活动 / 后端就绪" value={`${yesNo(nav?.navigation_active)} / ${yesNo(nav?.local_ready)}`} />
            <Field label="控制模式 / 本地覆盖" value={`${ctrl?.control_mode ? modes[ctrl.control_mode] ?? ctrl.control_mode : '未知'} / ${yesNo(ctrl?.local_override)}`} />
            <Field label="急停 / 控制门就绪" value={`${yesNo(ctrl?.estop)} / ${yesNo(ctrl?.control_gate_ready)}`} />
            <Field label="导航 TF 年龄" value={nav?.tf_age_ms == null ? '未知' : `${number(nav.tf_age_ms, 0)} 毫秒`} />
            <Field label="位置 X / Y（米）" value={pose ? `${number(pose.value.x)} / ${number(pose.value.y)}` : '未知'} />
            <Field label="朝向（弧度） / 来源坐标系" value={pose ? `${number(pose.value.yaw)} / ${pose.value.frame_id}` : '未知'} />
            <Field label="电压 / 电量百分比" value={`${voltage ? number(voltage.value, 2) + ' V' : '未知'} / ${robot.battery_soc == null ? '未知' : (robot.battery_soc * 100).toFixed(1) + '%'}`} />
            <Field label="导航数据新鲜度" value={freshness(navigation, elapsed)} />
            <Field label="位姿数据新鲜度" value={freshness(pose, elapsed)} />
            <Field label="控制数据新鲜度" value={freshness(control, elapsed)} />
            <Field label="电压数据新鲜度" value={freshness(voltage, elapsed)} />
            <Field label="中央上报注册 / 本页任务下发" value={`${robot.rmf_registered == null ? '未知' : robot.rmf_registered ? '已注册' : '未注册'} / ${robot.dispatch_enabled ? '已启用' : '未启用'}`} />
          </Grid>
          <Divider sx={{ my: 1 }} />
          <Typography variant="body2">导航反馈：{nav?.message || nav?.readiness_reason || '暂无'}</Typography>
          <Typography variant="body2">定位反馈：{nav?.localization_status || '暂无'}</Typography>
          <Typography variant="caption" color="text.secondary">位姿来自车辆本地坐标系，尚未配准到中央 RMF 地图；电量百分比未知时不会根据电压推算。超过 3 秒的数据标记过期。</Typography>
        </Paper>;
      })}
      {!data?.robots.length && <Alert severity="info">等待中央状态桥传入车辆状态。</Alert>}
    </Box>
  );
});
