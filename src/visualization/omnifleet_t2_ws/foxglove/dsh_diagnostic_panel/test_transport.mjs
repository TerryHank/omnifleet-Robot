import './model_timing.mjs';
import http from 'node:http';
import assert from 'node:assert/strict';
const events=[];const write=process.stderr.write.bind(process.stderr);
process.stderr.write=(text,...args)=>{if(text.includes('DSH_TIMING '))events.push(JSON.parse(text.trim().slice(11)));return true;};
const body='data: {"choices":[{"delta":{"reasoning_content":"test"}}]}\n\ndata: {"choices":[{"delta":{"content":"answer"}}]}\n\ndata: [DONE]\n\n';
const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/event-stream'});res.write(body.slice(0,40));setTimeout(()=>res.end(body.slice(40)),30);});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
try{
 const response=await fetch(`http://127.0.0.1:${server.address().port}/chat/completions`,{method:'POST'});
 assert.equal(await response.text(),body);
 assert.deepEqual(events.map(x=>x.stage),['request_start','response_headers','first_model_token','model_stream_end']);
 assert(!JSON.stringify(events).includes('reasoning_content'));
 console.log('PASS HTTP timing, first token, stream completion; response bytes unchanged');
}finally{server.closeAllConnections();server.close();process.stderr.write=write;}
