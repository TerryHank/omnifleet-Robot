from pathlib import Path
import shutil
import time
import os
import pwd

HERE = Path(__file__).resolve().parent
BUNDLE = Path('/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js')
EXT = Path('/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/foxglove_extension/omnifleet-t2-semantic-waypoints/src')
backup = Path('/home/iecme/.local/share/omnifleet_t2/nav2-parameter-backups') / str(time.time_ns())
backup.mkdir(parents=True)
owner = pwd.getpwnam('iecme')
os.chown(backup.parent, owner.pw_uid, owner.pw_gid)
os.chown(backup, owner.pw_uid, owner.pw_gid)
for p in (BUNDLE, EXT / 'Nav2HotParamsPanel.ts', Path('/etc/omnifleet_t2/foxglove.yaml')):
    shutil.copy2(p, backup / p.name)

code = (HERE / 'Nav2PermanentPanel.js').read_text()
function = code.replace('export function initNav2HotParamsPanel(context)', 'function initNav2Builtin(context)', 1)
bundle = BUNDLE.read_text()
start = bundle.index('function initNav2Builtin(')
end = bundle.index('function ru({open:e,onClose:t})', start)
assert bundle.count('function initNav2Builtin(') == 1
BUNDLE.write_text(bundle[:start] + function + bundle[end:])
# This fork has no local extension loader. Keep the reusable extension source in sync.
shutil.copy2(HERE / 'Nav2PermanentPanel.js', EXT / 'Nav2PermanentPanel.js')
(EXT / 'Nav2PermanentPanel.d.ts').write_text('import type { PanelExtensionContext } from "@foxglove/extension";\nexport function initNav2HotParamsPanel(context: PanelExtensionContext): () => void;\n')
(EXT / 'Nav2HotParamsPanel.ts').write_text('export { initNav2HotParamsPanel } from "./Nav2PermanentPanel.js";\n')
for name in ('Nav2HotParamsPanel.ts', 'Nav2PermanentPanel.js', 'Nav2PermanentPanel.d.ts'):
    os.chown(EXT / name, owner.pw_uid, owner.pw_gid)

bridge = Path('/etc/omnifleet_t2/foxglove.yaml')
text = bridge.read_text()
if '^/omnifleet_t2/nav2/(read_saved|save_parameters)$' not in text:
    text = text.replace('    service_whitelist:\n', '    service_whitelist:\n      - "^/omnifleet_t2/nav2/(read_saved|save_parameters)$"\n', 1)
if 'FollowPath' not in text:
    text = text.replace('    param_whitelist:\n', "    param_whitelist:\n      - '^/controller_server[./]FollowPath\\.(max_vel_x|max_speed_xy|max_vel_theta)$'\n", 1)
bridge.write_text(text)
runtime_config = Path('/home/iecme/omnifleet_ws/src/system/workspace_support/omnifleet_t2_ws/runtime/etc/omnifleet_t2/foxglove.yaml')
if runtime_config.exists():
    shutil.copy2(runtime_config, backup / 'runtime-foxglove.yaml')
    shutil.copy2(bridge, runtime_config)
print('backup:', backup)
