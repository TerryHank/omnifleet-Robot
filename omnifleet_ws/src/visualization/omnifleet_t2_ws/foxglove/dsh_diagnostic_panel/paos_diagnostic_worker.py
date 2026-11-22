"""PhyAgentOS AgentLoop for a single isolated, read-only diagnostic request."""
import asyncio,json,sys,time,uuid
from pathlib import Path
import yaml
from loguru import logger
from PhyAgentOS.agent.loop import AgentLoop
from PhyAgentOS.bus.queue import MessageBus
from PhyAgentOS.providers.custom_provider import CustomProvider
from PhyAgentOS.providers.base import LLMResponse

HERE=Path(__file__).parent
POLICY=json.loads((HERE/'qwen-policy.json').read_text())

def emit(stage,**fields):
    print('DSH_TIMING '+json.dumps({'stage':stage,'time':time.time(),'attempt':1,'engine':'phyagentos',**fields}),file=sys.stderr,flush=True)

class DiagnosticProvider(CustomProvider):
    def __init__(self,*args,selected_model,**kwargs):
        super().__init__(*args,**kwargs);self.selected_model=selected_model

    async def chat(self,messages,tools=None,model=None,**_kwargs):
        if tools:raise RuntimeError('Diagnostic tools must be empty')
        persona=next(x['config']['persona'] for x in yaml.safe_load((HERE/'dsh-readonly.patch.yml').read_text()) if x.get('id')=='system-prompt')
        messages=[dict(m) for m in messages]
        if messages and messages[0]['role']=='system':messages[0]['content']+='\n'+persona
        else:messages.insert(0,{'role':'system','content':persona})
        emit('request_start',model=self.selected_model,framework='PhyAgentOS AgentLoop',tool_count=0)
        content=[];first=False;reasoning=False;last=time.monotonic();answer_chars=reasoning_chars=0;finish='stop'
        try:
            options=dict(model=self.selected_model,messages=messages,stream=True,
                max_tokens=POLICY['max_tokens'],response_format=POLICY['response_format'])
            if self.selected_model.lower().startswith('qwen'):
                options['extra_body']=({'enable_thinking':False} if '-flash' in self.selected_model.lower() else
                    {'enable_thinking':POLICY['enable_thinking'],'thinking_budget':POLICY['thinking_budget']})
            stream=await self._client.chat.completions.create(**options)
            emit('response_headers',http_status=200)
            async for chunk in stream:
                for choice in chunk.choices:
                    delta=choice.delta;text=delta.content or '';thought=getattr(delta,'reasoning_content',None) or ''
                    if thought:
                        reasoning_chars+=len(thought)
                        if not reasoning:reasoning=True;emit('first_reasoning_token')
                    if text:
                        content.append(text);answer_chars+=len(text)
                        if not first:first=True;emit('first_model_token')
                    if choice.finish_reason:finish=choice.finish_reason
                if time.monotonic()-last>10:
                    last=time.monotonic();emit('model_progress',answer_chars=answer_chars,reasoning_chars=reasoning_chars)
            emit('model_finish',finish_reason=finish,answer_chars=answer_chars)
            emit('model_stream_end',answer_chars=answer_chars)
            return LLMResponse(content=''.join(content),finish_reason=finish)
        except Exception as error:
            emit('request_error',http_status=getattr(error,'status_code',None),error_type=type(error).__name__)
            raise RuntimeError('PhyAgentOS model request failed: '+type(error).__name__) from None

async def main():
    request=json.load(sys.stdin)
    model=request.get('model',POLICY['model'])
    if not isinstance(model,str) or not model or len(model)>128:raise RuntimeError('Invalid diagnostic model')
    settings=yaml.safe_load(Path('/home/iecme/.dsh-t2/settings.yaml').read_text())
    name=settings['agent-default-model']['provider'];provider=settings['llm-pi-ai']['providers'][name]
    credentials=yaml.safe_load(Path('/home/iecme/.dsh-t2/.credentials.yaml').read_text())
    key=credentials['refs'][provider['apiKeyEnv']]
    if not isinstance(key,str) or not key:raise RuntimeError('Configured model credential unavailable')
    workspace=Path.home()/'.local/share/omnifleet_t2/paos-diagnostics';workspace.mkdir(parents=True,exist_ok=True)
    llm=DiagnosticProvider(api_key=key,api_base=provider['baseURL'],default_model=model,timeout_s=120,selected_model=model)
    loop=AgentLoop(bus=MessageBus(),provider=llm,workspace=workspace,model=model,max_iterations=1,context_window_tokens=262144,
                   restrict_to_workspace=True,mcp_servers={})
    for name in list(loop.tools.tool_names):loop.tools.unregister(name)
    assert not loop.tools.get_definitions()
    try:
        answer=await loop.process_direct(request['prompt'],session_key='diagnostic:'+uuid.uuid4().hex)
        print(answer,flush=True)
    finally:await llm._client.close()

if __name__=='__main__':
    logger.remove();logger.add(sys.stderr,level='WARNING')
    try:asyncio.run(main())
    except Exception as error:
        print('PhyAgentOS diagnostic failed: '+type(error).__name__,file=sys.stderr)
        raise SystemExit(1)
