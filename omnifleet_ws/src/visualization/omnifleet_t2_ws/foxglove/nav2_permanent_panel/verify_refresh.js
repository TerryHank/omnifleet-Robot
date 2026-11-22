(async()=>{
 document.querySelector('[data-testid="nav2-refresh-saved"]').click();
 await new Promise(r=>setTimeout(r,1500));
 return {value:document.querySelector('[data-testid="nav2-input-linear_speed"]').value,status:document.querySelector('[data-testid="nav2-save-status"]').textContent};
})()
