const fs=require('fs'),acorn=require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/acorn');
const file='/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js';
const s=fs.readFileSync(file,'utf8'),ast=acorn.parse(s,{ecmaVersion:'latest'});
let fn;const edits=[];
function walk(node,visit){if(!node||typeof node!=='object')return;visit(node);for(const v of Object.values(node)){if(Array.isArray(v))v.forEach(x=>walk(x,visit));else if(v&&typeof v==='object')walk(v,visit);}}
walk(ast,node=>{if(node.type==='FunctionDeclaration'&&node.id.name==='iu')fn=node;});
if(!fn)throw Error('Missing semantic component');
function hasText(node,text){let found=false;walk(node,n=>{if(n.type==='Literal'&&n.value===text)found=true;});return found;}
let matched=0;
walk(fn,node=>{
 if(node.type==='ArrayExpression'){
  const first=node.elements.findIndex(e=>hasText(e,'1. 给下一个点命名'));
  const last=node.elements.findIndex(e=>hasText(e,'3. 选择一个语义点，或开始整条路线'));
  if(first>=0&&last-first===5){edits.push([node.elements[first].start,node.elements[last+1].start,'']);matched++;}
 }
 if(node.type==='VariableDeclaration'){
  const declarations=node.declarations;
  declarations.forEach((d,i)=>{
   const remove=d.id.type==='Identifier'&&['y','L'].includes(d.id.name)||d.id.type==='ArrayPattern'&&d.id.elements.map(e=>e.name).join(',')==='s,a';
   if(remove)edits.push(i<declarations.length-1?[d.start,declarations[i+1].start,'']:[declarations[i-1].end,d.end,'']);
  });
 }
});
if(matched!==1||edits.length!==4)throw Error('Unexpected removal boundaries '+JSON.stringify(edits));
let out=s;for(const [start,end,replacement] of edits.sort((a,b)=>b[0]-a[0]))out=out.slice(0,start)+replacement+out.slice(end);
acorn.parse(out,{ecmaVersion:'latest'});
fs.writeFileSync(__dirname+'/bundle.before.js',s);
fs.writeFileSync(__dirname+'/removed-fragments.json',JSON.stringify(edits.map(([start,end])=>s.slice(start,end)),null,2));
fs.writeFileSync(file+'.trim.tmp',out);fs.renameSync(file+'.trim.tmp',file);
console.log('Removed 6 UI blocks and 3 unused declarations; syntax verified');
