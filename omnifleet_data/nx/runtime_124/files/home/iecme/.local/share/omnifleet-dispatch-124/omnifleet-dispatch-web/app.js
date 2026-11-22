"use strict";

const controls = new Map([...document.querySelectorAll("[id]")].map(node=>[node.id,node]));
const element = (id) => controls.get(id);
const shapes = {column:"纵队",line:"横队",wedge:"楔形",rectangle:"矩形",custom:"自绘",current:"保持当前位置"};
const map = element("map");
let scale = 0, renderer;
let world, state, squad, squadDraft, feedbackTimer;
let selectedPoint=null, pointDraft=null, pickingPoint=false;
let routeQueue=[], queueDrag=null, editingTask=null, draggedTask=null;
let pending = false;
let teamRun;
let zoneDraft = null;
let roadEditing=false, roadFrom=null, roadUndoRevision;
const roadHistory=[];
let draggedCard=null, selectedRobot=null, waypointSquadId=null;
let mapAction="map_save";

function svg(tag, attributes, parent) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  parent.append(node);
  return node;
}

function convertFrame(vector,source,target) {
  if(source===target)return vector;
  const pose={position:{x:vector.x,y:vector.y,z:vector.z},orientation:{x:0,y:0,z:0,w:1}};
  const t=renderer.currentTime;
  const transformed=renderer.transformTree.apply(pose,pose,target,renderer.fixedFrameId,source,t,t);
  if(!transformed)return vector.set(NaN,NaN,NaN);
  return vector.set(pose.position.x,pose.position.y,pose.position.z);
}

function toScreen([x, y]) {
  const camera=renderer.cameraHandler.getActiveCamera();
  const v=camera.position.clone().set(x,y,0);
  convertFrame(v,"fleet_map",renderer.followFrameId??"fleet_map").project(camera);
  const box=map.getBoundingClientRect();
  return [(v.x+1)*box.width/2,(1-v.y)*box.height/2];
}

function fromPointer(event) {
  const rect=map.getBoundingClientRect(),camera=renderer.cameraHandler.getActiveCamera();
  const x=2*(event.clientX-rect.left)/rect.width-1,y=1-2*(event.clientY-rect.top)/rect.height;
  const frame=renderer.followFrameId??"fleet_map";
  const a=convertFrame(camera.position.clone().set(x,y,-1).unproject(camera),frame,"fleet_map");
  const b=convertFrame(camera.position.clone().set(x,y,1).unproject(camera),frame,"fleet_map");
  const dz=b.z-a.z;
  if(!Number.isFinite(dz) || Math.abs(dz)<1e-9 || -a.z/dz<0)return null;
  const point=a.lerp(b,-a.z/dz);
  const [left, bottom, right, top] = world.bounds;
  return [
    Number(Math.min(right, Math.max(left, point.x)).toFixed(3)),
    Number(Math.min(top, Math.max(bottom, point.y)).toFixed(3)),
  ];
}

function drawMap() {
  if (!scale) return;
  drawRoads();
  drawZones();
  const draft=element("draft");draft.replaceChildren();
  if(pointDraft?.picked && renderer){
    const [cx,cy]=toScreen(pointDraft.node.xy);
    svg("circle",{cx,cy,r:7,stroke:"#e6d9ff",fill:"#937fdb","stroke-width":2},draft);
  }
}

function feedback(message, error = false) {
  const node = element("task-compose").open ? element("task-message") : element("feedback");
  node.textContent = message;
  node.hidden = false;
  node.classList.toggle("error", error);
  clearTimeout(feedbackTimer);
  feedbackTimer = setTimeout(() => { node.hidden = true; }, error ? 8000 : 3800);
}

function robotName(id) {
  return state?.robot_names?.[id] || state?.assignments?.[id]?.robot_name || id;
}

function renderRobotCards(){
  const body=element("robots"),traffic=state?.missions?.traffic;
  if(!traffic)return;
  const robots=Object.keys(state.robots??{});
  const order=[...new Set([...traffic.order.filter(id=>robots.includes(id)),...robots])];
  if(body.dataset.order!==JSON.stringify(order) && !draggedCard){
    const previous=new Map([...body.rows].map(row=>[row.dataset.robot,row.offsetTop]));
    body.dataset.order=JSON.stringify(order);body.replaceChildren();
    for(const [index,id] of order.entries()){
      const row=body.insertRow();row.className="robot-card";row.dataset.robot=id;row.tabIndex=0;row.draggable=true;
      const identity=document.createElement("div");identity.className="robot-identity";
      const handle=document.createElement("span");handle.className="order-handle";handle.textContent="⠿ "+(index+1);
      handle.title="拖动排序，或选中卡片后按上下键";
      const manage=document.createElement("a");manage.className="robot-manage";
      manage.draggable=false;
      manage.title="打开单车管理";
      identity.append(handle,manage);row.insertCell().append(identity);
      for(let i=0;i<4;i++)row.insertCell();
      row.onclick=e=>{
        if(e.target.closest("button,a"))return;
        selectedRobot=id;waypointSquadId=null;render();
      };
      row.ondblclick=e=>{if(!e.target.closest("button,a"))manage.click();};
      row.onkeydown=e=>{
        if(e.target!==row)return;
        if(["ArrowUp","ArrowDown"].includes(e.key)){
          e.preventDefault();reorder(id,traffic.order.indexOf(order[index+(e.key==="ArrowUp"?-1:1)]),state.missions.traffic);
        }else if(e.key==="Enter")manage.click();
        else if(e.key===" "){e.preventDefault();row.click();}
      };
      row.ondragstart=e=>{
        if(pending || e.target.closest("button,a")){e.preventDefault();return;}
        draggedCard={id,traffic:state.missions.traffic};e.dataTransfer.effectAllowed="move";e.dataTransfer.setData("text/plain",id);
        requestAnimationFrame(()=>{if(draggedCard?.id===id)row.dataset.dragging="true";});
      };
      row.ondragend=()=>{
        draggedCard=null;delete row.dataset.dragging;
        for(const card of body.rows)delete card.dataset.drop;
        render();
      };
      row.ondragover=e=>{
        if(!draggedCard || draggedCard.id===id)return;
        e.preventDefault();e.dataTransfer.dropEffect="move";
        row.dataset.drop=traffic.order.indexOf(id)<draggedCard.traffic.order.indexOf(draggedCard.id)?"before":"after";
      };
      row.ondragleave=e=>{if(!row.contains(e.relatedTarget))delete row.dataset.drop;};
      row.ondrop=e=>{
        if(!draggedCard)return;
        e.preventDefault();delete row.dataset.drop;
        const from=draggedCard;draggedCard=null;
        reorder(from.id,from.traffic.order.indexOf(id),from.traffic);
      };
    }
    if(!matchMedia("(prefers-reduced-motion: reduce)").matches){
      for(const row of body.rows){
        const top=previous.get(row.dataset.robot);
        if(top!==undefined && top!==row.offsetTop){
          row.animate([{transform:`translateY(${top-row.offsetTop}px)`},{transform:"translateY(0)"}],{duration:180,easing:"ease-out"});
        }
      }
    }
  }
  for(const row of body.rows){
    const id=row.dataset.robot,robot=state.robots?.[id];if(!robot)continue;
    const nav=robot.samples?.navigation,voltage=robot.samples?.voltage,job=state.missions.jobs[id];
    const manage=row.cells[0].querySelector(".robot-manage"),name=robotName(id);
    manage.setAttribute("href", id === state.dispatcher_id ? "/single/" : "/vehicle/"+encodeURIComponent(id)+"/");
    manage.textContent=name;
    manage.setAttribute("aria-label","打开 "+name+" 单车管理");
    row.title=name+" · 单击选车，双击管理";
    row.setAttribute("aria-selected",String(id===selectedRobot));
    const motion=robot.samples?.control;
    const velocity=motion?.value?.velocity;
    const odometryFresh=robot.online && robot.fresh?.control &&
      Number.isFinite(motion?.age_seconds) && Number.isFinite(motion?.value?.velocity_age) &&
      motion.age_seconds+motion.value.velocity_age+(robot.ipc_age_seconds??0)<1;
    const measured=odometryFresh && Array.isArray(velocity) && velocity.length===2 && velocity.every(Number.isFinite);
    row.cells[1].className="odometry-speed";
    row.cells[1].title=measured?"里程计反馈 · linear.x / angular.z":"等待新鲜的里程计反馈";
    row.cells[1].textContent=measured
      ? `Vx ${(Math.round(velocity[0]*1000)/1000).toFixed(3)} m/s\nωz ${(Math.round(velocity[1]*1000)/1000).toFixed(3)} rad/s`
      : "Vx — m/s\nωz — rad/s";
    row.cells[2].textContent=Number.isFinite(voltage?.value)&&voltage.age_seconds<10?voltage.value.toFixed(2)+" V":"—";
    row.cells[3].textContent=coordinates(state.maps?.poses?.[id]);
    const status=row.cells[4];
    const jobPhase=job && !["IDLE","STOPPED"].includes(job.phase)?job.phase:null;
    let label, tone;
    if(!(robot.transport_connected??robot.online)){
      label="离线";tone="error";
    }else if(!robot.fresh?.pose){
      label="定位过期";tone="warning";
    }else if(nav?.value?.readiness_reason){
      label=nav.value.readiness_reason;tone="warning";
    }else if(jobPhase){
      label=phaseName(jobPhase);
      tone=robotPhaseTones[jobPhase]??"active";
    }else{
      label=nav?.value?.local_ready?"空闲":"准备中";tone=nav?.value?.local_ready?"good":"warning";
    }
    status.textContent=label;status.dataset.tone=tone;
  }
}

