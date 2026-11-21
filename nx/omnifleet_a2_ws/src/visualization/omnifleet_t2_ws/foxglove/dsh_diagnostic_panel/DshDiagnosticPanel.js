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
  .dsh-answer-text{white-space:normal}
  .dsh-answer-text h4{margin:16px 0 7px;font-size:1em;font-weight:750;color:#20252d}
  .dsh-answer-text h4:first-child{margin-top:0}
  .dsh-answer-text ul,.dsh-answer-text ol{margin:0;padding-left:1.5em}
  .dsh-answer-text li{padding:5px 0;line-height:1.65;white-space:pre-wrap}
  .dsh-answer-text li+li{border-top:1px solid #dde2e8}
  .dsh-answer-text p{margin:5px 0 10px;white-space:pre-wrap;line-height:1.65}
  .dsh-answer button{margin:7px 6px 0 0}
  .dsh-parameter-links>p{margin:12px 0 0;font-size:.9em;font-weight:600;color:#334155}
  .dsh-parameter-links button{max-width:100%;text-align:left;overflow-wrap:anywhere;border-radius:8px}
  .omnifleet-nav2-hot-params .row.dsh-located-parameter,.omnifleet-nav2-hot-params .algorithm-row.dsh-located-parameter{outline:2px solid #6585ad;outline-offset:3px;border-radius:6px;background:#f1f5fa}
  .dsh-meta{font-size:16.5px;color:#666;flex-shrink:0}
  </style><div class="dsh-question-row"><input data-testid="dsh-question" aria-label="问题" maxlength="4000" placeholder="例如：为什么发航点后不动？"><button type="button" data-testid="dsh-ask">诊断</button></div><div class="dsh-answer" data-testid="dsh-answer" role="status" aria-live="polite"><div class="dsh-answer-text">输入问题，DSH 会结合当前话题、参数、地图和错误信息分析。</div><div class="dsh-parameter-links"></div></div><div class="dsh-meta">只读诊断，结果不会自动修改参数或让机器人运动。</div>`;
  const engineBar=document.createElement('div');engineBar.style.cssText='display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:6px 0';
  const engineSelect=document.createElement('select');engineSelect.style.font='inherit';engineSelect.dataset.testid='diagnostic-engine';engineSelect.setAttribute('aria-label','诊断引擎');
  for(const [value,label] of [['dsh','DSH'],['phyagentos','PhyAgentOS']]){const o=document.createElement('option');o.value=value;o.textContent=label;engineSelect.append(o);}
  const engineLabel=value=>value==='phyagentos'?'PhyAgentOS':'DSH';
  const modelSelect=document.createElement('select');modelSelect.style.font='inherit';modelSelect.dataset.testid='diagnostic-model';modelSelect.setAttribute('aria-label','诊断模型');
  let selectedEngine=context.initialState?.diagnostic_engine==='phyagentos'?'phyagentos':'dsh',requestEngine=selectedEngine;
  let selectedModel=typeof context.initialState?.diagnostic_model==='string'?context.initialState.diagnostic_model:'MiniMax-M3',requestModel=selectedModel;
  const persist=()=>context.saveState?.({...context.initialState,diagnostic_engine:selectedEngine,diagnostic_model:selectedModel});
  engineSelect.value=selectedEngine;
  engineSelect.onchange=()=>{selectedEngine=engineSelect.value;persist();};
  const setModels=(models,defaultModel)=>{
    const unique=[...new Set((models||[]).filter(value=>typeof value==='string'&&value.length))];
    if(!unique.length)return;
    const previous=selectedModel;
    modelSelect.replaceChildren(...unique.map(value=>{const option=document.createElement('option');option.value=value;option.textContent=value;return option;}));
    if(!unique.includes(selectedModel))selectedModel=unique.includes(defaultModel)?defaultModel:unique[0];
    modelSelect.value=selectedModel;modelSelect.disabled=false;
    if(selectedModel!==previous)persist();
  };
  setModels(['MiniMax-M3'],'MiniMax-M3');
  modelSelect.onchange=()=>{selectedModel=modelSelect.value;persist();};
  const switchingHint=document.createElement('small');switchingHint.textContent='热切换用于下一次提问；进行中的请求保持原引擎和模型。';
  engineBar.append('诊断引擎 ',engineSelect,'模型：',modelSelect,switchingHint);root.prepend(engineBar);
  const question = root.querySelector('[data-testid="dsh-question"]');
  const ask = root.querySelector('[data-testid="dsh-ask"]');
  const answer = root.querySelector('.dsh-answer-text');
  const links = root.querySelector('.dsh-parameter-links');
  const meta = root.querySelector('.dsh-meta');
  const QUESTION = '/omnifleet_t2/diagnostics/question', ANSWER = '/omnifleet_t2/diagnostics/answer', MODELS = '/omnifleet_t2/diagnostics/models';
  let requestId = '', timer, ackTimer, retryTimer, requestStage = '', highlightTimer, highlightedRow, disposed = false;
  const MODEL_TIMEOUT_MS = 150000;
  const finish = () => { clearTimeout(timer); clearTimeout(ackTimer); clearTimeout(retryTimer); ask.disabled = false; };
  const show = text => {
    answer.replaceChildren(); links.replaceChildren();
    let list;
    for (const raw of text.split(/\r?\n/)) {
      const line=raw.trim();
      if (!line) {list=undefined;continue;}
      const heading=line.replace(/^#{1,4}\s*/, '').replace(/\*\*/g,'').replace(/[：:]$/, '');
      if (['发现的问题','判断依据','处理步骤','还需确认'].includes(heading)) {
        const title=document.createElement('h4');title.textContent=heading;answer.append(title);list=undefined;continue;
      }
      const match=line.match(/^(?:([-*•])\s+|\d+[.、)]\s*)(.+)$/);
      if (match) {
        const type=match[1] ? 'UL' : 'OL';
        if (!list || list.tagName!==type) {list=document.createElement(type.toLowerCase());answer.append(list);}
        const item=document.createElement('li');item.textContent=match[2];list.append(item);
      } else {
        const paragraph=document.createElement('p');paragraph.textContent=line;answer.append(paragraph);list=undefined;
      }
    }
    root.querySelector('.dsh-answer').scrollTop=0;
  };
  if (context.advertise && context.publish) {
    context.advertise(QUESTION, 'std_msgs/msg/String', {datatypes:new Map([['std_msgs/msg/String',{definitions:[{name:'data',type:'string'}]}]])});
  } else { ask.disabled = true; show('当前连接不支持提问，请连接 113 的 Foxglove Bridge。'); }
  function submit(reportedError = null) {
    const text = question.value.trim();
    if (!text || ask.disabled || disposed) return false;
    requestEngine=selectedEngine;
    requestModel=selectedModel;
    requestId = crypto.randomUUID();
    requestStage='waiting_ack'; ask.disabled = true; show('正在提交问题，等待诊断服务确认……');
    try {
      const payload = {data:JSON.stringify({request_id:requestId,engine:requestEngine,model:requestModel,question:text,foxglove:{},reported_error:reportedError})};
      context.publish(QUESTION,payload);
      let retries = 0;
      const retry = () => {
        if (disposed || requestStage !== 'waiting_ack') return;
        try { context.publish(QUESTION,payload); }
        catch (error) { finish(); show('提问失败：'+String(error)); return; }
        if (++retries < 2) retryTimer = setTimeout(retry,3000);
      };
      retryTimer = setTimeout(retry,3000);
      ackTimer = setTimeout(() => {
        if (!disposed && requestStage === 'waiting_ack') {
          finish(); show('未收到请求确认：诊断服务尚未确认收到问题。请检查连接和诊断服务后重试。');
        }
      },10000);
      timer = setTimeout(() => {
        if (disposed) return;
        finish();
        show(requestStage === 'collecting' ? '数据采集超时：诊断服务已收到问题，但采集尚未完成。' :
          requestStage === 'first_model_token' || requestStage === 'model_stream_end' ?
          '模型仍在处理，面板暂未收到最终结果；稍后到达的结果会自动替换此提示。' :
          '等待模型响应超时：服务已确认请求，但尚未返回最终结果。稍后到达的结果仍会显示。');
      },MODEL_TIMEOUT_MS);
      return true;
    } catch (error) { finish(); show('提问失败：'+String(error)); return false; }
  }
  ask.onclick = () => submit();
  question.onkeydown = event => { if (event.key === 'Enter' && !event.isComposing) { event.preventDefault(); submit(); } };
  context.watch('currentFrame'); context.subscribe([{topic:ANSWER},{topic:MODELS}]);
  context.onRender = (state,done) => {
    try {
      if (disposed) return;
      for (const event of state.currentFrame || []) {
        if (event.topic === MODELS) {
          try {
            const catalog = JSON.parse(event.message.data);
            if (Array.isArray(catalog.models) && catalog.models.length) setModels(catalog.models, catalog.default_model);
          } catch { /* keep the last valid model list */ }
          continue;
        }
        if (event.topic !== ANSWER) continue;
        let result;
        try { result = JSON.parse(event.message.data); } catch { continue; }
        if (result.request_id !== requestId) continue;
        clearTimeout(ackTimer); clearTimeout(retryTimer); requestStage=result.stage || result.status;
        const legacyTimeout = result.status === 'error' && result.error_code === 'model_analysis_timeout';
        show(legacyTimeout ? '模型未及时完成，旧请求已结束；请重新提交当前问题。\n\n本次没有完整诊断结论，未提供参数修改建议。' : String(result.answer || '正在诊断……'));
        if (result.status === 'complete' || result.status === 'error') {
          finish();
          if (legacyTimeout) meta.textContent = '旧请求超时已转换为可重试提示 · DSH 只读诊断';
          if (result.status === 'complete') {
            if (Array.isArray(result.causal_chain) && result.causal_chain.length) {
              const details=document.createElement('details'),summary=document.createElement('summary');
              summary.textContent='模型因果链与证据编号';details.append(summary);
              for (const step of result.causal_chain) {
                const row=document.createElement('p');
                row.textContent=(step.confidence==='confirmed'?'已确认：':'待验证：')+step.cause+' → '+step.effect+' ['+(step.evidence_ids||[]).join(', ')+']';
                details.append(row);
              }
              answer.append(details);
            }
            meta.textContent = '数据采集：' + new Date(result.captured_at*1000).toLocaleTimeString() + ' · '+engineLabel(result.engine||requestEngine)+' · '+String(result.model||requestModel)+' · 只读诊断';
            if (result.model_fallback) meta.textContent = '模型未及时完成，已显示实时快照检查 · '+engineLabel(result.engine||requestEngine)+' · '+String(result.model||requestModel);
            if (result.timings) {
              const timing=result.timings, parts=[];
              if (Number.isFinite(timing.collection_seconds)) parts.push('采集 '+timing.collection_seconds.toFixed(1)+'秒');
              if (Number.isFinite(timing.model_connect_seconds)) parts.push('连接/响应 '+timing.model_connect_seconds.toFixed(1)+'秒');
              if (Number.isFinite(timing.model_generation_seconds)) parts.push('生成 '+timing.model_generation_seconds.toFixed(1)+'秒');
              if (Number.isFinite(timing.total_seconds)) parts.push('总计 '+timing.total_seconds.toFixed(1)+'秒');
              if (Array.isArray(timing.skills) && timing.skills.length) parts.unshift('Skill '+timing.skills.join(', '));
              if (Array.isArray(timing.skill_errors) && timing.skill_errors.length) parts.unshift('Skill 加载失败');
              meta.textContent += ' · '+parts.join(' · ');
            }
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
  return () => { disposed = true; clearTimeout(timer); clearTimeout(ackTimer); clearTimeout(retryTimer); clearTimeout(highlightTimer); highlightedRow?.classList.remove('dsh-located-parameter'); context.onRender = undefined; context.subscribe([]); context.unadvertise?.(QUESTION); host.style.position = oldPosition; };
}
