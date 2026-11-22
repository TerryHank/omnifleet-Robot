/* Foxglove guided tour. UI only: no ROS transport or parameter writes. */
(() => {
  'use strict';
  if (document.getElementById('fg-tour-style')) return;
  const $ = (s) => document.querySelector(s);
  const three = () => $('[data-testid^="panel-mouseenter-container 3D!"]');
  const panel = (name) => Array.from(document.querySelectorAll('[data-testid^="panel-mouseenter-container "]')).find(e => e.getAttribute('data-testid').includes(name));
  const settings = () => three()?.querySelector('button[title="设置"], button[title="Settings"]');
  const sidebar = () => $('[data-tourid="left-sidebar-button"]');
  const docs = 'https://docs.foxglove.dev/docs/visualization/';
  const steps = [
    { title: '认识 Foxglove', target: () => $('#fg-tour-help'), body: 'Foxglove 把机器人数据整理成地图、点云、图像和图表。接下来带你认识常用入口，再了解本机的导航面板。', tip: '教程只介绍界面，不会发布目标、改变参数或控制机器人。随时按 Esc 退出。', link: 'panels' },
    { title: '先确认数据源', target: () => $('[data-tourid="app-bar"] [data-testid="text-middle-truncate"]'), fallback: () => $('[data-tourid="app-bar"]'), body: `顶部显示当前连接地址和数据时间。本机的实时连接为 ws://${location.hostname}:8765。操作前先确认连接的是目标机器人。`, tip: '网页从本机地址打开；WebSocket 的 8765 是数据端口。没有数据时先检查网络和连接状态。' },
    { title: '打开连接或数据文件', target: () => $('#app-menu-button'), body: '左上角 Foxglove 菜单提供“文件”“查看”等入口。在“文件”中打开连接，或打开支持的录制文件进行离线查看。', tip: '实时连接显示机器人当前数据；录制文件用于回放历史数据。回放进度不代表机器人正在运动。', link: 'playback' },
    { title: '添加可视化面板', target: () => $('#add-panel-button'), body: '点击“添加面板”，选择三维、图像、图表、原始消息等类型。每个面板负责一种观察方式，也可以把面板拖到合适位置。', tip: '例如：三维看地图与点云，图像看相机画面，图表看数值随时间的变化。', link: 'panels' },
    { title: '调整面板布局', target: () => three()?.querySelector('[data-testid="mosaic-drag-handle"]'), fallback: () => $('[data-testid="mosaic-drag-handle"]'), body: '拖动面板标题栏重新排列面板，拖动面板之间的分隔线调整大小。面板右上角的“更多”菜单提供该面板的操作。', tip: '布局决定你如何查看数据，布局调整与机器人导航参数是不同的设置。', link: 'layouts' },
    { title: '打开面板设置', target: settings, fallback: sidebar, body: '每个面板右上角的齿轮打开其设置。三维面板中可以选择展示参考系、设置视角，并显示或隐藏话题图层。', tip: '查看全局地图时使用 map 参考系。图层不显示时，检查话题、坐标变换和图层开关。', link: 'panels/3d#topics' },
    { title: '读懂地图、点云和路径', target: three, body: '中央三维视图叠加显示地图、机器人模型、传感器点云及规划路径。用设置中的话题图层分别开关显示，避免把地图与实时点云混淆。', tip: '点云可以调整点大小和着色方式；路径用于观察规划结果。显示配置本身不会让机器人行驶。', link: 'panels/3d' },
    { title: '操作三维视角', target: three, body: '在三维视图的空白处拖动可平移，滚轮缩放，Shift＋拖动或右键拖动可旋转视角。面板内的 2D／3D 按钮切换查看方式。', tip: '退出教程后再练习。先确认处于查看模式；发布目标模式下，在地图上的操作可能发送目标。', link: 'shortcuts' },
    { title: '查看话题和消息', target: () => $('[data-testid="topics-left"]') || sidebar(), body: '展开左侧边栏，选择“话题”查看数据通道。想查看具体字段时，添加“原始消息”面板并选择对应话题。', tip: '观察消息是否持续更新，再判断是显示设置问题还是数据源没有输出。', link: 'panels/raw-messages' },
    { title: '查看相机与数值变化', target: () => $('#add-panel-button'), body: '添加“图像”面板后选择相机话题；添加“图表”面板后选择需要观察的数值字段。仪表面板适合显示电压、角速度等当前值。', tip: '本机已配置电压和角速度面板。话题与字段选择在各面板设置中完成。', link: 'panels' },
    { title: '认识本机航点功能', target: () => Array.from(document.querySelectorAll('.omnifleet-nav2-hot-params details')).find(e => e.querySelector('summary')?.textContent.includes('多点路线导航')), fallback: () => panel('nav2-hot-params'), body: '本机的航点面板用于管理路线。“开始整条路线”执行任务，“停止导航”取消任务；添加或编辑航点与启动导航是两个操作。', tip: '三维发布工具和航点按钮会影响真实任务。教程仅高亮说明，不会点击它们。', scroll: true },
    { title: '区分显示设置与导航参数', target: () => $('[data-testid="nav2-parameter-search"]'), fallback: () => panel('nav2-hot-params'), body: '左侧 Nav2 面板调整机器人导航行为，可用中文、英文或功能词搜索参数。它与 Foxglove 的颜色、视角等显示设置不同。', tip: '本机部分参数在离开输入框或勾选后自动保存。需要修改时，退出教程再有针对性地操作。', scroll: true },
    { title: '手动控制面板', target: () => panel('.drive-joystick!'), fallback: () => panel('Teleop!'), body: '手动控制面板用于控制底盘前后移动和转向。在摇杆布局中，拖动摇杆控制方向，松手停车，也可以点击「急停」。', tip: '教程只高亮面板。退出教程后再按实际需要操作。' },
    { title: '完成，开始使用 Foxglove', target: () => $('#fg-tour-help'), body: '先确认数据源，再选面板与话题，最后调整三维显示。遇到显示问题，优先检查连接、话题和参考系。', tip: '点击“完成”恢复操作。之后仍可点击右上角“？”重新查看本教程。', link: 'panels' },
  ];

  const style = document.createElement('style');
  style.id = 'fg-tour-style';
  style.textContent = `
    #fg-tour-help { display:inline-flex; align-items:center; justify-content:center; flex:0 0 40px; width:40px; height:40px; padding:0; border:0; border-radius:6px; background:transparent; color:inherit; cursor:pointer; }
    #fg-tour-help:hover { background:rgba(141,118,255,.22); }
    #fg-tour-help:focus-visible { outline:2px solid #b19aff; outline-offset:-3px; }
    #fg-tour-help svg { width:23px; height:23px; }
    #fg-vision-follow { display:inline-flex; align-items:center; gap:6px; height:32px; padding:0 8px; border-radius:6px; color:inherit; text-decoration:none; white-space:nowrap; font-size:13px; }
    #fg-vision-follow:hover { background:rgba(141,118,255,.22); }
    #fg-vision-follow:focus-visible { outline:2px solid #b19aff; outline-offset:-3px; }
    #fg-vision-follow svg { width:18px; height:18px; }
    #fg-tour { position:fixed; inset:0; z-index:2147483000; font:14px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; color:#eef2ff; }
    #fg-tour *, #fg-tour *::before { box-sizing:border-box; }
    #fg-tour-mask { position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }
    #fg-tour-blocker { position:absolute; inset:0; touch-action:none; }
    #fg-tour-ring { position:fixed; border:2px solid #b9a7ff; border-radius:8px; pointer-events:none; box-shadow:0 0 0 3px rgba(176,150,255,.18); }
    #fg-tour-card { position:fixed; width:380px; max-width:calc(100vw - 24px); max-height:calc(100dvh - 24px); overflow:auto; padding:22px; background:#23232e; border:1px solid #535064; border-radius:14px; box-shadow:0 20px 70px #0007; color:#eef2ff; }
    #fg-tour-card h2 { margin:9px 28px 12px 0; font-size:20px; line-height:1.4; color:#fff; }
    #fg-tour-card p { margin:0 0 12px; }
    #fg-tour-card .fg-tour-progress { font-size:12px; color:#bdacff; letter-spacing:.4px; }
    #fg-tour-card .fg-tour-tip { font-size:13px; color:#c4c7d5; padding:11px 12px; background:#ffffff08; border-radius:7px; }
    #fg-tour-card .fg-tour-missing { font-size:12px; color:#f3d59b; }
    #fg-tour-card .fg-tour-footer { display:flex; align-items:center; gap:8px; margin-top:18px; }
    #fg-tour-card button { font:inherit; cursor:pointer; border-radius:7px; padding:7px 13px; color:#e5e7f2; border:1px solid #5c5a6d; background:transparent; }
    #fg-tour-card button:focus-visible, #fg-tour-card a:focus-visible { outline:2px solid #c5b6ff; outline-offset:3px; }
    #fg-tour-card button:disabled { opacity:.35; cursor:default; }
    #fg-tour-card .fg-tour-next { background:#8964ed; border-color:#8964ed; color:white; min-width:86px; }
    #fg-tour-card .fg-tour-next:hover { background:#9a7af1; }
    #fg-tour-card .fg-tour-exit { margin-right:auto; padding-left:0; padding-right:4px; border-color:transparent; color:#bcc0d0; }
    #fg-tour-card .fg-tour-close { position:absolute; top:12px; right:12px; font-size:23px; line-height:24px; border:0; padding:2px 7px; }
    #fg-tour-card a { color:#c5b5ff; font-size:12px; text-decoration:none; }
    #fg-tour-card a:hover { text-decoration:underline; }
    #fg-tour-card [hidden] { display:none !important; }
    @media(max-width:600px) { #fg-tour-card { padding:17px; font-size:13px; } #fg-tour-card h2 { font-size:18px; } #fg-tour-card .fg-tour-footer { gap:5px; } #fg-tour-card button { padding:7px 10px; } }
  `;
  document.head.append(style);
  const help = document.createElement('button');
  help.id = 'fg-tour-help'; help.type = 'button';
  help.title = 'Foxglove 使用教程'; help.setAttribute('aria-label', '打开 Foxglove 使用教程');
  help.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.7"/><path d="M9.5 8.7a2.6 2.6 0 0 1 5 .7c0 1.8-2.5 2-2.5 3.8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="16.5" r="1" fill="currentColor"/></svg>';
  const vision = document.createElement('a');
  vision.id = 'fg-vision-follow';
  vision.href = '/vision-follow.html';
  vision.target = '_blank';
  vision.rel = 'noopener';
  vision.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/><circle cx="12" cy="12" r="3.5"/></svg>视觉跟随';
  let index = 0, overlay, card, target, raf = 0, timer, previousFocus;
  const scrollStates = new Map();
  function mount() {
    const group = $('[data-tourid="sidebar-button-group"]');
    if (!group) return;
    if (help.nextElementSibling !== group) group.before(help);
    if (vision.nextElementSibling !== help) help.before(vision);
  }
  // React may rebuild its toolbar; attach to the semantic anchor, never overwrite its markup.
  new MutationObserver(mount).observe(document.documentElement, { childList:true, subtree:true });
  mount();

  function rectOf(el) {
    if (!el?.isConnected) return null;
    let r = el.getBoundingClientRect();
    if (!r.width || !r.height) return null;
    let left=r.left,top=r.top,right=r.right,bottom=r.bottom;
    for (let p=el.parentElement;p;p=p.parentElement) {
      const s=getComputedStyle(p), b=p.getBoundingClientRect();
      if (/(auto|scroll|hidden|clip)/.test(s.overflowX)) { left=Math.max(left,b.left);right=Math.min(right,b.right); }
      if (/(auto|scroll|hidden|clip)/.test(s.overflowY)) { top=Math.max(top,b.top);bottom=Math.min(bottom,b.bottom); }
    }
    left=Math.max(4,left-5);top=Math.max(4,top-5);right=Math.min(innerWidth-4,right+5);bottom=Math.min(innerHeight-4,bottom+5);
    return right>left && bottom>top ? {left,top,right,bottom,width:right-left,height:bottom-top} : null;
  }
  function scrollToTarget(el) {
    // Only scroll the parameter panel, not the page, and restore it when closing.
    const scroller=el?.closest('.omnifleet-nav2-hot-params');
    if (!scroller) return;
    if (!scrollStates.has(scroller)) scrollStates.set(scroller, scroller.scrollTop);
    const b=scroller.getBoundingClientRect(),r=el.getBoundingClientRect();
    if (r.top<b.top+10 || r.bottom>b.bottom-10) scroller.scrollTop += r.top-b.top-18;
  }
  function position() {
    raf=0;if(!overlay) return;
    const step=steps[index];
    target=step.target();
    let r=rectOf(target);
    if (!r && step.fallback) r=rectOf(step.fallback());
    const ring=overlay.querySelector('#fg-tour-ring');
    ring.hidden=!r;
    const path=overlay.querySelector('path');
    let mask=`M0 0H${innerWidth}V${innerHeight}H0Z`;
    if (r) {
      mask+=`M${r.left} ${r.top}V${r.bottom}H${r.right}V${r.top}Z`;
      Object.assign(ring.style,{left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px'});
    }
    path.setAttribute('d',mask);
    overlay.querySelector('.fg-tour-missing').hidden=!!r;
    const w=card.offsetWidth,h=card.offsetHeight,gap=16,edge=12;
    const clamp=(x,a,b)=>Math.max(a,Math.min(x,Math.max(a,b)));
    let x=(innerWidth-w)/2,y=(innerHeight-h)/2;
    if(r) {
      const choices=[
        [r.right+gap,clamp(r.top,edge,innerHeight-h-edge)],
        [r.left-w-gap,clamp(r.top,edge,innerHeight-h-edge)],
        [clamp(r.left,edge,innerWidth-w-edge),r.bottom+gap],
        [clamp(r.left,edge,innerWidth-w-edge),r.top-h-gap]
      ];
      const fit=choices.find(([a,b])=>a>=edge&&b>=edge&&a+w<=innerWidth-edge&&b+h<=innerHeight-edge);
      if(fit) [x,y]=fit;
      else { x=clamp(r.left+gap,edge,innerWidth-w-edge);y=clamp(r.bottom-h-gap,edge,innerHeight-h-edge); }
    }
    Object.assign(card.style,{left:clamp(x,edge,innerWidth-w-edge)+'px',top:clamp(y,edge,innerHeight-h-edge)+'px'});
  }
  function schedule() { if (overlay && !raf) raf=requestAnimationFrame(position); }
  function show(next) {
    index=next; const s=steps[index];
    if (index === 10 || index === 11) {
      document.querySelector('[data-panel-view="' + (index === 10 ? 'operations' : 'parameters') + '"]')?.click();
    }
    card.querySelector('.fg-tour-progress').textContent=`FOXGLOVE 使用教程 · ${index+1} / ${steps.length}`;
    card.querySelector('h2').textContent=s.title;
    card.querySelector('.fg-tour-body').textContent=s.body;
    card.querySelector('.fg-tour-tip').textContent=s.tip;
    const link=card.querySelector('a');link.hidden=!s.link;if(s.link)link.href=docs+s.link;
    card.querySelector('.fg-tour-prev').disabled=index===0;
    card.querySelector('.fg-tour-next').textContent=index===steps.length-1?'完成':'下一步';
    card.dataset.step=String(index+1);
    if(s.scroll)scrollToTarget(s.target());
    card.scrollTop=0;position();
  }
  function close() {
    if(!overlay)return;
    clearInterval(timer);cancelAnimationFrame(raf);raf=0;
    window.removeEventListener('keydown',keyboard,true);
    window.removeEventListener('keyup',stopKey,true);
    window.removeEventListener('resize',schedule);document.removeEventListener('scroll',schedule,true);
    overlay.remove();overlay=null;
    for(const [el,y] of scrollStates) if(el.isConnected)el.scrollTop=y;
    scrollStates.clear();
    help.setAttribute('aria-expanded','false');
    (previousFocus?.isConnected?previousFocus:help).focus({preventScroll:true});
  }
  function stopKey(e) { e.stopImmediatePropagation(); }
  function keyboard(e) {
    // Stop Foxglove/map/teleop shortcuts while the tutorial owns keyboard focus.
    e.stopImmediatePropagation();
    if(e.key==='Escape'){e.preventDefault();close();return;}
    if(e.key==='Tab') {
      const es=Array.from(card.querySelectorAll('button:not(:disabled),a[href]')).filter(el=>!el.hidden);
      const i=es.indexOf(document.activeElement),n=e.shiftKey?(i<=0?es.length-1:i-1):(i+1)%es.length;
      e.preventDefault();es[n].focus();
    } else if (!['Enter',' '].includes(e.key)) e.preventDefault();
  }
  function open() {
    if(overlay)return;
    previousFocus=document.activeElement;
    overlay=document.createElement('div');overlay.id='fg-tour';
    overlay.innerHTML='<svg id="fg-tour-mask" aria-hidden="true"><path fill="rgba(9,12,20,.74)" fill-rule="evenodd"/></svg><div id="fg-tour-blocker"></div><div id="fg-tour-ring"></div><section id="fg-tour-card" role="dialog" aria-modal="true" aria-labelledby="fg-tour-title" aria-describedby="fg-tour-body"><button type="button" class="fg-tour-close" aria-label="退出教程">×</button><div class="fg-tour-progress" aria-live="polite"></div><h2 id="fg-tour-title"></h2><p class="fg-tour-body" id="fg-tour-body"></p><p class="fg-tour-tip"></p><p class="fg-tour-missing" hidden>当前布局未显示此入口，可先阅读说明，退出教程后再添加相应面板。</p><a href="https://docs.foxglove.dev/docs/visualization/panels" target="_blank" rel="noopener noreferrer">Foxglove 官方说明 ↗</a><div class="fg-tour-footer"><button type="button" class="fg-tour-exit">退出教程</button><button type="button" class="fg-tour-prev">上一步</button><button type="button" class="fg-tour-next">下一步</button></div></section>';
    document.body.append(overlay);card=overlay.querySelector('#fg-tour-card');
    // No click is forwarded to a highlighted element; the mask also covers the hole.
    for(const event of ['pointerdown','pointerup','click','dblclick','contextmenu','wheel']) overlay.addEventListener(event,e=>{e.stopPropagation();if(!card.contains(e.target))e.preventDefault();},{passive:false});
    card.querySelector('.fg-tour-close').onclick=close;card.querySelector('.fg-tour-exit').onclick=close;
    card.querySelector('.fg-tour-prev').onclick=()=>{if(index>0)show(index-1);};
    card.querySelector('.fg-tour-next').onclick=()=>index===steps.length-1?close():show(index+1);
    window.addEventListener('keydown',keyboard,true);
    window.addEventListener('keyup',stopKey,true);
    window.addEventListener('resize',schedule);document.addEventListener('scroll',schedule,true);
    timer=setInterval(schedule,350);help.setAttribute('aria-expanded','true');
    show(0);card.querySelector('.fg-tour-next').focus({preventScroll:true});
  }
  help.setAttribute('aria-haspopup','dialog');help.setAttribute('aria-expanded','false');
  help.addEventListener('click',open);
})();