function orderIds(order) {
  return order.map((id) => state.assignments[id].robot_name);
}

function currentSquad() {
  return state?.catalog?.squads.find((entry) => entry.id === squad);
}

function mapNavigationTarget(){
  const missions=state?.missions;
  const follow=missions?.follow;
  if(follow?.active){
    return {robot:follow.leader,leader:true,fields:{target:"follow_leader",follow_term:follow.term}};
  }
  const entry=state?.catalog?.squads?.find(s=>s.id===waypointSquadId);
  const robot=entry ? entry.leader??entry.order[0] : selectedRobot;
  const formation=missions?.formation;
  if(entry && formation?.active && formation.saved?.leader===robot &&
      JSON.stringify(formation.saved.order)===JSON.stringify(entry.order)){
    return {robot,leader:true,fields:{target:"formation"},offset:formation.saved.offsets?.[robot]};
  }
  return {robot,leader:Boolean(entry),fields:{robot_id:state?.assignments?.[robot]?.robot_name}};
}

function currentPoint() {
  return state?.roads?.nodes.find(n=>n.id===selectedPoint);
}
function pointName(node){return node.name||node.id;}
function pointPose(node){return [...node.xy,node.yaw??0];}
function editActive(){return Boolean(pointDraft||zoneDraft||roadEditing);}
function updateMapInteraction(){map.classList.toggle("editing",Boolean(pickingPoint||zoneDraft||roadEditing));}

function renderSquads(){
  const entries=state?.catalog?.squads??[],body=element("squads");
  const key=JSON.stringify(entries.map(entry=>[entry.id,entry.revision,entry.order.map(robotName)]));
  if(body.dataset.content!==key){
    body.dataset.content=key;body.replaceChildren();
    if(!entries.length){
      const cell=body.insertRow().insertCell();cell.colSpan=4;cell.className="empty";cell.textContent="暂无已保存的编队小队";
    }
    for(const entry of entries){
      const row=body.insertRow();row.tabIndex=0;row.title="双击编辑";
      row.insertCell().textContent=entry.name;
      const members=document.createElement("ol");members.className="squad-order";
      row.insertCell().append(members);
      const compact=entry.order.length>3;
      entry.order.slice(0,compact?1:3).forEach((id,i)=>{
        const member=document.createElement("li"),rank=document.createElement("span");
        rank.className="member-rank";rank.textContent=String(i+1);
        const name=document.createElement("span");
        name.className="member-name";name.textContent=(i===0?"领队 ":"")+robotName(id);name.title=name.textContent;
        member.append(rank,name);members.append(member);
      });
      if(compact){
        const more=document.createElement("li");
        more.append(previewButton(entry,"查看全部 "+entry.order.length+" 辆"));members.append(more);
      }
      const shape=row.insertCell(),layout=document.createElement("div");
      layout.className="squad-shape";shape.append(layout);
      if(entry.mode!=="follow"){
        const open=previewButton(entry,"");
        open.className="thumb-button";open.title="查看完整队形与队序";
        layout.append(open);
        svg("svg",{viewBox:"0 0 68 56","aria-hidden":"true",class:"formation-thumb formation-diagram"},open);
        layout.title="领队朝上，编号对应队内顺序";
      }
      layout.append(entry.mode==="follow"?"领队跟随":shapes[entry.shape]??entry.shape);
      row.insertCell();
      row.onclick=()=>{squad=entry.id;waypointSquadId=entry.id;render();};
      row.ondblclick=()=>editSquad(entry);
      row.onkeydown=e=>{
        if(e.target!==row)return;
        if(e.key==="Enter")editSquad(entry);
        if(e.key===" "){e.preventDefault();row.click();}
      };
    }
  }
  entries.forEach((entry,i)=>{
    const row=body.rows[i];
    row.setAttribute("aria-selected",String(squad===entry.id));
    const thumbnail=row.cells[2].querySelector("svg");
    if(thumbnail)drawFormationThumbnail(thumbnail,entry);
  });
  const dialog=element("squad-preview");
  if(dialog.open){
    const entry=entries.find(item=>item.id===dialog.dataset.squad);
    if(entry)renderSquadPreview(entry);else dialog.close();
  }
}

function previewButton(entry,label){
  const button=document.createElement("button");button.type="button";button.textContent=label;
  button.setAttribute("aria-label","查看"+entry.name+"完整队序");
  button.ondblclick=e=>e.stopPropagation();
  button.onclick=e=>{
    e.stopPropagation();
    const dialog=element("squad-preview");
    dialog.dataset.squad=entry.id;dialog.dataset.member=entry.order[0];
    renderSquadPreview(entry);dialog.showModal();
  };
  return button;
}

element("preview-close").onclick=()=>element("squad-preview").close();
element("squad-preview").onkeydown=e=>{
  if(e.key==="Escape"){e.preventDefault();e.stopPropagation();e.currentTarget.close();}
};

function renderSquadPreview(entry){
  const dialog=element("squad-preview"),list=element("preview-members"),image=element("preview-map");
  const names=entry.order.map(robotName);
  const key=JSON.stringify([entry.id,entry.order,names]);
  if(list.dataset.key!==key){
    list.dataset.key=key;list.replaceChildren();
    entry.order.forEach((id,i)=>{
      const li=document.createElement("li"),button=document.createElement("button");
      button.type="button";button.dataset.member=id;
      button.textContent=(i+1)+" · "+(i===0?"领队 ":"")+names[i];
      button.onclick=()=>{dialog.dataset.member=id;renderSquads();};
      li.append(button);list.append(li);
    });
  }
  if(!entry.order.includes(dialog.dataset.member))dialog.dataset.member=entry.order[0];
  for(const item of list.children)item.firstChild.setAttribute("aria-pressed",String(item.firstChild.dataset.member===dialog.dataset.member));
  element("preview-title").textContent=entry.name+" · "+entry.order.length+" 辆";
  image.style.display="none";
  if(entry.mode!=="follow")drawFormationThumbnail(image,entry,entry.order.indexOf(dialog.dataset.member));
}

function drawFormationThumbnail(image,entry,selected=-1){
  const formation=state.missions.formation;
  let points;
  if(entry.shape==="custom"){
    points=entry.cell_offsets;
  }else if(entry.shape==="current" && formation.active && formation.saved?.shape==="current" &&
      JSON.stringify(formation.saved.order)===JSON.stringify(entry.order)){
    points=entry.order.map(id=>formation.saved.offsets[id]);
  }else if(entry.shape!=="current" || entry.order.every(id=>state.maps.poses?.[id])){
    points=presetSlots(entry.order,entry.shape,entry.spacing||1);
  }
  if(!points?.length){
    image.style.display="";
    if(image.dataset.points!=="missing"){
      image.dataset.points="missing";image.replaceChildren();
      const {width,height}=image.viewBox.baseVal;
      const label=svg("text",{x:width/2,y:height/2},image);
      label.style.fill="#aaaab9";label.textContent="暂无位置";
    }
    return;
  }
  const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
  const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
  const {width,height}=image.viewBox.baseVal;
  const pad=selected<0?8:14;
  const scale=Math.min((width-2*pad)/Math.max(1,ymax-ymin),(height-2*pad)/Math.max(1,xmax-xmin));
  const pixels=points.map(([x,y])=>[Math.round(width/2-(y-(ymin+ymax)/2)*scale),Math.round(height/2-(x-(xmin+xmax)/2)*scale)]);
  const key=JSON.stringify([pixels,selected]);
  image.style.display="";
  if(image.dataset.points===key)return;
  image.dataset.points=key;image.replaceChildren();
  const radius=pad-1.5;
  // Compare nearby grid cells only. Crowded layouts use dots instead of overlapping labels.
  const bins=new Map(),diameter=2*radius+1;
  const dense=pixels.some(([x,y])=>{
    const col=Math.floor(x/diameter),row=Math.floor(y/diameter);
    for(let i=col-1;i<=col+1;i++)for(let j=row-1;j<=row+1;j++){
      if(bins.get(i+","+j)?.some(([a,b])=>Math.hypot(x-a,y-b)<diameter))return true;
    }
    const cell=col+","+row;
    if(!bins.has(cell))bins.set(cell,[]);
    bins.get(cell).push([x,y]);return false;
  });
  function mark(i,r,number){
    const [cx,cy]=pixels[i];
    const circle=svg("circle",{cx,cy,r,fill:i===0?"#ad96ff":"#6ed9b2"},image);
    if(i===selected){circle.setAttribute("stroke","#fff");circle.setAttribute("stroke-width","2");}
    if(number)svg("text",{x:cx,y:cy},image).textContent=String(i+1);
  }
  // Paint the leader and selected member last so they remain visible even at coincident positions.
  pixels.forEach((_,i)=>{if(i!==0 && i!==selected)mark(i,dense?2:radius,!dense);});
  if(selected!==0)mark(0,dense?3.5:radius,!dense);
  if(selected>=0)mark(selected,radius,true);
}

