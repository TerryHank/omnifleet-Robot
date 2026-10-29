const labels: Record<string, string> = {
  agv: '机器人模式', task: '任务', warning: '警告',
  labels: '标签', doors: '自动门', lifts: '电梯', robots: '机器人',
  waypoints: '导航点', dispensers: '出料设备', ingestors: '入料设备', trajectories: '轨迹',
  'waypoint labels': '导航点标签', 'pickup point labels': '取货点标签', 'dropoff point labels': '送达点标签',
  up: '向上', down: '向下', open: '已打开', closed: '已关闭', moving: '移动中',
  uninitialized: '未初始化', idle: '空闲', working: '执行中', charging: '充电中',
  underway: '执行中', active: '执行中', queued: '排队中', pending: '待执行',
  completed: '已完成', canceled: '已取消', cancelled: '已取消', failed: '失败',
  killed: '已终止', paused: '已暂停', delayed: '延迟', blocked: '受阻',
  standby: '待命', stopped: '已停止', waiting: '等待中', error: '错误',
  skipped: '已跳过', rejected: '已拒绝', forfeited: '已放弃', unknown: '未知',
  shutdown: '已关机', online: '在线', offline: '离线', healthy: '正常',
  unhealthy: '异常', dead: '无响应', emergency: '紧急状态', fire: '火警',
  clean: '清扫', patrol: '巡逻', delivery: '配送', loop: '循环任务',
  charge: '充电', station: '驻留任务', move: '移动', go_to_place: '前往地点',
  responsive_wait: '等待', perform_action: '执行操作', pickup: '取货', dropoff: '送达',
};

export function displayText(value?: string | null): string {
  if (!value) return '未知';
  return labels[value.toLowerCase()] || value;
}
