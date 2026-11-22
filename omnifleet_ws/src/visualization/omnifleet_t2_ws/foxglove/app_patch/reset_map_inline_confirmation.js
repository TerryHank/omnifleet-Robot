const confirmMapReset=()=>new Promise(resolve=>{
const dialog=document.createElement('dialog');dialog.id='omnifleet-map-reset-confirmation';
dialog.style.cssText='border:1px solid #aaa;border-radius:8px;padding:20px;max-width:420px;background:#fff;color:#222;font:14px/1.6 system-ui,sans-serif';
dialog.innerHTML='<h3 style="margin:0 0 10px">清空当前地图并重新建图？</h3><p>请先停止导航。定位原点会重置，之后需要重新设置航点。已保存的地图文件不会删除。</p><div style="display:flex;justify-content:flex-end;gap:10px"><button type="button" data-reset-cancel autofocus>取消</button><button type="button" data-reset-confirm>清空并重新建图</button></div>';
for(const b of dialog.querySelectorAll('button'))b.style.cssText='padding:7px 12px;border:1px solid #aaa;border-radius:4px;font:inherit;cursor:pointer';
dialog.querySelector('[data-reset-confirm]').style.background='#b3261e';dialog.querySelector('[data-reset-confirm]').style.color='#fff';
let done=false;const finish=value=>{if(done)return;done=true;dialog.close();dialog.remove();if(resetButton.isConnected)resetButton.focus();resolve(value)};
dialog.querySelector('[data-reset-cancel]').onclick=()=>finish(false);
dialog.querySelector('[data-reset-confirm]').onclick=()=>finish(true);
dialog.addEventListener('cancel',event=>{event.preventDefault();finish(false)});
document.body.append(dialog);dialog.showModal();
});
resetButton.addEventListener('click',async()=>{
resetButton.disabled=true;
try{
if(!await confirmMapReset())return;
saveButton.disabled=true;loadButton.disabled=true;
const result=await mapSvc('/omnifleet_t2/nav2/reset_map',{});
if(result?.success!==true)throw new Error(result?.message||'重置未确认');
flash(resetButton,true,result.message);l(result.message);
}catch(error){const message='清空地图未确认：'+String(error);flash(resetButton,false,message);l(message)}
finally{resetButton.disabled=false;saveButton.disabled=false;loadButton.disabled=false}
});
