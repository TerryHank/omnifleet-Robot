"use strict";

// The 124 CN renderer exposes its live camera to the waypoint editing integration.
// The SVG contains only editable fleet annotations. The native panel owns the map.
let layerKey=null;
function syncVehicleLayers(){
  if(!renderer || !state?.discovery)return;
  const names=state.discovery.robots.map(id=>state.assignments[id]?.namespace).filter(Boolean);
  const key=JSON.stringify([names,state.loaded_map]);
  if(key===layerKey)return;
  layerKey=key;
  renderer.updateConfig(config=>{
    config.layers??={};
    for(const id of Object.keys(config.layers))if(id.startsWith("vehicle:") && !names.includes(id.slice(8)))delete config.layers[id];
    names.forEach((ns,i)=>{
      const id="vehicle:"+ns;
      config.layers[id]={layerId:"foxglove.Urdf",visible:true,frameLocked:true,sourceType:"topic",topic:ns+"/robot_description",framePrefix:ns.slice(1)+"/",displayMode:"visual",instanceId:id,label:ns.slice(1),order:i};
    });
    config.topics["/fleet/map"]={...config.topics["/fleet/map"],visible:!state.loaded_map};
    config.topics["/fleet/saved_map"]={...config.topics["/fleet/map"],visible:Boolean(state.loaded_map)};
  });
}
window.OmniFleetWaypointDrag={
  publishClick(event,frame,multi){
    const pointOnly=event.publishClickType==="point";
    const estimate=event.publishClickType==="pose_estimate";
    const target=estimate
      ? {robot:selectedRobot,fields:{robot_id:state?.assignments?.[selectedRobot]?.robot_name}}
      : mapNavigationTarget();
    const robot=target.robot;
    if(!state?.assignments?.[robot]){
      feedback(estimate?"请选择要设置初始位姿的车辆":"请选择小队或车辆，再发布航点",true);
      return true;
    }
    if(frame!=="fleet_map"){feedback("请切换到共享地图坐标系 fleet_map",true);return true;}

    const position=pointOnly?event.point:event.pose.position;
    const orientation=event.pose?.orientation;
    const yaw=pointOnly?state.maps?.poses?.[robot]?.[2]:
      Math.atan2(2*(orientation.w*orientation.z+orientation.x*orientation.y),
        1-2*(orientation.y*orientation.y+orientation.z*orientation.z));
    let pose=[position.x,position.y,yaw];
    if(!pose.every(Number.isFinite)){feedback("缺少有效的目标位置或车辆朝向",true);return true;}
    if(target.offset){
      const [dx,dy,dyaw]=target.offset;
      const heading=yaw-dyaw,c=Math.cos(heading),s=Math.sin(heading);
      pose=[position.x-c*dx+s*dy,position.y-s*dx-c*dy,Math.atan2(s,c)];
    }

    perform(async()=>{
      const result=await command(estimate?"web_estimate":"web_goal",{
        ...target.fields,pose,...(estimate?{}:{multi:!pointOnly&&multi}),
      });
      const group=target.fields.target==="formation";
      const message=target.leader && multi && !pointOnly
        ? group?"航点已加入编队路线，使用「执行编队航点」发车":"航点已加入领车路线，使用「执行领车航点」发车"
        : result.message;
      feedback((target.leader?"领车 ":"")+robotName(robot)+" · "+message);
    });
    return true;
  },
  attach(view){
    renderer=view;layerKey=null;syncVehicleLayers();
    view.updateConfig(config=>{
      const markers=config.topics['/fleet/robots'];
      if(markers)markers.namespaces={...markers.namespaces,fleet_heading:{visible:false}};
    });
    const canvas=view.gl.domElement;
    canvas.insertAdjacentElement("afterend",map);
    canvas.insertAdjacentElement("afterend",element("road-tools"));
    element("road-tools").hidden=false;
    element("road-edit").hidden=true;
    const toolbarButtons=[];
    function installMapTools(){
      const native=[...canvas.parentElement.querySelectorAll('button')].find(b=>/^(2D|3D)$/.test(b.textContent.trim()));
      if(!native)return;
      const toolbar=native.parentElement;
      for(const [label,paths,action] of [
        ['保存地图',['M5 3h12l4 4v14H3V3z','M7 3v6h10V3','M7 21v-8h10v8'],()=>openMapDialog('map_save')],
        ['加载地图',['M3 19V5h6l2 3h9v4','M3 19l3-8h16l-3 8z'],()=>openMapDialog('map_load')],
        ['路网工具',['M6 6l12 4-6 9-6-13','M4 4h4v4H4z','M16 8h4v4h-4z','M10 17h4v4h-4z'],()=>{if(roadEditing)finishRoad();else element("road-edit").click();}],
      ]){
        const button=document.createElement('button');
        button.type='button';button.className=native.className;button.title=label;button.setAttribute('aria-label',label);
        const icon=document.createElementNS('http://www.w3.org/2000/svg','svg');
        icon.setAttribute('viewBox','0 0 24 24');icon.setAttribute('width','20');icon.setAttribute('height','20');
        icon.setAttribute('fill','none');icon.setAttribute('stroke','currentColor');icon.setAttribute('stroke-width','1.6');
        icon.setAttribute('stroke-linejoin','round');icon.setAttribute('stroke-linecap','round');icon.setAttribute('aria-hidden','true');
        for(const d of paths){const path=document.createElementNS(icon.namespaceURI,'path');path.setAttribute('d',d);icon.append(path);}
        button.append(icon);Object.assign(button.style,{padding:'5px',minWidth:'30px',height:'30px',color:'inherit'});
        button.onclick=action;toolbar.append(button);toolbarButtons.push(button);
      }
      watcher.disconnect();
    }
    const watcher=new MutationObserver(()=>{if(!toolbarButtons.length)installMapTools();});
    watcher.observe(canvas.parentElement,{childList:true,subtree:true});
    installMapTools();
    const resize=new ResizeObserver(alignEditor);
    resize.observe(canvas);
    let frame=0;
    function moved(){
      cancelAnimationFrame(frame);
      frame=requestAnimationFrame(alignEditor);
    }
    view.addListener("cameraMove",moved);
    alignEditor();
    return ()=>{
      cancelAnimationFrame(frame);resize.disconnect();watcher.disconnect();toolbarButtons.forEach(b=>b.remove());view.removeListener("cameraMove",moved);
      if(renderer===view){
        renderer=undefined;scale=0;element("panel-stock").append(map,element("road-tools"));
        element("road-tools").hidden=true;syncButtons();
      }
    };
  },
  update(){},
};

