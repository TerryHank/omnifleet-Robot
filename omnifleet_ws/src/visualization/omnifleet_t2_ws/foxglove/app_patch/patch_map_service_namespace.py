#!/usr/bin/env python3
"""Repair the two legacy map-toolbar calls in the deployed CN.8 bundle."""
import argparse
import hashlib
import json
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('bundle', type=Path)
p.add_argument('--robot', help='Compatibility argument; local services are unprefixed')
args = p.parse_args()
s = args.bundle.read_text()
before = hashlib.sha256(s.encode()).hexdigest()
for op, button in [('load', 'loadButton'), ('save', 'saveButton')]:
    pattern = re.compile(r'callMapService\("/(?:(?:robot_[0-9]+/)?|omnifleet_t2/waypoints/)map_' + op + r'",path,' + button + r'\)')
    if not pattern.search(s):
        raise SystemExit(f'Expected exactly one map_{op} toolbar call; bundle not changed')
    s = pattern.sub(f'callMapService("/omnifleet_t2/waypoints/map_{op}",path,{button})', s)
old = 'service==="/map_save"?"保存":"加载"'
new = 'service.endsWith("/map_save")?"保存":"加载"'
if old in s:
    s = s.replace(old, new)
elif new not in s:
    raise SystemExit('Expected exactly one operation label; bundle not changed')
s = s.replace('saveWaypointMap({data:path})', '').replace('loadWaypointMap({data:path});', '')
if 'confirmMapLoadPath=initial' not in s:
    s = s.replace('const callMapService=', Path(__file__).with_name('load_path_dialog.js').read_text() + '\nconst callMapService=')
s = s.replace(',path=stripExt(nativePath||`${lastDir}/${file.name}`);', ';const requestedPath=nativePath||await confirmMapLoadPath(`${lastDir}/${file.name}`);if(!requestedPath)return;const path=stripExt(requestedPath);')
args.bundle.write_text(s)
print(json.dumps({'before': before, 'after': hashlib.sha256(s.encode()).hexdigest(), 'robot': args.robot}))
