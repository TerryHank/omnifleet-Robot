import os,subprocess,yaml
from pathlib import Path
here=Path(__file__).resolve().parent
env=os.environ.copy();env['DSH_HOME']='/home/iecme/.dsh-t2';env['PATH']='/home/iecme/.local/node-v24.20.0-linux-arm64/bin:'+env['PATH']
r=subprocess.run(['/home/iecme/omnifleet_ws/src/system/tools/deepseek-harness/node_modules/.bin/dsh','--profile','headless','--patch',str(here/'dsh-readonly.patch.yml'),'--dump-config'],env=env,cwd=here,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=30,check=True)
tree=yaml.load(r.stdout,Loader=yaml.BaseLoader)
def rows(value):
 if isinstance(value,list):
  for v in value:yield from rows(v)
 elif isinstance(value,dict):
  if 'name' in value and 'id' in value:yield value
  for k,v in value.items():
   if k in ('children','entries','plugins','tree','insert'):yield from rows(v)
providers=[v for v in rows(tree) if (str(v.get('name','')).startswith('@deepseek-ai/dsh-tool-') and 'timeout-policy' not in v['name']) or v.get('id')=='t2-ros-mcp']
assert providers,'No provider entries found; cannot verify'
enabled=[{'id':v['id'],'name':v['name']} for v in providers if str(v.get('disabled','false')).lower()!='true']
assert not enabled,enabled
print('Verified composed DSH profile: all',len(providers),'tool/MCP providers disabled')
