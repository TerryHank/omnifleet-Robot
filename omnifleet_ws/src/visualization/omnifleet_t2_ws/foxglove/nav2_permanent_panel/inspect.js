JSON.stringify({
  status: document.querySelector('[data-testid="nav2-save-status"]')?.textContent,
  inputs: [...document.querySelectorAll('.omnifleet-nav2-hot-params input')].map(x=>({id:x.dataset.testid,value:x.value,disabled:x.disabled})),
  text: document.querySelector('.omnifleet-nav2-hot-params')?.innerText,
});
