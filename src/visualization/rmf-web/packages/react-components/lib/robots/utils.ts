import { ApiServerModelsRmfApiRobotStateStatus as RobotStatus } from 'api-client';
import { RobotMode as RmfRobotMode } from 'rmf-models';

/**
 * Returns a uniquely identifiable string representing a robot.
 */
export function robotHash(name: string, fleet: string): string {
  return `${name}__${fleet}`;
}

export function robotStatusToUpperCase(status: RobotStatus): string {
  switch (status) {
    case RobotStatus.Charging:
      return '充电中';
    case RobotStatus.Idle:
      return '空闲';
    case RobotStatus.Working:
      return '执行中';
    case RobotStatus.Offline:
      return '离线';
    case RobotStatus.Uninitialized:
      return '未初始化';
    case RobotStatus.Shutdown:
      return '已关机';
    case RobotStatus.Error:
      return '故障';
    default:
      return `未知（${status})`;
  }
}

export function robotModeToString(robotMode: RmfRobotMode): string {
  switch (robotMode.mode) {
    case RmfRobotMode.MODE_CHARGING:
      return '充电中';
    case RmfRobotMode.MODE_DOCKING:
      return '对接中';
    case RmfRobotMode.MODE_EMERGENCY:
      return '紧急状态';
    case RmfRobotMode.MODE_GOING_HOME:
      return '返回起点';
    case RmfRobotMode.MODE_IDLE:
      return '空闲';
    case RmfRobotMode.MODE_MOVING:
      return '移动中';
    case RmfRobotMode.MODE_PAUSED:
      return '已暂停';
    case RmfRobotMode.MODE_WAITING:
      return '等待中';
    default:
      return `未知（${robotMode.mode})`;
  }
}
