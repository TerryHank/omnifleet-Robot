export function initFleetPanel(context) {
  const COMMAND='/fleet/ui/command', STATE='/fleet/ui/state';
  const host=context.panelElement,root=document.createElement('div');host.append(root);
  root.dataset.testid='fleet-panel';root.style.cssText='height:100%;box-sizing:border-box;overflow:auto;padding:12px;font:14px sans-serif;';
  root.innerHTML=`<style>
    .fleet-card{border:1px solid #8793a355;border-radius:8px;padding:10px;margin:10px 0;display:grid;gap:8px}
    .fleet-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.fleet-row>*{min-width:0}
    .fleet-panel-input{box-sizing:border-box;padding:6px;border:1px solid #8793a377;border-radius:5px;color:inherit;background:transparent;font:inherit}
    [data-testid=fleet-panel] button{font:inherit;padding:7px 10px;border-radius:5px;border:1px solid #8793a377;cursor:pointer}
    [data-testid=fleet-panel] button:disabled{opacity:.45;cursor:default}
    .fleet-muted{font-size:.88em;opacity:.75}.fleet-status{white-space:pre-wrap;overflow-wrap:anywhere;padding:8px;border-left:3px solid #4389dc;background:#4389dc14}
  </style>
  <div class="fleet-row"><strong style="font-size:1.2em;flex:1">多机协同</strong><button data-ui="smaller">−</button><button data-ui="larger">＋</button><button data-ui="reset">恢复</button></div>
  <div class="fleet-card"><strong>1 · 域内在线车辆</strong><div data-ui="robots"></div><label>当前编辑车辆 <select class="fleet-panel-input" data-ui="selected"></select></label><div class="fleet-muted">自动发现域内在线车辆，离线约2秒移出列表。勾选只参与任务选择，不会立即发车。未接入协同接口的车辆仅显示。</div></div>
  <div class="fleet-card"><strong>2 · 协同模式</strong><select class="fleet-panel-input" data-ui="mode"><option value="independent">每辆车独立规划航点</option><option value="leader">领航模式</option></select><div data-ui="formation"><label>领航车（编号1） <select class="fleet-panel-input" data-ui="leader"></select></label><label style="display:block;margin-top:8px">相邻车辆跟随距离（米） <input class="fleet-panel-input" style="width:90px" type="number" min="1.4" max="5" step="0.1" data-ui="spacing"></label><div class="fleet-muted">编号2跟随领航车。距离按两车中心沿行驶轨迹计算；转弯保留走过的轨迹。</div></div></div>
  <div class="fleet-card"><strong>3 · 所选车辆的多点路线</strong><div class="fleet-muted">在“多机协同3D”工具栏使用“发布点”或“发布位姿”添加航点。也可逐行输入：x, y, 朝向角度（°）。</div><textarea class="fleet-panel-input" rows="6" data-ui="route" placeholder="1.0, 0.0, 0&#10;2.0, 0.0, 0"></textarea><div class="fleet-row"><button data-ui="save">保存航点</button><button data-ui="undo">删除最后点</button><button data-ui="clear">清空路线</button><button data-ui="preview">预检路线</button></div><div class="fleet-muted">浅色线为共享地图预检路径，实色线为车辆Nav2实际路径；最终点保留所填朝向。</div></div>
  <div class="fleet-row"><button data-ui="start" style="background:#2475c9;color:white">开始所选车辆</button><button data-ui="stop" style="background:#a63838;color:white">停止所选任务</button></div><p class="fleet-status" data-ui="status">正在连接协同后台…</p><div class="fleet-muted" data-ui="health"></div><div class="fleet-card"><strong>任务状态</strong><div data-ui="tasks">暂无任务</div></div>`;
  const ui={};root.querySelectorAll('[data-ui]').forEach(e=>{ui[e.dataset.ui]=e;e.dataset.testid='fleet-'+e.dataset.ui;});
  const reload=document.createElement('button');reload.textContent='载入已保存';reload.dataset.testid='fleet-reload';ui.save.after(reload);ui.reload=reload;
  let state,membership="",revision=-1,disposed=false,dirty=false,serial=0,receivedAt=0,draftBase=null,draftOwner=null;const pending=new Map(),rows=new Map();
  let scale=Number(context.initialState?.fontScale)||1;
  const setScale=()=>{root.style.fontSize=(14*scale)+'px';context.saveState?.({...context.initialState,fontScale:scale});};
  root.style.fontSize=(14*scale)+'px';
  ui.smaller.onclick=()=>{scale=Math.max(.8,scale-.1);setScale();};ui.larger.onclick=()=>{scale=Math.min(1.8,scale+.1);setScale();};ui.reset.onclick=()=>{scale=1;setScale();};
  function message(text,error=false){if(disposed)return;ui.status.textContent=text;ui.status.style.borderColor=error?'#d65c5c':'#4389dc';}
  function send(op,body={}) {
    if(!state)return Promise.reject(Error('协同后台尚未连接'));
    const id='fg-'+Date.now().toString(36)+'-'+(++serial);
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{pending.delete(id);reject(Error('请求结果未确认，请先查看任务状态，勿重复发车'));render();},15000);
      pending.set(id,{resolve,reject,timer});
      try{context.publish(COMMAND,{data:JSON.stringify({id,created_at:Date.now()/1000,op,revision:state.revision,...body})});}
      catch(error){clearTimeout(timer);pending.delete(id);reject(error);}
      render();
    });
  }
  const run=operation=>Promise.resolve().then(operation).catch(error=>message(error.message||String(error),true));
  const configure=body=>send('configure',body);
  function parseRoute(){return ui.route.value.split(/\n/).filter(x=>x.trim()).map((line,i)=>{const p=line.split(/[,，\s]+/).filter(Boolean).map(Number);if(p.length!==3||!p.every(Number.isFinite))throw Error('第'+(i+1)+'行需要三个有效数字：x, y, 角度');return[p[0],p[1],p[2]*Math.PI/180];});}
  async function saveRoute(){if(!state.config.selected)throw Error('先激活并选中车辆');if(!dirty)return;if(draftOwner!==state.config.selected||draftBase!==JSON.stringify(state.config.routes[state.config.selected]))throw Error('已保存路线有更新，请先载入已保存航点后再编辑');const routes={...state.config.routes,[state.config.selected]:parseRoute()};await configure({routes});dirty=false;}
  ui.route.oninput=()=>{if(!dirty){draftOwner=state.config.selected;draftBase=JSON.stringify(state.config.routes[draftOwner]);}dirty=true;};
  ui.reload.onclick=()=>{dirty=false;ui.route.value=(state.config.routes[state.config.selected]??[]).map(p=>[p[0],p[1],p[2]*180/Math.PI].join(', ')).join('\n');message('已载入保存的路线');};
  ui.selected.onchange=()=>{const selected=ui.selected.value;run(async()=>{if(dirty)await saveRoute();await configure({selected});});};
  ui.mode.onchange=()=>run(()=>configure({mode:ui.mode.value}));
  ui.leader.onchange=()=>run(()=>configure({leader:ui.leader.value}));
  ui.spacing.onchange=()=>run(()=>{if(!ui.spacing.value.trim())throw Error('跟随距离不能为空');return configure({spacing:Number(ui.spacing.value)});});
  ui.save.onclick=()=>run(saveRoute);
  ui.undo.onclick=()=>run(()=>{const robot=state.config.selected;return configure({routes:{...state.config.routes,[robot]:state.config.routes[robot].slice(0,-1)}});});
  ui.clear.onclick=()=>run(()=>configure({routes:{...state.config.routes,[state.config.selected]:[]}}));
  ui.preview.onclick=()=>run(async()=>{if(dirty)await saveRoute();await send('preview',{robot_id:state.config.selected});});
  ui.start.onclick=()=>run(async()=>{if(dirty)await saveRoute();const robot=state.config.mode==='leader'?state.config.leader:state.config.selected;await send('preview',{robot_id:robot});await send('start',{robot_id:robot});});
  ui.stop.onclick=()=>run(()=>send('stop'));
  function options(select,active){const chosen=select.value;select.replaceChildren();for(const r of active){const o=document.createElement('option');o.value=r.id;o.textContent=r.name;select.append(o);}select.value=chosen;}
  function render(){
    if(!state||disposed)return;
    const c=state.config,stale=Date.now()-receivedAt>2000,online=stale?[]:state.robots.filter(r=>r.online),active=online.filter(r=>r.active),robot=online.find(r=>r.id===c.selected),waiting=pending.size>0||stale;
    if(stale)message('协同后台数据已中断，等待重新连接',true);
    if(revision!==state.revision||membership!==JSON.stringify(online.map(r=>[r.id,r.registered]))){
      membership=JSON.stringify(online.map(r=>[r.id,r.registered]));
      revision=state.revision;ui.robots.replaceChildren();rows.clear();if(!online.length)ui.robots.textContent="当前未发现在线车辆";
      for(const r of online){
        const line=document.createElement('div');line.className='fleet-card';line.style.margin='4px 0';
        const top=document.createElement('div');top.className='fleet-row';const check=document.createElement('input');check.type='checkbox';check.checked=r.active;check.dataset.testid='fleet-active-'+r.id;
        check.onchange=()=>run(()=>configure({active:check.checked?[...c.active,r.id]:c.active.filter(id=>id!==r.id)}));
        const id=document.createElement('span');id.textContent=r.id;
        const name=document.createElement('input');name.className='fleet-panel-input';name.value=r.name;name.style.width='120px';name.dataset.testid='fleet-name-'+r.id;
        name.onchange=()=>run(()=>configure({names:{...state.config.names,[r.id]:name.value}}));
        const rank=document.createElement('select');rank.className='fleet-panel-input';rank.dataset.testid='fleet-rank-'+r.id;
        if(!r.active){const o=document.createElement('option');o.value='';o.textContent='未激活';rank.append(o);}
        else for(let i=1;i<=active.length;i++){const o=document.createElement('option');o.value=String(i);o.textContent='编号 '+i;rank.append(o);}rank.value=String(r.rank??'');
        rank.onchange=()=>run(()=>configure({leader:rank.value==='1'?r.id:active.find(v=>v.id!==r.id)?.id}));
        const health=document.createElement('div');health.className='fleet-muted';top.append(check,id,name,rank);line.append(top,health);ui.robots.append(line);rows.set(r.id,{check,name,rank,health});
      }
      options(ui.selected,active);options(ui.leader,active);ui.selected.value=c.selected??'';ui.leader.value=c.leader??'';ui.mode.value=c.mode;ui.spacing.value=c.spacing;
      if(!dirty)ui.route.value=(c.routes[c.selected]??[]).map(p=>[p[0].toFixed(3),p[1].toFixed(3),(p[2]*180/Math.PI).toFixed(1)].join(', ')).join('\n');
    }
    const healthNames={MANUAL:'手动控制',OFFLINE:'离线',READY:'就绪',ESTOP:'急停',FAULT:'故障',WAITING_ALIGNMENT:'等待协同对齐',WAITING_CONTROL_GATE:'等待控制接口',WAITING_LOCALIZATION_OR_NAV2:'等待定位/导航'};
    for(const r of online){const e=rows.get(r.id);e.check.disabled=e.name.disabled=waiting||state.busy||r.registered===false;e.rank.disabled=waiting||state.busy||!r.active;e.health.textContent=stale?'通讯中断':(r.online?'在线':'离线')+' · '+(r.pose?'定位可显示':'等待共享定位')+' · '+(healthNames[r.health]??r.health)+(r.reason?' · '+r.reason:'');}
    ui.selected.disabled=waiting||!active.length;ui.mode.disabled=ui.leader.disabled=ui.spacing.disabled=waiting||state.busy;
    ui.formation.style.display=c.mode==='leader'?'block':'none';
    const readonly=!robot||robot.busy||(c.mode==='leader'&&c.selected!==c.leader);
    ui.route.disabled=waiting||readonly;for(const key of ['save','reload','undo','clear','preview'])ui[key].disabled=waiting||readonly;
    ui.start.textContent=c.mode==='leader'?'开始领航编队':'开始所选车辆';ui.stop.textContent=c.mode==='leader'?'停止编队任务':'停止所选任务';
    ui.start.disabled=waiting||readonly||!state.motion_enabled||!robot?.ready;ui.stop.disabled=waiting||!state.busy;
    ui.health.textContent=state.motion_enabled?'运动接口已启用；开始时仍检查定位、地图和车间安全条件。':'当前为不运动验收模式：可激活显示、设置路线和预检，发车按钮禁用。';
    ui.tasks.textContent=Object.entries(state.tasks).map(([id,t])=>`${t.owner||t.robot_id||'待分配'}：${t.state}${t.reason?' · '+t.reason:''}`).join('\n')||'暂无独立任务';
    if(c.mode==='leader')ui.tasks.textContent+='\n编队：'+(state.mission?.state??'IDLE');
  }
  context.advertise?.(COMMAND,'std_msgs/msg/String');context.watch('currentFrame');context.subscribe([{topic:STATE}]);
  const healthTimer=setInterval(render,500);
  context.onRender=(renderState,done)=>{try{for(const event of renderState.currentFrame??[]){if(event.topic!==STATE)continue;state=JSON.parse(event.message.data);receivedAt=Date.now();const ack=state.ack;if(ack&&!ack.pending){const request=pending.get(ack.id);if(request){clearTimeout(request.timer);pending.delete(ack.id);ack.ok?request.resolve(ack):request.reject(Error(ack.message));}message(ack.message,!ack.ok);}render();}}catch(error){message('状态解析失败：'+error.message,true);}finally{done();}};
  return()=>{disposed=true;clearInterval(healthTimer);for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('面板已关闭'));}pending.clear();context.onRender=undefined;context.subscribe([]);context.unadvertise?.(COMMAND);root.remove();};
}
