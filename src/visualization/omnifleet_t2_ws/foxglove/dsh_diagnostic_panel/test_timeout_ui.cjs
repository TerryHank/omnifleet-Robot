const {JSDOM}=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/jsdom');const assert=require('assert');
(async()=>{
const dom=new JSDOM('<div><div id="panel"></div></div>');global.document=dom.window.document;global.crypto=require('crypto').webcrypto;
const originalSet=global.setTimeout,originalClear=global.clearTimeout;const tasks=new Map();let next=1;
global.setTimeout=(fn,ms)=>{const id=next++;tasks.set(id,{fn,ms});return id;};global.clearTimeout=id=>tasks.delete(id);
let sent;const ctx={panelElement:document.querySelector('#panel'),advertise(){},watch(){},subscribe(){},publish(t,m){sent=JSON.parse(m.data);}};
try{
const {initDshDiagnosticPanel}=await import('./DshDiagnosticPanel.mjs');const dispose=initDshDiagnosticPanel(ctx);const input=document.querySelector('[data-testid="dsh-question"]');const button=document.querySelector('[data-testid="dsh-ask"]');input.value='why';button.click();
[...tasks.values()].find(x=>x.ms===10000).fn();assert(document.querySelector('.dsh-answer-text').textContent.includes('未收到请求确认'));assert(!button.disabled);
button.click();ctx.onRender({currentFrame:[{topic:'/omnifleet_t2/diagnostics/answer',message:{data:JSON.stringify({request_id:sent.request_id,status:'thinking',stage:'first_model_token',answer:'生成中'})}}]},()=>{});
assert(![...tasks.values()].some(x=>x.ms===10000));[...tasks.values()].find(x=>x.ms===75000).fn();assert(document.querySelector('.dsh-answer-text').textContent.includes('模型仍在处理'));
ctx.onRender({currentFrame:[{topic:'/omnifleet_t2/diagnostics/answer',message:{data:JSON.stringify({request_id:sent.request_id,status:'complete',answer:'迟到结果',captured_at:1})}}]},()=>{});assert(document.querySelector('.dsh-answer-text').textContent.includes('迟到结果'));dispose();console.log('PASS no-ack vs generating timeout; late result recovery');
}finally{global.setTimeout=originalSet;global.clearTimeout=originalClear;}
})().catch(e=>{console.error(e);process.exitCode=1;});