function syncButtons() {
  const formation = state?.missions?.formation;
  const follow = state?.missions?.follow;
  element("add-squad").disabled = !state?.ready || pending;
  element("add-point").disabled = !state?.ready || !scale || pending || editActive();
  element("leader-go").disabled = !follow?.active || !currentPoint() || pending;
  element("leader-go").hidden=!follow?.active;
  const target=mapNavigationTarget();
  const leaderRoute=state?.missions?.routes?.[target.robot];
  const leaderEpoch=state?.robots?.[target.robot]?.samples?.navigation?.value?.localization_epoch;
  const leaderPoints=target.fields.target==="formation" ? formation?.route?.points?.length??0 :
    target.leader && leaderRoute?.epoch===leaderEpoch ? leaderRoute?.points?.length??0 : 0;
  const routeStart=element("leader-route-start");
  routeStart.parentElement.hidden=!leaderPoints;
  routeStart.disabled=pending;
  routeStart.textContent=(target.fields.target==="formation"?"执行编队航点":"执行领车航点")+"（"+leaderPoints+"）";
  element("navigate").hidden=!formation?.active;
  const leaderJob=state?.missions?.jobs?.[follow?.leader];
  element("leader-stop").hidden = !follow?.leader || !leaderJob || !["single","route"].includes(leaderJob.source)
    || ["STOPPED","COMPLETED","FAILED","INVALIDATED"].includes(leaderJob.phase);
  element("leader-stop").disabled=pending;
  element("follow-status").textContent = follow?.active
    ? `领队 ${robotName(follow.leader)} · 设定 ${follow.distance} 米 · 实测 ${follow.order.slice(1).map((id,i)=>{
      const front=state.maps.poses[follow.order[i]], back=state.maps.poses[id];
      return front && back ? Math.hypot(front[0]-back[0],front[1]-back[1]).toFixed(2)+" 米" : "—";
    }).join(" / ")}`
    : "";
  element("follow-status").hidden=!follow?.active;
  renderSquadActions();
  element("navigate").disabled = !currentPoint() || !formation?.active || pending;
  element("add-zone").disabled=!scale || !state?.ready || pending || editActive();
  element("road-edit").disabled=!scale || !state?.ready || pending || editActive();
  element("road-undo").disabled=pending || !roadHistory.length || state?.roads?.revision!==roadUndoRevision;
  element("road-clear").disabled=pending || !state?.roads?.nodes.length;
  element("route-add").disabled=pending || !element("dispatch-point").value;
  element("route-clear").disabled=pending || !routeQueue.length;
  const corridor=element("dispatch-kind").value==="corridor";
  const zcar=element("zone-robot").value;
  element("new-task").disabled=pending;
  element("queue-start").disabled=pending || !state?.task_queue?.some(t=>t.phase==="READY");
  element("dispatch-send").disabled = pending ||
    !(corridor ? element("zone-select").value && zcar : (routeQueue.length || element("dispatch-point").value));
  const activeJob=state?.missions?.jobs?.[zcar]?.phase;
  element("dispatch-stop").hidden=!(corridor ? activeJob && !["IDLE","STOPPED","COMPLETED","FAILED","INVALIDATED"].includes(activeJob) : state?.missions?.goal_dispatch?.active);
  element("dispatch-stop").disabled=pending;
}

function render() {
  if (!currentSquad()) squad=state?.catalog?.squads?.[0]?.id;
  const grid=state?.maps?.shared_map;
  if(grid?.origin && grid.width && grid.height){
    const [x,y]=grid.origin;
    const first=!world;
    world={bounds:[x,y,x+grid.width*grid.resolution,y+grid.height*grid.resolution],camera_distance:18};
    if(first)alignEditor();
  }
  syncVehicleLayers();
  const robots = state?.robots ?? {};
  element("robot-count").textContent = `${Object.keys(robots).length} 辆`;
  renderRobotCards();
  renderSquads();
  renderWaypoints();
  renderMapLibrary();
  renderDispatch();
  syncButtons();
  drawMap();
}

async function pull() {
  const initial = window.OmniFleetInitialStateRequest;
  delete window.OmniFleetInitialStateRequest;
  const response = (await initial) ?? await fetch("/dispatch-api/state", {cache: "no-store"});
  if (!response.ok) throw new Error("车载调度暂不可用");
  state = await response.json();
  render();
}

async function poll() {
  try { await pull(); }
  catch {
    // Retry on the next poll after a temporary connection failure.
  }
  setTimeout(poll, 450);
}

async function command(op, fields = {}) {
  const id = "sim-ui-" + Date.now() + "-" + Math.random().toString(36).slice(2);
  const response = await fetch("/dispatch-api/command", {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-OmniFleet-Token": state.token},
    body: JSON.stringify({id, op, identity_revision: state.identity_revision, ...fields}),
  });
  if (!response.ok) throw new Error(`调度请求失败（${response.status}）`);
  for (let attempt = 0; attempt < 28; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    await pull();
    const result = state.commands[id];
    if (result?.phase === "rejected") throw new Error(result.message);
    if (result) return result;
  }
  throw new Error("调度请求未返回结果");
}

async function perform(fn) {
  if (pending) return;
  pending = true;
  syncButtons();
  try { await fn(); }
  catch (error) { feedback(error.message, true); }
  finally { pending = false; syncButtons(); }
}

function editSquad(entry = null) {
  squadDraft = entry ? { ...entry, order: [...entry.order] } : {order: []};
  squadDraft.slots=Object.fromEntries((entry?.cell_offsets??[]).map((point,i)=>[entry.order[i],[...point]]));
  element("squad-title").textContent = entry ? "编辑小队" : "新建小队";
  element("squad-name").value = entry?.name ?? "";
  element("shape").value = entry?.shape ?? "column";
  element("squad-mode").value = entry?.mode ?? (entry?"formation":"follow");
  squadDraft.followSpacing=entry?.mode==="follow"?entry.spacing:1.5;
  squadDraft.gridSpacing=entry && entry.mode!=="follow"?entry.spacing:1;
  element("spacing").value = entry?.spacing ?? 1.5;
  showMembers();
  if (!element("squad-dialog").open) element("squad-dialog").showModal();
  updateSlotEditor();
}

let slotView,slotDrag;
function slotPositions(){
  const order=squadDraft.order,shape=element("shape").value,unit=Number(element("spacing").value)||1;
  if(shape==="custom"){
    const slots=squadDraft.slots;
    for(const id of order){
      if(slots[id])continue;
      let x=0;while(Object.values(slots).some(p=>p[0]===x && p[1]===0))x--;
      slots[id]=[x,0];
    }
    const origin=slots[order[0]]??[0,0];
    return order.map(id=>[slots[id][0]-origin[0],slots[id][1]-origin[1]]);
  }
  return presetSlots(order,shape,unit);
}

function presetSlots(order,shape,unit){
  const leader=state.maps.poses?.[order[0]],c=Math.cos(leader?.[2]??0),s=Math.sin(leader?.[2]??0);
  return order.map((id,i)=>{
    if(shape==="line")return [0,i];
    if(shape==="wedge"){const rank=Math.ceil(i/2);return [-rank,i%2?rank:-rank];}
    if(shape==="rectangle"){const cols=Math.ceil(Math.sqrt(order.length));return [-Math.floor(i/cols),-(i%cols)];}
    if(shape==="current" && leader && state.maps.poses[id]){
      const [x,y]=state.maps.poses[id],dx=x-leader[0],dy=y-leader[1];
      return [(dx*c+dy*s)/unit,(-dx*s+dy*c)/unit];
    }
    return [-i,0];
  });
}

function drawSlots(fit=true){
  const canvas=element("slot-canvas"),ctx=canvas.getContext("2d"),w=canvas.width,h=canvas.height;
  const points=slotPositions(),order=squadDraft.order;
  if(fit || !slotView){
    const xs=[0,...points.map(p=>p[0])],ys=[0,...points.map(p=>p[1])];
    const hiX=Math.max(...xs),loX=Math.min(...xs),hiY=Math.max(...ys),loY=Math.min(...ys);
    const step=Math.min(42,h/(hiX-loX+4),w/(hiY-loY+5));
    slotView={step,cx:w/2+(hiY+loY)*step/2,cy:h/2+(hiX+loX)*step/2};
  }
  const {cx,cy,step}=slotView;
  ctx.fillStyle="#17171f";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#393846";ctx.lineWidth=1;ctx.beginPath();
  const visibleStep=step*Math.max(1,Math.ceil(6/step));
  for(let x=(cx%visibleStep+visibleStep)%visibleStep;x<=w;x+=visibleStep){ctx.moveTo(x,0);ctx.lineTo(x,h);}
  for(let y=(cy%visibleStep+visibleStep)%visibleStep;y<=h;y+=visibleStep){ctx.moveTo(0,y);ctx.lineTo(w,y);}
  ctx.stroke();
  points.forEach(([x,y],i)=>{
    const px=cx-y*step,py=cy-x*step;
    ctx.fillStyle=i===0?"#ad96ff":"#6ed9b2";ctx.beginPath();ctx.arc(px,py,9,0,2*Math.PI);ctx.fill();
    ctx.font="12px system-ui";ctx.fillStyle="#f7f4ff";ctx.fillText(robotName(order[i])+(i===0?" · 领队":""),px+12,py-5);
  });
  element("slot-hint").textContent=`车头朝上 · 每格 ${element("spacing").value||"—"} 米 · 拖动车辆自绘队形`;
}

