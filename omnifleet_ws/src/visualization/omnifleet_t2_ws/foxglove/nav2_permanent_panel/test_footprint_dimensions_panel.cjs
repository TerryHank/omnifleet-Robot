const {JSDOM,VirtualConsole}=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');
const assert=require('assert');
const dom=new JSDOM('<div id="panel"></div>',{virtualConsole:new VirtualConsole()});
global.document=dom.window.document;global.window=dom.window;global.CustomEvent=dom.window.CustomEvent;
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));let dispose;
(async()=>{
 const {initNav2HotParamsPanel}=await import('./Nav2PermanentPanel.js');
 const footprint='[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]';
 const saved={
  geometry_local_footprint:{footprint},geometry_global_footprint:{footprint},
  geometry_local_robot_radius:{robot_radius:.01},geometry_global_robot_radius:{robot_radius:.01},
  geometry_local_footprint_padding:{footprint_padding:0},geometry_global_footprint_padding:{footprint_padding:0},
  geometry_local_inflation_radius:{inflation_radius:.4},geometry_global_inflation_radius:{inflation_radius:.4},
  geometry_mppi_consider_footprint:{consider_footprint:true},
 };
 let mode='body';const calls=[];
 const data=()=>({saved,collision_model:{mode,restore_available:true},algorithms:{global:{current:'smac_2d'},local:{current:'rpp'}},parameter_links:{}});
 const context={panelElement:document.querySelector('#panel'),initialState:{},saveState:()=>{},watch:()=>{},subscribe:()=>{},advertise:()=>{},unadvertise:()=>{},callService:async(service,request)=>{
  if(service.endsWith('/read_saved'))return {success:true,message:JSON.stringify(data())};
  if(request.parameters?.some(parameter=>parameter.name.endsWith('_footprint'))){
   calls.push(request.parameters);
   for(const parameter of request.parameters){saved[parameter.name].footprint=parameter.value.string_value;}
   mode='custom';
   return {results:request.parameters.map(()=>({successful:true,reason:JSON.stringify({...data(),restart_required:true,runtime_confirmed:false,runtime:{geometry:'永久保存成功；重启后生效'}})}))};
  }
  return {results:[{successful:true,reason:JSON.stringify({strategy:'sequential',status:'idle',command:'',startup_mode:'mapping'})}]};
 }};
 dispose=initNav2HotParamsPanel(context);
 const nav=()=>context.onRender({currentFrame:[{topic:'/navigation/status',message:{data:JSON.stringify({navigation_active:false})}}]},()=>{});
 await delay(650);nav();
 const input=id=>document.querySelector('[data-testid="nav2-input-'+id+'"]');
 assert.equal(input('geometry_local_footprint'),null);
 assert.equal(input('geometry_global_footprint'),null);
 const length=input('geometry_body_half_length'),width=input('geometry_body_half_width');
 assert(length && width);
 assert.equal(length.value,'0.25');assert.equal(width.value,'0.185');
 const edit=async(element,value)=>{element.value=value;element.dispatchEvent(new dom.window.Event('input'));element.dispatchEvent(new dom.window.Event('blur'));await delay(60);};
 await edit(width,'0.2');
 assert.equal(calls.length,1);assert.deepEqual(calls[0].map(parameter=>parameter.name),['geometry_local_footprint','geometry_global_footprint']);
 assert.deepEqual(JSON.parse(calls[0][0].value.string_value),[[.25,.2],[.25,-.2],[-.25,-.2],[-.25,.2]]);
 assert.equal(calls[0][0].value.type,4);assert.equal(calls[0][0].value.string_value,calls[0][1].value.string_value);
 nav();await edit(length,'0.3');
 assert.deepEqual(JSON.parse(calls[1][0].value.string_value),[[.3,.2],[.3,-.2],[-.3,-.2],[-.3,.2]]);
 assert.equal(length.value,'0.3');assert.equal(width.value,'0.2');
 saved.geometry_global_footprint.footprint='[[0.4,0.2],[0.4,-0.2],[-0.4,-0.2],[-0.4,0.2]]';
 await document.querySelector('[data-testid="nav2-refresh-saved"]').onclick();nav();
 assert.equal(length.value,'');assert(length.placeholder.includes('不是一致的中心矩形'));
 const search=document.querySelector('[data-testid="nav2-parameter-search"]');search.value='半宽';search.dispatchEvent(new dom.window.Event('input'));
 assert(document.querySelector('[data-parameter-id="geometry_body_half_width"]'));
 dispose();console.log('PASS: half-length/half-width inputs generate paired rectangular footprints and reject inconsistent saved shapes');
})().catch(error=>{dispose?.();console.error(error);process.exitCode=1;});
