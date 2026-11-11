from pathlib import Path
import shutil,time
here=Path(__file__).resolve().parent
bundle=Path('/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js')
backup=Path('/home/iecme/robot_backups/dsh_diagnostic_panel')/str(time.time_ns());backup.mkdir(parents=True)
shutil.copy2(bundle,backup/bundle.name)
s=bundle.read_text()
start='/*OMNIFLEET_DSH_DIAGNOSTIC_START*/';end='/*OMNIFLEET_DSH_DIAGNOSTIC_END*/'
code=start+'\n'+(here/'DshDiagnosticPanel.js').read_text().replace('export function','function',1)+'\n'+end+'\n'
if start in s:
 a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+code+s[b:]
else:
 marker='function initNav2Builtin(context) {';assert s.count(marker)==1;s=s.replace(marker,code+marker,1)
panel_type='omnifleet-t2-dsh-diagnostics'
if 'type:"'+panel_type+'"' not in s:
 a=s.index('{title:"OmniFleet Nav2 热参数",type:"omnifleet-t2-semantic-waypoints.nav2-hot-params-panel"')
 b=s.index('},{title:"履带实车语义多点导航"',a)+1
 entry=s[a:b]
 new=entry.replace('OmniFleet Nav2 热参数','DSH 诊断助手').replace('omnifleet-t2-semantic-waypoints.nav2-hot-params-panel',panel_type).replace('实时读取和修改 OmniFleet Nav2 InflationLayer 参数','根据当前数据回答机器人问题').replace('initNav2Builtin','initDshDiagnosticPanel')
 s=s[:a]+new+','+s[a:]
bundle.write_text(s)
config=Path('/etc/omnifleet_t2/foxglove.yaml');shutil.copy2(config,backup/'foxglove.yaml')
text=config.read_text()
rule='      - "^/omnifleet_t2/diagnostics/question$"\n'
if rule not in text:text=text.replace('    client_topic_whitelist:\n','    client_topic_whitelist:\n'+rule,1)
config.write_text(text)
print('Installed DSH panel; backup:',backup)
