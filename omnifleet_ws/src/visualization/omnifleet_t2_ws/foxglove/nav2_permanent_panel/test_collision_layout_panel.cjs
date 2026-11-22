const {JSDOM,VirtualConsole}=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');
const assert=require('assert'),fs=require('fs');
const fields=JSON.parse(fs.readFileSync(__dirname+'/geometry-fields.test.json','utf8'));
const dom=new JSDOM('<div id="panel"></div>',{virtualConsole:new VirtualConsole()});
global.document=dom.window.document;global.window=dom.window;global.CustomEvent=dom.window.CustomEvent;
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
const delay=ms=>new Promise(r=>setTimeout(r,ms));let dispose;
(async()=>{
 const {initNav2HotParamsPanel}=await import('./Nav2PermanentPanel.js');
 const saved={local_radius:{inflation_radius:.01},global_radius:{inflation_radius:.01},local_padding:{footprint_padding:0},global_padding:{footprint_padding:0}};
 for(const f of fields){const key=f[0],leaf=key.startsWith('geometry_mppi')?'consider_footprint':key.replace(/^geometry_(local|global)_/,'');saved[key]={[leaf]:key.includes('consider_footprint')?false:key.endsWith('_footprint')?'[]':key.includes('padding')?0:.01};}
 let mode='point';const calls=[];
 const data=()=>({saved,collision_model:{mode,restore_available:true,applies_to:'next_restart'},algorithms:{global:{current:'smac_2d'},local:{current:'mppi'}},parameter_links:{}});
 const context={panelElement:document.querySelector('#panel'),initialState:{},saveState:()=>{},watch:()=>{},subscribe:()=>{},advertise:()=>{},unadvertise:()=>{},callService:async(service,request)=>{
  if(service.endsWith('/read_saved'))return {success:true,message:JSON.stringify(data())};
  const p=request.parameters?.[0];
  if(p?.name==='__collision_model'){
   calls.push(p);mode=p.value.string_value;
   for(const scope of ['local','global']) saved['geometry_'+scope+'_footprint'].footprint=mode==='point'?'[]':'[[0.25,0.18],[0.25,-0.18],[-0.25,-0.18],[-0.25,0.18]]';
   return {results:[{successful:true,reason:JSON.stringify({...data(),message:'模型已保存，重启生效'})}]};
  }

  if(p?.name.startsWith('geometry_')){
   calls.push(p);const leaf=Object.keys(saved[p.name])[0];saved[p.name][leaf]=p.value.type===4?p.value.string_value:p.value.type===1?p.value.bool_value:p.value.double_value;mode='custom';
   return {results:[{successful:true,reason:JSON.stringify({...data(),runtime_confirmed:false,runtime:{[p.name]:'永久保存成功；该参数需重启导航栈后生效'}})}]};
  }
  return {results:[{successful:true,reason:JSON.stringify({strategy:'sequential',status:'idle',command:'',startup_mode:'mapping'})}]};
 }};
 dispose=initNav2HotParamsPanel(context);
 const nav=active=>context.onRender({currentFrame:[{topic:'/navigation/status',message:{data:JSON.stringify({navigation_active:active})}}]},()=>{});
 await delay(650);nav(false);assert.equal(calls.length,0);
 const uiIds=['geometry_body_half_length','geometry_body_half_width','geometry_local_resolution','geometry_local_robot_radius','geometry_local_footprint_padding','geometry_local_inflation_radius','geometry_global_robot_radius','geometry_global_footprint_padding','geometry_global_inflation_radius','geometry_mppi_consider_footprint'];
 for(const id of uiIds){const input=document.querySelector('[data-testid="nav2-input-'+id+'"]');assert(input && !input.disabled,id);assert.equal(input.closest('details').dataset.sectionKey,'group:全局与局部代价地图共用');}
 const select=document.querySelector('[data-testid="nav2-collision-model"]');
 const row=id=>document.querySelector('[data-testid="nav2-input-'+id+'"]').closest('.row');
 assert.equal([...document.querySelectorAll('details')].filter(x=>x.dataset.sectionKey==='group:碰撞模型详细参数 · 修改后重启生效').length,0);
 assert.equal(row('geometry_body_half_length').hidden,true);assert.equal(row('geometry_body_half_width').hidden,true);
 assert.equal(row('geometry_local_robot_radius').hidden,false);
 assert.equal(row('geometry_local_inflation_radius').hidden,false);
 assert.equal(row('costmap_radius').hidden,true);
 assert.equal(row('costmap_padding').hidden,true);
 select.value='body';select.dispatchEvent(new dom.window.Event('change'));await delay(60);nav(false);
 assert.equal(row('geometry_body_half_length').hidden,false);assert.equal(row('geometry_body_half_width').hidden,false);
 assert.equal(row('geometry_local_robot_radius').hidden,true);
 assert.equal(row('geometry_local_footprint_padding').hidden,false);
 select.value='point';select.dispatchEvent(new dom.window.Event('change'));await delay(60);nav(false);
 assert.equal(row('geometry_body_half_length').hidden,true);assert.equal(row('geometry_body_half_width').hidden,true);
 assert.equal(row('geometry_local_robot_radius').hidden,false);
 assert.equal(document.querySelector('[data-testid="nav2-input-geometry_local_footprint"]'),null);
 const edit=async(input,value)=>{input.value=value;input.dispatchEvent(new dom.window.Event('input'));input.dispatchEvent(new dom.window.Event('blur'));await delay(40);};
 await edit(document.querySelector('[data-testid="nav2-input-geometry_global_robot_radius"]'),'.07');assert.equal(calls.at(-1).value.double_value,.07);
 const checkbox=document.querySelector('[data-testid="nav2-input-geometry_mppi_consider_footprint"]');checkbox.checked=true;checkbox.dispatchEvent(new dom.window.Event('change'));await delay(40);assert.deepEqual(calls.at(-1).value,{type:1,bool_value:true});
 assert.equal(document.querySelector('[data-testid="nav2-collision-model"]').value,'custom');
 assert(document.querySelector('[data-testid="nav2-save-status"]').textContent.includes('重启'));
 nav(true);for(const id of uiIds)assert(document.querySelector('[data-testid="nav2-input-'+id+'"]')?.disabled);
 nav(false);await delay(3100);assert(document.querySelector('[data-testid="nav2-input-geometry_local_robot_radius"]').disabled);nav(false);assert(!document.querySelector('[data-testid="nav2-input-geometry_local_robot_radius"]').disabled);
 const search=document.querySelector('[data-testid="nav2-parameter-search"]');
 for(const term of ['footprint','robot_radius','footprint_padding','inflation_radius','consider_footprint']){search.value=term;search.dispatchEvent(new dom.window.Event('input'));assert(document.querySelector('[data-parameter-id^="geometry_"]'),term);}
 dispose();console.log('PASS: one merged card; half-dimension point/body visibility; duplicate controls hidden; model save contract; typed field saves; nav/stale guards; search');
})().catch(e=>{dispose?.();console.error(e);process.exitCode=1;});
