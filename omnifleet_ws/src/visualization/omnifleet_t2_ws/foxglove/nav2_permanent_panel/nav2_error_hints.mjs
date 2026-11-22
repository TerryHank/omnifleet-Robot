export function classifyNav2Error(log, saved = {}, selected = {}) {
  const name = String(log.name || ''), msg = String(log.msg || '');
  if (!/(planner_server|controller_server|costmap|bt_navigator|behavior_server)/.test(name)) return undefined;
  if (Number(log.level) < 30 && !/Message Filter dropping|Timed out waiting for transform/.test(msg)) return undefined;
  const local = name.includes('local_costmap');
  const prefix = local ? '局部路径规划 → 局部代价地图' : '全局路径规划 → 全局代价地图';
  const tolerance = selected.global === 'navfn' ? 'navfn_tolerance' : selected.global === 'theta_star' ? null : 'planner_tolerance';
  const hint = (key, title, action, field = null, priority = 2) => ({key, title, action, field, priority});
  if (/inflation radius.*smaller than.*inscribed radius/i.test(msg)) {
    const match = msg.match(/inscribed radius\s*\(([\d.]+)\)/i);
    return hint('inflation', '膨胀半径小于机器人外形要求', `${prefix}膨胀半径：${match ? '不应小于 ' + match[1] : '至少覆盖 footprint 的内切半径'}。同时核对 footprint 安全边界；不要设置为 0。`, local ? 'local_radius' : 'global_radius', 3);
  }
  const radius = saved.local_radius && Object.values(saved.local_radius)[0];
  if (/Aborting handle|Failed to make progress/.test(msg) && name === 'controller_server' && radius === 0) {
    return hint('zero-inflation', '保存的局部膨胀半径为 0', '位置：局部路径规划 → 局部代价地图膨胀半径。设为正值并覆盖机器人外形；本机曾因此在清图后一直等待地图就绪。', 'local_radius', 3);
  }
  if (/Starting point in lethal space|start.*(?:occupied|lethal)/i.test(msg)) {
    return hint('start-blocked', '规划起点被地图判为障碍', '先核对机器人定位、起点附近障碍及 footprint 安全边界；若地面被误判为障碍，检查 MOLA 建图高度上下限。单改路径权重不能解决起点占用。', 'costmap_padding');
  }
  if (/goal.*(?:occupied|lethal)|goal.*outside.*map/i.test(msg)) {
    return hint('goal-blocked', '目标点在障碍区或地图外', '先把目标点移到已观测的空闲区域；若只需到达目标附近，再检查当前全局算法的“规划目标容差”。', tolerance);
  }
  if (/maximum iterations|exceeded.*iterations|max_iterations/i.test(msg)) {
    return hint('iterations', '规划搜索达到迭代上限', '检查目标是否可达；必要时在全局路径规划中适当增大“最大搜索迭代次数”，并检查“最大规划时间”。', 'planner_max_iterations');
  }
  if (name.includes('planner') && /planning.*(?:timed out|timeout)|(?:exceeded|maximum).*planning time/i.test(msg)) {
    return hint('planning-time', '全局规划超过时间预算', '检查目标是否可达和处理器负载；必要时适当增大当前算法的“最大规划时间”。', selected.global === 'smac_2d' ? 'planner_max_planning_time' : null);
  }
  if (/No valid path|no path.*found|failed to generate a valid path/i.test(msg)) {
    return hint('no-path', '未找到可通行的全局路径', '先检查目标、未知区域和通道是否连通；再检查全局膨胀半径与 footprint 是否符合实车尺寸。只有确认未知区域可以通行时，才考虑“允许穿越未知区域”。', 'global_radius', 1);
  }
  if (/No (?:valid|legal) trajector|Could not find a valid trajector|No valid control|Collision detected ahead/i.test(msg)) {
    return hint('no-control', '局部控制没有找到可行轨迹', '先检查局部障碍、膨胀半径及 footprint；若空间足够，再检查当前控制器的速度限制。DWB 还可检查轨迹仿真时间与采样数。', 'local_radius');
  }
  if (/Failed to make progress/i.test(msg)) {
    return hint('progress', '机器人位置长时间没有改善', '先核对实际位姿变化、底盘是否执行指令及前方是否受阻。仅凭此错误不能判断应改哪个参数；可提交给大模型结合运行数据诊断。');
  }
  if (/transform.*(?:unavailable|available)|Invalid frame ID|earlier than all.*transform cache|extrapolation/i.test(msg)) {
    return hint('tf', '坐标变换或时间戳异常', '检查定位是否正常、map → base_link → 雷达的 TF，以及点云与 TF 的时间。该问题应修复 TF/时间链路，不宜靠调整规划权重处理。', null, 3);
  }
  if (/Aborting handle/.test(msg)) return hint('abort', '导航子任务中止，原因尚未明确', '查看下方原始错误和随后更具体的提示；目前证据不足，不能确定应修改哪个参数。', null, 0);
  if (Number(log.level) >= 40 || /Goal failed/.test(msg)) return hint('other', '导航报告错误', '查看下方原始错误；当前没有足够依据推荐某个参数。', null, 0);
  return undefined;
}
