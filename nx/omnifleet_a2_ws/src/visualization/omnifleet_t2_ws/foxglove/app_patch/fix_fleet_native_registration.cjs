#!/usr/bin/env node
"use strict";

const fs = require("fs");

const [inputPath, outputPath, wrapperPath] = process.argv.slice(2);
if (!inputPath || !outputPath || !wrapperPath) {
  throw new Error("Usage: fix_fleet_native_registration.cjs INPUT OUTPUT WRAPPER");
}

let bundle = fs.readFileSync(inputPath, "utf8");
const wrapper = fs.readFileSync(wrapperPath, "utf8").trim();

if (bundle.includes("function FleetSemanticNative(")) {
  throw new Error("FleetSemanticNative is already defined in the bundle");
}

const endMarker = "/* OMNIFLEET_FLEET_PANEL_END */";
const markerIndex = bundle.indexOf(endMarker);
if (markerIndex < 0) {
  throw new Error(`Missing ${endMarker} marker`);
}

const insertAt = markerIndex + endMarker.length;
bundle = `${bundle.slice(0, insertAt)}\n\n${wrapper}\n${bundle.slice(insertAt)}`;

if (!bundle.includes("function FleetSemanticNative(")) {
  throw new Error("FleetSemanticNative definition was not injected");
}
if (!bundle.includes('type:"omnifleet-t2-semantic-waypoints.fleet-panel"')) {
  throw new Error("Fleet panel registration is missing");
}
if ((bundle.match(/FleetSemanticNative/g) || []).length !== 2) {
  throw new Error("Unexpected FleetSemanticNative reference count");
}

fs.writeFileSync(outputPath, bundle, "utf8");
console.log(`Injected FleetSemanticNative into ${outputPath}`);