function updateSlotEditor(){
  const fixed=element("squad-mode").value==="formation";
  element("shape-label").hidden=!fixed;element("slot-editor").hidden=!fixed;
  element("spacing-label").textContent=fixed?"每格（米）":"跟车间距（米）";
  element("spacing").value=fixed?squadDraft.gridSpacing:squadDraft.followSpacing;
  if(fixed)drawSlots();
}
element("squad-mode").onchange=updateSlotEditor;
element("shape").onchange=()=>drawSlots();
element("spacing").oninput=()=>{
  if(element("squad-mode").value==="formation"){squadDraft.gridSpacing=element("spacing").value;drawSlots();}
  else squadDraft.followSpacing=element("spacing").value;
};
element("add-online").onclick=()=>{
  for(const id of Object.keys(state.assignments))if(state.robots[id]?.online && !squadDraft.order.includes(id))squadDraft.order.push(id);
  showMembers();
};
function slotPointer(event){
  const canvas=element("slot-canvas"),rect=canvas.getBoundingClientRect();
  return [(event.clientX-rect.left)*canvas.width/rect.width,(event.clientY-rect.top)*canvas.height/rect.height];
}
element("slot-canvas").onpointerdown=event=>{
  if(event.button!==0)return;
  const [x,y]=slotPointer(event),{cx,cy,step}=slotView,positions=slotPositions();
  const i=positions.findIndex(([a,b])=>Math.hypot(x-(cx-b*step),y-(cy-a*step))<=15);
  if(i<0)return;
  slotDrag={id:squadDraft.order[i],positions,initial:[x,y]};
  event.currentTarget.setPointerCapture(event.pointerId);
};
element("slot-canvas").onpointerup=event=>{
  if(!slotDrag)return;
  const [x,y]=slotPointer(event),{cx,cy,step}=slotView,{id,positions,initial}=slotDrag;slotDrag=null;
  if(Math.hypot(x-initial[0],y-initial[1])<3)return;
  const target=[Math.round((cy-y)/step),Math.round((cx-x)/step)];
  const slots=positions.map((pos,i)=>squadDraft.order[i]===id?target:pos.map(Math.round));
  if(new Set(slots.map(p=>p.join(","))).size!==slots.length){feedback("目标格已有车辆",true);drawSlots();return;}
  squadDraft.slots=Object.fromEntries(squadDraft.order.map((r,i)=>[r,slots[i]]));
  element("shape").value="custom";drawSlots();
};
element("slot-canvas").onpointermove=event=>{
  if(!slotDrag)return;
  drawSlots(false);
  const [x,y]=slotPointer(event),ctx=element("slot-canvas").getContext("2d");
  ctx.strokeStyle="#ad96ff";ctx.lineWidth=2;ctx.strokeRect(x-9,y-9,18,18);
};
element("slot-canvas").onpointercancel=()=>{slotDrag=null;drawSlots();};

function showMembers() {
  const available = element("available");
  available.replaceChildren();
  for (const id of Object.keys(state.assignments).filter((id) => state.robots[id]?.online && !squadDraft.order.includes(id))) {
    available.add(new Option(robotName(id), id));
  }
  element("add-member").disabled = !available.options.length;
  element("roster").replaceChildren();
  squadDraft.order.forEach((id, index, order) => {
    const item = document.createElement("li");
    const controls = document.createElement("div");
    const name = document.createElement("span");
    name.textContent = `${robotName(id)}${index === 0 ? " · 领队" : ""}${state.robots[id]?.online?"":" · 离线"}`;
    item.append(controls);
    controls.append(name);
    function memberButton(label, action, disabled = false) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.disabled = disabled;
      button.onclick = () => { action(); showMembers(); };
      controls.append(button);
    }
    const move = (destination) => { order.splice(index, 1); order.splice(destination, 0, id); };
    memberButton("设为领队", () => move(0), index === 0);
    memberButton("上移", () => move(index - 1), index === 0);
    memberButton("下移", () => move(index + 1), index === order.length - 1);
    memberButton("移除", () => order.splice(index, 1));
    element("roster").append(item);
  });
  updateSlotEditor();
}

map.addEventListener("pointerdown",event=>{
  if(event.button!==0 || !scale)return;
  const point=fromPointer(event);if(!point)return;
  if(roadEditing){if(!pending)editRoadAt(point,event);return;}
  if(zoneDraft){
    if(zoneDraft.points.length===2)zoneDraft.points=[];
    zoneDraft.points.push(point);drawZones();return;
  }
  if(pickingPoint && pointDraft){
    pointDraft.node.xy=point;pointDraft.picked=true;pickingPoint=false;
    element("point-x").value=point[0];element("point-y").value=point[1];
    element("point-hint").textContent="位置已选定，填写名称后保存";
    updateMapInteraction();drawMap();
  }
});
map.addEventListener("pointermove",event=>{
  if(!scale)return;
  const point=fromPointer(event);
  if(point)element("cursor").textContent=point.map(v=>v.toFixed(2)).join(", ");
});
element("add-squad").onclick = () => editSquad();
element("cancel-squad").onclick = () => element("squad-dialog").close();
element("add-member").onclick = () => { squadDraft.order.push(element("available").value); showMembers(); };
element("squad-form").onsubmit = (event) => {
  event.preventDefault();
  perform(async () => {
    const result = await command("squad_save", {entry_id: squadDraft.id, revision: squadDraft.revision,
      name: element("squad-name").value, order: orderIds(squadDraft.order),
      mode:element("squad-mode").value,
      shape:element("squad-mode").value==="follow"?null:element("shape").value,
      spacing:Number(element("spacing").value),
      cell_offsets:element("shape").value==="custom"?slotPositions():undefined});
    squad = result.entry.id;
    element("squad-dialog").close();
    render();
    feedback(result.message);
  });
};
element("leader-route-start").onclick=()=>perform(async()=>{
  const target=mapNavigationTarget();
  const result=await command("route_start",target.fields);
  feedback(result.message || "已提交多点路线");
});
element("leader-go").onclick = () => perform(async () => {
  const leader=state.missions.follow.leader;
  const result=await command("web_goal",{robot_id:state.assignments[leader].robot_name,pose:pointPose(currentPoint())});
  feedback(result.message || "已提交领队目标");
});
element("leader-stop").onclick = () => perform(async () => {
  feedback((await command("route_stop",{robot_id:state.assignments[state.missions.follow.leader].robot_name})).message);
});
async function startSquad(entry) {
  if(teamRun || pending || !entry)return;
  squad=entry.id;waypointSquadId=entry.id;
  const kind=entry.mode??"formation";
  const order=orderIds(entry.order);
  const run={kind,leader:order[0],entryId:entry.id};
  teamRun=run;syncButtons();
  try {
    if(kind==="formation"){
      await command("formation_capture",{order,shape:entry.shape,spacing:entry.spacing,cell_offsets:entry.cell_offsets});
      if(teamRun!==run)return;
    }
    const op=kind==="follow" ? "follow_start" : "formation_start";
    const result=await command(op,{order,distance:entry.spacing});
    {
      const end=Date.now()+30000;
      while(teamRun===run){
        await pull();
        const status=state.missions[kind];
        const task=state.rmf.dispatch.tasks.find(t=>t.request_id===result.rmf_request_id);
        if(task && ["FAILED","INVALIDATED","STOPPED"].includes(task.phase))throw Error(task.message);
        if(status.active && (kind==="follow" ? status.leader===entry.leader : status.phase==="HOLDING"))break;
        if(Date.now()>end)throw Error("尚未就绪，可在路点列表查看并单独发送目标");
        await new Promise(resolve=>setTimeout(resolve,250));
      }
      if(teamRun!==run)return;
    }
    if(teamRun===run)feedback(kind==="follow"?"领队跟随已启动":"小队已完成集合");
  } catch(error){if(teamRun===run)feedback(error.message,true);}
  finally{if(teamRun===run)teamRun=null;syncButtons();}
}
async function stopSquad() {
  const run=teamRun;
  teamRun=null;
  const follow=state.missions.follow;
  try {
    if(follow.active || run?.kind==="follow"){
      const leader=state.assignments[follow.leader]?.robot_name || run?.leader;
      try { if(leader)await command("route_stop",{robot_id:leader}); }
      finally { await command("follow_stop"); }
    } else await command("formation_stop");
    feedback("已请求停止小队");
  } catch(error){feedback(error.message,true);}
}
element("stop-current-squad").onclick=stopSquad;

