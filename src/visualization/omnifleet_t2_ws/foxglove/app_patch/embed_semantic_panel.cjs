#!/usr/bin/env node
"use strict";

const fs = require("fs");

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  throw new Error("Usage: embed_semantic_panel.cjs INPUT OUTPUT");
}

let source = fs.readFileSync(inputPath, "utf8");
if (source.includes('type:"SemanticWaypointPanel"')) {
  throw new Error("SemanticWaypointPanel is already registered");
}

const styleOwner = source.indexOf("Ha=(0,ee.au)()");
const styleStart = source.indexOf('paper:{position:"absolute"', styleOwner);
const styleEndMarker = "boxShadow:e.shadows[12]}";
const styleEndStart = source.indexOf(styleEndMarker, styleStart);
if (styleOwner < 0 || styleStart < 0 || styleEndStart < 0) {
  throw new Error("Could not locate floating semantic panel styles");
}
const styleEnd = styleEndStart + styleEndMarker.length;
const embeddedStyle = 'paper:{position:"relative",width:"100%",height:"100%",maxWidth:"none",display:"flex",flexDirection:"column",overflow:"hidden",border:"none",boxShadow:"none"}';
source = source.slice(0, styleStart) + embeddedStyle + source.slice(styleEnd);

const controlIndex = source.indexOf('"data-testid":"semantic-waypoint-control"');
const closeLabelIndex = source.indexOf('"aria-label":', controlIndex);
const closeStart = source.lastIndexOf(",(0,n.jsx)(", closeLabelIndex);
if (controlIndex < 0 || closeLabelIndex < 0 || closeStart < 0) {
  throw new Error("Could not locate semantic panel close button");
}

function matchingParen(text, openIndex) {
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = openIndex; index < text.length; index++) {
    const character = text[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === '"' || character === "'" || character === "`") {
      quote = character;
      continue;
    }
    if (character === "(") depth++;
    else if (character === ")") {
      depth--;
      if (depth === 0) return index;
    }
  }
  return -1;
}

const secondCallOpen = source.indexOf(")(", closeStart + 1) + 1;
const closeEnd = matchingParen(source, secondCallOpen);
if (secondCallOpen <= 0 || closeEnd < closeLabelIndex || closeEnd - closeStart > 1000) {
  throw new Error("Could not resolve semantic close button call boundaries");
}
source = source.slice(0, closeStart) + source.slice(closeEnd + 1);

const tabEntry = '{title:e("tab"),type:Dn.g';
const tabIndex = source.indexOf(tabEntry);
if (tabIndex < 0) {
  throw new Error("Could not locate built-in panel registry insertion point");
}
const semanticEntry = '{title:"履带实车语义多点导航",type:"SemanticWaypointPanel",description:"固定在页面中的中文语义多点导航卡片",thumbnail:ui,module:async()=>({default:(0,bg.c)(()=>(0,n.jsx)(ru,{open:!0,onClose:()=>{}}))})},';
source = source.slice(0, tabIndex) + semanticEntry + source.slice(tabIndex);

for (const required of [
  'type:"SemanticWaypointPanel"',
  'title:"履带实车语义多点导航"',
  embeddedStyle,
]) {
  if (!source.includes(required)) throw new Error(`Missing embedded panel result: ${required}`);
}
if (source.includes('"data-tourid":"semantic-waypoint-control-button"')) {
  throw new Error("Floating semantic toolbar button remains");
}

fs.writeFileSync(outputPath, source, "utf8");
console.log(`Embedded SemanticWaypointPanel in ${outputPath}`);
