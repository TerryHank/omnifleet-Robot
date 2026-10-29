import { LiveStatusApp } from './live-status-app';
import { BeaconsApp } from './beacons-app';
import { DoorsApp } from './doors-app';
import { LiftsApp } from './lifts-app';
import { MapApp } from './map-app';
import { RobotInfoApp } from './robots/robot-info-app';
import { RobotsApp } from './robots/robots-app';
import { TaskDetailsApp } from './tasks/task-details-app';
import { TaskLogsApp } from './tasks/task-logs-app';
import { TasksApp } from './tasks/tasks-app';

export const AppRegistry = {
  'Live Status': LiveStatusApp,
  Beacons: BeaconsApp,
  Doors: DoorsApp,
  Lifts: LiftsApp,
  Map: MapApp,
  Tasks: TasksApp,
  'Task Details': TaskDetailsApp,
  'Task Logs': TaskLogsApp,
  Robots: RobotsApp,
  'Robot Info': RobotInfoApp,
};

export const AppLabels: Record<keyof typeof AppRegistry, string> = {
  'Live Status': '104 与中央调度实时状态',
  Beacons: '信号灯',
  Doors: '自动门',
  Lifts: '电梯',
  Map: '地图',
  Tasks: '任务',
  'Task Details': '任务详情',
  'Task Logs': '任务日志',
  Robots: '机器人',
  'Robot Info': '机器人信息',
};
