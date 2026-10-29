import { Door as RmfDoor, DoorMode as RmfDoorMode } from 'rmf-models';

export enum DoorType {
  SingleSwing = RmfDoor.DOOR_TYPE_SINGLE_SWING,
  SingleSliding = RmfDoor.DOOR_TYPE_SINGLE_SLIDING,
  SingleTelescope = RmfDoor.DOOR_TYPE_SINGLE_TELESCOPE,
  DoubleSwing = RmfDoor.DOOR_TYPE_DOUBLE_SWING,
  DoubleSliding = RmfDoor.DOOR_TYPE_DOUBLE_SLIDING,
  DoubleTelescope = RmfDoor.DOOR_TYPE_DOUBLE_TELESCOPE,
}

export enum DoorMotion {
  Clockwise = 1,
  AntiClockwise = -1,
}

export enum DoorMode {
  Open = RmfDoorMode.MODE_OPEN,
  Closed = RmfDoorMode.MODE_CLOSED,
  Moving = RmfDoorMode.MODE_MOVING,
}

export interface DoorData {
  level: string;
  door: RmfDoor;
}

export function doorModeToString(doorMode?: number): string {
  if (doorMode === undefined) {
    return '暂无';
  }
  switch (doorMode) {
    case RmfDoorMode.MODE_OPEN:
      return '已打开';
    case RmfDoorMode.MODE_CLOSED:
      return '已关闭';
    case RmfDoorMode.MODE_MOVING:
      return '移动中';
    default:
      return '未知';
  }
}

export function doorTypeToString(doorType: number): string {
  switch (doorType) {
    case RmfDoor.DOOR_TYPE_DOUBLE_SLIDING:
      return '双扇滑动门';
    case RmfDoor.DOOR_TYPE_DOUBLE_SWING:
      return '双扇平开门';
    case RmfDoor.DOOR_TYPE_DOUBLE_TELESCOPE:
      return '双扇伸缩门';
    case RmfDoor.DOOR_TYPE_SINGLE_SLIDING:
      return '单扇滑动门';
    case RmfDoor.DOOR_TYPE_SINGLE_SWING:
      return '单扇平开门';
    case RmfDoor.DOOR_TYPE_SINGLE_TELESCOPE:
      return '单扇伸缩门';
    default:
      return `未知（${doorType})`;
  }
}
