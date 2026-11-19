(function () {
  let fleetApi=window.OmniFleetFleetApiBase||'http://127.0.0.1:8081';
  async function fleetFetch(path,options){
    if(window.OmniFleetFleetWebSocket)return fetch(fleetApi+path,options);
    try{return await fetch(fleetApi+path,options)}catch(error){
      if(fleetApi!=='http://127.0.0.1:8081'&&path!=='/state')throw error;
      const fallback=fleetApi==='http://127.0.0.1:8081'?'http://127.0.0.1:18081':'http://127.0.0.1:8081';
      const response=await fetch(fallback+path,options);
      window.OmniFleetFleetApiBase=fleetApi=fallback;
      return response;
    }
  }
  function robotMessage(state,text){
    return String(text??'').replace(/[A-Za-z0-9_]+/g,id=>state?.assignments?.[id]?.robot_name||id);
  }
  function currentMissionJob(state,robot){
    const job=state.missions?.jobs?.[robot],follow=state.missions?.follow;
    return job?.source==='follow'&&follow&&job.term!==follow.term?undefined:job;
  }
  function discoveredRobots(state){
    return state?.discovery?.fresh?(state.discovery.robots||[]).filter(robot=>state.assignments?.[robot]):[];
  }
  function bindPanelTheme(context,root){
    root.classList.add('fm-themed-panel');
    const style=document.createElement('style');
    style.textContent=`
      .fm-themed-panel{--fm-bg:#f4f4f5;--fm-surface:#ffffff;--fm-text:#393939;--fm-muted:#6f6d79;--fm-border:#d6d6d6;--fm-primary:#6f3be8;--fm-on-primary:#ffffff;--fm-tint:#eee8fb;--fm-danger:#db3553;color-scheme:light}
      .fm-themed-panel[data-color-scheme=dark]{--fm-bg:#15151a;--fm-surface:#27272b;--fm-text:#e1e1e4;--fm-muted:#a7a6af;--fm-border:#585861;--fm-primary:#9480ed;--fm-on-primary:#15151a;--fm-tint:#35313f;--fm-danger:#f54966;color-scheme:dark}
      .fm-themed-panel input,.fm-themed-panel select,.fm-themed-panel textarea{background:var(--fm-bg);color:var(--fm-text);border:1px solid var(--fm-border);border-radius:4px}
      .fm-themed-panel input::placeholder,.fm-themed-panel textarea::placeholder{color:var(--fm-muted);opacity:1}
      .fm-themed-panel input[type=checkbox]{accent-color:var(--fm-primary)}
      .fm-themed-panel :is(button,input,select,textarea,summary):focus-visible{outline:2px solid var(--fm-primary);outline-offset:2px}
      .fm-themed-panel button:not(:disabled):hover{filter:brightness(1.1)}
      .fm-themed-panel button:disabled{opacity:.5;cursor:default}
    `;
    root.append(style);
    context.watch('colorScheme');
    context.onRender=(state,done)=>{
      if(state.colorScheme)root.dataset.colorScheme=state.colorScheme;
      done();
    };
  }
  function TrafficView(root,send){
    root.innerHTML=`<b>任务调度与反馈</b><div class="fm-dispatch-summary"><span data-traffic="online"></span><span data-traffic="rmf"></span><span data-traffic="policy">路权：按车辆顺序；执行中不抢占</span></div>
      <div style="overflow:auto;max-height:300px"><table class="fm-compact-table"><thead><tr>${['任务 / 车辆','位置','优先级','计划 / 状态','进度与反馈','操作'].map(t=>'<th>'+t+'</th>').join('')}</tr></thead><tbody data-traffic="rows"></tbody></table></div>
      <details><summary>设置车辆的计划时间</summary><label>车辆 <select data-traffic="robot" aria-label="计划时间所属车辆"></select></label><p>任务标题由实际任务自动显示：单点导航、多点导航、编队、领车跟随。优先顺序请在原车辆列表中拖动调整，两个前端同步。</p>
        <label>任务标题 <output data-traffic="title" aria-label="调度任务标题"></output></label><p data-traffic="priority" aria-label="自动调度优先级"></p>
        <p><label>最早开始时间 <input data-traffic="time" type="datetime-local" aria-label="计划开始时间"></label></p><button data-traffic="settings">保存调度参数</button>
      </details><details><summary>跟随、调度与任务历史</summary><div data-traffic="events" class="fm-history"></div></details><details><summary>共享代价地图参数</summary><p>首次复制参考车，之后由 WSL 独立保存。共享图包含所有车辆；修改这里不修改车端导航参数。实际行驶规划仍由各车 Nav2 执行。</p><div data-shared="fields"></div><button data-shared="save">保存共享代价参数到 WSL</button><p data-shared="status"></p></details><details><summary data-traffic="rmfSummary">Open-RMF 自动分配与任务记录</summary><div data-traffic="rmfMembers" class="fm-history"></div><div style="overflow:auto"><table class="fm-rmf-table"><thead><tr><th>RMF 任务编号</th><th>车辆</th><th>状态 / 反馈</th></tr></thead><tbody data-traffic="rmfRows"></tbody></table></div></details>`;
    const ui={};root.querySelectorAll('[data-traffic]').forEach(e=>ui[e.dataset.traffic]=e);
    let state,lastRobot,planRobot;
    const shared={};root.querySelectorAll('[data-shared]').forEach(e=>shared[e.dataset.shared]=e);
    const sharedInputs=new Map();let sharedRevision,sharedSaving=false,sharedRequest,sharedSent=0;
    shared.save.onclick=async()=>{
      if(!state?.maps?.shared_costmap||[...sharedInputs.values()].some(input=>!input.reportValidity()))return;
      sharedSaving=true;sharedSent=Date.now();shared.save.disabled=true;
      const parameters=Object.fromEntries([...sharedInputs].map(([key,input])=>[key,Number(input.value)]));
      for(const input of sharedInputs.values())input.disabled=true;
      sharedRequest=await send('shared_costmap_configure',{shared_costmap_revision:sharedRevision,parameters});
      if(!sharedRequest){sharedSaving=false;shared.save.disabled=false;for(const input of sharedInputs.values())input.disabled=false}
    };
    const phases={RMF_PAUSED:'等待 RMF 交通恢复',IDLE:'空闲',SCHEDULED:'等待计划时间',ARMING:'申请租约',PLANNING:'规划中',YIELDING:'等待路权',EXECUTING:'执行中',STOPPING:'确认停止',STOPPED:'停止',COMPLETED:'完成',FAILED:'失败',INVALIDATED:'会话失效',BLOCKED:'受阻',CANCEL_UNCONFIRMED:'停止未确认'};
    const pose=p=>p?`${p[0].toFixed(2)}, ${p[1].toFixed(2)}, ${(p[2]*180/Math.PI).toFixed(0)}°`:'—';
    const name=r=>state.assignments[r]?.robot_name||r||'未选择车辆';
    const taskTitle=robot=>{
      const {formation,follow,jobs,routes}=state.missions;
      if(formation?.active&&formation.saved?.order?.includes(robot))return '编队';
      if(follow?.active&&follow.order?.includes(robot))return '领车跟随';
      return {single:'单点导航',dispatch:'目标调度',route:'多点导航',formation:'编队',follow:'领车跟随'}[jobs?.[robot]?.source]||(routes?.[robot]?.points?.length?'多点导航':'—');
    };
    ui.settings.onclick=()=>send('dispatch_settings',{robot_id:planRobot,not_before:ui.time.value?new Date(ui.time.value).getTime()/1000:0});
    ui.robot.onchange=()=>{planRobot=ui.robot.value;this.render(state)};
    this.render=s=>{
      state=s;const traffic=s.missions.traffic||{},robots=discoveredRobots(s);
      if(!robots.includes(planRobot))planRobot=robots[0];
      if([...ui.robot.options].map(o=>o.value).join(',')!==robots.join(','))ui.robot.replaceChildren(...robots.map(r=>new Option(name(r),r)));
      for(const option of ui.robot.options)option.textContent=name(option.value);
      ui.robot.value=planRobot||'';ui.robot.disabled=!robots.length;
      const robot=planRobot;
      ui.policy.textContent=s.missions.traffic?.policy==='distance_then_order'?'实验性路权：距调度目标越近越优先，其次按车辆顺序；执行中不抢占':'路权：领车最高，其后按车辆顺序；执行中不抢占';
      const rmf=s.rmf,registered=robots.filter(r=>rmf?.traffic?.robots?.[r]?.registered).length,tasks=rmf?.dispatch?.tasks||[];
      ui.online.textContent=robots.filter(r=>s.robots?.[r]?.online).length+'/'+robots.length+' 台在线';
      ui.rmf.textContent='RMF '+registered+' 台已注册 · 分配'+(rmf?.dispatch?.connected?'已连接':'未连接')+' · 交通'+(rmf?.traffic?.connected?'已连接':'未连接');
      ui.rmfSummary.textContent='Open-RMF 自动分配与任务记录 · '+tasks.length+' 项';
      ui.rmfMembers.textContent=Object.entries(rmf?.traffic?.robots||{}).filter(([r])=>robots.includes(r)).map(([r,v])=>name(r)+'：'+(v.registered?'已注册':'注册中')+' · '+(v.state||'等待状态')).join('  ')||'暂无 RMF 车辆';
      const config=s.maps.shared_costmap;
      if(sharedSaving&&(config?.revision!==sharedRevision||['saved','rejected','failed'].includes(s.commands?.[sharedRequest]?.phase)||Date.now()-sharedSent>15000))sharedSaving=false;
      shared.save.disabled=!config||sharedSaving;
      if(config&&sharedRevision!==config.revision){
        if(!sharedInputs.size)for(const field of config.fields){const label=document.createElement('label'),input=document.createElement('input');label.textContent=field.label+' ';input.type='number';input.required=true;input.min=field.min;input.max=field.max;input.step=field.step;input.setAttribute('aria-label','共享'+field.label);input.style.width='100px';label.append(input);shared.fields.append(label,document.createElement('br'));sharedInputs.set(field.id,input)}
        for(const [key,input] of sharedInputs)input.value=config.parameters[key];sharedRevision=config.revision;
      }
      for(const input of sharedInputs.values())input.disabled=sharedSaving;
      shared.status.textContent='独立共享层：'+(config?.ready?'已生成':'等待地图')+' · 车辆占用区与车体膨胀半径是不同参数。';
      if(lastRobot!==robot){lastRobot=robot;const value=traffic.settings?.[robot]||{};ui.time.value=value.not_before?new Date(value.not_before*1000-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):''}
      ui.title.textContent=taskTitle(robot);
      const order=traffic.order||s.missions.follow.order||Object.keys(s.assignments),index=order.indexOf(robot);
      ui.priority.textContent=traffic.policy==='distance_then_order'?'实验性调度：距离优先，距离相同按第 '+(index+1)+' 位':index<0?'等待车辆顺序':'第 '+(index+1)+' 位'+(index===0?'（领车）':'')+' · 自动优先级 '+(order.length-index);
      ui.events.textContent=(s.missions.events||[]).map(event=>new Date(event.time*1000).toLocaleTimeString()+' '+robotMessage(s,event.message)).join('\n')||'尚无任务历史';
      ui.rmfRows.replaceChildren(...tasks.map(task=>{const tr=document.createElement('tr');for(const value of [task.task_id||'等待任务编号',name(task.robot),(task.phase||'等待状态')+(task.message?' · '+robotMessage(s,task.message):'')]){const td=document.createElement('td');td.textContent=value;tr.append(td)}return tr}),...(tasks.length?[]:[(()=>{const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=3;td.textContent='暂无 RMF 任务';tr.append(td);return tr})()]));
      ui.rows.replaceChildren(...(s.missions.dispatch_rows||[]).filter(row=>robots.includes(row.car)).map(row=>{
        const tr=document.createElement('tr');tr.dataset.car=row.car;
        const job=currentMissionJob(s,row.car);
        if(s.missions.jobs?.[row.car]&&!job)row={...row,phase:'IDLE',message:'上次跟随任务已结束',init_pose:null,target_pose:null};
        const values=[[taskTitle(row.car),name(row.car)],['当前 '+pose(row.pose),'起点 '+pose(row.init_pose)+' → 目标 '+pose(row.target_pose)],[traffic.policy==='distance_then_order'?'距离 '+(Number.isFinite(row.distance_to_dispatch_goal)?row.distance_to_dispatch_goal.toFixed(2)+' m':'待定位'):'任务 '+row.task_priority,traffic.policy==='distance_then_order'?'同距按第 '+row.dispatch_index+' 位':'路权 '+row.local_priority],[row.not_before?new Date(row.not_before*1000).toLocaleString():'立即',phases[row.phase]||'状态待确认'],[job?(job.index||0)+'/'+(job.points?.length||0):'—',robotMessage(s,job?.message||row.message)||'暂无执行反馈']];
        for(const [primary,secondary] of values){const td=document.createElement('td'),top=document.createElement('span'),small=document.createElement('small');top.textContent=primary;small.textContent=secondary;td.append(top,small);tr.append(td)}
        const td=document.createElement('td');for(const [op,label] of [['route_start','执行'],['route_stop','停止']]){const b=document.createElement('button');b.textContent=label;b.disabled=op==='route_start'&&!s.missions.routes?.[row.car]?.points?.length;b.onclick=()=>send(op,{robot_id:row.car});td.append(b)}tr.append(td);return tr;
      }));
    };
  }

  function syncMapPrefixes(assignments,waypoint,revision,costmapRobot,showGlobal=true,showLocal=false,descriptions={},sessions={},sharedMode=true,formationTarget=false,dispatchMode=null){
    const api=window.foxgloveDemoControl,current=api?.layout();
    const mapKey=Object.keys(current?.data?.configById||{}).find(k=>(k.startsWith('3D!fleetMap')||k.startsWith('3D!dispatchLiveMap')));
    const map=current?.data?.configById?.[mapKey];
    if(!map)return;
    const mapTitle=sharedMode?'共享代价地图':(assignments[costmapRobot]?.robot_name||'车辆')+' · 车端代价预览';
    const removed=Object.entries(map.layers||{}).filter(([robot,layer])=>layer.layerId==='foxglove.Urdf'&&layer.instanceId===robot&&!assignments[robot]);
    const peerTopics=new Set(['/fleet/peer_map',...Object.values(assignments).map(a=>a.namespace+'/navigation/peer_map')]);
    const stalePeers=Object.keys(map.topics||{}).filter(topic=>topic.endsWith('/peer_map')&&!peerTopics.has(topic));
    const replacements=[];let changed=map.foxglovePanelTitle!==mapTitle||removed.length>0||stalePeers.length>0;
    for(const [robot,a] of Object.entries(assignments)){
      const layer=map.layers?.[robot];if(!layer){changed=true;continue}
      const old=(layer.framePrefix||'').replace(/\/$/,''),next=a.namespace.slice(1);
      if(old!==next)replacements.push([old,next]);
      const modelUrl=descriptions[robot]?'data:application/xml;charset=utf-8,'+encodeURIComponent(descriptions[robot]):undefined;
      if(old!==next||layer.label!==a.robot_name||layer.topic!==a.namespace+'/robot_description'||(modelUrl&&(layer.sourceType!=='url'||layer.url!==modelUrl)))changed=true;
      for(const [kind,enabled] of [['global_costmap',showGlobal],['local_costmap',showLocal]]){
        const settings=map.topics?.[a.namespace+'/'+kind+'/costmap'];
        if(settings?.visible!==(!sharedMode&&robot===costmapRobot&&enabled)||settings?.colorMode!=='custom'||settings?.maxColor!==(kind==='global_costmap'?'#f28e2bcc':'#e15759dd'))changed=true;
      }
    }
    const base=r=>assignments[r]?.namespace+'/ui/r'+revision;
    const target=assignments[waypoint];
    const waypointBase=dispatchMode?'/fleet/dispatch/'+dispatchMode+'/ui/r'+revision:formationTarget?'/fleet/formation/ui/r'+revision:base(waypoint);
    const waypointTopic=target?waypointBase+'/goal':undefined;
    let modelVersion=2166136261;
    for(const robot of Object.keys(assignments).sort())for(const char of (descriptions[robot]||'')+'|'+(sessions[robot]||''))modelVersion=Math.imul(modelVersion^char.charCodeAt(0),16777619)>>>0;
    if(map.topics?.['/fleet/global_costmap/costmap']?.visible!==(sharedMode&&showGlobal)||map.topics?.['/fleet/peer_map']?.visible!==false)changed=true;
    const nextMapKey='3D!fleetMap_'+(dispatchMode?'dispatch_'+dispatchMode:formationTarget?'formation':target?.robot_name)+'_r'+revision+'_model'+modelVersion+'_inflation_'+(sharedMode?'wsl':assignments[costmapRobot]?.robot_name)+'_'+Number(showGlobal)+Number(showLocal);
    if(target&&(map.publish?.poseTopic!==waypointTopic||mapKey!==nextMapKey))changed=true;
    if(!changed)return;
    const rewrite=text=>{
      const tag=text.startsWith('frame:')?'frame:':'',value=text.slice(tag.length);
      for(const [old,next] of replacements)for(const lead of ['', '/'])if(value===lead+old||value.startsWith(lead+old+'/'))return tag+lead+next+value.slice((lead+old).length);
      return text;
    };
    const data=JSON.parse(JSON.stringify(current.data)),next=data.configById[mapKey];
    const rebase=value=>typeof value==='string'?rewrite(value):Array.isArray(value)?value.map(rebase):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([k,v])=>[rewrite(k),rebase(v)])):value;
    next.topics=rebase(map.topics||{});next.transforms=rebase(map.transforms||{});next.followTf=rewrite(map.followTf||'fleet_map');
    next.layers||={};next.foxglovePanelTitle=mapTitle;
    for(const topic of stalePeers)delete next.topics[topic];
    for(const [robot,layer] of removed){
      delete next.layers[robot];
      const prefix='/'+(layer.framePrefix||'').replace(/\/$/,'');
      for(const topic of Object.keys(next.topics))if(topic.startsWith(prefix+'/'))delete next.topics[topic];
    }
    if(!lead){
      if(controlKey)data.configById[controlKey]={...control,topic:'',foxglovePanelTitle:'等待车辆广播'};
      next.publish={...next.publish,poseTopic:'',pointTopic:'',poseEstimateTopic:''};
    }
    Object.entries(assignments).forEach(([robot,a],index)=>{
      next.layers[robot]={layerId:'foxglove.Urdf',visible:true,frameLocked:true,instanceId:robot,sourceType:'topic',displayMode:'visual',fallbackColor:'#9e9e9e',...next.layers[robot],framePrefix:a.namespace.slice(1)+'/',topic:a.namespace+'/robot_description',label:a.robot_name};
      if(descriptions[robot]){
        next.layers[robot].sourceType='url';
        next.layers[robot].url='data:application/xml;charset=utf-8,'+encodeURIComponent(descriptions[robot]);
      }
      next.topics[a.namespace+'/map']||={visible:false};
      next.topics[a.namespace+'/robot_description']||={visible:false};
      for(const [kind,enabled] of [['global_costmap',showGlobal],['local_costmap',showLocal]])
        next.topics[a.namespace+'/'+kind+'/costmap']={...next.topics[a.namespace+'/'+kind+'/costmap'],visible:!sharedMode&&robot===costmapRobot&&enabled,colorMode:'custom',minColor:kind==='global_costmap'?'#fff2cc35':'#e8f5e955',maxColor:kind==='global_costmap'?'#f28e2bcc':'#e15759dd',unknownColor:'#ffffff00',alpha:1.,frameLocked:kind==='local_costmap'};
      next.topics[a.namespace+'/missions/preview_path']||={visible:true,color:index%2===0?'#ffd600':'#00c8ff',lineWidth:.035};
    });
    next.topics['/fleet/global_costmap/costmap']={visible:sharedMode&&showGlobal,colorMode:'custom',minColor:'#fff2cc00',maxColor:'#f28e2bdd',unknownColor:'#ffffff00',alpha:1.,frameLocked:false};
    next.topics['/fleet/peer_map']={...next.topics['/fleet/peer_map'],visible:false};
    if(target){
      next.publish={...next.publish,type:next.publish?.type||'pose',poseTopic:waypointTopic,pointTopic:waypointBase+'/point',poseEstimateTopic:base(waypoint)+'/pose_estimate'};
      next.foxglovePanelTitle=mapTitle;
      next.topics['/fleet/waypoints']={visible:true};
      if(mapKey!==nextMapKey){delete data.configById[mapKey];data.configById[nextMapKey]=next}
      const retarget=value=>value===mapKey?nextMapKey:value&&typeof value==='object'?{...value,first:retarget(value.first),second:retarget(value.second)}:value;
      data.layout=retarget(data.layout);
    }
    api.setLayout(current.name||'WSL 多车调度',data);
    if(replacements.length)api.connect(window.OmniFleetFleetWebSocket||'ws://127.0.0.1:8767');
  }
  function syncUnalignedViews(state){
    const api=window.foxgloveDemoControl,current=api?.layout(),configs=current?.data?.configById||{};
    const sharedKey=Object.keys(configs).find(k=>(k.startsWith('3D!fleetMap')||k.startsWith('3D!dispatchLiveMap')));
    if(!sharedKey)return;
    const views=[];
    for(const [robot,assignment] of Object.entries(state.assignments||{})){
      const vehicle=state.robots?.[robot];
      if(!vehicle?.online||state.maps?.alignment_valid||state.maps?.transforms?.[robot])continue;
      const model=configs[sharedKey].layers?.[robot];if(!model)continue;
      const session=vehicle.samples?.navigation?.value?.localization_epoch||'';
      let version=2166136261;
      for(const char of assignment.namespace+'|'+session+'|'+(model.url||''))version=Math.imul(version^char.charCodeAt(0),16777619)>>>0;
      const key='3D!fleetLocal_'+robot+'_r'+state.identity_revision+'_'+version;
      views.push([key,{
        foxglovePanelTitle:assignment.robot_name+' · 本车地图（等待共享配准）',
        followTf:assignment.namespace.slice(1)+'/base_link',followMode:'follow-pose',
        cameraState:{...configs[sharedKey].cameraState,distance:6,phi:.15,thetaOffset:0,targetOffset:[0,0,0]},
        scene:configs[sharedKey].scene,transforms:{},
        topics:{[assignment.namespace+'/map']:{visible:true},[assignment.namespace+'/global_costmap/costmap']:{visible:true,colorMode:'custom',minColor:'#fff2cc35',maxColor:'#f28e2bcc',unknownColor:'#ffffff00',alpha:1.}},
        layers:{[robot]:model},
        publish:{...configs[sharedKey].publish,poseTopic:assignment.namespace+'/ui/r'+state.identity_revision+'/goal',pointTopic:assignment.namespace+'/ui/r'+state.identity_revision+'/point',poseEstimateTopic:assignment.namespace+'/ui/r'+state.identity_revision+'/pose_estimate'}
      }]);
    }
    const previous=Object.keys(configs).filter(k=>k.startsWith('3D!fleetLocal_'));
    if(JSON.stringify(previous.sort())===JSON.stringify(views.map(([k])=>k).sort()))return;
    const data=JSON.parse(JSON.stringify(current.data));
    for(const key of previous)delete data.configById[key];
    const strip=value=>typeof value==='string'?value.startsWith('3D!fleetLocal_')?undefined:value:value&&typeof value==='object'?(()=>{
      const first=strip(value.first),second=strip(value.second);
      return first&&second?{...value,first,second}:first||second;
    })():value;
    data.layout=strip(data.layout);
    let maps=sharedKey;
    for(const [key,config] of views){data.configById[key]=config;maps={direction:'row',splitPercentage:50,first:maps,second:key}}
    const insert=value=>value===sharedKey?maps:value&&typeof value==='object'?{...value,first:insert(value.first),second:insert(value.second)}:value;
    data.layout=insert(data.layout);api.setLayout(current.name,data);
  }
  function initDispatchControls(context){
    const root=document.createElement('div');context.panelElement.append(root);
    root.style.cssText='height:100%;overflow:auto;box-sizing:border-box;padding:12px;background:var(--fm-bg);color:var(--fm-text);font:14px sans-serif';
    root.innerHTML=`<style>.fm-dispatch{background:var(--fm-surface);border:1px solid var(--fm-border);border-radius:8px;padding:12px}.fm-dispatch .fm-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.fm-dispatch input,.fm-dispatch select,.fm-dispatch button{font:inherit;padding:6px;box-sizing:border-box}.fm-dispatch small{display:block;color:var(--fm-muted);line-height:1.45;margin-top:3px;white-space:normal}.fm-dispatch label{display:inline-block;margin:5px}.fm-dispatch summary{padding:8px 0;cursor:pointer}.fm-dispatch button{cursor:pointer;background:var(--fm-primary);color:var(--fm-on-primary);border:0;border-radius:5px}.fm-dispatch button:disabled{cursor:default;opacity:.5}.fm-dispatch-summary{display:flex;gap:7px;flex-wrap:wrap;margin:9px 0}.fm-dispatch-summary span{background:var(--fm-tint);border-radius:999px;padding:4px 8px;font-size:12px}.fm-compact-table,.fm-rmf-table{border-collapse:collapse;width:100%;min-width:720px}.fm-compact-table th,.fm-compact-table td,.fm-rmf-table th,.fm-rmf-table td{padding:6px;text-align:left;border-top:1px solid var(--fm-border);vertical-align:top}.fm-history{white-space:pre-wrap;line-height:1.6;color:var(--fm-muted)}.fm-compact-table td:last-child{white-space:nowrap}</style>
      <div class="fm-dispatch" data-dispatch="view"></div><p data-dispatch="receipt" role="status">尚无操作</p>`;
    const ui={};root.querySelectorAll('[data-dispatch]').forEach(e=>ui[e.dataset.dispatch]=e);
    let state,disposed=false,working=false,updated=0,requestId;
    const name=r=>state?.assignments?.[r]?.robot_name||r;
    const view=new TrafficView(ui.view,send);
    async function refresh(){
      try{
        const response=await fleetFetch('/state',{cache:'no-store'});
        if(!response.ok)throw Error('调度端未响应');
        const next=await response.json();if(disposed)return;state=next;updated=Date.now();
        view.render(state);
        if(ui.receipt.dataset.connectionError){ui.receipt.textContent='调度连接已恢复';delete ui.receipt.dataset.connectionError}
        const result=state.commands?.[requestId];
        if(result)ui.receipt.textContent=({accepted:'已接收',saved:'已保存',rejected:'请求未通过',failed:'请求失败',queued:'等待处理'}[result.phase]||'处理结果')+(result.message?'：'+robotMessage(state,result.message):'');
      }catch(error){if(!disposed){ui.receipt.dataset.connectionError='true';ui.receipt.textContent='调度连接中断：'+error.message}}
    }
    async function send(op,fields={}){
      if(!state||working||Date.now()-updated>1500){ui.receipt.textContent='请等待新鲜调度状态后再操作';return}
      working=true;
      const id='fox-dispatch-'+Date.now()+'-'+Math.random().toString(16).slice(2);requestId=id;
      try{
        const response=await fleetFetch('/command',{method:'POST',headers:{'Content-Type':'application/json','X-OmniFleet-Token':state.token},
          body:JSON.stringify({op,id,identity_revision:state.identity_revision,...fields,...(fields.robot_id?{robot_id:name(fields.robot_id)}:{})})});
        if(!response.ok)throw Error('调度端拒绝请求（'+response.status+'）');
        ui.receipt.textContent='请求已提交，等待调度回执';
        return id;
      }catch(error){ui.receipt.textContent=error.message}
      finally{working=false;await refresh()}
    }
    bindPanelTheme(context,root);context.watch('currentFrame');
    const timer=setInterval(refresh,1000);void refresh();
    return()=>{disposed=true;clearInterval(timer);root.remove()};
  }

  function waypointList(element,editable,emptyText){
    let text='',selected=-1;
    element.classList.add('fm-waypoint-list');
    function render(){
      const lines=text.split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
      selected=lines.length?Math.max(0,Math.min(selected,lines.length-1)):-1;
      const list=document.createElement('ol');list.className='fm-waypoints';
      if(!lines.length){const empty=document.createElement('li');empty.className='fm-waypoint-empty';empty.textContent=emptyText;list.append(empty)}
      lines.forEach((line,index)=>{
        const values=line.split(/[,，\s]+/).map(Number),row=document.createElement('li');
        row.className='fm-waypoint';row.dataset.selected=String(index===selected);
        const choose=document.createElement('button');choose.type='button';choose.className='fm-waypoint-select';
        choose.setAttribute('aria-pressed',String(index===selected));choose.setAttribute('aria-label','选中航点 '+(index+1));
        const number=document.createElement('span');number.className='fm-waypoint-number';number.textContent=index+1;
        const detail=document.createElement('span');detail.className='fm-waypoint-detail';detail.textContent='航点 '+(index+1);
        const coordinates=document.createElement('small');coordinates.textContent='x '+values[0].toFixed(2)+' m · y '+values[1].toFixed(2)+' m · '+values[2].toFixed(1)+'°';
        detail.append(coordinates);choose.append(number,detail);choose.onclick=()=>{selected=index;render()};row.append(choose);
        if(editable){
          const actions=document.createElement('span');actions.className='fm-waypoint-actions';
          for(const [action,label] of [['up','↑'],['down','↓'],['remove','删除']]){
            const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.action=action;
            button.setAttribute('aria-label',({up:'上移',down:'下移',remove:'删除'})[action]+'航点 '+(index+1));
            button.disabled=action==='up'&&index===0||action==='down'&&index===lines.length-1;
            button.onclick=()=>{
              if(action==='remove'){lines.splice(index,1);selected=Math.min(index,lines.length-1)}
              else{const next=index+(action==='up'?-1:1);[lines[index],lines[next]]=[lines[next],lines[index]];selected=next}
              text=lines.join('\n');render();element.dispatchEvent(new Event('input',{bubbles:true}));
            };
            actions.append(button);
          }
          row.append(actions);
        }
        list.append(row);
      });
      element.replaceChildren(list);
    }
    // Keep the existing route draft/save contract; coordinates are displayed as list rows.
    Object.defineProperty(element,'value',{get:()=>text,set:value=>{value=String(value??'');if(value!==text){text=value;render()}}});
    render();
  }

  function initWslFleetPanel(context) { return initFleetOverview(context,false); }
  function initDispatchPanel(context) { return initFleetOverview(context,true); }
  function initFleetOverview(context,mutexOnly) {
    const root=document.createElement('div');context.panelElement.append(root);
    root.className='fleet-overview';
    const card=(title,columns,body,kind)=>`<section class="ov-card"><h2>${title}</h2><div class="ov-scroll"><table><thead><tr>${columns.map(label=>'<th>'+label+'</th>').join('')}</tr></thead><tbody data-rows="${kind}">${body?'<tr><td colspan="'+columns.length+'" class="ov-empty">'+body+'</td></tr>':''}</tbody></table></div><footer data-count="${kind}">共 0 条</footer></section>`;
    root.innerHTML=`<style>
      .fleet-overview{height:100%;overflow:auto;box-sizing:border-box;background:var(--fm-bg);color:var(--fm-text);font:13px "Segoe UI","Microsoft YaHei",sans-serif}
      .fleet-overview *{box-sizing:border-box}.fleet-overview [hidden]{display:none!important}
      .fleet-overview .ov-header{display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid var(--fm-border);background:var(--fm-surface);position:sticky;top:0;z-index:1}
      .fleet-overview .ov-health{margin-left:auto;color:var(--fm-muted);font-size:12px}
      .fleet-overview button{font:inherit;color:var(--fm-text);border:1px solid var(--fm-border);border-radius:4px;background:var(--fm-surface);padding:6px 12px;cursor:pointer}
      .fleet-overview button[aria-selected=true]{color:var(--fm-on-primary);background:var(--fm-primary);border-color:var(--fm-primary)}
      .fleet-overview .ov-cards{display:flex;flex-direction:column;gap:8px;padding:8px;min-height:calc(100% - 49px);container-type:inline-size}
      .fleet-overview .ov-card{border:1px solid var(--fm-border);border-radius:4px;background:var(--fm-surface);overflow:hidden;flex:1;min-height:150px}
      .fleet-overview h2{font-size:15px;font-weight:600;margin:0;padding:10px 12px;border-bottom:1px solid var(--fm-border)}
      .fleet-overview .ov-scroll{overflow:auto}.fleet-overview table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:12px}
      .fleet-overview th{text-align:left;font-weight:600;color:var(--fm-muted);background:var(--fm-bg)}
      .fleet-overview th,.fleet-overview td{padding:10px 12px;border-bottom:1px solid var(--fm-border)}
      .fleet-overview .ov-empty{text-align:center;height:55px;color:var(--fm-muted)}
      .fleet-overview footer{padding:8px 12px;text-align:right;color:var(--fm-muted);font-size:12px}
      .fleet-overview .ov-warning{color:#eba800}.fleet-overview .ov-good{color:var(--fm-primary)}
      .fleet-overview .ov-controls{height:calc(100% - 49px);display:flex;flex-direction:column}
      .fleet-overview .ov-task-panel{flex:1;min-height:0}
      .fleet-overview .ov-controls>details{overflow:auto;border-bottom:1px solid var(--fm-border)}
      .fleet-overview .ov-controls>details[open]{flex:1;min-height:0}
      .fleet-overview .ov-controls>details>summary{padding:9px 12px;cursor:pointer}
      .fleet-overview .ov-formation{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:12px}
      .fleet-overview .ov-formation select,.fleet-overview .ov-formation input,.fleet-overview td input{font:inherit;padding:5px 7px}
      .fleet-overview .ov-formation input{width:74px}.fleet-overview td input{width:120px}
      .fleet-overview .ov-robot-card{display:inline-flex;align-items:center;gap:5px;padding:4px;border:1px solid var(--fm-border);border-radius:5px;background:var(--fm-bg);cursor:pointer;user-select:none}
      .fleet-overview .ov-robot-card:hover{border-color:var(--fm-primary)}.fleet-overview .ov-robot-card:focus-visible{outline:2px solid var(--fm-primary)}
      .fleet-overview .ov-order{cursor:grab;padding:2px 4px}.fleet-overview .ov-edit{padding:2px 5px}
      .fleet-overview tr[data-drop=true]{box-shadow:inset 0 2px var(--fm-primary)}
      .fleet-overview .ov-feedback{padding:0 12px 10px;color:var(--fm-muted);margin:0}
      .fleet-overview .ov-result{padding:8px 12px}.fleet-overview .ov-result:empty{display:none}
      @container(max-width:740px){
        .fleet-overview th,.fleet-overview td{padding:8px 6px}
        .fleet-overview th,.fleet-overview td:last-child{white-space:normal}
      }
      @media(max-width:650px){.fleet-overview .ov-health{display:none}.fleet-overview th,.fleet-overview td{padding:8px}}
    </style><header class="ov-header"><button data-page="overview" aria-selected="true">${mutexOnly?'互斥组':'系统概览'}</button>${mutexOnly?'<button data-page="tasks">调度与反馈</button>':''}<span class="ov-health" role="status">连接中</span></header><p class="ov-feedback ov-result" role="status"></p><main class="ov-cards">${mutexOnly?
      card('互斥组',['组名','锁定中','等待中'],'','mutex'):
      card('机器人',['顺序 / 名称','编队位置','预计完成时间','楼层','电源电压','最后更新时间','状态'],'','robots')+
      card('编队小队',['小队','领队','成员顺序','队形','状态'],'暂无已保存的编队小队','squads')+
      card('区域命名',['已命名区域','宽度','占用车辆'],'','regions')}
    </main>${mutexOnly?`<section class="ov-controls" hidden><details><summary>编队与航点</summary><form class="ov-formation" aria-label="队形设置"><label>队形 <select name="shape"><option value="current">保持当前位置</option><option value="column">纵队</option><option value="line">横队</option><option value="wedge">楔形</option></select></label><label class="ov-spacing" hidden>间距 <input name="spacing" type="number" min="0.1" step="0.1" value="1.5" required> m</label><button type="submit" disabled>保存队形</button></form><p class="ov-feedback ov-saved"></p><div class="ov-formation-panel"></div></details><div class="ov-task-panel"></div></section>`:''}`;
    const cards=root.querySelector('.ov-cards'),controls=root.querySelector('.ov-controls'),health=root.querySelector('.ov-health');
    const peers=document.createElement('section');peers.className='ov-card';peers.hidden=true;
    peers.innerHTML='<h2>其他车辆的调度任务</h2><div class="ov-scroll"><table><thead><tr><th>任务</th><th>派发车辆</th><th>执行车辆</th><th>状态</th></tr></thead><tbody></tbody></table></div>';
    if(!mutexOnly)cards.append(peers);
    let disposed=false,busy=false,cleanupControls,cleanupFormation,state,visibleOrder=[],dragRobot,editing,requestId,sending=false,loadedShape=false;
    const row=values=>{const tr=document.createElement('tr');for(const value of values){const td=document.createElement('td');td.textContent=value;tr.append(td)}return tr};
    const formationForm=root.querySelector('.ov-formation'),result=root.querySelector('.ov-result');
    const shapeNames={current:'保持当前位置',column:'纵队',line:'横队',wedge:'楔形'};
    const robotId=id=>state.assignments[id]?.robot_name||id;
    const displayName=id=>state.robot_names?.[id]||robotId(id);
    function placeholder(body,message,columns){
      const tr=row([message]);tr.firstChild.colSpan=columns;tr.firstChild.className='ov-empty';body.append(tr);
    }
    async function submit(op,fields){
      if(!state||sending)return;
      sending=true;
      const id='fox-overview-'+Date.now()+'-'+Math.random().toString(16).slice(2);
      try{
        const response=await fleetFetch('/command',{method:'POST',headers:{'Content-Type':'application/json','X-OmniFleet-Token':state.token},body:JSON.stringify({op,id,identity_revision:state.identity_revision,...fields})});
        if(!response.ok)throw Error('调度端拒绝请求（'+response.status+'）');
        requestId=id;result.textContent='等待调度回执…';
      }catch(error){result.textContent=error.message}
      finally{sending=false;void refresh()}
    }
    function moveRobot(from,to){
      const fromIndex=visibleOrder.indexOf(from),toIndex=visibleOrder.indexOf(to);
      if(fromIndex<0||toIndex<0||fromIndex===toIndex)return;
      const order=[...visibleOrder];order.splice(fromIndex,1);order.splice(toIndex,0,from);
      const traffic=state.missions.traffic;
      void submit('dispatch_order',{order:[...order,...traffic.order.filter(id=>!order.includes(id))].map(robotId),order_revision:traffic.order_revision});
    }
    if(formationForm){
      formationForm.elements.shape.onchange=()=>{root.querySelector('.ov-spacing').hidden=formationForm.elements.shape.value==='current'};
      formationForm.onsubmit=event=>{
        event.preventDefault();
        void submit('formation_capture',{order:visibleOrder.map(robotId),shape:formationForm.elements.shape.value,spacing:Number(formationForm.elements.spacing.value)});
      };
      const details=formationForm.closest('details');
      details.ontoggle=()=>{
        if(details.open&&!cleanupFormation)cleanupFormation=initWslControls({...context,panelElement:details.querySelector('.ov-formation-panel')});
        if(!details.open&&cleanupFormation){cleanupFormation();cleanupFormation=undefined}
      };
    }
    function renderVehicle(body,id,index){
      const robot=state.robots?.[id],nav=robot?.samples?.navigation?.value||{},voltage=robot?.samples?.voltage;
      const job=currentMissionJob(state,id),connected=robot?.transport_connected??robot?.online;
      const status=!connected?'离线':!robot.fresh?.pose?'通信在线 · 定位数据过期':nav.readiness_reason||({EXECUTING:'工作中',COMPLETED:'完成',PLANNING:'规划中',BLOCKED:'受阻'}[job?.phase])||(nav.local_ready?'空闲':'等待导航就绪');
      const age=robot?.samples?.navigation?.age_seconds;
      const updated=Number.isFinite(age)?new Date(Date.now()-age*1000).toLocaleTimeString('zh-CN',{hour12:false}):'—';
      const power=typeof voltage?.value==='number'&&voltage.age_seconds<10?voltage.value.toFixed(2)+' V':'—';
      const {formation,follow}=state.missions;
      const activeOrder=formation.active?formation.saved?.order:follow.active?follow.order:undefined;
      const teamIndex=(activeOrder||visibleOrder).indexOf(id);
      const tr=row(['',teamIndex<0?'未编入':teamIndex===0?'领队':'第 '+(teamIndex+1)+' 位','—','—',power,updated,status]);
      const cell=tr.firstChild,name=displayName(id);
      const handle=document.createElement('button');handle.className='ov-order';handle.type='button';handle.textContent='⠿ '+(index+1);handle.draggable=true;handle.dataset.robot=id;
      handle.title='拖动排序，或使用方向键调整';handle.setAttribute('aria-label',name+' 路权顺序');
      handle.ondragstart=event=>{dragRobot=id;event.dataTransfer.setData('text/plain',id);event.dataTransfer.effectAllowed='move'};
      handle.ondragend=()=>{dragRobot=undefined;void refresh()};
      handle.onkeydown=event=>{
        if(event.key!=='ArrowUp'&&event.key!=='ArrowDown')return;
        event.preventDefault();moveRobot(id,visibleOrder[index+(event.key==='ArrowUp'?-1:1)]);
      };
      tr.ondragover=event=>{if(dragRobot&&dragRobot!==id){event.preventDefault();tr.dataset.drop='true'}};
      tr.ondragleave=()=>{delete tr.dataset.drop};
      tr.ondrop=event=>{if(dragRobot){event.preventDefault();delete tr.dataset.drop;moveRobot(dragRobot,id)}};
      const edit=document.createElement('button');edit.type='button';edit.className='ov-edit';edit.textContent='更名';
      edit.onclick=()=>{
        editing=id;
        const form=document.createElement('form'),input=document.createElement('input');
        input.value=name;input.maxLength=40;input.required=true;input.pattern='[A-Za-z][A-Za-z0-9_]{0,39}';input.title='字母开头，可含英文字母、数字和下划线，最多40字符';input.setAttribute('aria-label','车辆调度名称');
        const save=edit.cloneNode();save.type='submit';save.textContent='保存';
        const cancel=edit.cloneNode();cancel.textContent='取消';cancel.onclick=()=>{editing=undefined;void refresh()};
        form.append(input,save,cancel);cell.replaceChildren(form);input.focus();input.select();
        form.onsubmit=event=>{event.preventDefault();editing=undefined;void submit('robot_rename',{robot_id:robotId(id),name:input.value.trim()})};
      };
      const card=document.createElement('div');card.className='ov-robot-card';card.tabIndex=0;card.title='双击打开 '+name+' 的单车控制';card.setAttribute('aria-label',card.title);card.dataset.robot=id;
      const openRobot=()=>{
        const host=state?.discovery?.fresh&&state.discovery.control_hosts?.[id];
        if(typeof host!=='string'||!/^\d{1,3}(?:\.\d{1,3}){3}$/.test(host)){
          result.textContent='暂未找到 '+name+' 的单车控制地址';return;
        }
        const localVehicle=id===state.dispatcher_id;
        if(localVehicle&&window.OmniFleetFleetWebSocket){
          location.assign('/single/');
        }else{
          window.open('http://'+host+(localVehicle?'/single/':'/'),'_blank','noopener');
        }
      };
      card.ondblclick=event=>{if(!event.target.closest('button'))openRobot()};
      card.onkeydown=event=>{if(event.target===card&&event.key==='Enter')openRobot()};
      card.append(handle,document.createTextNode(name),edit);cell.append(card);
      tr.lastChild.className=robot?.online&&nav.local_ready?'ov-good':'ov-warning';body.append(tr);
    }
    function showPage(page){
      cards.hidden=page==='tasks';if(controls)controls.hidden=page!=='tasks';
      root.querySelectorAll('[data-page]').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.page===page)));
      if(page==='tasks'&&!cleanupControls)cleanupControls=initDispatchControls({...context,panelElement:controls.querySelector('.ov-task-panel')});
      if(page==='overview'&&controls)controls.querySelector('details').open=false;
    }
    root.querySelectorAll('[data-page]').forEach(button=>button.onclick=()=>showPage(button.dataset.page));
    async function refresh(){
      if(disposed||busy)return;busy=true;
      try{
        const response=await fleetFetch('/state',{signal:AbortSignal.timeout(5000)});if(!response.ok)throw Error('HTTP '+response.status);
        state=await response.json();if(disposed)return;
        const name=id=>displayName(id);
        const receipt=state.commands?.[requestId];
        if(receipt){result.textContent=receipt.message||(receipt.phase==='renamed'?'名称已保存':'调度操作已更新');requestId=undefined}
        const peerTasks=state.missions?.peer_tasks||[];peers.hidden=!peerTasks.length;
        const peerRows=peers.querySelector('tbody');peerRows.replaceChildren();
        for(const task of peerTasks)peerRows.append(row([task.title||task.source_task_id,name(task.dispatcher),name(task.robot_id)||'—',task.phase||'—']));
        const body=root.querySelector('[data-rows='+ (mutexOnly?'mutex':'robots')+']');
        if(editing||dragRobot)return;
        const focused=body.contains(document.activeElement)&&document.activeElement.dataset.robot?
          '.'+document.activeElement.classList[0]+'[data-robot="'+CSS.escape(document.activeElement.dataset.robot)+'"]':undefined;
        const zones=state.missions?.traffic?.zones||[];
        const detected=discoveredRobots(state),order=state.missions?.traffic?.order||[];
        visibleOrder=[...new Set([...order.filter(id=>detected.includes(id)),...detected])];
        const formation=state.missions?.formation,saved=formation?.saved;
        if(formationForm){
          if(!loadedShape){
            loadedShape=true;
            formationForm.elements.shape.value=saved?.shape||'current';
            if(saved?.spacing)formationForm.elements.spacing.value=saved.spacing;
            formationForm.elements.shape.onchange();
          }
          root.querySelector('.ov-saved').textContent=saved
            ?'已保存 '+(shapeNames[saved.shape]||shapeNames.current)+' · '+saved.order.map(name).join(' → ')
            :visibleOrder.length<2?'至少需要两辆车保存队形':'当前顺序 · '+visibleOrder.map(name).join(' → ');
          formationForm.querySelector('button').disabled=visibleOrder.length<2;
        }
        body.replaceChildren();
        let count=0;
        if(mutexOnly){
          for(const zone of zones){
            body.append(row([zone.name||zone.id,zone.owner?name(zone.owner):'—',(zone.queue||[]).map(name).join('、')||'—']));count++;
          }
        }else{
          visibleOrder.forEach((id,index)=>renderVehicle(body,id,index));count=visibleOrder.length;
          const squads=root.querySelector('[data-rows=squads]');squads.replaceChildren();
          if(saved){
            squads.append(row([saved.name||'当前编队',name(saved.leader||saved.order[0]),saved.order.map(name).join(' → '),shapeNames[saved.shape]||shapeNames.current,formation.active?'编队中':'已保存']));
          }else placeholder(squads,'暂无已保存的编队小队',5);
          root.querySelector('[data-count=squads]').textContent=saved?'共 1 支':'共 0 支';
          const regions=root.querySelector('[data-rows=regions]');regions.replaceChildren();
          for(const zone of zones)regions.append(row([zone.name||zone.id,zone.width+' m',zone.owner?name(zone.owner):'—']));
          if(!zones.length)placeholder(regions,'暂无已命名区域',3);
          root.querySelector('[data-count=regions]').textContent='共 '+zones.length+' 条';
        }
        if(!count){const tr=row([mutexOnly?'暂无互斥组数据':'等待局域网车辆广播']);tr.firstChild.colSpan=mutexOnly?3:7;tr.firstChild.className='ov-empty';body.append(tr)}
        if(focused)body.querySelector(focused)?.focus({preventScroll:true});
        root.querySelector('[data-count='+ (mutexOnly?'mutex':'robots')+']').textContent='共 '+count+' 条';
        health.textContent=state.dispatcher_id?'● 车载调度在线 · '+state.dispatcher_id:'● 本机调度在线';
      }catch(error){if(!disposed)health.textContent='连接异常 · '+error.message}
      finally{busy=false}
    }
    bindPanelTheme(context,root);
    const timer=setInterval(refresh,1500);void refresh();
    return()=>{disposed=true;clearInterval(timer);cleanupControls?.();cleanupFormation?.();root.remove()};
  }
  function initWslControls(context) {
    const root=document.createElement('div');context.panelElement.append(root);
    root.style.cssText='height:100%;overflow:auto;box-sizing:border-box;padding:14px;background:var(--fm-bg);color:var(--fm-text);font:15px sans-serif';
    root.innerHTML=`<style>.fm-card{background:var(--fm-surface);border:1px solid var(--fm-border);border-radius:9px;padding:12px;margin:12px 0}.fm-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.fm-card input,.fm-card select,.fm-card textarea{font:inherit;padding:7px;box-sizing:border-box}.fm-card textarea{width:100%;margin:8px 0}.fm-card small{color:var(--fm-muted);line-height:1.6}.fm-row button,.fm-card button{font:inherit;padding:8px;border:0;border-radius:5px;background:var(--fm-primary);color:var(--fm-on-primary);cursor:pointer}.fm-card button:disabled{opacity:.45;cursor:default}.fm-stop{background:var(--fm-danger)!important}.fm-status{white-space:pre-wrap;line-height:1.65}.fm-tabs{display:flex;gap:8px}.fm-tabs button{flex:1;background:var(--fm-tint);color:var(--fm-text)}.fm-tabs button[aria-selected=true]{background:var(--fm-primary);color:var(--fm-on-primary)}</style>
      <h2 style="margin:0">多车协同</h2>
      <div class="fm-card fm-tabs"><button data-ui="dispatchView" aria-selected="true">调度控制</button><button data-ui="parametersView" aria-selected="false">永久导航参数</button></div><p class="fm-status" data-ui="activeTarget" aria-live="polite"></p><section data-ui="dispatchPage">
      <div class="fm-card" data-ui="formationCard"><b>当前位置编队</b><p><small>点击“开始编队”自动记录各车当前位置和朝向，并启用编队。目标发给全队中心，所有成员共同规划和起步；允许个别车临时绕障，随后回到自己的位置。各车朝向可随可行轨迹调整，最终恢复保存的相对朝向。</small></p><div class="fm-row"><button data-ui="formationStart">开始编队</button><button data-ui="formationStop" class="fm-stop">停止编队</button></div><p class="fm-status" data-ui="formationState">尚未开始编队</p><b>队形中心多点导航</b><p><small>在共享地图添加多点航点，下方按顺序列出坐标和朝向。可调整顺序、删除后保存；点击执行后全队出发。</small></p><div data-ui="formationRoute" aria-label="队形中心航点列表"></div><div class="fm-row"><button data-ui="formationSave">保存队形航点</button><button data-ui="formationExecute">规划并执行队形航点</button><button data-ui="formationClear">清除队形航点</button></div><p data-ui="formationRouteState"></p></div>
      <div class="fm-card"><b data-ui="health">正在连接 WSL 调度端…</b><p data-ui="permission"></p><p data-ui="discoveryState" role="status"></p><b>调度 ID / ROS 前缀与跟随顺序</b><p><small>输入实际前缀后点击应用或按回车。仅支持英文字母开头，后续可含数字和下划线。拖动手柄排序，第一辆为领车。</small></p><ol class="fm-vehicles" data-ui="order" aria-label="领车及跟随车辆顺序"></ol><small data-ui="orderNote"></small><button data-ui="align" style="margin-top:10px">手动重新配准地图</button><details style="margin-top:10px"><summary>共享地图与同伴占用</summary><p data-ui="maps"></p><p><small>参与车辆静止、就绪后会自动配准新定位会话。离线车辆的最后位置继续作为避让障碍。</small></p></details></div>

      <div class="fm-card"><small data-ui="mapTarget"></small><div class="fm-row" style="margin-top:8px"><button data-ui="clearTarget" class="fm-stop">清除本车航点</button><button data-ui="clearAll" class="fm-stop">清除全部航点</button></div><small>清除正在执行的航点会同时停止对应导航。</small></div><div class="fm-card fm-tabs"><button data-ui="followTab" aria-selected="true">跟随领车</button><button data-ui="routeTab" aria-selected="false">编队</button><button data-ui="dispatchTab" aria-selected="false">调度</button></div>
      <section data-ui="followPage"><div class="fm-card"><b>实时前车跟随</b><p><small>进入本页自动开启调度许可。按上方列表顺序：第2车跟第1车，第3车跟第2车，以此类推。</small></p><div class="fm-row"><label>跟车距离 <input data-ui="distance" type="number" min="0" step="any" value="1" style="width:80px"> m</label></div><p><small>每车按与前车的实时相对位置和速度保持指定距离，由本车导航规划避障路线，不必复走前车历史轨迹。间距以两车定位中心计算。队列车辆掉线时停止跟随；恢复后需重新开始。本页单点航点发给领车并立即执行；多点先布置再点击“规划并执行”；开始跟随用于启动跟随车。</small></p><div class="fm-row"><button data-ui="followStart">开始跟随</button><button data-ui="followStop" class="fm-stop">停止跟随</button></div><p data-ui="followHint" role="status"></p><p class="fm-status" data-ui="followState">跟随尚未启动</p></div></section>
      <section data-ui="routePage" hidden></section><section data-ui="goalDispatchPage" hidden><div class="fm-card"><b>目标点调度（实验性）</b><p><label>派车方式 <select data-ui="dispatchMode"><option value="nearest">最近车辆前往</option><option value="all">全部车辆到达后返回，依次前往</option></select></label></p><small>在共享地图发布单点位姿即派车。最近车辆从在线空闲且导航就绪的车辆中选择；路权先按距目标的直线距离，再按车辆列表顺序；已放行车辆不抢占。全部车辆模式纳入当前在线、地图有效且已开启调度许可的车辆：每辆到达后返回本次出发位置，确认返回后再放行下一辆。</small><p><b>目标航点</b></p><div data-ui="dispatchPoint" aria-label="调度目标航点列表"></div><p><small>地图发布的调度目标会显示在此；点击列表选中，发送按钮可再次下发该目标。</small></p><div class="fm-row"><button data-ui="dispatchSend">发送调度目标</button><button data-ui="dispatchStop" class="fm-stop">停止调度</button></div><p class="fm-status" data-ui="goalDispatchState">尚无调度目标</p><small data-ui="dispatchQueue"></small></div></section><section data-ui="navigationPage"><div class="fm-card"><b>选中车辆多点导航</b><p><small>点击车辆卡片或下拉框选择车辆，编辑并保存该车航点，再规划执行。跟随运行时，航点属于领车。编队使用上方独立的“队形中心多点导航”。</small></p><div class="fm-row"><button data-ui="routesStart">规划并执行所选车辆多点导航</button><button data-ui="routesStop" class="fm-stop">停止所选车辆导航</button></div></div><div class="fm-card"><b>多点路线编辑</b><p><label>车辆 <select data-ui="robot" aria-label="航点所属车辆"></select></label></p><small>坐标属于所选车辆自己的 map。地图添加多点后，航点按顺序列在下方；可选中、调整顺序或删除，再保存。沿用本车永久导航参数及逐点／连续策略。多点先部署，点击“规划并执行”后发车；发布单点位姿仍立即执行。删除全部航点并保存可取消本车安排。</small><div data-ui="route" aria-label="本车多点导航航点列表"></div><div class="fm-row"><button data-ui="import">导入车端现有航点</button><button data-ui="append">追加本车当前位置</button><button data-ui="save">保存航点</button></div><p data-ui="saved"></p><div class="fm-row"><button data-ui="prepare">预检已保存航点（不发车）</button></div><small>同伴占用进入各车 Nav2；交叉路径由 WSL 先后放行。路线受阻时等待，导航执行失败则停止队列，不反复重发失败目标。</small></div></section>
      </section><section data-ui="parametersPage" hidden><details class="fm-card" open><summary><b>远离障碍与碰撞模型 · 单车永久参数</b></summary><p><label>参数与膨胀层所属车辆 <select data-ui="parameterRobot" aria-label="永久导航参数所属车辆"></select></label></p><div class="fm-row"><label><input type="checkbox" data-ui="globalCostmap" checked> 全局膨胀层</label><label><input type="checkbox" data-ui="localCostmap"> 局部膨胀层</label><button data-ui="parameterRead">读取本车</button></div><small data-ui="costmapStatus"></small><div data-ui="parameterFields"></div><p><label>导航碰撞模型 <select data-ui="collisionModel" aria-label="导航碰撞模型"><option value="point">近似点模型（半径 1 cm）</option><option value="body">实际车体模型</option><option value="custom" disabled>自定义模型（详细参数）</option></select></label></p><div class="fm-row"><button data-ui="parameterSave">保存修改到本车</button><button data-ui="parameterSync">将当前参数同步到全部车辆</button></div><p><small>与单车“永久导航参数”共用保存服务。全局和局部共用轮廓、半径、余量、膨胀范围与衰减。膨胀范围与衰减停车后可即时应用；车体几何、完整车体检查和模型切换保存后需重启导航栈。切换模型预设请单独保存。</small></p><p class="fm-status" data-ui="parameterStatus">等待读取各车永久参数…</p></details></section>
      <div class="fm-card"><b>操作回执</b><p class="fm-status" data-ui="result">尚无操作</p></div>`;
    const ui={};root.querySelectorAll('[data-ui]').forEach(e=>ui[e.dataset.ui]=e);
    ui.routePage.append(ui.formationCard);
    const listStyle=document.createElement('style');
    listStyle.textContent='.fm-waypoints{list-style:none;padding:0;margin:10px 0;max-height:320px;overflow:auto}.fm-waypoint{display:flex;align-items:center;gap:6px;border:1px solid var(--fm-border);border-radius:6px;margin:6px 0;padding:5px}.fm-waypoint[data-selected=true]{border-color:var(--fm-primary);background:var(--fm-tint)}.fm-card .fm-waypoint-select{display:flex;gap:10px;align-items:center;flex:1;min-width:0;text-align:left;background:transparent;color:var(--fm-text)}.fm-waypoint-number{display:grid;place-items:center;min-width:26px;height:26px;border-radius:50%;background:var(--fm-tint);color:var(--fm-primary)}.fm-waypoint-detail{min-width:0}.fm-waypoint-detail small{display:block;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}.fm-waypoint-actions{display:flex;gap:4px;flex-shrink:0}.fm-card .fm-waypoint-actions button{font-size:12px;padding:6px;background:var(--fm-tint);color:var(--fm-text)}.fm-waypoint-empty{padding:20px 10px;text-align:center;color:var(--fm-muted);border:1px dashed var(--fm-border);border-radius:6px}';
    root.append(listStyle);
    waypointList(ui.route,true,'尚无航点，请在地图添加多点航点，或导入车端航点。');
    waypointList(ui.formationRoute,true,'尚无队形航点，请在共享地图添加多点航点。');
    waypointList(ui.dispatchPoint,false,'尚无目标，请在共享地图发布调度目标。');
    ui.registrationStatus=document.createElement('p');ui.registrationStatus.dataset.ui='registrationStatus';ui.registrationStatus.className='fm-status';ui.registrationStatus.setAttribute('role','status');ui.registrationStatus.setAttribute('aria-live','polite');ui.align.after(ui.registrationStatus);
    ui.mapTarget.setAttribute('role','status');ui.mapTarget.setAttribute('aria-live','polite');
    const panelState={...context.initialState};
    const savePanelState=change=>{Object.assign(panelState,change);context.saveState?.({...panelState})};
    if(!panelState.foxglovePanelTitle||['跟随领车 / 各车航点导航','跟随领车 / 编队'].includes(panelState.foxglovePanelTitle))savePanelState({foxglovePanelTitle:'跟随领车 / 编队 / 调度'});
    function parameterView(show,persist=false){
      ui.dispatchPage.hidden=show;ui.parametersPage.hidden=!show;
      ui.dispatchView.setAttribute('aria-selected',String(!show));ui.parametersView.setAttribute('aria-selected',String(show));
      if(persist)savePanelState({parameterPage:show});
      if(persist)syncControls();
    }
    ui.dispatchView.onclick=()=>parameterView(false,true);ui.parametersView.onclick=()=>parameterView(true,true);
    parameterView(context.initialState?.parameterPage===true);
    if(['routes','formation'].includes(panelState.navigationMode)){
      ui.followPage.hidden=true;ui.routePage.hidden=false;ui.followTab.setAttribute('aria-selected','false');ui.routeTab.setAttribute('aria-selected','true');
    }

    const style=document.createElement('style');style.textContent='.fm-vehicles{list-style:none;padding:0;margin:0}.fm-vehicle{display:flex;gap:8px;align-items:center;border:1px solid var(--fm-border);border-radius:7px;padding:9px;margin:8px 0}.fm-vehicle.dragging{opacity:.45}.fm-vehicle-body{min-width:0;flex:1}.fm-vehicle-body input{width:100%;min-width:0}.fm-vehicle-body small{display:block;margin-top:5px}.fm-drag{background:transparent!important;color:var(--fm-muted)!important;padding:8px 4px!important;cursor:grab!important;touch-action:none;user-select:none;font-size:23px!important}.fm-prefix-row{flex-wrap:nowrap}.fm-prefix-row input{flex:1;width:0}.fm-prefix-save{white-space:nowrap;font-size:12px!important;padding:7px!important}.fm-prefix-feedback{color:var(--fm-primary)!important}.fm-drag:active{cursor:grabbing!important}.fm-role{font-size:12px;color:var(--fm-primary);white-space:nowrap}';root.append(style);
    style.textContent+='.fm-vehicle{background:var(--fm-surface);transition:transform 180ms cubic-bezier(.2,.8,.2,1)}.fm-vehicle.dragging{opacity:.2;border:1px dashed var(--fm-primary);background:var(--fm-tint)}.fm-drag-ghost{position:fixed;box-sizing:border-box;margin:0;pointer-events:none;z-index:100000;color:var(--fm-text);font:15px sans-serif;box-shadow:0 12px 30px #00000040;border-color:var(--fm-primary);will-change:transform}.fm-drag-ghost input{font:inherit;padding:7px;box-sizing:border-box}.fm-drag-ghost small{color:var(--fm-muted);line-height:1.6}html.fm-sorting,html.fm-sorting *{cursor:grabbing!important;user-select:none!important}@media(prefers-reduced-motion:reduce){.fm-vehicle{transition:none}}';
    style.textContent+='.fm-vehicle{cursor:pointer}.fm-vehicle[data-control-selected=true]{border-color:var(--fm-primary);box-shadow:inset 0 0 0 1px var(--fm-primary);background:var(--fm-tint)}';
    const preferencesKey='omnifleet.fleet.preferences';let preferences;
    try{preferences=JSON.parse(localStorage.getItem(preferencesKey)||'{}')}catch{preferences={}}
    const prefixDrafts=new Map(),pendingPrefixes=new Map(),prefixErrors=new Map();
    let permitFollowOnRefresh=true,permissionPending=false;const permissionRequests=new Set();
    let order=Array.isArray(preferences?.order)?preferences.order.filter(r=>typeof r==='string'):[],dragRobot,pendingOrder;
    const drafts=new Map(),dirty=new Set(),pendingSaves=new Map(),pendingClears=new Map();let fleetUpdatedAt=0;let state,disposed=false,working=false,selected=panelState.selectedRobot,requestId,requestOperation,settingsLoaded=false;
    let controlledRobot=panelState.controlledRobot;
    const robotLabel=r=>state?.assignments?.[r]?.robot_name||r;
    const mapReason=r=>robotMessage(state,state.maps?.validation_reasons?.[r])||'等待当前地图会话配准';
    let parameterRobot,parameterBusy=false,parameterInitialized=false;
    const parameterDrafts=new Map(),parameterReceipts=new Map(),parameterInputs=new Map();
    const scalar=value=>value&&typeof value==='object'?Object.values(value)[0]:value;
    const parameterSnapshot=robot=>state?.robots?.[robot]?.samples?.navigation_parameters?.value;
    function parameterDraft(robot){if(!parameterDrafts.has(robot))parameterDrafts.set(robot,{});return parameterDrafts.get(robot)}
    function renderParameters(){
      const robots=discoveredRobots(state),fields=state?.navigation_parameter_fields||[];
      if(!robots.includes(parameterRobot))parameterRobot=selected||order[0]||robots[0];
      if([...ui.parameterRobot.options].map(o=>o.value).join(',')!==robots.join(','))ui.parameterRobot.replaceChildren(...robots.map(r=>new Option(robotLabel(r),r)));
      for(const option of ui.parameterRobot.options)option.textContent=robotLabel(option.value);
      ui.parameterRobot.value=parameterRobot||'';
      ui.parameterRobot.disabled=parameterBusy;
      if(parameterInputs.size!==fields.length){
        parameterInputs.clear();ui.parameterFields.replaceChildren();
        for(const field of fields){
          const row=document.createElement('label');row.style.cssText='display:flex;gap:8px;align-items:center;justify-content:space-between;margin:10px 0';
          const label=document.createElement('span');label.textContent=field.label+(field.unit?'（'+field.unit+'）':'');
          const input=document.createElement('input');input.dataset.parameter=field.id;input.setAttribute('aria-label',field.label);
          input.type=field.type==='bool'?'checkbox':field.type==='string'?'text':'number';input.style.cssText='max-width:48%;min-width:0';
          if(field.type==='double'){input.min=field.min;input.max=field.max;input.step=field.step}
          input.oninput=()=>{parameterDraft(parameterRobot)[field.id]=field.type==='bool'?input.checked:field.type==='string'?input.value:Number(input.value);renderParameters()};
          for(const event of ['keydown','keyup','pointerdown'])input.addEventListener(event,e=>e.stopPropagation());
          row.append(label,input);ui.parameterFields.append(row);parameterInputs.set(field.id,input);
        }
      }
      const snapshot=parameterSnapshot(parameterRobot),draft=parameterDraft(parameterRobot),saved=snapshot?.saved;
      for(const [key,input] of parameterInputs){
        const value=key in draft?draft[key]:scalar(saved?.[key]);
        if(input.type==='checkbox')input.checked=Boolean(value);
        else if(document.activeElement!==input)input.value=value===undefined?'':String(value);
        input.disabled=parameterBusy||!saved;input.title='永久参数键：'+key;
      }
      ui.collisionModel.value=draft.__collision_model||snapshot?.collision_model?.mode||'custom';
      ui.collisionModel.disabled=parameterBusy||!snapshot?.collision_model;
      ui.collisionModel.querySelector('[value="body"]').disabled=!snapshot?.collision_model?.restore_available&&snapshot?.collision_model?.mode!=='body';
      ui.parameterRead.disabled=parameterBusy||!parameterRobot;
      ui.parameterSave.disabled=parameterBusy||!saved||!Object.keys(draft).length;
      ui.parameterSync.disabled=parameterBusy||!saved;
      const cells=state?.robots?.[parameterRobot]?.samples||{};
      ui.costmapStatus.textContent=robotLabel(parameterRobot)+'：'+['global_costmap','local_costmap'].map(key=>{
        const sample=cells[key];return (key==='global_costmap'?'全局':'局部')+(sample?'已收到，'+sample.age_seconds.toFixed(1)+' 秒前':'等待代价地图');
      }).join('；');
      ui.parameterStatus.textContent=(parameterBusy?'正在读取或保存，请等待车端回执…\n':'')+robots.map(r=>{
        const p=parameterSnapshot(r),receipt=parameterReceipts.get(r);return robotLabel(r)+'：'+(receipt||(!p?'未读取':p.phase==='failed'||p.phase==='rejected'?p.message:'已读取本车永久配置'));
      }).join('\n');
      if(saved){
        const mismatches=['footprint','robot_radius','footprint_padding','inflation_radius'].filter(key=>JSON.stringify(scalar(saved['geometry_local_'+key]))!==JSON.stringify(scalar(saved['geometry_global_'+key])));
        if(mismatches.length)ui.parameterStatus.textContent+='\n当前全局与局部值不同：'+mismatches.join('、')+'；保存对应项时同步两张代价地图。';
      }
      if(!parameterInitialized&&robots.length&&fields.length){parameterInitialized=true;void parameterOperation(true,false,robots)}
    }
    async function parameterRequest(robot,op,changes){
      const id='params-'+Date.now()+'-'+Math.random().toString(16).slice(2),revision=state.identity_revision;
      const response=await fleetFetch('/command',{method:'POST',headers:{'Content-Type':'application/json','X-OmniFleet-Token':state.token},body:JSON.stringify({op,id,robot_id:robotLabel(robot),identity_revision:revision,...(changes?{changes}:{})})});
      if(!response.ok)throw Error('调度端拒绝参数请求（'+response.status+'）');
      const deadline=Date.now()+55000;
      while(!disposed&&Date.now()<deadline){
        await new Promise(resolve=>setTimeout(resolve,250));
        const reply=await fleetFetch('/state',{cache:'no-store'});if(!reply.ok)throw Error('等待参数回执时连接中断');
        const current=await reply.json(),receipt=current.commands?.[id];
        if(receipt&&receipt.phase!=='forwarding'){
          if(['rejected','failed'].includes(receipt.phase))throw Error(receipt.message||'保存失败');
          return receipt;
        }
      }
      throw Error('保存或读取结果未确认，请重新读取');
    }
    async function parameterOperation(read,all,targets){
      if(parameterBusy||!state)return;
      const source=parameterRobot,draft={...parameterDraft(source)},saved=parameterSnapshot(source)?.saved;
      let changes;
      try{
        if(!read){
          if('__collision_model' in draft){if(Object.keys(draft).length!==1)throw Error('碰撞模型预设需单独保存，请先保存详细参数或重新读取');changes=draft}
          else changes=all?Object.fromEntries((state.navigation_parameter_fields||[]).map(f=>[f.id,f.id in draft?draft[f.id]:scalar(saved?.[f.id])])):draft;
          for(const [key,value] of Object.entries(changes)){
            const input=parameterInputs.get(key);if(input?.type==='number'&&(!input.value.trim()||!input.checkValidity()||!Number.isFinite(value)))throw Error('请输入有效数值：'+input.getAttribute('aria-label'));
          }
        }
        parameterBusy=true;renderParameters();
        for(const robot of targets||(all?discoveredRobots(state):[source])){
          try{
            const receipt=await parameterRequest(robot,read?'nav_parameters_read':'nav_parameters_save',changes);
            parameterReceipts.set(robot,read?'已读取永久参数':receipt.runtime_confirmed?'永久保存成功，已应用并回读确认':'永久保存成功；'+(Object.values(receipt.runtime||{}).join('；')||receipt.message||'需要重启导航栈生效'));
            if(!read)parameterDrafts.delete(robot);
          }catch(error){parameterReceipts.set(robot,error.message)}
        }
      }catch(error){parameterReceipts.set(source,error.message)}
      finally{parameterBusy=false;await refresh()}
    }
    ui.parameterRobot.onchange=()=>{parameterRobot=ui.parameterRobot.value;renderParameters();syncControls();void parameterOperation(true,false)};
    ui.parameterRead.onclick=()=>{parameterDrafts.delete(parameterRobot);void parameterOperation(true,false)};
    ui.parameterSave.onclick=()=>void parameterOperation(false,false);
    ui.parameterSync.onclick=()=>void parameterOperation(false,true);
    ui.collisionModel.onchange=()=>{parameterDraft(parameterRobot).__collision_model=ui.collisionModel.value;renderParameters()};
    ui.globalCostmap.onchange=ui.localCostmap.onchange=()=>syncControls();
    function savePreferences(){
      try{localStorage.setItem(preferencesKey,JSON.stringify({order}))}catch{ui.result.textContent='车辆顺序未能保存，请重试'}
      pendingOrder={revision:state.missions.traffic?.order_revision||0,sent:Date.now()};
      const savedOrder=state.missions.traffic?.order||Object.keys(state.assignments);
      void command('dispatch_order',{order:[...order,...savedOrder.filter(r=>!order.includes(r))],order_revision:pendingOrder.revision}).then(id=>{if(pendingOrder){if(id)pendingOrder.id=id;else pendingOrder=undefined}});
    }
    function renderPrefixState(row,robot){
      const pending=[...pendingPrefixes.values()].some(p=>p.robot===robot);
      row.querySelector('.fm-prefix-save').disabled=working||pending||!prefixDrafts.has(robot)||state?.identity_revision===undefined;
      row.querySelector('.fm-prefix-feedback').textContent=prefixErrors.get(robot)||(pending?'前缀应用中…':prefixDrafts.has(robot)?'前缀尚未应用':'当前话题：'+(state?.assignments?.[robot]?.namespace||'')+'/map');
    }
    function moveRobot(robot,index){
      if(working||pendingOrder||!state||Date.now()-fleetUpdatedAt>1500||state.missions?.follow?.active||state.missions?.formation?.active)return;
      const from=order.indexOf(robot);if(from<0||index<0||index>=order.length||from===index)return;
      order.splice(from,1);order.splice(index,0,robot);savePreferences();renderVehicles(state.missions?.follow||{});renderFollowState(state.missions?.follow||{});syncControls();
    }
    let landingTimer,landingGhost,landingRow;
    const reducedMotion=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
    function clearLanding(){clearTimeout(landingTimer);landingGhost?.remove();landingRow?.classList.remove('dragging');landingGhost=landingRow=undefined}
    function startDrag(event,robot,row,handle){
      if(event.button!==0||dragRobot||state?.missions?.follow?.active||state?.missions?.formation?.active)return;
      event.preventDefault();clearLanding();
      const rows=[...ui.order.children],rects=new Map(rows.map(e=>[e.dataset.robot,e.getBoundingClientRect()])),rect=rects.get(robot);
      const ghost=row.cloneNode(true);ghost.className='fm-vehicle fm-drag-ghost fm-themed-panel';ghost.dataset.colorScheme=root.dataset.colorScheme||'light';ghost.setAttribute('aria-hidden','true');ghost.setAttribute('inert','');
      ghost.style.cssText='left:'+rect.left+'px;top:'+rect.top+'px;width:'+rect.width+'px;transform:scale('+(reducedMotion()?1:1.02)+')';
      document.body.append(ghost);row.classList.add('dragging');document.documentElement.classList.add('fm-sorting');
      dragRobot={robot,row,handle,ghost,rect,rects,rows,pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,offsetY:event.clientY-rect.top,index:order.indexOf(robot)};
      handle.setAttribute('aria-grabbed','true');handle.setPointerCapture?.(event.pointerId);
    }
    function dragMove(event){
      const drag=dragRobot;if(!drag||event.pointerId!==drag.pointerId)return;
      event.preventDefault();
      drag.ghost.style.transform='translate3d('+(event.clientX-drag.startX)+'px,'+(event.clientY-drag.startY)+'px,0) scale('+(reducedMotion()?1:1.02)+')';
      const center=event.clientY-drag.offsetY+drag.rect.height/2;
      const rest=order.filter(r=>r!==drag.robot),index=rest.filter(r=>center>drag.rects.get(r).top+drag.rects.get(r).height/2).length;
      if(index===drag.index)return;drag.index=index;
      const preview=[...rest];preview.splice(index,0,drag.robot);
      const first=drag.rects.get(order[0]),gap=order.length>1?drag.rects.get(order[1]).top-first.bottom:0;
      let top=first.top;
      for(const robot of preview){const rect=drag.rects.get(robot),row=drag.rows.find(e=>e.dataset.robot===robot);row.style.transform='translate3d(0,'+(top-rect.top)+'px,0)';top+=rect.height+gap}
    }
    function finishDrag(cancel=false){
      const drag=dragRobot;if(!drag)return;dragRobot=undefined;
      document.documentElement.classList.remove('fm-sorting');drag.handle.setAttribute('aria-grabbed','false');
      if(drag.handle.hasPointerCapture?.(drag.pointerId))drag.handle.releasePointerCapture(drag.pointerId);
      for(const row of drag.rows){row.style.transform='';row.classList.remove('dragging')}
      if(!cancel)moveRobot(drag.robot,drag.index);
      const row=[...ui.order.children].find(e=>e.dataset.robot===drag.robot),rect=cancel?drag.rect:row?.getBoundingClientRect()||drag.rect;
      const duration=disposed||reducedMotion()?0:180;
      drag.ghost.style.transition='transform '+duration+'ms cubic-bezier(.2,.8,.2,1),box-shadow '+duration+'ms ease';
      drag.ghost.style.transform='translate3d('+(rect.left-drag.rect.left)+'px,'+(rect.top-drag.rect.top)+'px,0) scale(1)';drag.ghost.style.boxShadow='none';
      row?.classList.add('dragging');landingGhost=drag.ghost;landingRow=row;landingTimer=setTimeout(clearLanding,duration);
    }
    function dragEnd(event){
      if(!dragRobot||event.pointerId!==dragRobot.pointerId)return;
      const rect=ui.order.getBoundingClientRect();
      finishDrag(event.type==='pointercancel'||event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom);
    }
    const cancelDrag=()=>finishDrag(true);
    const dragKey=event=>{if(event.key==='Escape'&&dragRobot){event.preventDefault();finishDrag(true)}};
    window.addEventListener('pointermove',dragMove,{passive:false});window.addEventListener('pointerup',dragEnd);window.addEventListener('pointercancel',dragEnd);window.addEventListener('keydown',dragKey);window.addEventListener('blur',cancelDrag);
    function renderVehicles(follow){
      if(dragRobot&&(follow.active||!order.includes(dragRobot.robot)))finishDrag(true);
      if([...ui.order.children].map(e=>e.dataset.robot).join(',')!==order.join(',')){
        if(dragRobot)finishDrag(true);
        ui.order.replaceChildren(...order.map(robot=>{
          const row=document.createElement('li');row.className='fm-vehicle';row.dataset.robot=robot;
          row.tabIndex=0;
          const selectControl=()=>{controlledRobot=robot;const routeRobot=state.missions?.formation?.active?state.missions.formation.saved.leader:state.missions?.follow?.active?state.missions.follow.leader:robot;ui.robot.value=routeRobot;showRobot(routeRobot);savePanelState({controlledRobot:robot,selectedRobot:routeRobot});syncControls()};
          row.onclick=event=>{if(!event.target.closest('input,button,select,textarea,a'))selectControl()};
          row.onkeydown=event=>{if(event.target===row&&(event.key==='Enter'||event.key===' ')){event.preventDefault();selectControl()}};
          const handle=document.createElement('button');handle.className='fm-drag';handle.type='button';handle.textContent='⠿';handle.title='拖动排序，也可用上下方向键';
          const role=document.createElement('span');role.className='fm-role';
          const body=document.createElement('div');body.className='fm-vehicle-body';
          const input=document.createElement('input');input.maxLength=40;input.placeholder='请输入调度前缀';
          const save=document.createElement('button');save.className='fm-prefix-save';save.type='button';save.textContent='应用前缀';
          const savePrefix=()=>{
            if([...pendingPrefixes.values()].some(p=>p.robot===robot))return;
            const prefix=input.value.trim();prefixDrafts.set(robot,prefix);input.value=prefix;
            if(!/^[A-Za-z][A-Za-z0-9_]{0,39}$/.test(prefix)){prefixErrors.set(robot,'前缀仅支持英文字母、数字、下划线，必须以字母开头');renderPrefixState(row,robot);return}
            prefixErrors.delete(robot);void command('robot_reassign',{connection_id:robot,prefix});
          };
          input.oninput=input.onchange=()=>{prefixErrors.delete(robot);if(input.value===robotLabel(robot))prefixDrafts.delete(robot);else prefixDrafts.set(robot,input.value);renderPrefixState(row,robot)};
          input.onkeydown=e=>{if(e.key==='Enter'&&!e.isComposing){e.preventDefault();savePrefix()}};save.onclick=savePrefix;
          const nameRow=document.createElement('div');nameRow.className='fm-row fm-prefix-row';nameRow.append(input,save);
          const status=document.createElement('small'),feedback=document.createElement('small'),permission=document.createElement('small'),telemetry=document.createElement('small');feedback.className='fm-prefix-feedback';permission.className='fm-execution-state';telemetry.className='fm-telemetry';telemetry.style.cssText='white-space:pre-wrap;font-variant-numeric:tabular-nums';body.append(nameRow,status,feedback,permission,telemetry);row.append(handle,role,body);
          handle.addEventListener('pointerdown',e=>startDrag(e,robot,row,handle));
          handle.addEventListener('lostpointercapture',e=>{if(dragRobot?.handle===handle&&dragRobot.pointerId===e.pointerId)finishDrag(true)});
          handle.onkeydown=e=>{if(dragRobot)return;if(e.key==='ArrowUp'||e.key==='ArrowDown'){e.preventDefault();moveRobot(robot,order.indexOf(robot)+(e.key==='ArrowUp'?-1:1));ui.order.querySelector('[data-robot="'+robot+'"] button')?.focus()}};
          return row;
        }));
      }
      [...ui.order.children].forEach((row,index)=>{
        const robot=row.dataset.robot,s=state.robots?.[robot],n=s?.samples?.navigation?.value||{};
        const input=row.querySelector('input'),value=prefixDrafts.has(robot)?prefixDrafts.get(robot):robotLabel(robot);if(input.value!==value)input.value=value;
        input.setAttribute('aria-label',robotLabel(robot)+' 调度前缀');row.querySelector('.fm-prefix-save').setAttribute('aria-label',robotLabel(robot)+' 应用前缀');
        renderPrefixState(row,robot);
        const requested=state.execution_requested?.[robot]??state.execution_enabled?.[robot];
        row.querySelector('.fm-execution-state').textContent='调度许可：'+(state.execution_enabled?.[robot]?'已开启':requested?'等待接入端同步':'进入跟随领车页自动开启');
        const handle=row.querySelector('button');handle.disabled=!!follow.active;handle.draggable=false;handle.setAttribute('aria-label','拖动 '+robotLabel(robot)+' 排序');
        const formation=state.missions?.formation;
        row.querySelector('.fm-role').textContent=formation?.active?(formation.saved.order.includes(robot)?'编队成员':'未加入当前编队'):index===0?'领车':'跟随 '+robotLabel(order[index-1]);
        row.querySelector('small').textContent=(s?.online?'在线':'离线')+' · '+(n.local_ready?'导航就绪':(n.readiness_reason||'导航未就绪'))+' · '+(state.maps?.valid_robots?.includes(robot)?'地图坐标有效':mapReason(robot))+(state.maps?.held_offline_robots?.includes(robot)?' · 保留最后占用':'');
        const alignmentError=state.registration?.errors?.[robot];if(alignmentError&&!state.maps?.valid_robots?.includes(robot))row.querySelector('small').textContent+=' · 自动配准：'+alignmentError;
        const samples=s?.samples||{},control=samples.control?.value||{},pose=samples.pose?.value,voltage=samples.voltage?.value;
        const fresh=key=>s?.online&&samples[key]&&(s.fresh?.[key]??(Number.isFinite(samples[key].age_seconds)&&samples[key].age_seconds<=3));
        const show=(key,text)=>samples[key]?.value===undefined?'未收到':text+(fresh(key)?'':'（已过期）');
        const number=(value,digits=2)=>Number.isFinite(value)?value.toFixed(digits):'—';
        const mode={MANUAL:'手动',LOCAL:'本车导航',FLEET:'车队调度',ESTOP:'急停'};
        const phases={idle:'空闲',running:'执行中',executing:'执行中',completed:'已完成',stopped:'已停止',failed:'失败',cancelled:'已取消',stopping:'正在停止'};
        const job=currentMissionJob(state,robot),task=job?labels[job.phase]||'等待反馈':state.missions?.follow?.active&&state.missions.follow.leader===robot&&!n.navigation_active?'领车待命':phases[n.phase]||'等待反馈';
        row.querySelector('.fm-telemetry').textContent=[
          '通信：'+(s?.transport_connected?'已连接':'未连接')+' · 电压：'+show('voltage',number(voltage)+' V'),
          '模式：'+show('control',mode[control.control_mode]||'未知')+' · 任务：'+show('navigation',task)+' · 急停：'+show('control',typeof control.estop==='boolean'?(control.estop?'已触发':'未触发'):'未知'),
          '速度：'+show('control',number(control.velocity?.[0])+' m/s · 转速：'+number(control.velocity?.[1])+' rad/s'),
          '本车定位：'+show('pose',pose?'x '+number(pose.x)+'，y '+number(pose.y)+'，'+number(pose.yaw*180/Math.PI,0)+'°（'+(pose.frame_id||'map')+'）':'未收到')+(Number.isFinite(samples.pose?.age_seconds)?' · 更新 '+number(samples.pose.age_seconds,1)+' 秒前':''),
          '调度状态：'+(s?.dispatch_enabled?'可执行':!s?.online?'车辆离线':!state.maps?.valid_robots?.includes(robot)?mapReason(robot):'等待调度许可同步')
        ].join('\n');
      });
      ui.orderNote.textContent=state.missions?.formation?.active?'全体成员跟踪共同的虚拟队形；允许临时绕障后归位。':follow.active?'跟随任务执行中，停止后可调整顺序。':'';
    }
    const labels={RMF_PAUSED:'等待 RMF 交通恢复',SCHEDULED:'等待计划时间',IDLE:'尚未启动',WAIT_TRAIL:'等待实时跟随目标',WAIT_MAP:'等待当前会话配准；保留领车身份',HANDOVER:'正在停止旧任务',FOLLOWING:'跟随中',ARMING:'申请本车控制租约',PLANNING:'车内规划中',BLOCKED:'路线受阻，等待可通行',YIELDING:'让行等待',EXECUTING:'正在导航',STOPPING:'取消目标并确认停稳',CANCEL_UNCONFIRMED:'停止尚未确认，后续目标已锁住',STOPPED:'已停止',COMPLETED:'全部航点已到达',FAILED:'任务失败',INVALIDATED:'地图会话或连接变化，任务已停止',PRECHECKING:'正在检查全部航点',PREPARING:'等待本车准备回执',PREPARED:'多点预检及车端准备通过（未发车）',REJECTED:'车端拒绝',TIMED_OUT:'车端回执超时',accepted:'请求已接受',saved:'航点已保存',cleared:'航点已清除',renamed:'车辆名称已保存',reassigned:'实际调度前缀已生效',registering:'已开始重新配准',execution_configured:'调度许可已保存',rejected:'请求未通过'};
    function renderFollowState(follow){
      const leader=follow.active?follow.leader:order[0];
      const executionBlocked=order.filter(r=>!state.execution_enabled?.[r]);
      const failed=[...permissionRequests].map(id=>state.commands?.[id]).find(r=>r?.phase==='rejected');
      ui.followHint.textContent=permissionPending?'正在自动开启调度许可…':failed?'自动许可未完成：'+robotMessage(state,failed.message):working?'请求正在提交':follow.active?'跟随已启动；停止后可调整领车和顺序':order.length<2?'至少需要两辆车才能开始跟随':executionBlocked.length?'正在同步调度许可：'+executionBlocked.map(robotLabel).join('、')+'。可再次点击“跟随领车”页签重试。':'已自动开启调度许可；点击“开始跟随”下发任务。';
      ui.followStart.title=ui.followHint.textContent;ui.followStop.title=follow.active?'停止当前跟随':'跟随尚未启动';
      ui.followState.textContent=(follow.active?'当前领车：':'已选领车：')+(leader?robotLabel(leader):'未选择')+(follow.active?' · 会话 '+(follow.term||0):'（列表首位）')+'\n'+(labels[follow.phase]||follow.phase||'尚未启动')+(follow.message?'\n'+robotMessage(state,follow.message):'')+Object.entries(state?.missions?.jobs||{}).filter(([,j])=>j.source==='follow'&&j.term===follow.term).map(([r,j])=>'\n'+robotLabel(r)+'：'+(labels[j.phase]||j.phase)+(j.message?' · '+robotMessage(state,j.message):'')).join('');
    }
    const format=points=>(points||[]).map(p=>p.pose.map((v,i)=>Number((i===2?v*180/Math.PI:v).toFixed(4))).join(', ')).join('\n');
    function parse(text){return text.split(/\r?\n/).map(s=>s.trim()).filter(Boolean).map((line,i)=>{const p=line.split(/[,，\s]+/).map(Number);if(p.length!==3||!p.every(Number.isFinite))throw Error('第 '+(i+1)+' 行需要三个数字：x, y, 朝向角度');return{name:'航点'+(i+1),pose:[p[0],p[1],p[2]*Math.PI/180]}})}
    function showRobot(robot){selected=robot;if(!drafts.has(robot))drafts.set(robot,format(state?.missions?.routes?.[robot]?.points));ui.route.value=drafts.get(robot);}
    function edit(text){ui.route.value=text;drafts.set(selected,text);dirty.add(selected);ui.prepare.disabled=ui.routesStart.disabled=true;syncControls();}
    function syncControls(){
      if(!state)return;
      const assignments=Object.fromEntries(discoveredRobots(state).map(r=>[r,state.assignments[r]]));
      if(!order.length){
        window.OmniFleetFleetEditor={state,target:undefined,receivedAt:fleetUpdatedAt,owner:root};
        ui.activeTarget.textContent=ui.mapTarget.textContent='等待车辆广播，当前没有已发现车辆';
        syncMapPrefixes(assignments,undefined,state.identity_revision);
        syncUnalignedViews({...state,assignments});
        return;
      }
      const formation=state.missions?.formation||{};
      const dispatchMode=ui.goalDispatchPage.hidden?null:ui.dispatchMode.value;
      const formationTarget=!dispatchMode&&!!formation.active||(!ui.routePage.hidden&&!!formation.saved);
      const target=formation.active?formation.saved.leader:state.missions?.follow?.active?state.missions.follow.leader:selected||order[0];
      const vehicle=state.robots?.[target],nav=vehicle?.samples?.navigation?.value;
      const mapValid=state.maps?.valid_robots?.includes(target);
      const unavailableMembers=(formation.saved?.order||[]).filter(r=>!state.robots?.[r]?.online||!state.maps?.valid_robots?.includes(r));
      const availability=formationTarget?(unavailableMembers.length?'等待成员连接和地图：'+unavailableMembers.map(robotLabel).join('、'):formation.active?'编队已启动':'队形已保存，尚未启动'):!vehicle?.online?'离线，等待自动重连':!mapValid?'在线，'+mapReason(target):!nav?.local_ready?'在线，'+(nav?.readiness_reason||'等待本车导航就绪'):'在线，导航就绪';
      ui.activeTarget.textContent='地图航点将发送给：'+(formationTarget?'队形中心':robotLabel(target))+'（'+(formationTarget?'全体成员联动':state.missions?.follow?.active?'跟随领车':'所选车辆导航')+'）。'+availability+'。';
      ui.clearTarget.textContent='清除 '+(formationTarget?'队形中心':robotLabel(target))+' 航点';
      ui.clearTarget.disabled=working||!target;ui.clearAll.disabled=working||!order.length;
      ui.mapTarget.textContent='地图选点目标：'+(formationTarget?'队形中心':robotLabel(target))+'。发布位姿：立即执行单点目标；添加多点航点：仅保存，布置完成后点击“规划并执行”。';
      if(dispatchMode){
        ui.activeTarget.textContent=ui.mapTarget.textContent='地图选点目标：'+(dispatchMode==='all'?'全部车辆依次前往':'最近可用车辆前往')+'。共享地图发布单点位姿即调度；先距离、后列表顺序。';
        ui.clearTarget.textContent='停止当前目标调度';
      }
      if(!dispatchMode&&!mapValid)ui.mapTarget.textContent+=' 当前不可执行：'+mapReason(target)+'。';
      window.OmniFleetFleetEditor={state,target,scope:dispatchMode?'dispatch':formationTarget?'formation':'vehicle',receivedAt:fleetUpdatedAt,dirty:formationTarget?formationDirty:dirty.has(target),owner:root};
      const job=state.missions?.jobs?.[target];
      if(job&&['route','single'].includes(job.source))ui.mapTarget.textContent+=' '+robotLabel(target)+'：'+(labels[job.phase]||job.phase)+' '+job.index+'/'+job.points.length+(job.message?' · '+robotMessage(state,job.message):'');
      const costmapTarget=ui.parametersPage.hidden?target:parameterRobot||target;
      const descriptions=Object.fromEntries(Object.entries(state.robots||{}).map(([r,v])=>[r,v.samples?.robot_description?.value]));
      const sessions=Object.fromEntries(Object.entries(state.robots||{}).map(([r,v])=>[r,String(!!v.online)+'|'+(v.samples?.navigation?.value?.localization_epoch||'')]));
      const grouped=formation.active||state.missions?.follow?.active;
      const explicitControl=controlledRobot&&assignments[controlledRobot]?controlledRobot:undefined;
      const controlled=explicitControl||(grouped?formation.active?formation.saved.leader:order[0]:target);
      for(const row of ui.order.children){
        const active=row.dataset.robot===controlled;row.dataset.controlSelected=String(active);
        row.setAttribute('aria-current',String(active));row.setAttribute('aria-label',robotLabel(row.dataset.robot)+(active?'，当前操控车辆':'，点击选择操控'));
      }
      syncMapPrefixes(assignments,target,state.identity_revision,costmapTarget,ui.globalCostmap.checked,ui.localCostmap.checked,descriptions,sessions,ui.parametersPage.hidden,formationTarget,dispatchMode);
      syncUnalignedViews({...state,assignments});
    }
    function tab(mode){
      const follow=mode===true,dispatch=mode==='dispatch';
      ui.followPage.hidden=!follow;ui.routePage.hidden=follow||dispatch;ui.goalDispatchPage.hidden=!dispatch;ui.navigationPage.hidden=dispatch;
      ui.followTab.setAttribute('aria-selected',String(follow));ui.routeTab.setAttribute('aria-selected',String(!follow&&!dispatch));ui.dispatchTab.setAttribute('aria-selected',String(dispatch));
      savePanelState({navigationMode:dispatch?'dispatch':follow?'follow':'formation'});syncControls();
      if(follow||dispatch){permitFollowOnRefresh=true;permissionRequests.clear();void refresh()}
    }
    async function permitFollow(){
      permissionPending=true;
      try{for(const robot of [...order])if(!(state.execution_requested?.[robot]??state.execution_enabled?.[robot])){
        const id=await command('execution_permission',{robot_id:robot,enabled:true});if(id)permissionRequests.add(id);
      }}finally{permissionPending=false;void refresh()}
    }
    async function command(op,extra={}){
      if(!state||working)return;working=true;
      const id='fox-'+Date.now()+'-'+Math.random().toString(16).slice(2);requestId=id;requestOperation=op;
      const clearedRobots=op==='route_clear'&&extra.target!=='formation'?[extra.robot_id]:op==='routes_clear'?discoveredRobots(state):null;
      const savedDraft=op==='route_save'&&extra.target!=='formation'?{robot:extra.robot_id,text:drafts.get(extra.robot_id)}:null;
      const savedPrefix=op==='robot_reassign'?{robot:extra.connection_id,text:extra.prefix,sent:Date.now()}:null;
      try{
        const response=await fleetFetch('/command',{method:'POST',headers:{'Content-Type':'application/json','X-OmniFleet-Token':state.token},body:JSON.stringify({op,id,identity_revision:state.identity_revision,...extra,...(extra.robot_id?{robot_id:robotLabel(extra.robot_id)}:{}),...(extra.order?{order:extra.order.map(robotLabel)}:{})})});
        if(!response.ok)throw Error('调度端拒绝请求（'+response.status+'）');
        if(savedDraft)pendingSaves.set(id,savedDraft);
        if(clearedRobots)pendingClears.set(id,clearedRobots);
        if(savedPrefix)pendingPrefixes.set(id,savedPrefix);
        ui.result.textContent='请求已提交，等待调度回执';
        return id;
      }catch(error){ui.result.textContent=error.message}
      finally{working=false;await refresh()}
    }
    async function refresh(){
      try{
        const response=await fleetFetch('/state',{cache:'no-store'});if(!response.ok)throw Error('调度端未响应');
        state=await response.json();fleetUpdatedAt=Date.now();if(disposed)return;
        const robots=discoveredRobots(state),missions=state.missions||{},follow=missions.follow||{},formation=missions.formation||{};
        for(const [id,saved] of pendingPrefixes){
          const result=state.commands?.[id];if(!result&&Date.now()-saved.sent<10000)continue;
          if(result?.phase==='reassigned'){if(prefixDrafts.get(saved.robot)===saved.text)prefixDrafts.delete(saved.robot);prefixErrors.delete(saved.robot)}
          else prefixErrors.set(saved.robot,result?.message||'前缀应用未收到回执，请重试');
          pendingPrefixes.delete(id);
        }
        
        ui.health.textContent=state.ready?'WSL 调度在线':'调度端正在启动';
        ui.discoveryState.textContent=!state.discovery?.fresh?'等待新鲜广播数据；不使用固定车辆地址':state.discovery.conflicts?.length?'广播身份或通信域冲突：'+state.discovery.conflicts.join('、'):'当前广播发现 '+state.discovery.robots.length+' 辆；新车接入后自动等待地图就绪并配准';
        ui.permission.textContent=state.motion_enabled?'单点发布即执行；多点先布置，点击“规划并执行”后发车':'进入跟随领车页自动开启调度许可；保存和预检航点不发车';
        const offline=robots.filter(r=>!state.robots?.[r]?.online),registration=state.registration;
        ui.maps.textContent=(robots.length===0?'等待车辆广播':offline.length?'离线车辆：'+offline.map(robotLabel).join('、')+'；等待自动重连':state.maps?.alignment_valid?'当前会话已配准':registration?.phase==='running'?'车辆在线，正在自动配准当前地图会话':registration?.phase==='failed'||registration?.phase==='partial'?'自动配准部分未通过，后台自动重试：'+(registration.message||Object.entries(registration.errors||{}).map(([r,e])=>robotLabel(r)+'：'+e).join('；')):'车辆在线，等待自动配准当前地图会话')+(state.maps?.reference_map_fresh===false?'；参考地图当前为缓存，各车仍要求自己的实时地图':'');
        const traffic=missions.traffic||{};
        if(pendingOrder&&((traffic.order_revision||0)>pendingOrder.revision||state.commands?.[pendingOrder.id]?.phase==='rejected'||Date.now()-pendingOrder.sent>15000))pendingOrder=undefined;
        if(!settingsLoaded){
          const restore=!traffic.order_configured&&order.length&&!follow.active&&!formation.active;
          if(!order.length)order=traffic.order||follow.order||robots;
          if(Number.isFinite(follow.distance))ui.distance.value=follow.distance;settingsLoaded=true;
          if(restore){order=[...new Set([...order.filter(r=>robots.includes(r)),...robots])];savePreferences()}
        }
        if(!pendingOrder&&traffic.order)order=[...traffic.order];
        if(follow.active&&follow.order)order=[...follow.order];
        order=[...new Set(order)].filter(r=>robots.includes(r));order.push(...robots.filter(r=>!order.includes(r)));renderVehicles(formation.active?{...follow,active:true,leader:formation.saved.leader}:follow);
        if([...ui.robot.options].map(o=>o.value).join(',')!==robots.join(',')){ui.robot.replaceChildren(...robots.map(r=>new Option(robotLabel(r),r)));ui.robot.value=robots.includes(selected)?selected:order[0]||robots[0];showRobot(ui.robot.value)}
        for(const option of ui.robot.options)option.textContent=robotLabel(option.value);
        if(!selected&&robots.length)showRobot(ui.robot.value);
        const groupLeader=formation.active?formation.saved.leader:follow.active?follow.leader:undefined;
        ui.robot.disabled=!!groupLeader;
        const routeRobot=groupLeader||(robots.includes(controlledRobot)?controlledRobot:selected);
        if(routeRobot&&selected!==routeRobot){ui.robot.value=routeRobot;showRobot(routeRobot)}
        for(const [id,robots] of pendingClears){
          const result=state.commands?.[id];if(!result)continue;
          if(result.phase==='cleared')for(const robot of robots){
            drafts.set(robot,'');dirty.delete(robot);if(selected===robot)ui.route.value='';
            for(const [saveId,saved] of pendingSaves)if(saved.robot===robot)pendingSaves.delete(saveId);
          }
          pendingClears.delete(id);
        }
        renderParameters();syncControls();
        const receipt=state.operator;
        if(receipt){
          if(['saved','accepted'].includes(receipt.phase)&&!dirty.has(receipt.robot_id)){
            drafts.set(receipt.robot_id,format(missions.routes?.[receipt.robot_id]?.points));
            if(selected===receipt.robot_id)ui.route.value=drafts.get(selected);
          }
          ui.mapTarget.textContent+=' 上次选点（'+robotLabel(receipt.robot_id)+'）：'+(labels[receipt.phase]||receipt.phase)+'，'+robotMessage(state,receipt.message)+(missions.jobs?.[receipt.robot_id]?' · '+(labels[missions.jobs[receipt.robot_id].phase]||missions.jobs[receipt.robot_id].phase)+' '+missions.jobs[receipt.robot_id].index+'/'+missions.jobs[receipt.robot_id].points.length+(missions.jobs[receipt.robot_id].message?' · '+robotMessage(state,missions.jobs[receipt.robot_id].message):''):'');
        }
        for(const r of robots)if(!dirty.has(r)){
          drafts.set(r,format(missions.routes?.[r]?.points));if(selected===r)ui.route.value=drafts.get(r);
        }
        for(const [id,saved] of pendingSaves)if(state.commands?.[id]?.phase==='saved'){
          if(drafts.get(saved.robot)===saved.text){dirty.delete(saved.robot);drafts.set(saved.robot,format(missions.routes?.[saved.robot]?.points));if(selected===saved.robot)ui.route.value=drafts.get(selected)}pendingSaves.delete(id);
        }
        ui.followStart.disabled=working||follow.active||formation.active||order.length<2||order.some(r=>!state.execution_enabled?.[r]);
        ui.followStop.disabled=working||!follow.active;
        renderFollowState(follow);
        if(missions.traffic?.zones?.length){ui.followStart.disabled=true;ui.followHint.textContent='已配置窄道互斥区域，请逐车调度通行；编队或连续跟随通道尚未验收'}
        const savedFormation=formation.saved;
        const formationOrder=savedFormation?.shape&&savedFormation.shape!=='current'?savedFormation.order:order;
        const formationUnavailable=formationOrder.filter(r=>!state.robots?.[r]?.online||!state.robots?.[r]?.samples?.navigation?.value?.local_ready||!state.maps?.valid_robots?.includes(r));
        ui.formationStart.disabled=!!missions.traffic?.zones?.length||working||formation.active||follow.active||formationOrder.length<2||formationUnavailable.length>0||formationOrder.some(r=>!state.execution_enabled?.[r]);
        ui.formationStop.disabled=working||!formation.active;
        if(formationSaveId&&state.commands?.[formationSaveId]?.phase==='saved'){
          if(ui.formationRoute.value===formationSaveText)formationDirty=false;formationSaveId=null;
        }
        if(!formationDirty)ui.formationRoute.value=format(formation.route?.points);
        ui.formationSave.disabled=working||!formation.saved;
        ui.formationExecute.disabled=working||formationDirty||!formation.active||!formation.route?.points?.length;
        ui.formationClear.disabled=working||!formation.saved;
        ui.formationRouteState.textContent=formationDirty?'队形航点有未保存修改':'已保存 '+(formation.route?.points?.length||0)+' 点；已完成 '+(formation.completed||0)+' 点';
        const phases={PLANNING:'全队联合规划中',MOVING:'全队行进中',AVOIDING:'临时绕障，等待归位',WAITING:'等待交通放行',UNSAVED:'尚未开始编队',SAVED:'队形已保存，未发车',FORMING:'全队准备中',HOLDING:'已到达，保持队形',STOPPED:'编队已停止',FAILED:'编队已停止，请检查原因'};
        ui.formationState.textContent=(phases[formation.phase]||'尚未开始编队')+(formation.message?'\n'+robotMessage(state,formation.message):'')+(savedFormation?'\n参考：队形中心'+savedFormation.order.map(r=>{
          const p=savedFormation.offsets[r],error=formation.position_errors?.[r];
          return '\n'+robotLabel(r)+'：相对队形中心 x '+p[0].toFixed(2)+' m，y '+p[1].toFixed(2)+' m，朝向 '+(p[2]*180/Math.PI).toFixed(1)+'°'+(Number.isFinite(error)?'；当前位置偏差 '+error.toFixed(2)+' m':'')+(Number.isFinite(formation.heading_errors?.[r])?'，朝向偏差 '+(formation.heading_errors[r]*180/Math.PI).toFixed(1)+'°':'');
        }).join(''):'');

        if(!formation.active&&formationUnavailable.length)ui.formationState.textContent+='\n暂不能开始：'+formationUnavailable.map(r=>robotLabel(r)+' '+(!state.robots?.[r]?.online?'离线':!state.maps?.valid_robots?.includes(r)?mapReason(r):state.robots?.[r]?.samples?.navigation?.value?.readiness_reason||'导航未就绪')).join('；');
        if(requestOperation?.startsWith('formation_')&&state.commands?.[requestId]?.phase==='rejected')ui.formationState.textContent+='\n'+robotMessage(state,state.commands[requestId].message);
        const route=missions.routes?.[selected];
        ui.saved.textContent=dirty.has(selected)?'有未保存修改，请先保存':route?.points?.length?'本车已保存 '+route.points.length+' 个航点，绑定保存时的地图会话':'本车尚未保存航点';
        ui.prepare.disabled=working||dirty.has(selected)||!route?.points?.length||!state.robots?.[selected]?.online;
        ui.routesStart.disabled=working||formation.active||dirty.has(selected)||!route?.points?.length;
        ui.routesStart.textContent='规划并执行 '+(robotLabel(selected)||'所选车辆')+' 多点导航';
        ui.routesStart.title=dirty.has(selected)?'请先保存所选车辆的修改':!route?.points?.length?'请先为所选车辆保存航点':'';
        const selectedJob=missions.jobs?.[selected];
        ui.routesStop.disabled=working||!selectedJob||!['route','single'].includes(selectedJob.source)||['STOPPED','COMPLETED','FAILED','INVALIDATED'].includes(selectedJob.phase);
        const dispatch=missions.goal_dispatch||{};
        ui.dispatchPoint.value=dispatch.goal?format([{pose:dispatch.goal}]):'';
        ui.dispatchSend.disabled=working;ui.dispatchStop.disabled=working||!dispatch.active;
        ui.goalDispatchState.textContent=(dispatch.message?robotMessage(state,dispatch.message):'尚无调度目标')+(dispatch.goal?'\n目标：'+dispatch.goal.slice(0,2).map(v=>v.toFixed(2)).join(', '):'')+(dispatch.current?'\n当前车辆：'+robotLabel(dispatch.current):'');
        ui.dispatchQueue.textContent='已到达：'+((dispatch.arrived||[]).map(robotLabel).join('、')||'无')+'；已完成'+(dispatch.mode==='all'?'往返':'')+'：'+((dispatch.completed||[]).map(robotLabel).join('、')||'无')+'；等待：'+((dispatch.ranking||[]).filter(row=>(dispatch.pending||[]).includes(row.robot)).map(row=>robotLabel(row.robot)+(Number.isFinite(row.distance)?' '+row.distance.toFixed(2)+' m':' 等待定位')).join(' → ')||'无');
        const registrationRunning=state.registration?.phase==='running';
        ui.align.disabled=working||registrationRunning;
        ui.align.textContent=registrationRunning?'正在配准地图…':working?'正在提交请求…':'手动重新配准地图';
        const registrationStages={'capture_clouds.py':'采集两车地图点云','register_maps.py':'匹配栅格地图','register_clouds.py':'匹配点云并校验'};
        const elapsed=Number.isFinite(state.registration?.updated_at)?Math.max(0,Math.floor(Date.now()/1000-state.registration.updated_at)):null;
        ui.registrationStatus.textContent=registrationRunning?(state.registration.trigger==='manual'?'手动':'自动')+'配准进行中：'+(registrationStages[state.registration.step]||'处理地图')+(state.registration.robot_id?' · '+robotLabel(state.registration.robot_id):'')+(elapsed===null?'':' · 本阶段已用 '+elapsed+' 秒')+'。完成或失败后可再次手动配准。':working?'正在提交其他请求，请稍候。':['failed','partial'].includes(state.registration?.phase)?'上次配准未通过：'+(state.registration.message||Object.entries(state.registration.errors||{}).map(([r,e])=>robotLabel(r)+'：'+e).join('；')||'请查看配准反馈')+'。可点击上方按钮重新配准。':state.maps?.alignment_valid?'当前地图配准有效，可按需重新配准。':'可点击上方按钮手动配准当前地图。';
        ui.align.title=registrationRunning?'后台已有配准任务，当前阶段和结果见下方说明':working?'等待当前请求提交完成':'手动重新采集并配准当前地图';
        if((!ui.followPage.hidden||!ui.goalDispatchPage.hidden)&&permitFollowOnRefresh&&!permissionPending&&!working&&order.length){permitFollowOnRefresh=false;void permitFollow()}
        const result=state.commands?.[requestId];if(result)ui.result.textContent=(labels[result.phase]||result.phase)+(result.message?'\n'+robotMessage(state,result.message):'')+(result.vehicles?'\n'+Object.entries(result.vehicles).map(([r,v])=>robotLabel(r)+'：'+robotMessage(state,v.message)).join('\n'):'')+(typeof result.receipt?.point_count==='number'?'\n'+result.receipt.point_count+' 个航点 · motion_sent=false':result.receipt?.message?'\n'+robotMessage(state,result.receipt.message):'');
      }catch(error){if(!disposed)ui.health.textContent='调度端未连接：'+error.message}
    }
    ui.followTab.onclick=()=>tab(true);ui.routeTab.onclick=()=>tab(false);ui.dispatchTab.onclick=()=>tab('dispatch');
    ui.dispatchMode.value=panelState.dispatchMode==='all'?'all':'nearest';
    ui.dispatchMode.onchange=()=>{savePanelState({dispatchMode:ui.dispatchMode.value});syncControls()};
    ui.dispatchSend.onclick=()=>{try{const value=parse(ui.dispatchPoint.value);if(value.length!==1)throw Error('请先在共享地图发布一个调度目标');command('dispatch_goal',{mode:ui.dispatchMode.value,point:value[0]})}catch(error){ui.result.textContent=error.message}};
    ui.dispatchStop.onclick=()=>command('dispatch_stop');
    if(panelState.navigationMode==='dispatch')tab('dispatch');
    ui.robot.onchange=()=>{showRobot(ui.robot.value);controlledRobot=selected;savePanelState({selectedRobot:selected,controlledRobot:selected});syncControls()};ui.route.oninput=()=>{drafts.set(selected,ui.route.value);dirty.add(selected);ui.prepare.disabled=ui.routesStart.disabled=true;syncControls()};
    ui.followStart.onclick=()=>command('follow_start',{order:[...order],distance:ui.distance.value===''?null:Number(ui.distance.value)});
    ui.followStop.onclick=()=>command('follow_stop');
    let formationDirty=false,formationSaveId=null,formationSaveText='';
    ui.formationRoute.oninput=()=>{formationDirty=true;ui.formationExecute.disabled=true;syncControls()};
    ui.formationSave.onclick=async()=>{try{formationSaveText=ui.formationRoute.value;formationSaveId=await command('route_save',{target:'formation',points:parse(formationSaveText)})}catch(error){ui.result.textContent=error.message}};
    ui.formationExecute.onclick=()=>command('route_start',{target:'formation'});
    ui.formationClear.onclick=async()=>{await command('route_clear',{target:'formation'});formationDirty=false;await refresh()};
    ui.formationStart.onclick=()=>{
      const saved=state?.missions?.formation?.saved;
      return saved?.shape&&saved.shape!=='current'
        ?command('formation_start',{order:saved.order})
        :command('formation_start',{order:[...order],capture_current:true});
    };
    ui.formationStop.onclick=()=>command('formation_stop');
    ui.save.onclick=()=>{try{command('route_save',{robot_id:selected,points:parse(ui.route.value)})}catch(error){ui.result.textContent=error.message}};
    ui.prepare.onclick=()=>command('route_prepare',{robot_id:selected});
    ui.import.onclick=()=>{const catalog=state?.robots?.[selected]?.samples?.waypoints?.value;if(!catalog||catalog.frame_id!=='map'){ui.result.textContent='尚未收到本车 map 航点';return}edit(catalog.waypoints.map(p=>[p.x,p.y,p.yaw_deg].join(', ')).join('\n'));ui.result.textContent='已导入本车航点，请检查并保存'};
    ui.append.onclick=()=>{const p=state?.robots?.[selected]?.samples?.pose?.value;if(!p){ui.result.textContent='本车定位未就绪';return}edit((ui.route.value.trim()+'\n'+[p.x.toFixed(4),p.y.toFixed(4),(p.yaw*180/Math.PI).toFixed(4)].join(', ')).trim())};
    ui.clearTarget.onclick=()=>window.OmniFleetFleetEditor?.scope==='dispatch'?command('dispatch_stop'):window.OmniFleetFleetEditor?.scope==='formation'?command('route_clear',{target:'formation'}):command('route_clear',{robot_id:state.missions?.formation?.active?state.missions.formation.saved.leader:state.missions?.follow?.active?state.missions.follow.leader:selected});
    ui.clearAll.onclick=()=>command('routes_clear');
    ui.routesStart.onclick=()=>command('route_start',{robot_id:selected});ui.routesStop.onclick=()=>command('route_stop',{robot_id:selected});
    ui.align.onclick=()=>command('align_maps');
    bindPanelTheme(context,root);context.watch('currentFrame');
    const timer=setInterval(refresh,1000);refresh();
    return()=>{disposed=true;clearInterval(timer);finishDrag(true);clearLanding();window.removeEventListener('pointermove',dragMove);window.removeEventListener('pointerup',dragEnd);window.removeEventListener('pointercancel',dragEnd);window.removeEventListener('keydown',dragKey);window.removeEventListener('blur',cancelDrag);if(window.OmniFleetFleetEditor?.owner===root)delete window.OmniFleetFleetEditor;root.remove()};
  }
  let attempts=0;
  const timer=setInterval(()=>{
    const fiber=document.getElementById('root')?._reactRootContainer?.current;
    if(!fiber){if(++attempts>150)clearInterval(timer);return}
    const stack=[fiber],seen=new Set();let catalog;
    while(stack.length&&!catalog){const f=stack.pop();if(!f||seen.has(f))continue;seen.add(f);const values=[f.memoizedProps?.value];let d=f.dependencies?.firstContext;while(d){values.push(d.memoizedValue);d=d.next}for(const v of values)if(v&&typeof v.getState==='function'&&typeof v.getState().installExtension==='function'){catalog=v;break}stack.push(f.child,f.sibling)}
    if(!catalog){if(++attempts>150)clearInterval(timer);return}
    const name='local.omnifleet-wsl';
    const register=()=>{
      const state=catalog.getState();
      if(state.installedPanels?.[name+'.fleet-panel']?.registration?.initPanel===initWslFleetPanel&&state.installedPanels?.[name+'.调度管理']?.registration?.initPanel===initDispatchPanel)return;
      catalog.setState({installedExtensions:[...(state.installedExtensions||[]).filter(x=>x.id!==name),{id:name,qualifiedName:name,namespace:'local',name:'omnifleet-wsl',publisher:'local',version:'0.1.0',displayName:'WSL 广播车队调度',main:'./omnifleet-wsl-panel.js'}],installedPanels:{...state.installedPanels,[name+'.fleet-panel']:{extensionName:name,extensionNamespace:'local',registration:{name:'fleet-panel',initPanel:initWslFleetPanel}},[name+'.调度管理']:{extensionName:name,extensionNamespace:'local',registration:{name:'调度管理',initPanel:initDispatchPanel}}}});
    };
    catalog.subscribe(register);register();
    window.__omnifleetWslPanelReady=true;clearInterval(timer);
  },200);
})();
