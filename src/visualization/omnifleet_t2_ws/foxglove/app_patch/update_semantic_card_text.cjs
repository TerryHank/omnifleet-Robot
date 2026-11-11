#!/usr/bin/env node
"use strict";

const fs = require("fs");

const [inputPath, outputPath] = process.argv.slice(2);
if (!inputPath || !outputPath) {
  throw new Error("Usage: update_semantic_card_text.cjs INPUT OUTPUT");
}

function escaped(text) {
  return text
    .split("")
    .map((character) => {
      const code = character.charCodeAt(0);
      return code > 127 ? `\\u${code.toString(16).padStart(4, "0").toUpperCase()}` : character;
    })
    .join("");
}

let source = fs.readFileSync(inputPath, "utf8");
const replacements = [
  ["单实车语义多点导航", "履带实车语义多点导航（页面卡片）"],
  ["需要时打开；关闭后不占布局、不收发话题", "固定在页面中；与地图、控制按钮和曲线同时显示"],
  ["2. 在左侧 3D 地图点击“发布姿态”放置点位", "2. 在左侧 3D 地图点击“添加多点航点”放置点位"],
  ["本窗口不拦截左侧地图操作，可以连续添加任意数量的点。", "本卡片不遮挡左侧地图，可以连续添加任意数量的点。"],
];

for (const [beforeText, afterText] of replacements) {
  const before = escaped(beforeText);
  const after = escaped(afterText);
  const count = source.split(before).length - 1;
  if (count !== 1) {
    throw new Error(`Expected one runtime string '${beforeText}', found ${count}`);
  }
  source = source.replace(before, after);
}

fs.writeFileSync(outputPath, source, "utf8");
console.log(`Updated semantic card text in ${outputPath}`);
