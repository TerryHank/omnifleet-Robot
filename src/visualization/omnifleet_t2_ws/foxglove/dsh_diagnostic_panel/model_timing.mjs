// Per-invocation transport timing only: no request bodies, credentials or model text.
const originalFetch=globalThis.fetch;
let attempt=0;
const emit=(stage,extra={})=>process.stderr.write('\nDSH_TIMING '+JSON.stringify({stage,time:Date.now()/1000,...extra})+'\n');
globalThis.fetch=async function(input,init) {
  const url=typeof input==='string' ? input : input instanceof URL ? input.href : input.url;
  if(!/\/chat\/completions(?:\?|$)/.test(url || ''))return originalFetch.call(this,input,init);
  const id=++attempt;emit('request_start',{attempt:id});
  let response;
  try {response=await originalFetch.call(this,input,init);} catch(error) {emit('request_error',{attempt:id});throw error;}
  emit('response_headers',{attempt:id,http_status:response.status});
  if(!response.body || !response.ok)return response;
  let first=false,buffer='';const decoder=new TextDecoder();
  const body=response.body.pipeThrough(new TransformStream({
    transform(chunk,controller) {
      if(!first) {
        buffer+=decoder.decode(chunk,{stream:true});
        const lines=buffer.split('\n');buffer=lines.pop() || '';
        for(const line of lines) {
          if(!line.startsWith('data:'))continue;
          try {
            const message=JSON.parse(line.slice(5).trim());
            if(message.choices?.some(x=>x.delta?.content || x.delta?.reasoning_content)) {
              first=true;emit('first_model_token',{attempt:id});break;
            }
          } catch {}
        }
        if(buffer.length>65536)buffer='';
      }
      controller.enqueue(chunk);
    },
    flush(){emit('model_stream_end',{attempt:id});},
  }));
  return new Response(body,{status:response.status,statusText:response.statusText,headers:response.headers});
};