function mountControl(id){
  return context=>{
    const content=element(id);
    context.panelElement.append(content);
    return ()=>{if(content.parentElement===context.panelElement)element("panel-stock").append(content);};
  };
}

// Register against the same desktop-CN extension catalog as the onboard 124 panels.
const extensionName="local.omnifleet-onboard";
const panels={fleet:mountControl("fleet-panel"),dispatch:mountControl("dispatch-panel")};
const registerTimer=setInterval(()=>{
  const root=document.getElementById("root")._reactRootContainer?.current;
  if(!root)return;
  const stack=[root];
  while(stack.length){
    const f=stack.pop();
    if(!f)continue;
    const values=[f.memoizedProps?.value];
    for(let d=f.dependencies?.firstContext;d;d=d.next)values.push(d.memoizedValue);
    const catalog=values.find(v=>typeof v?.getState==="function" && typeof v.getState()?.installExtension==="function");
    if(!catalog){stack.push(f.child,f.sibling);continue;}
    function register(){
      const snapshot=catalog.getState();
      if(Object.entries(panels).every(([name,init])=>
        snapshot.installedPanels?.[extensionName+"."+name]?.registration.initPanel===init))return;
      const entries={...snapshot.installedPanels};
      for(const [name,initPanel] of Object.entries(panels)){
        entries[extensionName+"."+name]={extensionName,extensionNamespace:"local",registration:{name,initPanel}};
      }
      catalog.setState({installedPanels:entries,installedExtensions:[
        ...(snapshot.installedExtensions??[]).filter(x=>x.id!==extensionName),
        {id:extensionName,qualifiedName:extensionName,namespace:"local",name:"omnifleet-onboard",
         publisher:"local",version:"1.0.0",displayName:"车载协同调度",main:"/native-panels.js"}]});
    }
    clearInterval(registerTimer);catalog.subscribe(register);register();break;
  }
},150);
