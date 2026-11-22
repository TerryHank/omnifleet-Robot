const {JSDOM,VirtualConsole}=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');
const assert=require('assert');
const dom=new JSDOM('<div id="panel"></div>',{virtualConsole:new VirtualConsole()});
global.document=dom.window.document;global.window=dom.window;global.CustomEvent=dom.window.CustomEvent;
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
const delay=ms=>new Promise(r=>setTimeout(r,ms));let dispose;
(async()=>{
 const {initNav2HotParamsPanel}=await import('./Nav2PermanentPanel.js');
 const saved={};const suffixes=['footprint','robot_radius','footprint_padding','inflation_radius'];
 for(const scope of ['local','global'])for(const suffix of suffixes)saved['geometry_'+scope+'_'+suffix]={[suffix]:suffix==='footprint'?'[]':suffix==='footprint_padding'?0:.01};
 saved.geometry_mppi_consider_footprint={consider_footprint:false};
 let mode='point';const calls=[];
 const data=()=>({saved,collision_model:{mode,restore_available:true},algorithms:{global:{current:'smac_2d'},local:{current:'mppi'}},parameter_links:{}});
 const context={panelElement:document.querySelector('#panel'),initialState:{},saveState:()=>{},watch:()=>{},subscribe:()=>{},advertise:()=>{},unadvertise:()=>{},callService:async(service,request)=>{
  if(service.endsWith('/read_saved'))return {success:true,message:JSON.stringify(data())};
  if(request.parameters?.[0]?.name.startsWith('geometry_')){
   calls.push(request.parameters);
   for(const p of request.parameters){const leaf=Object.keys(saved[p.name])[0];saved[p.name][leaf]=p.value.type===4?p.value.string_value:p.value.type===1?p.value.bool_value:p.value.double_value;}
   mode='custom';return {results:request.parameters.map(()=>({successful:true,reason:JSON.stringify({...data(),restart_required:true,runtime_confirmed:false})}))};
  }
  return {results:[{successful:true,reason:JSON.stringify({strategy:'sequential',status:'idle',command:'',startup_mode:'mapping'})}]};
 }};
 dispose=initNav2HotParamsPanel(context);
 const nav=active=>context.onRender({currentFrame:[{topic:'/navigation/status',message:{data:JSON.stringify({navigation_active:active})}}]},()=>{});
 const input=id=>document.querySelector('[data-testid="nav2-input-'+id+'"]');
 const row=id=>input(id).closest('.row');
 const visibleGeometry=()=>[...document.querySelectorAll('[data-testid^="nav2-input-geometry_"]')].filter(x=>!x.closest('.row').hidden).map(x=>x.dataset.testid);
 await delay(650);nav(false);assert.equal(calls.length,0);
 assert.equal(visibleGeometry().length,4,visibleGeometry());
 for(const suffix of ['robot_radius','footprint_padding','inflation_radius'])assert(row('geometry_global_'+suffix).hidden);
 assert(row('geometry_body_half_length').hidden);assert(row('geometry_body_half_width').hidden);
 for(const suffix of ['robot_radius','footprint_padding','inflation_radius'])assert(!row('geometry_local_'+suffix).hidden);
 const edit=async(id,value)=>{const x=input(id);x.value=value;x.dispatchEvent(new dom.window.Event('input'));x.dispatchEvent(new dom.window.Event('blur'));await delay(50);};
 for(const [suffix,value] of [['robot_radius','.07'],['footprint_padding','.03'],['inflation_radius','.2']]){
  nav(false);await edit('geometry_local_'+suffix,value);
  const sent=calls.at(-1);assert.deepEqual(sent.map(x=>x.name),['geometry_local_'+suffix,'geometry_global_'+suffix]);assert.deepEqual(sent[0].value,sent[1].value);
  assert.equal(saved['geometry_local_'+suffix][suffix],saved['geometry_global_'+suffix][suffix]);
 }
 assert.equal(visibleGeometry().length,6);
 saved.geometry_local_footprint.footprint=saved.geometry_global_footprint.footprint='[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]';
 mode='body';await document.querySelector('[data-testid="nav2-refresh-saved"]').onclick();nav(false);
 assert.equal(visibleGeometry().length,5);assert(!row('geometry_body_half_length').hidden);assert(!row('geometry_body_half_width').hidden);assert(row('geometry_local_robot_radius').hidden);
 saved.geometry_global_inflation_radius.inflation_radius=.3;
 await document.querySelector('[data-testid="nav2-refresh-saved"]').onclick();nav(false);
 assert.equal(input('geometry_local_inflation_radius').value,'');assert(input('geometry_local_inflation_radius').placeholder.includes('不一致'));
 const count=calls.length;await edit('geometry_local_inflation_radius','.2');assert.equal(calls.length,count+1);assert.equal(calls.at(-1).length,2);
 nav(true);assert(input('geometry_local_inflation_radius').disabled);
 nav(false);await delay(3100);assert(input('geometry_local_inflation_radius').disabled);
 const search=document.querySelector('[data-testid="nav2-parameter-search"]');search.value='inflation_radius';search.dispatchEvent(new dom.window.Event('input'));
 assert(!document.querySelector('[data-parameter-id="geometry_global_inflation_radius"]'));
 dispose();console.log('PASS: point/body/custom geometry controls; half-dimension body inputs; paired atomic requests; mixed-value editing; active/stale guards; deduplicated search');
})().catch(e=>{dispose?.();console.error(e);process.exitCode=1;});