function renderSquadActions(){
  const formation=state?.missions?.formation,follow=state?.missions?.follow;
  const entries=state?.catalog?.squads??[];
  let hasInlineStop=false;
  for(const [i,row] of [...element("squads").rows].entries()){
    const entry=entries[i];if(!entry || row.cells.length<4)continue;
    const running=entry.mode==="follow"
      ? follow?.active && JSON.stringify(follow.order)===JSON.stringify(entry.order)
      : formation?.active && formation.saved?.shape===entry.shape && JSON.stringify(formation.saved.order)===JSON.stringify(entry.order);
    const starting=teamRun?.entryId===entry.id;
    hasInlineStop ||= Boolean(running||starting);
    const actions=row.cells[3];
    if(!actions.firstChild){
      const group=document.createElement("div");group.className="squad-actions";
      for(const label of ["开始集合","编辑小队","删除小队"]){
        const control=document.createElement("button");control.type="button";control.textContent=label;
        group.append(control);
      }
      group.ondblclick=e=>e.stopPropagation();
      group.firstChild.className="accent";
      actions.append(group);
    }
    const [button,edit,remove]=actions.firstChild.children;
    button.textContent=running?"停止":starting?"取消集合":"开始集合";
    button.disabled=!running&&!starting&&Boolean(pending||teamRun||formation?.active||follow?.active);
    button.onclick=e=>{
      e.stopPropagation();
      if(running||starting)stopSquad();else startSquad(state.catalog.squads.find(s=>s.id===entry.id));
    };
    edit.disabled=remove.disabled=pending;
    edit.onclick=e=>{e.stopPropagation();editSquad(entry);};
    remove.onclick=e=>{
      e.stopPropagation();
      perform(async()=>feedback((await command("squad_delete",{entry_id:entry.id,revision:entry.revision})).message));
    };
  }
  element("stop-current-squad").hidden=hasInlineStop || !(teamRun || formation?.active || follow?.active);
}
element("navigate").onclick = () => perform(async () => {
  const entry = currentPoint();
  await command("route_save", {target: "formation", points: [{name: pointName(entry), pose: pointPose(entry)}]});
  const result = await command("route_start", {target: "formation"});
  feedback(result.message);
});

const phaseNames = {FREE:"空闲",BLOCKED:"受阻",OCCUPIED:"占用",IDLE:"空闲",WAITING:"等待",
  QUEUED:"等待分配",ASSIGNED:"已分配",ARMING:"准备执行",EXECUTING:"执行中",PLANNING:"规划中",
  YIELDING:"等待路权",RETURNING:"返回中",COMPLETED:"已完成",FAILED:"失败",STOPPED:"已停止",
  INVALIDATED:"已失效",CANCEL_UNCONFIRMED:"等待停车确认"};
const phaseName = (phase) => phaseNames[phase] ?? phase ?? "—";
const robotPhaseTones = {COMPLETED:"good",FAILED:"error",INVALIDATED:"error",
  WAITING:"warning",YIELDING:"warning",BLOCKED:"warning",CANCEL_UNCONFIRMED:"warning"};
const coordinates = (pose) => pose ? pose.slice(0,2).map((v) => v.toFixed(2)).join(", ") : "—";

function selectOptions(id, items) {
  const select = element(id);
  const key = JSON.stringify(items);
  if (select.dataset.items === key) return;
  const previous = select.value;
  select.replaceChildren(...items.map(([value,label]) => new Option(label,value)));
  if (items.some(([value]) => value === previous)) select.value = previous;
  select.dataset.items = key;
}

function drawZones() {
  const layer = element("map-zones");
  layer.replaceChildren();
  function mark(id, points, width, color) {
    if (!points.length) return;
    const projected = points.map(toScreen);
    if (projected.length === 2) {
      const [[x1,y1],[x2,y2]] = projected;
      const angle=Math.atan2(points[1][1]-points[0][1],points[1][0]-points[0][0]);
      const outline=[];
      for(const [end,base] of [[1,angle-Math.PI/2],[0,angle+Math.PI/2]]){
        for(let i=0;i<=12;i++){const a=base+Math.PI*i/12;
          outline.push(toScreen([points[end][0]+width/2*Math.cos(a),points[end][1]+width/2*Math.sin(a)]).join(","));
        }
      }
      svg("polygon",{points:outline.join(" "),fill:color,opacity:.25},layer);
      svg("line", {x1,y1,x2,y2,stroke:color,"stroke-width":2,"stroke-dasharray":"6 4"},layer);
    }
    projected.forEach(([x,y],i) => {
      svg("circle",{cx:x,cy:y,r:4,fill:color},layer);
      svg("text",{x:x+5,y:y-6,fill:color},layer).textContent = (i ? "B" : "A")+" "+(i ? "" : id);
    });
  }
  for (const zone of state?.missions?.traffic?.zones ?? []) {
    mark(zone.id,[zone.a,zone.b],zone.width,zone.state==="FREE" ? "#69d4a3" : "#ffad70");
  }
  if (zoneDraft) {
    mark(element("zone-id").value,zoneDraft.points,Number(element("zone-width").value),"#ae9aff");
    element("zone-hint").textContent = ["在地图上点选入口 A","再点选出口 B","可保存通道，再次点图可重选端点"][zoneDraft.points.length];
  }
}

function renderDispatch() {
  const traffic = state?.missions?.traffic;
  if (!traffic) return;
  const zones = traffic.zones.map(z=>({...z,queue:z.queue.filter(id=>id!==(z.rmf_owner||z.owner))}));
  const robots = Object.keys(state.assignments).map((id) => [id,robotName(id)]);
  selectOptions("zone-select",zones.map((z) => [z.id,z.id]));
  selectOptions("zone-robot",robots);
  const roads=state.roads??{nodes:[],edges:[]};
  const connected=new Set(roads.edges.flat());
  selectOptions("dispatch-point",roads.nodes.filter(n=>connected.has(n.id)).map(n=>[n.id,pointName(n)]));
  const roadStart=roads.nodes.find(n=>n.id===roadFrom);
  if(!roadStart)roadFrom=null;
  element("road-status").textContent=roadStart
    ? (element("road-tool").value==="move"?"点击新位置移动 "+pointName(roadStart):"请选择另一个路点，与 "+pointName(roadStart)+" 连接")
    : `${roads.nodes.length} 个路点 · ${roads.edges.length} 条双向路段`;
  const corridor=element("dispatch-kind").value==="corridor";
  element("route-editor").hidden=corridor;
  element("task-corridor").hidden=!corridor;
  element("route-clear").hidden=corridor || !routeQueue.length;
  renderRouteQueue();
  element("zone-actions").hidden = !corridor || !zones.length;
  element("task-road").hidden=corridor;
  element("zone-remove").hidden=!corridor || !zones.length;
  element("dispatch-stop").textContent=corridor?"停止所选车辆":"停止目标调度";
  const selected=zones.find(z=>z.id===element("zone-select").value);
  const detail=selected ? [selected.id,phaseName(selected.state),selected.occupants.length>0&&"区内 "+selected.occupants.map(robotName).join("、"),selected.rmf_owner&&"持锁 "+robotName(selected.rmf_owner),
    selected.queue.length>0&&"排队 "+selected.queue.map(robotName).join("、")].filter(Boolean).join(" · ") : "暂无通道，可在此划定";
  const liveLocks=zones.filter(z=>z.owner||z.rmf_owner||z.queue.length).map(z=>[
    z.id,(z.rmf_owner||z.owner)&&"持锁 "+robotName(z.rmf_owner||z.owner),
    z.occupants.length&&"通行 "+z.occupants.map(robotName).join("、"),
    z.queue.length&&"排队 "+z.queue.map(robotName).join(" → "),
  ].filter(Boolean).join(" · "));
  const message = [corridor&&detail,...liveLocks,traffic.message, ...zones.map((z) => z.message)].filter(Boolean);
  element("zone-status").textContent = [...new Set(message)].join(" · ");
  element("zone-status").hidden = !message.length;
  const goal = state.missions.goal_dispatch;
  element("dispatch-summary").textContent = goal.goal
    ? [goal.message, goal.road_nodes?.join(" → "), goal.current && "当前车辆 "+robotName(goal.current),
       goal.pending.length && "待派 "+goal.pending.map(robotName).join("、")].filter(Boolean).join(" · ")
    : "";
  element("dispatch-summary").hidden=!goal.goal;
  renderQueue(state.task_queue??[]);
  renderTasks(state.rmf.dispatch.tasks);
}

function renderTasks(tasks){
  const list=element("task-list");
  const key=JSON.stringify(tasks);
  if(list.dataset.content===key)return;
  const expanded=new Set([...list.querySelectorAll("details[open]")].map(row=>row.dataset.request));
  list.dataset.content=key;
  list.replaceChildren();
  if(!tasks.length){
    const empty=document.createElement("p");empty.className="empty";empty.textContent="暂无任务";list.append(empty);
  }
  for(const task of [...tasks].reverse()){
    const row=document.createElement("details"),header=document.createElement("summary"),detail=document.createElement("p");
    row.dataset.request=task.request_id;row.open=expanded.has(task.request_id);
    const road=task.road_nodes??[];
    const time=new Date(task.submitted_at*1000).toLocaleTimeString("zh-CN",{hour12:false});
    header.textContent=[time,road.at(-1)||task.task_id||"待分配任务",task.robot?robotName(task.robot):"等待分配",phaseName(task.phase)].join(" · ");
    detail.className="status-note";
    detail.textContent=[task.task_id||task.request_id,road.join(" → "),task.points>0&&`路点进度 ${task.progress??0}/${task.points}`,task.message].filter(Boolean).join(" · ");
    row.append(header,detail);list.append(row);
  }
}

