#!/usr/bin/env node
"use strict";

const fs = require("fs");

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  throw new Error("Usage: fix_semantic_panel_registration.cjs INPUT OUTPUT");
}

let source = fs.readFileSync(inputPath, "utf8");
const before = 'module:async()=>({default:(0,bg.c)(()=>(0,n.jsx)(ru,{open:!0,onClose:()=>{}}))})';
const after = 'module:async()=>{const e=()=>(0,n.jsx)(ru,{open:!0,onClose:()=>{}});return e.panelType="SemanticWaypointPanel",e.defaultConfig={},{default:(0,bg.c)(e)}}';
const count = source.split(before).length - 1;
if (count !== 1) {
  throw new Error(`Expected one incomplete semantic panel registration, found ${count}`);
}
source = source.replace(before, after);
if (!source.includes('e.panelType="SemanticWaypointPanel",e.defaultConfig={}')) {
  throw new Error("Semantic panel registration fields were not added");
}
fs.writeFileSync(outputPath, source, "utf8");
console.log(`Fixed semantic panel registration in ${outputPath}`);
