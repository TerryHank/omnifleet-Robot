// Keep the fleet panel as the only layout panel; mount the existing native
// semantic controls inside it so every navigation callback stays unchanged.
function FleetSemanticNative(props) {
  const [slot, setSlot] = (0,p.useState)(null);
  const init = (0,p.useCallback)(context => {
    const cleanup = initFleetBuiltin(context);
    const root = context.panelElement.querySelector('[data-testid="fleet-panel"]');
    const route = root.querySelector('[data-ui="route"]').closest('.fleet-card');
    route.querySelector('strong').textContent = '4 · 所选车辆的协同路线';
    const hint = route.querySelector('.fleet-muted');
    hint.textContent = '在“协同航点编辑”地图中使用“发布点”或“发布位姿”添加航点；也可逐行输入 x, y, 朝向角度（°）。';
    const section = document.createElement('details');
    section.className = 'fleet-card fleet-semantic-section';
    section.dataset.testid = 'fleet-semantic-section';
    section.open = true;
    const summary = document.createElement('summary');
    summary.textContent = '3 · 本车语义多点导航（113）';
    summary.style.cssText = 'cursor:pointer;font-weight:700;';
    const note = document.createElement('div');
    note.className = 'fleet-muted';
    note.textContent = '在“本车导航（单点／多点）”地图中添加语义航点。本节控制 113 本车，路线与下方协同任务分别保存。';
    const body = document.createElement('div');
    body.dataset.testid = 'fleet-semantic-slot';
    section.append(summary, note, body);
    route.before(section);
    const style = document.createElement('style');
    style.textContent = `
      .fleet-semantic-section{display:block}
      .fleet-semantic-section>summary{margin-bottom:8px}
      [data-testid="fleet-semantic-slot"] [data-testid="semantic-waypoint-control"]{height:auto;background:transparent;font:inherit}
      [data-testid="fleet-semantic-slot"] [data-testid="semantic-waypoint-control"]>div:first-child,
      [data-testid="fleet-semantic-slot"] [data-testid="semantic-waypoint-control"]>hr{display:none}
      [data-testid="fleet-semantic-slot"] [data-testid="semantic-waypoint-control"]>div:last-child{overflow:visible;padding:8px 0 0}
      [data-testid="fleet-semantic-slot"] .MuiTypography-root,
      [data-testid="fleet-semantic-slot"] .MuiInputBase-root,
      [data-testid="fleet-semantic-slot"] .MuiChip-label{font-size:inherit}
    `;
    root.append(style);
    setSlot(body);
    return () => { cleanup(); };
  }, []);
  return (0,n.jsxs)(p.Fragment, {children:[
    (0,n.jsx)(xg.e, {...props, initPanel:init}),
    slot ? o(80820).createPortal((0,n.jsx)(ru,{open:!0,onClose:()=>{}}),slot) : null
  ]});
}
