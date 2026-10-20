const {JSDOM,VirtualConsole}=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');
const assert=require('assert');
const dom=new JSDOM('<div id="panel"></div>',{virtualConsole:new VirtualConsole()});
global.document=dom.window.document;global.window=dom.window;global.CustomEvent=dom.window.CustomEvent;
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let dispose;
(async()=>{
 const {initNav2HotParamsPanel}=await import('./Nav2PermanentPanel.js');
 let mode='body', fail=false, calls=[];
 const saved={local_radius:{inflation_radius:.4},global_radius:{inflation_radius:.4},local_padding:{footprint_padding:.05},global_padding:{footprint_padding:.05}};
 const data=()=>({saved,collision_model:{mode,restore_available:true,applies_to:'next_restart'},algorithms:{global:{current:'smac_2d'},local:{current:'mppi'}},parameter_links:{}});
 const context={panelElement:document.querySelector('#panel'),initialState:{},saveState:()=>{},watch:()=>{},subscribe:()=>{},advertise:()=>{},unadvertise:()=>{},callService:async(service,request)=>{
  if(service.endsWith('/read_saved'))return {success:true,message:JSON.stringify(data())};
  const p=request.parameters?.[0];
  if(p?.name==='__collision_model'){
   calls.push(p);if(fail)return {results:[{successful:false,reason:'测试保存失败'}]};
   mode=p.value.string_value;return {results:[{successful:true,reason:JSON.stringify({...data(),message:'已永久保存；重启导航栈后生效',runtime_confirmed:false})}]};
  }
  return {results:[{successful:true,reason:JSON.stringify({strategy:'sequential',status:'idle',command:'',startup_mode:'mapping'})}]};
 }};
 dispose=initNav2HotParamsPanel(context);
 const nav=active=>context.onRender({currentFrame:[{topic:'/navigation/status',message:{data:JSON.stringify({navigation_active:active})}}]},()=>{});
 await delay(650);const select=document.querySelector('[data-testid="nav2-collision-model"]');
 assert(select && select.disabled);assert.equal(calls.length,0);nav(false);assert(!select.disabled && select.value==='body');
 const section=select.closest('details');assert.equal(section.dataset.sectionKey,'group:全局与局部代价地图共用');
 select.value='point';select.dispatchEvent(new dom.window.Event('change'));await delay(20);
 assert.equal(calls.length,1);assert.equal(calls[0].value.string_value,'point');assert(document.querySelector('[data-testid="nav2-save-status"]').textContent.includes('重启'));
 assert(document.querySelector('[data-testid="nav2-input-costmap_radius"]').disabled);
 nav(true);assert(select.disabled);select.value='body';select.dispatchEvent(new dom.window.Event('change'));await delay(20);assert.equal(calls.length,1);
 nav(false);select.value='body';select.dispatchEvent(new dom.window.Event('change'));await delay(20);assert.equal(calls.length,2);assert(!document.querySelector('[data-testid="nav2-input-costmap_padding"]').disabled);
 fail=true;select.value='point';select.dispatchEvent(new dom.window.Event('change'));await delay(20);assert.equal(select.value,'body');
 const search=document.querySelector('[data-testid="nav2-parameter-search"]');search.value='点模型';search.dispatchEvent(new dom.window.Event('input'));const hit=document.querySelector('[data-parameter-id="collision_model"]');assert(hit);hit.click();assert.equal(document.activeElement,select);
 await delay(3100);assert(select.disabled);dispose();console.log('PASS: initial state, no auto-enable, point/body save, restart notice, navigation/stale guards, geometry field lock, failed-save rollback, parameter search');
})().catch(e=>{dispose?.();console.error(e);process.exitCode=1});
