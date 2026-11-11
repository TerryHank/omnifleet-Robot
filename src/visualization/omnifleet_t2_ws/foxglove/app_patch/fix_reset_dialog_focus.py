from pathlib import Path
import shutil
p=Path('/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js')
b=Path('/home/iecme/robot_backups/map_reset_dialog_focus_20260907');b.mkdir(exist_ok=True);shutil.copy2(p,b/p.name)
s=p.read_text();start=s.index('resetButton.addEventListener("click"');end=s.index('const updateTitles=',start)
s=s[:start]+Path(__file__).with_name('reset_map_inline_confirmation.js').read_text()+s[end:]
old='document.getElementById("omnifleet-map-reset-button")?.remove();'
new='document.querySelector("#omnifleet-map-reset-confirmation [data-reset-cancel]")?.click();'+old
assert s.count(old)==1
s=s.replace(old,new,1)
p.write_text(s)
print('Replaced native map-reset dialogs with renderer HTML confirmation')
