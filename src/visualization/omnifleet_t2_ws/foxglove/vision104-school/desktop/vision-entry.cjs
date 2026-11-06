// Native shortcut entry: explicitly load the packaged visual demo layout.
const fs = require('node:fs');
const path = require('node:path');
const PANEL = 'local.omnifleet-vision.demo!functional-control';
const NAV = 'local.omnifleet-113-panels.nav2-hot-params-panel!vision104Navigation';
const TABS = 'Tab!vision104Controls';

function buildLayout(base, cases, previous) {
  const data = JSON.parse(JSON.stringify(base));
  const saved = previous?.data?.configById?.[PANEL];
  const entry = cases.find(item => item.id === saved?.selectedCase)
    || cases.find(item => item.id === base.configById[PANEL]?.selectedCase) || cases[0];
  const control = data.configById[PANEL];
  control.selectedCase = entry.id;
  control.selectedView = entry.ui.defaultView;
  control.dataTopic = entry.ui.dataTopic;
  if (saved?.parametersByCase) control.parametersByCase = saved.parametersByCase;
  control.views.result.config.imageMode.imageTopic = entry.displayTopic || entry.imageTopic;
  control.views.result.config.foxglovePanelTitle = entry.title + ' · 功能结果';
  control.views.data.config.topicPath = entry.ui.dataTopic;
  control.views.data.config.foxglovePanelTitle = entry.title + ' · 功能数据';
  const markerKind=entry.id==='02_05_qr'?'qr':entry.id==='02_06_apriltag'?'apriltag':undefined;
  const colorFollow=['02_04_color','04_01_color_follow'].includes(entry.id);
  const view = (entry.id==='02_07_kcf'||markerKind||colorFollow) && control.selectedView==='result'
    ? {id:'local.omnifleet-vision.kcf!interactive-follow',config:{markerKind,followKind:colorFollow?'color':undefined,caseId:colorFollow?entry.id:undefined,foxglovePanelTitle:colorFollow?'颜色点击跟随':markerKind?'二维码 / AprilTag 跟随':'目标物跟随窗口 · NanoTrack/KCF'}}
    : control.views[control.selectedView];
  view.id = view.id.split('!')[0] + '!case104_' + entry.id + '_' + control.selectedView;
  if (view.id.startsWith('Image!')) view.id += '_jpeg';
  if (control.selectedView === 'data') view.id += '_' + entry.ui.dataTopics.findIndex(([topic]) => topic === control.dataTopic);
  data.configById = { [PANEL]: control, [view.id]: view.config };
  data.layout.second = view.id;
  if(entry.id === '04_08_gesture_person_follow' && control.views.followMap){
    const map=control.views.followMap;
    if(saved?.views?.followMap)map.config=saved.views.followMap.config;
    data.configById[map.id]=map.config;
    data.layout.second={direction:'column',first:view.id,second:map.id,splitPercentage:55};
  }
  data.configById[NAV]=previous?.data?.configById?.[NAV]||control.navigationConfig;
  data.configById[TABS]={activeTabIdx:0,tabs:[
    {title:'视觉案例',layout:PANEL},{title:'104导航永久参数',layout:NAV},
  ]};
  data.layout.first=TABS;
  return data;
}

async function openVisionLayout(app, window) {
  async function request(route, body) {
    const credentials = JSON.parse(fs.readFileSync(path.join(app.getPath('userData'), 'demo-control.json'), 'utf8'));
    const response = await fetch('http://127.0.0.1:7335' + route, {
      method: body ? 'POST' : 'GET',
      headers: { Authorization: 'Bearer ' + credentials.token, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(1500),
    });
    if (!response.ok) throw new Error('Visual layout API: HTTP ' + response.status);
    return response.json();
  }
  let status;
  for (let attempt = 0; attempt < 60; attempt++) {
    if (window.isDestroyed()) return;
    try {
      const current = await request('/status');
      if (current.installedExtensionPanels?.includes('local.omnifleet-vision.demo')) { status = current; break; }
    } catch { }
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  if (!status) throw new Error('视觉功能面板未能完成加载，请重新打开104视觉案例。');
  const base = JSON.parse(fs.readFileSync(path.join(__dirname, 'vision-layout.json'), 'utf8'));
  const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'vision-cases.json'), 'utf8'));
  const data = buildLayout(base, cases, await request('/layout'));
  if ((status.source || '').trim().replace(/\/$/, '') !== 'ws://192.168.3.104:8765') {
    await request('/connect', { url: 'ws://192.168.3.104:8765' });
  }
  await request('/layout', { name: '104 视觉功能演示', data });
  if (window.isMinimized()) window.restore();
  window.show();
  window.focus();
}

module.exports = { openVisionLayout, buildLayout };
