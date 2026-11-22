(async()=>{
  const input=document.querySelector('[data-testid="nav2-input-linear_speed"]');
  const button=document.querySelector('[data-testid="nav2-save-linear_speed"]');
  if(!input || input.disabled || button.disabled) throw Error('Speed control not ready');
  input.value='0.35';
  button.click();
  const start=Date.now();
  while(button.disabled && Date.now()-start<15000) await new Promise(r=>setTimeout(r,100));
  return {status:document.querySelector('[data-testid="nav2-save-status"]').textContent,value:input.value,disabled:button.disabled};
})()
