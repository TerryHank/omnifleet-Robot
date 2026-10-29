import { DispenserState as RmfDispenserState } from 'rmf-models';

export function dispenserModeToString(mode: number): string {
  switch (mode) {
    case RmfDispenserState.IDLE:
      return '空闲';
    case RmfDispenserState.BUSY:
      return '在线';
    case RmfDispenserState.OFFLINE:
      return '离线';
    default:
      return '暂无';
  }
}
