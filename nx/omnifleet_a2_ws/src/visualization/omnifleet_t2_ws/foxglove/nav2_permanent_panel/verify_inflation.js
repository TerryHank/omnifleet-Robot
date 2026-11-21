(async()=>{
  const results=[];
  for(const id of ['local_radius','global_radius']){
    const button=document.querySelector('[data-testid="nav2-save-'+id+'"]');
    if(!button || button.disabled) throw Error('Parameter control not ready');
    button.click();
    const start=Date.now();
    while(button.disabled && Date.now()-start<14000) await new Promise(r=>setTimeout(r,100));
    results.push({id,status:document.querySelector('[data-testid="nav2-save-status"]').textContent});
  }
  return results;
})()
