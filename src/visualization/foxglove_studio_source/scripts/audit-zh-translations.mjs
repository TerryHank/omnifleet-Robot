import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const i18nRoot = path.resolve("packages/studio-base/src/i18n");
const languages = ["en", "zh"];
const entries = Object.fromEntries(languages.map((language) => [language, new Map()]));
const propertyPattern = /^\s+(?:"([^"]+)"|([A-Za-z0-9_]+)):/gm;

for (const language of languages) {
  const directory = path.join(i18nRoot, language);
  for (const filename of fs.readdirSync(directory).filter((name) => name.endsWith(".ts"))) {
    if (filename === "index.ts") {
      continue;
    }
    const source = fs.readFileSync(path.join(directory, filename), "utf8");
    const keys = new Set([...source.matchAll(propertyPattern)].map((match) => match[1] ?? match[2]));
    entries[language].set(filename, { keys, source });
  }
}

const failures = [];
for (const [filename, english] of entries.en) {
  const chinese = entries.zh.get(filename);
  if (!chinese) {
    failures.push(`${filename}: 缺少中文文件`);
    continue;
  }
  const missing = [...english.keys].filter((key) => !chinese.keys.has(key));
  if (missing.length > 0) {
    failures.push(`${filename}: 缺少键 ${missing.join(", ")}`);
  }
  if (/^\s+[^/\n]+:\s*undefined,/m.test(chinese.source)) {
    failures.push(`${filename}: 存在 undefined 中文翻译`);
  }
}

const englishKeyCount = [...entries.en.values()].reduce((sum, entry) => sum + entry.keys.size, 0);
const chineseKeyCount = [...entries.zh.values()].reduce((sum, entry) => sum + entry.keys.size, 0);
console.log(`英文键: ${englishKeyCount}; 中文键: ${chineseKeyCount}; 中文文件: ${entries.zh.size}`);

if (failures.length > 0) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("中文翻译键与英文资源完整对齐，且没有 undefined 回退项。");
