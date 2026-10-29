// import { Task } from 'api-client';
import { UserProfile } from 'rmf-auth';

export enum RmfAction {
  TaskRead = 'task_read',
  TaskSubmit = 'task_submit',
  TaskCancel = 'task_cancel',
}

export function getActionText(action: string): string {
  const labels: Record<string, string> = { task_read: '查看任务', task_submit: '下发任务', task_cancel: '取消任务' };
  if (labels[action]) return labels[action];
  return action.replace(/(?:^|_)([a-z])/g, (_, p1: string) => ` ${p1.toUpperCase()}`).slice(1);
}

export class Enforcer {
  static canCancelTask(profile: UserProfile): boolean {
    if (profile.user.is_admin) {
      return true;
    }
    // for (const p of profile.permissions) {
    //   if (p.authz_grp === task.authz_grp && p.action === RmfAction.TaskCancel) {
    //     return true;
    //   }
    // }
    return false;
  }
}
