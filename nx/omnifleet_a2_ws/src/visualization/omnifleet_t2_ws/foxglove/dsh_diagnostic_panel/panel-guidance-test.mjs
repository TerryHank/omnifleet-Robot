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
  .dsh-parameter-links>p{margin:12px 0 0;font-size:.9em;font-weight:600;color:#334155}
  .dsh-parameter-links button{max-width:100%;text-align:left;overflow-wrap:anywhere;border-radius:8px}
  .omnifleet-nav2-hot-params .row.dsh-located-parameter,.omnifleet-nav2-hot-params .algorithm-row.dsh-located-parameter{outline:2px solid #6585ad;outline-offset:3px;border-radius:6px;background:#f1f5fa}
  .dsh-meta{font-size:16.5px;color:#666;flex-shrink:0}
  </style><div class="dsh-question-row"><input data-testid="dsh-question" aria-label="问题" maxlength="4000" placeholder="例如：为什么发航点后不动？"><button type="button" data-testid="dsh-ask">诊断</button></div><div class="dsh-answer" data-testid="dsh-answer" role="status" aria-live="polite"><div class="dsh-answer-text">输入问题，DSH 会结合当前话题、参数、地图和错误信息分析。</div><div class="dsh-parameter-links"></div></div><div class="dsh-meta">只读诊断，结果不会自动修改参数或让机器人运动。</div>`;
  const question = root.querySelector('[data-testid="dsh-question"]');
  const ask = root.querySelector('[data-testid="dsh-ask"]');
  const answer = root.querySelector('.dsh-answer-text');
  const links = root.querySelector('.dsh-parameter-links');
  const meta = root.querySelector('.dsh-meta');
  const QUESTION = '/omnifleet_t2/diagnostics/question', ANSWER = '/omnifleet_t2/diagnostics/answer';
  let requestId = '', timer, highlightTimer, highlightedRow, disposed = false, topics = [];
  const finish = () => { clearTimeout(timer); ask.disabled = false; };
  const show = text => { answer.textContent = text; links.replaceChildren(); };
  if (context.advertise && context.publish) {
    context.advertise(QUESTION, 'std_msgs/msg/String', {datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string'}]}]])});
  } else { ask.disabled = true; show('当前连接不支持提问，请连接 113 的 Foxglove Bridge。'); }
  function submit(reportedError = null) {
    const text = question.value.trim();
    if (!text || ask.disabled || disposed) return false;
    requestId = crypto.randomUUID();
    ask.disabled = true; show('正在请求本次诊断……');
    try {
      context.publish(QUESTION,{data:JSON.stringify({request_id:requestId,question:text,foxglove:{topic_names:topics},reported_error:reportedError})});
      timer = setTimeout(() => { if (!disposed) { requestId = ''; finish(); show('诊断等待超时，请检查 DSH 和诊断服务后重试。'); } },150000);
      return true;
    } catch (error) { finish(); show('提问失败：'+String(error)); return false; }
  }
  ask.onclick = () => submit();
  question.onkeydown = event => { if (event.key === 'Enter' && !event.isComposing) { event.preventDefault(); submit(); } };
  const onReportedError = event => {
    const detail = event.detail;
    if (!detail || detail.accepted || disposed) return;
    if (ask.disabled) { detail.reason = requestId ? 'DSH 正在分析上一请求，请稍后再提交。' : 'DSH 当前连接不可用。'; return; }
    question.value = String(detail.question || '').slice(0,4000);
    detail.accepted = submit(detail.error || null);
    if (detail.accepted) root.querySelector('[data-testid="dsh-answer"]').scrollIntoView({block:'nearest'});
    else detail.reason = '提交失败，请查看 DSH 回答框。';
  };
  document.addEventListener('omnifleet-dsh-diagnose-error',onReportedError);
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
            for (const id of (result.parameter_ids || []).slice(0,6)) {
              if (typeof id !== 'string' || !/^[a-z0-9_]+$/.test(id)) continue;
              const action = (result.parameter_actions || []).find(a => a.id === id && ['inspect','adjust'].includes(a.intent));
              if (!action) continue;
              if (!links.childElementCount) {const heading=document.createElement('p');heading.textContent='相关参数 · 点击定位，由你修改';links.append(heading);}
              const label=result.parameter_labels?.[id] || id;
              const button = document.createElement('button'); button.textContent = '定位：'+label.split(' · ')[0];
              button.dataset.parameterId=id;
              button.setAttribute('aria-label','定位参数 '+label);
              button.title = label+'\n'+(action.reason || '');
              button.onclick = () => {
                const selectorId={local_controller_algorithm:'nav2-local-algorithm',global_planner_algorithm:'nav2-global-algorithm'}[id];
                const field = document.querySelector('[data-testid="'+(selectorId || 'nav2-input-'+id)+'"]');
                if (field) {
                  clearTimeout(highlightTimer); highlightedRow?.classList.remove('dsh-located-parameter');
                  const row=field.closest('.row, .algorithm-row'); if(row) row.hidden=false;
                  for(let parent=field.parentElement; parent; parent=parent.parentElement) if(parent.tagName==='DETAILS') parent.open=true;
                  field.scrollIntoView({block:'center'}); field.focus({preventScroll:true});
                  highlightedRow=row; row?.classList.add('dsh-located-parameter');
                  highlightTimer=setTimeout(()=>{row?.classList.remove('dsh-located-parameter');},5000);
                  meta.textContent='已定位：'+label+'。仅展开并定位，参数尚未修改。';
                }
                else {
                  const targetAlgorithm = id.startsWith('rpp_') ? 'Regulated Pure Pursuit（RPP）' : id.startsWith('dwb_') ? 'Hot DWB' : id.startsWith('mppi_') ? 'MPPI' : '';
                  const selector = targetAlgorithm ? document.querySelector('[data-testid="nav2-local-algorithm"]') : null;
                  if (selector) {
                    clearTimeout(highlightTimer); highlightedRow?.classList.remove('dsh-located-parameter');
                    const row=selector.closest('.algorithm-row');
                    for(let parent=selector.parentElement; parent; parent=parent.parentElement) if(parent.tagName==='DETAILS') parent.open=true;
                    selector.scrollIntoView({block:'center'}); selector.focus({preventScroll:true});
                    highlightedRow=row; row?.classList.add('dsh-located-parameter');
                    highlightTimer=setTimeout(()=>{row?.classList.remove('dsh-located-parameter');},5000);
                    meta.textContent='“'+label.split(' · ')[0]+'”属于 '+targetAlgorithm+'。请先在已定位的下拉框切换算法，再点击本按钮定位具体参数；不会自动切换。';
                  } else meta.textContent = '该参数未在当前算法栏显示，请先核对所用算法；不会自动切换算法。';
                }
              };
              links.append(button);
            }
          }
        }
      }
    } finally { done(); }
  };
  return () => { document.removeEventListener('omnifleet-dsh-diagnose-error',onReportedError); disposed = true; clearTimeout(timer); clearTimeout(highlightTimer); highlightedRow?.classList.remove('dsh-located-parameter'); context.onRender = undefined; context.subscribe([]); context.unadvertise?.(QUESTION); host.style.position = oldPosition; };
}