function reorder(id,index,traffic) {
  const order = [...traffic.order];
  const old = order.indexOf(id);
  if (old < 0 || old === index || index < 0 || index >= order.length) return;
  order.splice(old,1);
  order.splice(index,0,id);
  perform(async () => feedback((await command("dispatch_order",{
    order:orderIds(order),order_revision:traffic.order_revision})).message));
}

function closeZone() {
  zoneDraft = null;
  element("zone-form").hidden = true;
  updateMapInteraction();
  if(editingTask)element("task-compose").showModal();
  render();
}

element("add-zone").onclick = () => {
  const traffic = state.missions.traffic;
  zoneDraft = {points:[], revision:traffic.revision, zones:[...traffic.zones]};
  element("zone-form").reset();
  element("zone-form").hidden = false;
  map.classList.add("editing");
  drawZones();syncButtons();
  element("task-compose").close();
  element("zone-form").scrollIntoView({block:"nearest"});
};
element("cancel-zone").onclick = closeZone;
element("zone-width").oninput = drawZones;
element("zone-id").oninput = drawZones;
element("zone-form").onsubmit = (event) => {
  event.preventDefault();
  perform(async () => {
    const [a,b] = zoneDraft.points;
    if (!b) throw new Error("请在地图上选出通道 A、B 两端");
    const zone = {id:element("zone-id").value.trim(),a,b,width:Number(element("zone-width").value)};
    const result = await command("traffic_configure",{traffic_revision:zoneDraft.revision,zones:[...zoneDraft.zones,zone]});
    closeZone();element("zone-select").value=zone.id;feedback(result.message);
  });
};
element("zone-remove").onclick = () => perform(async () => {
  const traffic=state.missions.traffic;
  const zones=traffic.zones.filter((z) => z.id!==element("zone-select").value);
  feedback((await command("traffic_configure",{traffic_revision:traffic.revision,zones})).message);
});
element("dispatch-kind").onchange=render;
element("zone-robot").onchange=render;
element("zone-select").onchange=render;
function closeTaskEditor(){
  editingTask=null;
  routeQueue=[];
  element("task-compose").close();
  render();
}

function editQueueRow(task=null, nodes=null){
  if(pending)return;
  const spec=task?.spec??{};
  editingTask={id:task?.id??null,revision:task?.revision??null};
  routeQueue=nodes??(spec.nodes?.length>1?[...spec.nodes]:[]);
  element("task-dialog-title").textContent=task?"编辑任务":"新建任务";
  element("task-name").value=task?.name??"";
  element("task-message").hidden=true;
  element("dispatch-kind").value=spec.kind??"road";
  element("dispatch-mode").value=spec.mode??"nearest";
  if(spec.nodes?.length)element("dispatch-point").value=spec.nodes.at(-1);
  if(spec.kind==="corridor"){
    element("zone-select").value=spec.corridor;
    element("zone-side").value=spec.side;
    element("zone-robot").value=spec.robot;
  }else{
    element("zone-side").value="a";
  }
  element("task-compose").showModal();
  render();
}

function moveTask(task,target,side){
  if(!task || !target || task.id===target.id || task.phase==="EXECUTING")return;
  perform(async()=>{
    await command("queue_move",{entry_id:task.id,revision:task.revision,target_id:target.id,side});
  });
}

function clearTaskDrag(list){
  draggedTask=null;
  for(const card of list.children){
    delete card.dataset.dragging;
    delete card.dataset.drop;
  }
}

function renderQueue(tasks){
  const list=element("queue-list");
  if(editingTask?.id && !tasks.some(t=>t.id===editingTask.id && t.phase!=="EXECUTING")){
    editingTask=null;routeQueue=[];element("task-compose").close();
  }
  const ids=new Set(tasks.map(t=>t.id));
  for(const row of [...list.children]){
    if(!ids.has(row.dataset.task))row.remove();
  }
  tasks.forEach((task,index)=>{
    let row=list.querySelector('[data-task="'+task.id+'"]');
    if(!row){
      row=document.createElement("div");
      row.className="queue-line";
      row.dataset.task=task.id;
      row.innerHTML='<button class="queue-handle" type="button"></button><div class="queue-task-title"><strong></strong><small></small></div><span class="queue-status"></span><button type="button">编辑</button><button type="button">删除</button>';
    }
    if(list.children[index]!==row)list.insertBefore(row,list.children[index]??null);
    const [handle,title,status,edit,remove]=row.children;
    const spec=task.spec;
    const route=spec.kind==="road"?spec.nodes.map(id=>pointName(state.roads.nodes.find(n=>n.id===id)??{id})).join(" → "):
      spec.kind==="corridor"?spec.corridor+" · "+robotName(spec.robot)+" · "+(spec.side==="a"?"A → B":"B → A"):"";
    title.firstChild.textContent=task.name||route||"新任务";
    title.lastChild.textContent=task.name?route:"";
    title.lastChild.hidden=!task.name||!route;
    handle.textContent="⠿ "+(index+1);
    handle.title="拖拽排序，或使用上下方向键";
    handle.setAttribute("aria-label","调整第 "+(index+1)+" 项任务顺序");
    const running=task.phase==="EXECUTING";
    row.draggable=handle.draggable=!running;
    handle.disabled=running;
    handle.onkeydown=e=>{
      if(e.key==="ArrowUp" || e.key==="ArrowDown"){
        e.preventDefault();
        const before=e.key==="ArrowUp";
        moveTask(task,tasks[index+(before?-1:1)],before?"before":"after");
      }
    };
    row.ondragstart=e=>{
      if(pending || running || e.target===edit || e.target===remove){e.preventDefault();return;}
      draggedTask={task,index};
      e.dataTransfer.effectAllowed="move";
      e.dataTransfer.setData("text/plain",task.id);
      requestAnimationFrame(()=>{if(draggedTask?.task.id===task.id)row.dataset.dragging="true";});
    };
    row.ondragover=e=>{
      if(!draggedTask || draggedTask.task.id===task.id)return;
      e.preventDefault();e.dataTransfer.dropEffect="move";
      row.dataset.drop=index<draggedTask.index?"before":"after";
    };
    row.ondragleave=e=>{if(!row.contains(e.relatedTarget))delete row.dataset.drop;};
    row.ondrop=e=>{
      if(!draggedTask || !row.dataset.drop)return;
      e.preventDefault();
      const source=draggedTask.task,side=row.dataset.drop;
      clearTaskDrag(list);moveTask(source,task,side);
    };
    row.ondragend=()=>clearTaskDrag(list);
    status.textContent=({DRAFT:"草稿",READY:"待执行",QUEUED:"排队中"})[task.phase]??phaseName(task.phase);
    if(task.message && (running||task.phase==="FAILED"))status.textContent+=" · "+task.message;
    edit.textContent=running?"停止":"编辑";
    edit.onclick=()=>running?perform(()=>command("queue_stop",{entry_id:task.id,revision:task.revision})):editQueueRow(task);
    remove.disabled=running;
    remove.onclick=()=>perform(()=>command("queue_delete",{entry_id:task.id,revision:task.revision}));
  });
}

element("new-task").onclick=()=>editQueueRow();
element("task-cancel").onclick=closeTaskEditor;
element("task-compose").oncancel=e=>{e.preventDefault();closeTaskEditor();};
element("queue-start").onclick=()=>perform(()=>command("queue_start"));
element("task-form").onsubmit=e=>{
  e.preventDefault();
  perform(async()=>{
    const kind=element("dispatch-kind").value;
    const spec=kind==="road"?{nodes:routeQueue.length?[...routeQueue]:[element("dispatch-point").value],mode:element("dispatch-mode").value}:
      {corridor:element("zone-select").value,side:element("zone-side").value,robot_id:state.assignments[element("zone-robot").value].robot_name};
    await command("queue_save",{entry_id:editingTask.id,revision:editingTask.revision,name:element("task-name").value,kind,...spec});
    closeTaskEditor();
  });
};
element("dispatch-stop").onclick = () => perform(async () => {
  const corridor=element("dispatch-kind").value==="corridor";
  feedback((await command(corridor?"route_stop":"dispatch_stop",corridor?{
    robot_id:state.assignments[element("zone-robot").value].robot_name}:{})).message);
});

function drawRoads(){
  const layer=element("map-roads");layer.replaceChildren();
  const road=state?.roads;
  if(!road || !renderer)return;
  const pixels=new Map(road.nodes.map(n=>[n.id,toScreen(n.xy)]));
  const task=state?.missions?.goal_dispatch;
  const route=!roadEditing && task?.road_revision===road.revision ? task.road_nodes??[] : [];
  const nodeById=new Map(road.nodes.map(n=>[n.id,n]));
  for(const [from,to] of road.edges){
    const [x1,y1]=pixels.get(from),[x2,y2]=pixels.get(to);
    const selected=route.some((id,i)=>i>0&&((id===pointName(nodeById.get(from))&&route[i-1]===pointName(nodeById.get(to)))||(id===pointName(nodeById.get(to))&&route[i-1]===pointName(nodeById.get(from)))));
    svg("line",{x1,y1,x2,y2,stroke:selected?"#f5ab36":"#319bcc","stroke-width":selected?4:2},layer);
  }
  for(const [id,[cx,cy]] of pixels){
    svg("circle",{cx,cy,r:id===roadFrom||id===selectedPoint?7:4,fill:"#73d9ff",stroke:"#254557"},layer);
    svg("text",{x:cx+6,y:cy+15,fill:"#bfeaff"},layer).textContent=pointName(nodeById.get(id));
  }
}

