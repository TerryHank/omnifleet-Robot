import { WorkspaceState } from '../workspace';

export const robotsWorkspace: WorkspaceState = {
  layout: [
    { i: 'live-status', x: 0, y: 0, w: 12, h: 12 },
    { i: 'robots', x: 0, y: 12, w: 7, h: 5 },
    { i: 'map', x: 8, y: 12, w: 5, h: 12 },
    { i: 'doors', x: 0, y: 12, w: 7, h: 4 },
    { i: 'lifts', x: 0, y: 12, w: 7, h: 3 },
  ],
  windows: [
    { key: 'live-status', appName: 'Live Status' },
    { key: 'robots', appName: 'Robots' },
    { key: 'map', appName: 'Map' },
    { key: 'doors', appName: 'Doors' },
    { key: 'lifts', appName: 'Lifts' },
  ],
};
