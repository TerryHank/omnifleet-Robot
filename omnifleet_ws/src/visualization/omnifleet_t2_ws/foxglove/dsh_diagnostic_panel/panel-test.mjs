export function initDshDiagnosticPanel(context) {
  const root = context.panelElement, host = root.parentElement, oldPosition = host.style.position;
  host.style.position = 'relative';
  root.style.cssText = 'position:absolute;inset:0;display:flex;flex-direction:column;min-height:0;box-sizing:border-box;padding:10px;gap:8px;overflow:hidden;background:#fff;color:#222;font-size:19.5px;line-height:1.5;font-family:system-ui,sans-serif';
  root.innerHTML = `<style>
  .dsh-question-row{display:flex;gap:6px;flex-shrink:0}
  .dsh-question-row input{min-width:0;flex:1;font:inherit;padding:7px;border:1px solid #aaa;border-radius:4px}
  .dsh-question-row button,.dsh-answer button{font:inherit;border:0;background:#3478f6;color:white;border-radius:4px;padding:6px 10px;cursor:pointer}
  .dsh-question-row button:disabled{opacity:.5;cursor:wait}
  .dsh-answer{min-height:70px;flex:1;overflow:auto;padding:9px;background:#f3f5f7;border-radius:5px;overflow-wrap:anywhere}
  .dsh-answer-text{white-space:pre-wrap}
  .dsh-answer button{margin:7px 6px 0 0}
  .dsh-meta{font-size:16.5px;color:#666;flex-shrink:0}
  </style><div class="dsh-question-row"><input data-testid="dsh-question" aria-label="问题" maxlength="4000" placeholder="例如：为什么发航点后不动？"><button type="button" data-testid="dsh-ask">诊断</button></div><div class="dsh-answer" data-testid="dsh-answer" role="status" aria-live="polite"><div class="dsh-answer-text">输入问题，DSH 会结合当前话题、参数、地图和错误信息分析。</div><div class="dsh-parameter-links"></div></div><div class="dsh-meta">只读诊断，结果不会自动修改参数或让机器人运动。</div>`;
  const question = root.querySelector('[data-testid="dsh-question"]');
  const ask = root.querySelector('[data-testid="dsh-ask"]');
  const answer = root.querySelector('.dsh-answer-text');
  const links = root.querySelector('.dsh-parameter-links');
  const meta = root.querySelector('.dsh-meta');
  const QUESTION = '/omnifleet_t2/diagnostics/question', ANSWER = '/omnifleet_t2/diagnostics/answer';
  let requestId = '', timer, disposed = false, topics = [];
  const finish = () => { clearTimeout(timer); ask.disabled = false; };
  const show = text => { answer.textContent = text; links.replaceChildren(); };
  if (context.advertise && context.publish) {
    context.advertise(QUESTION, 'std_msgs/msg/String', {datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string'}]}]])});
  } else { ask.disabled = true; show('当前连接不支持提问，请连接 113 的 Foxglove Bridge。'); }
  function submit() {
    const text = question.value.trim();
    if (!text || ask.disabled || disposed) return;
    requestId = crypto.randomUUID();
    ask.disabled = true; show('正在请求本次诊断……');
    try {
      context.publish(QUESTION,{data:JSON.stringify({request_id:requestId,question:text,foxglove:{topic_names:topics}})});
      timer = setTimeout(() => { if (!disposed) { requestId = ''; finish(); show('诊断等待超时，请检查 DSH 和诊断服务后重试。'); } },150000);
    } catch (error) { finish(); show('提问失败：'+String(error)); }
  }
  ask.onclick = submit;
  question.onkeydown = event => { if (event.key === 'Enter' && !event.isComposing) { event.preventDefault(); submit(); } };
  context.watch('topics'); context.watch('currentFrame'); context.subscribe([{topic:ANSWER}]);
  context.onRender = (state,done) => {
    try {
      if (disposed) return;
      if (state.topics) topics = state.topics.map(t=>t.name).slice(0,200);
      for (const event of state.currentFrame || []) {
        if (event.topic !== ANSWER) continue;
        let result;
        try { result = JSON.parse(event.message.data); } catch { continue; }
        if (result.request_id !== requestId) continue;
        show(String(result.answer || '正在诊断……'));
        if (result.status === 'complete' || result.status === 'error') {
          finish();
          if (result.status === 'complete') {
            meta.textContent = '数据采集：' + new Date(result.captured_at*1000).toLocaleTimeString() + ' · DSH 只读诊断';
            for (const id of (result.parameter_ids || []).slice(0,3)) {
              if (typeof id !== 'string' || !/^[a-z0-9_]+$/.test(id)) continue;
              const button = document.createElement('button'); button.textContent = '定位：'+(result.parameter_labels?.[id] || id);
              button.onclick = () => {
                const field = document.querySelector('[data-testid="nav2-input-'+id+'"]');
                if (field) { field.scrollIntoView({block:'center'}); field.focus({preventScroll:true}); }
                else meta.textContent = '该参数未在当前算法栏显示，请先核对所用算法；不会自动切换算法。';
              };
              links.append(button);
            }
          }
        }
      }
    } finally { done(); }
  };
  return () => { disposed = true; clearTimeout(timer); context.onRender = undefined; context.subscribe([]); context.unadvertise?.(QUESTION); host.style.position = oldPosition; };
}
