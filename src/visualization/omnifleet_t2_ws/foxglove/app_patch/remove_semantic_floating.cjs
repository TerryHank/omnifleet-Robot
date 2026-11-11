#!/usr/bin/env node
"use strict";

const fs = require("fs");

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  throw new Error("Usage: remove_semantic_floating.cjs INPUT OUTPUT");
}

let source = fs.readFileSync(inputPath, "utf8");
const marker = '"data-tourid":"semantic-waypoint-control-button"';
if ((source.match(new RegExp(marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) ?? []).length !== 1) {
  throw new Error("Expected exactly one semantic toolbar button marker");
}

const markerIndex = source.indexOf(marker);
const buttonStart = source.lastIndexOf(",u&&(0,n.jsx)(vt,{", markerIndex);
const buttonEndMarker = 'children:(0,n.jsx)(Ee.c,{fontSize:"small"})})';
const buttonEndStart = source.indexOf(buttonEndMarker, markerIndex);
if (buttonStart < 0 || buttonEndStart < 0) {
  throw new Error("Could not resolve semantic toolbar button boundaries");
}
const buttonEnd = buttonEndStart + buttonEndMarker.length;
source = source.slice(0, buttonStart) + source.slice(buttonEnd);

const semanticProps = "semanticControlOpen:q,onSemanticControlToggle:()=>{Z(lt=>!lt)},";
if (source.split(semanticProps).length !== 2) {
  throw new Error("Expected exactly one semantic AppBar prop block");
}
source = source.replace(semanticProps, "");

const floatingControl = ",(0,n.jsx)(ru,{open:q,onClose:()=>{Z(!1)}})";
if (source.split(floatingControl).length !== 2) {
  throw new Error("Expected exactly one floating semantic control render");
}
source = source.replace(floatingControl, "");

for (const forbidden of [marker, semanticProps, floatingControl]) {
  if (source.includes(forbidden)) {
    throw new Error(`Floating semantic UI residue remains: ${forbidden}`);
  }
}

fs.writeFileSync(outputPath, source, "utf8");
console.log(`Patched ${inputPath} -> ${outputPath}`);
