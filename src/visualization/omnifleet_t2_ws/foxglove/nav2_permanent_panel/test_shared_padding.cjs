const assert = require('assert');
const fs = require('fs');

const source = fs.readFileSync('Nav2PermanentPanel.js', 'utf8');
assert(source.includes('["costmap_padding", "车体安全余量 · footprint_padding"'));
assert(source.includes("costmap_padding: ['local_padding', 'global_padding']"));
assert(!source.includes('["local_padding", "局部车身安全余量 · footprint_padding"'));
assert(!source.includes('["global_padding", "全局车身安全余量 · footprint_padding"'));
assert(source.includes("'start-blocked', '规划起点被地图判为障碍'"));
assert(source.includes("'costmap_padding');"));
console.log('PASS: one footprint-padding control maps to both costmaps');
