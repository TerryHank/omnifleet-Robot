// Per-process diagnostic policy and timing; never emit credentials or generated text.
import {diagnosticPolicy} from './diagnostic_policy.mjs';
const originalFetch=globalThis.fetch;
let attempt=0;
const emit=(stage,extra={})=>process.stderr.write('\nDSH_TIMING '+JSON.stringify({stage,time:Date.now()/1000,...extra})+'\n');
globalThis.fetch=async function(input,init) {
  const url=typeof input==='string'?input:input instanceof URL?input.href:input.url;
  if(!/\/chat\/completions(?:\?|$)/.test(url||''))return originalFetch.call(this,input,init);
  const id=++attempt;let options={};
  try {
    const b=diagnosticPolicy(JSON.parse(init?.body),process.env.DSH_DIAGNOSTIC_BOUNDED==='1');
    init={...init,body:JSON.stringify(b)};
    options={model:b.model,max_tokens:b.max_tokens,enable_thinking:b.enable_thinking,thinking_budget:b.thinking_budget,reasoning_effort:b.reasoning_effort};
  } catch {}
  emit('request_start',{attempt:id,...options});
  let response;
  try {response=await originalFetch.call(this,input,init);}catch(error){emit('request_error',{attempt:id});throw error;}
  emit('response_headers',{attempt:id,http_status:response.status});
  if(!response.body||!response.ok)return response;
  let firstAnswer=false,firstReasoning=false,buffer='',answerChars=0,reasoningChars=0,lastReport=Date.now();
  const decoder=new TextDecoder();
  const body=response.body.pipeThrough(new TransformStream({
    transform(chunk,controller) {
      buffer+=decoder.decode(chunk,{stream:true});const lines=buffer.split('\n');buffer=lines.pop()||'';
      for(const line of lines) {
        if(!line.startsWith('data:'))continue;
        try {
          const m=JSON.parse(line.slice(5).trim());
          for(const c of m.choices||[]) {
            const r=c.delta?.reasoning_content,a=c.delta?.content;
            if(typeof r==='string'&&r.length){reasoningChars+=r.length;if(!firstReasoning){firstReasoning=true;emit('first_reasoning_token',{attempt:id});}}
            if(typeof a==='string'&&a.length){answerChars+=a.length;if(!firstAnswer){firstAnswer=true;emit('first_model_token',{attempt:id});}}
            if(c.finish_reason)emit('model_finish',{attempt:id,finish_reason:c.finish_reason,answer_chars:answerChars,reasoning_chars:reasoningChars});
          }
          if(m.usage)emit('model_usage',{attempt:id,completion_tokens:m.usage.completion_tokens,reasoning_tokens:m.usage.completion_tokens_details?.reasoning_tokens});
        }catch {}
      }
      if(Date.now()-lastReport>10000){lastReport=Date.now();emit('model_progress',{attempt:id,answer_chars:answerChars,reasoning_chars:reasoningChars});}
      if(buffer.length>65536)buffer='';
      controller.enqueue(chunk);
    },
    flush(){emit('model_stream_end',{attempt:id,answer_chars:answerChars,reasoning_chars:reasoningChars});}
  }));
  return new Response(body,{status:response.status,statusText:response.statusText,headers:response.headers});
};
