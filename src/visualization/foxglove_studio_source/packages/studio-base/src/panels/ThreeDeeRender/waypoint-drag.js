// Native 3D waypoint editing. Changes route coordinates only; never starts navigation.
(function (root) {
  'use strict';
  const instances = new WeakMap();
  const catalogTopic = '/omnifleet_t2/waypoints/catalog';
  const stateTopic = '/navigation/status';
  const updateTopic = '/omnifleet_t2/waypoints/update';
  function attach(renderer, context) {
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
    const fresh = () => catalog && state && Date.now()-catalogAt<2000 && Date.now()-stateAt<2000;
    const allowed = () => fresh() && catalog.map_valid !== false && !catalog.navigation_active && !state.navigation_active && renderer.followFrameId === catalog.frame_id && renderer.publishClickTool.state === 'idle';
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
      const points=catalog?.waypoints || [], valid=renderer.followFrameId===catalog?.frame_id;
      for(const [id,element] of handles)if(!points.some(p=>p.index===id)){element.remove();handles.delete(id);}
      for(const point of points){
        let h=handles.get(point.index);
        if(!h){h=document.createElement('div');h.dataset.waypointDragHandle=String(point.index);h.style.cssText='position:absolute;width:15px;height:15px;border:2px solid #168447;border-radius:50%;background:#eaffea99;transform:translate(-50%,-50%)';handles.set(point.index,h);overlay.append(h);}
        const moved=drag?.point.index===point.index?drag.position:pending?.point.index===point.index?pending.position:point;
        const p=screen(moved.x,moved.y);h.style.left=p.x+'px';h.style.top=p.y+'px';h.hidden=!valid||p.z < -1||p.z > 1;
        h.style.borderColor=drag?.point.index===point.index?'#1689ed':pending?.point.index===point.index?'#d18500':'#168447';
      }
      if(!drag&&!pending)hint.textContent=Date.now()<noticeUntil?notice:!fresh()?'航点编辑：等待实时导航状态':catalog.map_valid===false?'地图切换中，航点不可拖动':state.navigation_active||catalog.navigation_active?'导航执行中，航点不可拖动':!valid?'请切换到航点地图坐标系后拖动':'拖动航点圆环调整位置；松手保存，Esc取消';
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
        context.publish(updateTopic,{data:JSON.stringify({index:current.point.index,name:current.point.name,frame_id:catalog.frame_id,previous_position:{x:current.point.x,y:current.point.y},position:current.position})});
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
    context.advertise?.(updateTopic,'std_msgs/msg/String');
    canvas.addEventListener('pointerdown',down,true);canvas.addEventListener('click',click,true);
    root.addEventListener('pointermove',move,true);root.addEventListener('pointerup',up,true);root.addEventListener('keydown',key,true);root.addEventListener('blur',blur);root.addEventListener('pointercancel',blur);
    renderer.addListener('cameraMove',render);
    const dispose=()=>{clearTimeout(timer);canvas.removeEventListener('pointerdown',down,true);canvas.removeEventListener('click',click,true);root.removeEventListener('pointermove',move,true);root.removeEventListener('pointerup',up,true);root.removeEventListener('keydown',key,true);root.removeEventListener('blur',blur);root.removeEventListener('pointercancel',blur);renderer.removeListener('cameraMove',render);context.unadvertise?.(updateTopic);overlay.remove();instances.delete(renderer);};
    instances.set(renderer,{update,dispose});render();return dispose;
  }
  const api={attach,update(renderer,context,messages){if(!renderer)return;if(!instances.has(renderer))attach(renderer,context);instances.get(renderer)?.update(messages);}};
  root.OmniFleetWaypointDrag=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