function editRoadAt(point,event){
  const before=state.roads, next=structuredClone(before), {nodes,edges}=next;
  const tool=element("road-tool").value;
  if(tool==="move" && roadFrom){
    const node=nodes.find(n=>n.id===roadFrom);
    roadFrom=null;
    if(!node || (node.xy[0]===point[0] && node.xy[1]===point[1])){render();return;}
    node.xy=point;
  }else if(tool==="add"){
    let number=nodes.length+1;
    while(nodes.some(n=>n.id==="P"+number||pointName(n)==="P"+number))number++;
    const id="P"+number;
    nodes.push({id,xy:point,name:id,yaw:0});
  }else{
    const rect=map.getBoundingClientRect();
    const matches=nodes.map(n=>{const [x,y]=toScreen(n.xy);return [Math.hypot(rect.left+x-event.clientX,rect.top+y-event.clientY),n.id]});
    matches.sort((a,b)=>a[0]-b[0]);
    if(!matches.length || matches[0][0]>15)return;
    const id=matches[0][1];
    if(tool==="delete"){
      next.nodes=nodes.filter(n=>n.id!==id);
      next.edges=edges.filter(e=>!e.includes(id));roadFrom=null;
    }else{
      if(!roadFrom){roadFrom=id;render();return;}
      const from=roadFrom;
      roadFrom=null;
      if(from===id){render();return;}
      const i=edges.findIndex(e=>e.includes(from)&&e.includes(id));
      if(i>=0)edges.splice(i,1);else edges.push([from,id]);
    }
  }
  perform(()=>saveRoad(before,next));
}

async function saveRoad(before,next,undo=false){
  const result=await command("road_save",{...next,revision:before.revision});
  if(before.revision!==roadUndoRevision)roadHistory.length=0;
  if(undo)roadHistory.pop();else roadHistory.push(before);
  roadUndoRevision=before.revision+1;
  feedback(result.message);
}

function finishRoad(){
  roadEditing=false;roadFrom=null;element("road-editor").hidden=true;
  updateMapInteraction();render();
}
element("road-edit").onclick=()=>{
  roadEditing=true;roadFrom=null;
  element("road-editor").hidden=false;updateMapInteraction();render();
};
element("road-tool").onchange=()=>{roadFrom=null;render();};
element("road-undo").onclick=()=>perform(async()=>{
  roadFrom=null;
  await saveRoad(state.roads,roadHistory.at(-1),true);
});
element("road-clear").onclick=()=>perform(async()=>{
  roadFrom=null;
  await saveRoad(state.roads,{nodes:[],edges:[]});
  routeQueue=[];render();
});

function choosePoint(id){
  selectedPoint=id;
  if([...element("dispatch-point").options].some(o=>o.value===id))element("dispatch-point").value=id;
  renderWaypoints();renderDispatch();syncButtons();drawMap();
}

function renderWaypoints(){
  const nodes=state?.roads?.nodes??[],edges=state?.roads?.edges??[],body=element("waypoints");
  if(selectedPoint && !nodes.some(n=>n.id===selectedPoint))selectedPoint=null;
  const key=JSON.stringify([nodes,edges]);
  if(body.dataset.content!==key){
    body.dataset.content=key;body.replaceChildren();
    for(const node of nodes){
      const row=body.insertRow();row.dataset.point=node.id;row.tabIndex=0;
      const nameInput=document.createElement("input");
      nameInput.type="text";nameInput.className="waypoint-name";nameInput.maxLength=40;
      nameInput.value=pointName(node);
      nameInput.setAttribute("aria-label",pointName(node)+"的路点名称");
      nameInput.title="回车保存，Esc 取消";
      nameInput.onclick=e=>e.stopPropagation();
      nameInput.onkeydown=e=>{
        if(e.isComposing)return;
        if(e.key==="Escape")nameInput.value=pointName(node);
        else if(e.key!=="Enter")return;
        e.preventDefault();nameInput.blur();
      };
      nameInput.onblur=()=>renamePoint(node.id,nameInput);
      row.insertCell().append(nameInput);
      row.insertCell().textContent=coordinates(node.xy);
      const degree=edges.filter(e=>e.includes(node.id)).length;
      row.insertCell().textContent=degree?degree+" 条":"未连接";
      const add=document.createElement("button");add.type="button";add.textContent="＋";add.title="加入任务路线";add.disabled=!degree;
      add.onclick=e=>{e.stopPropagation();addRoutePoint(node.id);};
      row.insertCell().append(add);
      row.onclick=()=>choosePoint(node.id);
      row.onkeydown=e=>{if(e.target===row&&e.key==="Enter")choosePoint(node.id);};
    }
    if(!nodes.length){const cell=body.insertRow().insertCell();cell.colSpan=4;cell.className="empty";cell.textContent="点击地图添加命名路点";}
  }
  for(const row of body.rows)row.dataset.selected=String(row.dataset.point===selectedPoint);
  const target=[...body.rows].find(row=>row.dataset.point===selectedPoint);
  const actions=target?.cells[3]??element("point-actions");
  actions.append(element("navigate"),element("leader-go"),element("leader-stop"));
  if(pointDraft)placePointEditor();
}

function renamePoint(id,input){
  const before=state.roads, node=before.nodes.find(n=>n.id===id);
  if(!node)return;
  const previous=pointName(node),name=input.value.trim();
  if(name===previous){input.value=previous;return;}
  if(pending){input.value=previous;return feedback("当前操作正在保存，请稍后重试",true);}
  perform(async()=>{
    try{
      if(!name)throw Error("路点名称不能为空");
      if(before.nodes.some(n=>n.id!==id&&pointName(n)===name))throw Error("路点名称已使用");
      await saveRoad(before,{nodes:before.nodes.map(n=>n.id===id?{...n,name}:n),edges:before.edges});
    }finally{
      if(input.isConnected)input.value=pointName(state.roads.nodes.find(n=>n.id===id)??node);
    }
  });
}

function placePointEditor(){
  const body=element("waypoints"),form=element("point-form");
  let row=body.querySelector('[data-editor]');
  if(!row){
    row=document.createElement('tr');row.dataset.editor="true";
    const cell=row.insertCell();cell.colSpan=4;cell.append(form);
    body.append(row);
  }else if(!row.contains(form))row.cells[0].append(form);
}
function openNewPoint(){
  if(editActive())return feedback("请先保存或取消当前地图编辑",true);
  pointDraft={revision:state.roads.revision,node:{xy:[0,0]},picked:false};
  placePointEditor();
  element("point-form").hidden=false;
  element("point-name").value="";
  element("point-x").value="";
  element("point-y").value="";
  element("point-yaw").value=0;
  pickingPoint=true;
  element("point-hint").textContent="点击地图设置路点位置";
  updateMapInteraction();syncButtons();drawMap();
  element("point-form").scrollIntoView({block:"nearest"});
}
function closePoint(){
  element("fleet-panel").append(element("point-form"));
  element("waypoints").querySelector('[data-editor]')?.remove();
  pointDraft=null;pickingPoint=false;element("point-form").hidden=true;
  updateMapInteraction();render();
}
element("add-point").onclick=openNewPoint;
element("point-cancel").onclick=closePoint;
element("point-pick").onclick=()=>{pickingPoint=true;element("point-hint").textContent="点击地图重新设置位置";updateMapInteraction();};
for(const id of ["point-x","point-y"]){
  element(id).oninput=()=>{
    const x=element("point-x").valueAsNumber,y=element("point-y").valueAsNumber;
    if(Number.isFinite(x)&&Number.isFinite(y)){pointDraft.node.xy=[x,y];pointDraft.picked=true;drawMap();}
  };
}
element("point-form").onsubmit=e=>{
  e.preventDefault();
  perform(async()=>{
    const x=element("point-x").valueAsNumber,y=element("point-y").valueAsNumber,yaw=element("point-yaw").valueAsNumber*Math.PI/180;
    if(![x,y,yaw].every(Number.isFinite))throw Error("请输入有效的路点位置和朝向");
    const name=element("point-name").value.trim(),nodes=state.roads.nodes;
    if(nodes.some(n=>pointName(n)===name))throw Error("路点名称已使用");
    const id="point_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2,7);
    const updated={id,name,xy:[x,y],yaw};
    if(pointDraft.revision!==state.roads.revision)throw Error("路网已更新，请重新打开编辑");
    await saveRoad(state.roads,{nodes:[...nodes,updated],edges:state.roads.edges});
    selectedPoint=id;closePoint();choosePoint(id);
  });
};

