import { LiftRequest as RmfLiftRequest, LiftState as RmfLiftState } from 'rmf-models';

export function liftModeToString(liftMode?: number): string {
  if (liftMode === undefined) {
    return `未知（${liftMode})`;
  }
  switch (liftMode) {
    case RmfLiftState.MODE_AGV:
      return '机器人模式';
    case RmfLiftState.MODE_EMERGENCY:
      return '紧急状态';
    case RmfLiftState.MODE_FIRE:
      return '火警';
    case RmfLiftState.MODE_HUMAN:
      return '人工模式';
    case RmfLiftState.MODE_OFFLINE:
      return '离线';
    default:
      return `未知（${liftMode})`;
  }
}

export function doorStateToString(doorState?: number): string {
  if (doorState === undefined) return '未知';

  switch (doorState) {
    case RmfLiftState.DOOR_OPEN:
      return '已打开';
    case RmfLiftState.DOOR_CLOSED:
      return '已关闭';
    case RmfLiftState.DOOR_MOVING:
      return '移动中';
    default:
      return `未知（${doorState})`;
  }
}

export function motionStateToString(motionState?: number): string {
  if (motionState === undefined) return 'Unknown';

  switch (motionState) {
    case RmfLiftState.MOTION_DOWN:
      return 'Down';
    case RmfLiftState.MOTION_STOPPED:
      return 'Stopped';
    case RmfLiftState.MOTION_UP:
      return 'Up';
    default:
      return `Unknown (${motionState})`;
  }
}

export const requestModes = [
  RmfLiftRequest.REQUEST_AGV_MODE,
  RmfLiftRequest.REQUEST_HUMAN_MODE,
  RmfLiftRequest.REQUEST_END_SESSION,
];

export const requestModeStrings: Record<number, string> = {
  [RmfLiftRequest.REQUEST_END_SESSION]: '结束会话',
  [RmfLiftRequest.REQUEST_AGV_MODE]: '机器人模式',
  [RmfLiftRequest.REQUEST_HUMAN_MODE]: '人工模式',
};

export function requestModeToString(requestMode: number): string {
  return requestModeStrings[requestMode] || `未知（${requestMode})`;
}

export const requestDoorModes = [RmfLiftRequest.DOOR_OPEN, RmfLiftRequest.DOOR_CLOSED];

export const requestDoorModeStrings: Record<number, string> = {
  [RmfLiftRequest.DOOR_OPEN]: '打开',
  [RmfLiftRequest.DOOR_CLOSED]: '已关闭',
};

export function requestDoorModeToString(requestDoorMode: number): string {
  return requestDoorModeStrings[requestDoorMode] || '未知';
}
