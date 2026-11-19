// Native 3D waypoint editing. Changes route coordinates only; never starts navigation.
(function (root) {
  'use strict';
  const instances = new WeakMap();
  const catalogTopic = '/omnifleet_t2/waypoints/catalog';
  const stateTopic = '/navigation/status';
  const updateTopic = '/omnifleet_t2/waypoints/update';
  function attach(renderer, context) {
    const fleet=new URL(location.href).searchParams.get("omnifleetProfile")==="fleet";
    if (!renderer || !context || instances.has(renderer)) return () => {};
    const canvas = renderer.gl.domElement, parent = canvas.parentElement;
    const Vector = renderer.cameraHandler.getActiveCamera().position.constructor;
    const overlay = document.createElement('div');
    overlay.dataset.waypointDragOverlay = 'true';
    overlay.style.cssText = 'position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:4';
    const hint = document.createElement('div');
    hint.dataset.waypointDragStatus = 'true';
    hint.style.cssText = 'position:absolute;left:8px;top:8px;padding:4px 7px;border-radius:5px;background:#ffffffe8;color:#234;font:12px sans-serif;max-width:75%';
    overlay.append(hint);parent.append(overlay);
    let catalog, state, catalogAt = 0, stateAt = 0, drag, pending, timer, swallowUntil = 0, notice='', noticeUntil=0;
    const handles = new Map();
    function syncFleet(){
      if(!fleet)return;
      const editor=root.OmniFleetFleetEditor;if(!editor){catalog=state=undefined;return;}
      if(editor.scope==='dispatch'){catalog=state=undefined;return;}
      if(editor.scope==='formation'){
        const data=editor.state,group=data.missions?.formation,route=group?.route;
        catalog={frame_id:'fleet_map',map_valid:!!group?.saved,editable:!editor.dirty,robot_id:'formation',public_id:'formation',identity_revision:data.identity_revision,
          route_revision:route?.revision||0,epoch:null,transform:[0,0,0],navigation_active:false,
          waypoints:(route?.points||[]).map((p,i)=>({index:i+1,name:p.name,x:p.pose[0],y:p.pose[1]}))};
        state={navigation_active:false};catalogAt=stateAt=editor.receivedAt;return;
      }
      const data=editor.state,robot=editor.target,route=data.missions?.routes?.[robot],transform=data.maps?.transforms?.[robot];
      const nav=data.robots?.[robot]?.samples?.navigation?.value||{},job=data.missions?.jobs?.[robot];
      const active=nav.navigation_active||job&&!['STOPPED','COMPLETED','FAILED','INVALIDATED'].includes(job.phase);
      const valid=data.maps?.valid_robots?.includes(robot)&&route?.epoch===nav.localization_epoch&&transform;
      const c=valid?Math.cos(transform[2]):1,s=valid?Math.sin(transform[2]):0;
      catalog={frame_id:'fleet_map',map_valid:!!valid,editable:!editor.dirty,robot_id:robot,public_id:data.assignments?.[robot]?.robot_name,identity_revision:data.identity_revision,
        route_revision:route?.revision||0,epoch:route?.epoch,transform,navigation_active:!!active,waypoints:valid?route.points.map((p,i)=>({index:i+1,name:p.name,x:transform[0]+c*p.pose[0]-s*p.pose[1],y:transform[1]+s*p.pose[0]+c*p.pose[1]})):[]};
      state={navigation_active:!!active};catalogAt=stateAt=editor.receivedAt;
    }
    const fresh = () => {syncFleet();return catalog && state && Date.now()-catalogAt<2000 && Date.now()-stateAt<2000};
    const allowed = () => fresh() && catalog.map_valid !== false && catalog.editable!==false && (!fleet||!drag||drag.fleet.robot_id===catalog.robot_id&&drag.fleet.identity_revision===catalog.identity_revision&&drag.fleet.route_revision===catalog.route_revision&&JSON.stringify(drag.fleet.map_transform)===JSON.stringify(catalog.transform)) && !catalog.navigation_active && !state.navigation_active && renderer.followFrameId === catalog.frame_id && renderer.publishClickTool.state === 'idle';
    const camera = () => renderer.cameraHandler.getActiveCamera();
    function screen(x,y) {
      const rect=canvas.getBoundingClientRect(), p=new Vector(x,y,0).project(camera());
      return {x:(p.x+1)*rect.width/2,y:(1-p.y)*rect.height/2,z:p.z};
    }
    function ground(event) {
      const rect=canvas.getBoundingClientRect(), x=2*(event.clientX-rect.left)/rect.width-1,y=1-2*(event.clientY-rect.top)/rect.height;
      const a=new Vector(x,y,-1).unproject(camera()), b=new Vector(x,y,1).unproject(camera());
      const dz=b.z-a.z;if(Math.abs(dz)<1e-9)return;
      const t=-a.z/dz;if(t<0||t>1)return;
      return {x:a.x+t*(b.x-a.x),y:a.y+t*(b.y-a.y)};
    }
    function render() {
      syncFleet();
      if(fleet&&pending){
        const result=root.OmniFleetFleetEditor?.state?.commands?.[pending.request];
        if(result||pending.fleet.robot_id!==catalog?.robot_id){
          notice=result?.phase==='saved'?'航点位置已保存':result?.message||'已切换车辆';noticeUntil=Date.now()+3000;
          pending=undefined;clearTimeout(timer);
        }
      }
      if(drag&&!allowed()){cancel('车辆、航点或导航状态已变化，已取消拖动');return;}
      const points=catalog?.waypoints || [], valid=renderer.followFrameId===catalog?.frame_id;
      for(const [id,element] of handles)if(!points.some(p=>p.index===id)){element.remove();handles.delete(id);}
      for(const point of points){
        let h=handles.get(point.index);
        if(!h){h=document.createElement('div');h.dataset.waypointDragHandle=String(point.index);h.style.cssText='position:absolute;width:15px;height:15px;border:2px solid #168447;border-radius:50%;background:#eaffea99;transform:translate(-50%,-50%)';handles.set(point.index,h);overlay.append(h);}
        const moved=drag?.point.index===point.index?drag.position:pending?.point.index===point.index?pending.position:point;
        const p=screen(moved.x,moved.y);h.style.left=p.x+'px';h.style.top=p.y+'px';h.hidden=!valid||p.z < -1||p.z > 1;
        h.style.borderColor=drag?.point.index===point.index?'#1689ed':pending?.point.index===point.index?'#d18500':'#168447';
      }
      if(!drag&&!pending)hint.textContent=Date.now()<noticeUntil?notice:!fresh()?'航点编辑：等待实时导航状态':catalog.map_valid===false?'请选择已安排航点且地图有效的车辆':catalog.editable===false?'请先保存文本修改后再拖动航点':state.navigation_active||catalog.navigation_active?'导航执行中，航点不可拖动':!valid?'请切换到航点地图坐标系后拖动':'拖动航点圆环调整位置；松手保存，Esc取消';
    }
    function cancel(message) {drag=undefined;pending=undefined;clearTimeout(timer);notice=message;noticeUntil=Date.now()+3000;render();}
    function consume(event){event.preventDefault();event.stopImmediatePropagation();}
    function down(event){
      if(event.button!==0||pending||!allowed())return;
      const rect=canvas.getBoundingClientRect();let best,nearest=19;
      for(const point of catalog.waypoints){
        const p=screen(point.x,point.y),d=Math.hypot(p.x-(event.clientX-rect.left),p.y-(event.clientY-rect.top));
        if(p.z>=-1&&p.z<=1&&d<nearest){best=point;nearest=d;}
      }
      if(!best)return;
      consume(event);drag={point:{...best},position:{x:best.x,y:best.y},start:{x:event.clientX,y:event.clientY},moved:false};
      if(fleet)drag.fleet={robot_id:catalog.robot_id,public_id:catalog.public_id,identity_revision:catalog.identity_revision,route_revision:catalog.route_revision,localization_epoch:catalog.epoch,map_transform:[...catalog.transform]};
      hint.textContent='正在移动 '+best.name+'；松手保存，Esc取消';render();
    }
    function move(event){
      if(!drag)return;consume(event);
      if(!allowed()){cancel('导航状态变化，已取消拖动');return;}
      const p=ground(event);if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.y))return;
      drag.moved ||= Math.hypot(event.clientX-drag.start.x,event.clientY-drag.start.y)>4;
      drag.position=p;render();
    }
    function up(event){
      if(!drag)return;consume(event);swallowUntil=Date.now()+300;
      const current=drag;drag=undefined;
      if(!current.moved||!allowed()){render();return;}
      const present=catalog.waypoints.find(p=>p.index===current.point.index);
      if(!present||present.name!==current.point.name||Math.hypot(present.x-current.point.x,present.y-current.point.y)>1e-4){cancel('航点已变化，请重新拖动');return;}
      try{
        pending=current;hint.textContent='正在保存 '+current.point.name+' 的位置……';render();
        if(fleet){
          const request='drag-'+Date.now()+'-'+Math.random().toString(16).slice(2);pending.request=request;
          const f=current.fleet;
          fetch((root.OmniFleetFleetApiBase||'http://127.0.0.1:8081')+'/command',{method:'POST',headers:{'Content-Type':'application/json','X-OmniFleet-Token':root.OmniFleetFleetEditor.state.token},body:JSON.stringify({op:'route_update',id:request,...(f.robot_id==='formation'?{target:'formation'}:{robot_id:f.public_id}),identity_revision:f.identity_revision,route_revision:f.route_revision,localization_epoch:f.localization_epoch,map_transform:f.map_transform,index:current.point.index,position:[current.position.x,current.position.y]})})
            .then(response=>{if(!response.ok&&pending?.request===request)cancel('位置保存请求被拒绝，请重新拖动')})
            .catch(error=>{if(pending?.request===request)cancel('保存失败：'+error.message)});
        }else context.publish(updateTopic,{data:JSON.stringify({index:current.point.index,name:current.point.name,frame_id:catalog.frame_id,previous_position:{x:current.point.x,y:current.point.y},position:current.position})});
        timer=setTimeout(()=>cancel('位置保存未确认，请检查航点后台'),4000);
      }catch(error){cancel('保存失败：'+String(error.message||error));}
    }
    function key(event){if(event.key==='Escape'&&drag){consume(event);cancel('已取消拖动');}}
    function click(event){if(Date.now()<swallowUntil)consume(event);}
    function blur(){if(drag)cancel('窗口失去焦点，已取消拖动');}
    function update(messages){
      for(const event of messages || []){
        if(event.topic!==catalogTopic&&event.topic!==stateTopic)continue;
        try{
          const value=JSON.parse(event.message.data);
          if(event.topic===catalogTopic&&Array.isArray(value.waypoints)){catalog=value;catalogAt=Date.now();}
          if(event.topic===stateTopic&&typeof value.navigation_active==='boolean'){state=value;stateAt=Date.now();}
        }catch(_){}
      }
      if(drag&&!allowed())cancel('导航状态变化，已取消拖动');
      if(pending){
        const point=catalog?.waypoints.find(p=>p.index===pending.point.index);
        if(point&&Math.hypot(point.x-pending.position.x,point.y-pending.position.y)<1e-4){pending=undefined;clearTimeout(timer);notice='航点位置已保存';noticeUntil=Date.now()+2000;}
      }
      render();
    }
    if(!fleet)context.advertise?.(updateTopic,'std_msgs/msg/String');
    const fleetTimer=fleet?setInterval(render,150):undefined;
    canvas.addEventListener('pointerdown',down,true);canvas.addEventListener('click',click,true);
    root.addEventListener('pointermove',move,true);root.addEventListener('pointerup',up,true);root.addEventListener('keydown',key,true);root.addEventListener('blur',blur);root.addEventListener('pointercancel',blur);
    renderer.addListener('cameraMove',render);
    const dispose=()=>{clearInterval(fleetTimer);clearTimeout(timer);canvas.removeEventListener('pointerdown',down,true);canvas.removeEventListener('click',click,true);root.removeEventListener('pointermove',move,true);root.removeEventListener('pointerup',up,true);root.removeEventListener('keydown',key,true);root.removeEventListener('blur',blur);root.removeEventListener('pointercancel',blur);renderer.removeListener('cameraMove',render);if(!fleet)context.unadvertise?.(updateTopic);overlay.remove();instances.delete(renderer);};
    instances.set(renderer,{update,dispose});render();return dispose;
  }
  const api={attach,update(renderer,context,messages){if(!renderer)return;if(!instances.has(renderer))attach(renderer,context);instances.get(renderer)?.update(messages);}};
  root.OmniFleetWaypointDrag=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