function addRoutePoint(id){
  if(routeQueue.length>=100)return feedback("一条路线最多 100 个路点",true);
  if(!editingTask){
    editQueueRow(null,[id]);
    return;
  }
  routeQueue.push(id);element("dispatch-kind").value="road";render();
}
function moveRoute(from,to){
  if(from===to||to<0||to>=routeQueue.length)return;
  const [id]=routeQueue.splice(from,1);routeQueue.splice(to,0,id);render();
}
function renderRouteQueue(){
  const nodes=new Map((state.roads?.nodes??[]).map(n=>[n.id,n]));
  const list=element("route-queue"),key=JSON.stringify(routeQueue.map(id=>[id,nodes.get(id)]));
  if(list.dataset.content!==key && queueDrag===null){
    list.dataset.content=key;list.replaceChildren();
    routeQueue.forEach((id,index)=>{
      const li=document.createElement("li");li.tabIndex=0;li.draggable=true;li.dataset.index=index;
      const text=document.createElement("span");text.textContent=(index+1)+" · "+(nodes.has(id)?pointName(nodes.get(id)):"已删除的路点");
      const remove=document.createElement("button");remove.type="button";remove.textContent="×";remove.title="移除此途经点";
      remove.onclick=()=>{routeQueue.splice(index,1);render();};
      li.append(text,remove);
      li.ondragstart=e=>{queueDrag=index;e.dataTransfer.setData("text/plain",String(index));};
      li.ondragover=e=>{if(queueDrag!==null)e.preventDefault();};
      li.ondrop=e=>{e.preventDefault();const from=queueDrag;queueDrag=null;if(from!==null)moveRoute(from,index);};
      li.ondragend=()=>{queueDrag=null;render();};
      li.onkeydown=e=>{if(e.target===li&&["ArrowUp","ArrowDown"].includes(e.key)){e.preventDefault();moveRoute(index,index+(e.key==="ArrowUp"?-1:1));}};
      list.append(li);
    });
  }
  element("route-hint").textContent=routeQueue.length?"将按上述顺序途经，路点之间由 Open-RMF 沿路网规划":"单个路点可直接提交，多点任务按加入顺序执行";
}
element("route-add").onclick=()=>addRoutePoint(element("dispatch-point").value);
element("route-clear").onclick=()=>{routeQueue=[];render();};

function alignEditor() {
  if (!renderer || !world) return;
  const canvas=renderer.gl.domElement;
  const rect=canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  map.setAttribute("viewBox", `0 0 ${rect.width} ${rect.height}`);
  scale=rect.height/world.camera_distance;
  drawMap();syncButtons();
}

function renderMapLibrary(){
  const body=element("saved-maps"),maps=state?.map_library??[];
  const key=JSON.stringify(maps);
  if(body.dataset.content!==key){
    body.dataset.content=key;body.replaceChildren();
    for(const item of maps){
      const row=body.insertRow();row.insertCell().textContent=item.name;row.insertCell().textContent=item.path;
      const actions=row.insertCell();
      for(const [label,op] of [["加载","map_load"],["删除","map_delete"]]){
        const button=document.createElement("button");button.textContent=label;button.type="button";
        button.onclick=()=>perform(async()=>feedback((await command(op,{map_id:item.id})).message));
        actions.append(button);
      }
    }
    if(!maps.length){const cell=body.insertRow().insertCell();cell.colSpan=3;cell.className="empty";cell.textContent="暂无已保存地图";}
  }
  const visible=maps.find(item=>item.id===state?.loaded_map),label=element("map-sync");
  label.hidden=!visible;
  if(visible)label.textContent="正在预览 "+visible.name;
}
element("library-save").onclick=()=>openMapDialog("map_save");

const fleetCards=document.querySelector("#fleet-cards");
const cardOrderKey="omnifleet.dispatch.card-order.v1";
const cardOrderEndpoint="/dispatch-api/card-order";
let draggedSection=null,cardOrderSaving=false,cardOrderLoading=false;
let cardOrderGeneration=0;

function fleetOrder(){
  return [...fleetCards.children].map(card=>card.dataset.card);
}

function applyFleetOrder(order){
  const cards=new Map([...fleetCards.children].map(card=>[card.dataset.card,card]));
  if(!Array.isArray(order) || order.length!==cards.size || new Set(order).size!==cards.size ||
      !order.every(key=>cards.has(key)))return;
  order.forEach((key,index)=>{
    const card=cards.get(key);
    if(fleetCards.children[index]!==card)fleetCards.insertBefore(card,fleetCards.children[index]);
  });
  try{localStorage.setItem(cardOrderKey,JSON.stringify(order));}catch{}
}

async function saveFleetOrder(order,initialize=false){
  const response=await fetch(cardOrderEndpoint,{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({order,initialize})
  });
  if(!response.ok)throw Error("卡片顺序保存失败，请检查 124 是否在线");
  return (await response.json()).order;
}

async function loadFleetOrder(){
  if(draggedSection || cardOrderSaving || cardOrderLoading)return;
  cardOrderLoading=true;
  const generation=cardOrderGeneration;
  try{
    const response=await fetch(cardOrderEndpoint,{cache:"no-store"});
    if(!response.ok)return;
    const {order}=await response.json();
    if(draggedSection || generation!==cardOrderGeneration)return;
    let legacy=null;
    try{legacy=JSON.parse(localStorage.getItem(cardOrderKey));}catch{}
    if(order)applyFleetOrder(order);
    else if(Array.isArray(legacy)){
      const initial=await saveFleetOrder(legacy,true);
      if(!draggedSection && generation===cardOrderGeneration)applyFleetOrder(initial);
    }
  }catch{
    // The most recently loaded order remains visible during a brief disconnection.
  }finally{cardOrderLoading=false;}
}

try{applyFleetOrder(JSON.parse(localStorage.getItem(cardOrderKey)));}catch{}
loadFleetOrder();
window.addEventListener("focus",loadFleetOrder);

async function moveFleetCard(source,target,before){
  if(!source || !target || source===target || cardOrderSaving)return;
  const order=fleetOrder().filter(key=>key!==source.dataset.card);
  order.splice(order.indexOf(target.dataset.card)+(before?0:1),0,source.dataset.card);
  cardOrderGeneration++;
  cardOrderSaving=true;
  try{applyFleetOrder(await saveFleetOrder(order));}
  catch(error){feedback(error.message,true);}
  finally{cardOrderSaving=false;}
}

function clearFleetDrag(){
  draggedSection=null;
  for(const card of fleetCards.children){
    delete card.dataset.cardDragging;
    delete card.dataset.cardDrop;
  }
}

for(const heading of document.querySelectorAll("#fleet-cards section > h2,#dispatch > h2")){
  const section=heading.parentElement;
  const title=heading.firstChild.textContent.trim();
  const tools=document.createElement("span");tools.className="card-heading";
  const toggle=document.createElement("button");toggle.className="card-toggle";toggle.type="button";
  toggle.textContent=title;toggle.setAttribute("aria-expanded","true");
  toggle.onclick=()=>{
    const collapsed=section.dataset.collapsed!=="true";
    section.dataset.collapsed=String(collapsed);toggle.setAttribute("aria-expanded",String(!collapsed));
  };
  if(section.parentElement===fleetCards){
    const grip=document.createElement("button");grip.type="button";grip.className="card-grip";grip.draggable=true;
    grip.textContent="⠿";grip.title="拖动卡片，或用上下键换位";
    grip.setAttribute("aria-label","调整"+title+"卡片位置");
    grip.ondragstart=e=>{
      if(cardOrderSaving){e.preventDefault();return;}
      draggedSection=section;
      e.dataTransfer.effectAllowed="move";
      e.dataTransfer.setData("text/plain",section.dataset.card);
      requestAnimationFrame(()=>{if(draggedSection===section)section.dataset.cardDragging="true";});
    };
    grip.ondragend=clearFleetDrag;
    grip.onkeydown=async e=>{
      if(e.key!=="ArrowUp" && e.key!=="ArrowDown")return;
      e.preventDefault();
      const up=e.key==="ArrowUp";
      await moveFleetCard(section,up?section.previousElementSibling:section.nextElementSibling,up);
      grip.focus({preventScroll:true});
    };
    section.ondragover=e=>{
      if(!draggedSection || draggedSection===section)return;
      e.preventDefault();e.dataTransfer.dropEffect="move";
      section.dataset.cardDrop=(draggedSection.compareDocumentPosition(section)&Node.DOCUMENT_POSITION_FOLLOWING)?"after":"before";
    };
    section.ondragleave=e=>{if(!section.contains(e.relatedTarget))delete section.dataset.cardDrop;};
    section.ondrop=e=>{
      const side=section.dataset.cardDrop;
      if(!draggedSection || !side)return;
      e.preventDefault();e.stopPropagation();
      const source=draggedSection;clearFleetDrag();moveFleetCard(source,section,side==="before");
    };
    tools.append(grip);
  }
  tools.append(toggle);heading.firstChild.replaceWith(tools);
}

function openMapDialog(action){
  mapAction=action;
  const loading=action==="map_load";
  element("map-dialog-title").textContent=loading?"加载地图":"保存地图";
  element("map-name-label").hidden=loading;element("map-choice-label").hidden=!loading;
  element("map-name").required=!loading;element("map-name").value="";
  selectOptions("map-choice",[["live","实时共享地图"],...(state?.map_library??[]).map(m=>[m.id,m.name+" · "+m.width+" × "+m.height])]);
  element("map-confirm").textContent=loading?"加载":"保存";
  element("map-confirm").disabled=loading&&!element("map-choice").value;
  element("map-dialog").showModal();
}
element("map-cancel").onclick=()=>element("map-dialog").close();
element("map-form").onsubmit=e=>{
  e.preventDefault();
  perform(async()=>{
    const result=await command(mapAction,mapAction==="map_load"?{map_id:element("map-choice").value}:{name:element("map-name").value});
    element("map-dialog").close();feedback(result.message);
  });
};
poll();
