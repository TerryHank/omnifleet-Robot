const assert=require('assert');
const {JSDOM}=require('jsdom');
const THREE=require(require('path').join(require('path').dirname(require.resolve('three')), 'three.cjs'));
const dom=new JSDOM('<div style="position:relative"><canvas></canvas></div>');global.window=dom.window;global.document=dom.window.document;
const api=require('./waypoint-drag.js');const canvas=document.querySelector('canvas');canvas.getBoundingClientRect=()=>({left:0,top:0,width:1000,height:1000});
const camera=new THREE.OrthographicCamera(-5,5,5,-5,.1,100);camera.position.set(0,0,10);camera.lookAt(0,0,0);camera.updateMatrixWorld();
const renderer={gl:{domElement:canvas},cameraHandler:{getActiveCamera:()=>camera},followFrameId:'map',publishClickTool:{state:'idle'},addListener:()=>{},removeListener:()=>{}};
const published=[];const context={advertise:()=>{},unadvertise:()=>{},publish:(t,m)=>published.push([t,JSON.parse(m.data)])};const dispose=api.attach(renderer,context);
let catalog={frame_id:'map',navigation_active:false,waypoints:[{index:1,name:'航点1',x:1,y:1,yaw_deg:30}]};
function update(active=false){api.update(renderer,context,[{topic:'/omnifleet_t2/waypoints/catalog',message:{data:JSON.stringify(catalog)}},{topic:'/navigation/status',message:{data:JSON.stringify({navigation_active:active})}}]);}
function mouse(target,type,x,y){target.dispatchEvent(new dom.window.MouseEvent(type,{clientX:x,clientY:y,button:0,bubbles:true,cancelable:true}));}
update();mouse(canvas,'pointerdown',600,400);mouse(window,'pointermove',650,350);mouse(window,'pointerup',650,350);
assert.equal(published.length,1);assert.equal(published[0][0],'/omnifleet_t2/waypoints/update');let request=published[0][1];assert(Math.abs(request.position.x-1.5)<1e-6);assert(Math.abs(request.position.y-1.5)<1e-6);assert.equal(request.index,1);assert.deepEqual(request.previous_position,{x:1,y:1});assert.equal(request.frame_id,'map');
catalog.waypoints[0].x=1.5;catalog.waypoints[0].y=1.5;update();assert(document.querySelector('[data-waypoint-drag-status]').textContent.includes('已保存'));
mouse(canvas,'pointerdown',650,350);mouse(window,'pointermove',675,325);window.dispatchEvent(new dom.window.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));mouse(window,'pointerup',675,325);assert.equal(published.length,1);
update(true);mouse(canvas,'pointerdown',650,350);mouse(window,'pointermove',675,325);mouse(window,'pointerup',675,325);assert.equal(published.length,1);
update(false);mouse(canvas,'pointerdown',650,350);mouse(window,'pointermove',675,325);update(true);mouse(window,'pointerup',675,325);assert.equal(published.length,1);
renderer.followFrameId='odom';update(false);mouse(canvas,'pointerdown',650,350);mouse(window,'pointermove',675,325);mouse(window,'pointerup',675,325);assert.equal(published.length,1);
renderer.followFrameId='map';update(false);mouse(canvas,'pointerdown',900,900);mouse(window,'pointermove',925,925);mouse(window,'pointerup',925,925);assert.equal(published.length,1);
dispose();assert(!document.querySelector('[data-waypoint-drag-overlay]'));
console.log('PASS: 3D projection, drag request, backend acknowledgement, Esc, active/start-during-drag guards, frame guard, empty-space pan, cleanup');
