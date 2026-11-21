const updateRouteOptions=(0,wn.c)({topic:"/omnifleet_t2/waypoints/update",schemaName:"std_msgs/msg/String",datatypes:jn,name:"连续路线与停靠设置"});
const [routeFilter,setRouteFilter]=(0,p.useState)("");
const [radiusDraft,setRadiusDraft]=(0,p.useState)(null);
const [waitDrafts,setWaitDrafts]=(0,p.useState)({});
// RENDER
const routeInputStyle={width:"100%",boxSizing:"border-box",padding:6,border:"1px solid #aaa",borderRadius:4,background:"inherit",color:"inherit"};
const routePhases={idle:"待开始",preplanning:"整条路线检查中",tracking:"连续跟踪中",replanning:"剩余路线重规划中",stopping:"确认底盘停止",waiting:"停靠等待中",completed:"整条路线完成",failed:"路线失败",canceled:"已停止",canceling:"正在取消",cancel_unconfirmed:"取消未确认",preview_ready:"预规划通过",single_point:"单点导航"};
const routeControls=(0,n.jsxs)("div",{"data-testid":"continuous-route-settings",style:{display:"grid",gap:6,margin:"10px 0"},children:[
 (0,n.jsxs)("label",{children:["途经半径（米）",(0,n.jsx)("input",{"data-testid":"route-pass-radius",type:"number",min:.05,max:.5,step:.01,style:routeInputStyle,disabled:U||!V,value:radiusDraft??i?.pass_radius??.25,onChange:ev=>setRadiusDraft(ev.target.value),onBlur:ev=>{const value=Number(ev.target.value);if(ev.target.value.trim()&&Number.isFinite(value)&&value>=.05&&value<=.5){updateRouteOptions({data:JSON.stringify({pass_radius:value})});setRadiusDraft(null)}else l("途经半径必须在0.05到0.50米之间")}})]}),
 (0,n.jsx)(mt.c,{"data-testid":"route-convert-pass",disabled:U||!V||K.length<2,variant:"outlined",size:"small",onClick:()=>updateRouteOptions({data:JSON.stringify({convert_intermediate:true})}),children:"将中间点改为途经点"}),
 (0,n.jsx)("small",{children:"新点默认途经；旧路线保留停靠。最终点始终停车、对齐。蓝色：整条预览；绿色：连续执行；灰色：规划结果（含单点）。"}),
 (0,n.jsx)("div",{"data-testid":"route-execution-phase",children:`整条预览：${({empty:"无航点",waiting:"等待就绪",pending:"待规划",planning:"规划中",ready:"已就绪",failed:"规划失败"})[i?.route_preview?.state]??"等待"}；执行：${routePhases[i?.execution?.phase??"idle"]??i?.execution?.phase}${i?.execution?.phase==="waiting"?`，剩余 ${Number(i.execution.remaining_wait).toFixed(1)} 秒`:""}`}),
 (0,n.jsx)("div",{"data-testid":"route-localization-health",children:i?.execution?.localization_status??"等待定位状态"}),
 (0,n.jsx)("input",{"data-testid":"route-point-search",placeholder:"搜索航点名称、途经或停靠",style:routeInputStyle,value:routeFilter,onChange:ev=>setRouteFilter(ev.target.value)})
]});
const renderRouteOptions=ve=>{
 const final=ve.index===K.length,kind=final?"stop":ve.kind??"stop";
 return (0,n.jsxs)("div",{"data-testid":"route-options-"+ve.index,style:{display:"grid",gap:6,padding:8,border:"1px solid #ddd",borderRadius:4},children:[
  (0,n.jsxs)("label",{children:[final?"最终点：停车并对齐":"航点类型",(0,n.jsxs)("select",{"data-testid":"route-kind-"+ve.index,style:routeInputStyle,disabled:U||!V||final,value:kind,onChange:ev=>updateRouteOptions({data:JSON.stringify({index:ve.index,kind:ev.target.value})}),children:[(0,n.jsx)("option",{value:"pass",children:"途经：连续通过"}),(0,n.jsx)("option",{value:"stop",children:"停靠：停车并对齐"})]})]}),
  (0,n.jsxs)("label",{children:["停稳后等待（秒）",(0,n.jsx)("input",{"data-testid":"route-dwell-"+ve.index,type:"number",min:0,max:600,step:.1,style:routeInputStyle,disabled:U||!V||kind==="pass",value:waitDrafts[ve.index]??ve.dwell_seconds??0,onChange:ev=>setWaitDrafts(old=>({...old,[ve.index]:ev.target.value})),onBlur:ev=>{const value=Number(ev.target.value);if(ev.target.value.trim()&&Number.isFinite(value)&&value>=0&&value<=600){updateRouteOptions({data:JSON.stringify({index:ve.index,dwell_seconds:value})});setWaitDrafts(old=>{const next={...old};delete next[ve.index];return next})}else l("等待时间必须在0到600秒之间")}})]}),
  (0,n.jsx)("small",{children:i?.execution?.waypoint_states?.[ve.index-1]??"待通过"})
 ]});
};
