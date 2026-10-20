const fs=require('fs'),path=require('path'),acorn=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/acorn');
const root='/home/iecme/robot_backups/fleet_panel_20260913',bundle='/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js';
const ext='/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/foxglove_extension/omnifleet-t2-semantic-waypoints/src';
let s=fs.readFileSync(bundle,'utf8');const source=fs.readFileSync(root+'/FleetPanel.js','utf8');
const type='omnifleet-t2-semantic-waypoints.fleet-panel',oldType='omnifleet-t2-semantic-waypoints.nav2-hot-params-panel';
const begin='/* OMNIFLEET_FLEET_PANEL_BEGIN */',end='/* OMNIFLEET_FLEET_PANEL_END */';
const fn=source.replace('export function initFleetPanel(context)','function initFleetBuiltin(context)');
if(s.includes(begin)){const a=s.indexOf(begin),b=s.indexOf(end,a);if(b<0)throw Error('Missing end anchor');s=s.slice(0,a)+begin+'\n'+fn+'\n'+s.slice(b);}
else{if(s.split('function initNav2Builtin(').length!==2)throw Error('Ambiguous function anchor');s=s.replace('function initNav2Builtin(',begin+'\n'+fn+'\n'+end+'\nfunction initNav2Builtin(');}
if(!s.includes('type:"'+type+'"')){
 const ast=acorn.parse(s,{ecmaVersion:'latest'});const found=[];
 function walk(node){if(!node||typeof node!=='object')return;if(node.type==='ObjectExpression'&&node.properties.some(p=>p.key?.name==='type'&&p.value?.value===oldType))found.push(node);for(const v of Object.values(node)){if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object'&&v.type)walk(v);}}
 walk(ast);if(found.length!==1)throw Error('Panel registry anchor not unique');const a=found[0];
 const entry=s.slice(a.start,a.end).replaceAll(oldType,type).replace('initPanel:initNav2Builtin','initPanel:initFleetBuiltin').replace('OmniFleet Nav2 热参数','多机协同').replace('实时读取和修改 OmniFleet Nav2 InflationLayer 参数','激活车辆、独立多点路线和领航跟随');
 s=s.slice(0,a.start)+entry+','+s.slice(a.start);
}
acorn.parse(s,{ecmaVersion:'latest'});fs.writeFileSync(bundle,s);
fs.writeFileSync(ext+'/FleetPanel.js',source);fs.writeFileSync(ext+'/FleetPanel.d.ts','import type { PanelExtensionContext } from "@foxglove/extension";\nexport function initFleetPanel(context: PanelExtensionContext): () => void;\n');
const index=ext+'/index.ts';let content=fs.readFileSync(index,'utf8');
if(!content.includes('initFleetPanel')){content='import { initFleetPanel } from "./FleetPanel.js";\n'+content;const a=content.lastIndexOf('}');content=content.slice(0,a)+'  extensionContext.registerPanel({name:"fleet-panel",initPanel:initFleetPanel});\n'+content.slice(a);fs.writeFileSync(index,content);}
console.log('Registered '+type+' and synchronized reusable extension source');
