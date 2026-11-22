const confirmMapLoadPath=initial=>new Promise(resolve=>{
const dialog=document.createElement('dialog');dialog.id='omnifleet-map-load-path-dialog';
dialog.style.cssText='border:1px solid #aaa;border-radius:8px;padding:20px;max-width:560px;background:#fff;color:#222;font:14px/1.6 system-ui,sans-serif';
const form=document.createElement('form'),label=document.createElement('label'),input=document.createElement('input'),actions=document.createElement('div'),cancel=document.createElement('button'),confirm=document.createElement('button');
label.textContent='确认机器人上的地图完整路径（支持 .mm、.simplemap 或不带扩展名的前缀）';input.value=initial;input.required=true;input.style.cssText='box-sizing:border-box;width:100%;margin:10px 0;padding:8px';input.setAttribute('data-map-load-path','');
cancel.type='button';cancel.textContent='取消';confirm.type='submit';confirm.textContent='加载地图及航点';confirm.setAttribute('data-map-load-confirm','');actions.style.cssText='display:flex;justify-content:flex-end;gap:10px';
const finish=value=>{dialog.close();dialog.remove();resolve(value)};
cancel.onclick=()=>finish(null);dialog.addEventListener('cancel',event=>{event.preventDefault();finish(null)});
form.onsubmit=event=>{event.preventDefault();const path=input.value.trim();if(!path.startsWith('/')&&!path.startsWith('~/')){input.setCustomValidity('请输入机器人上的绝对路径');input.reportValidity();return}finish(path)};
input.oninput=()=>input.setCustomValidity('');actions.append(cancel,confirm);form.append(label,input,actions);dialog.append(form);document.body.append(dialog);dialog.showModal();input.focus();input.select();
});
