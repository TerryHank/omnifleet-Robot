from pathlib import Path
import shutil
bundle=Path('/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js')
backup=Path('/home/iecme/robot_backups/map_reset_button_20260907');backup.mkdir(exist_ok=True)
shutil.copy2(bundle,backup/bundle.name)
s=bundle.read_text()
marker='const updateTitles=()=>{'
assert s.count(marker)==1
handler='const resetId="omnifleet-map-reset-button";\nconst resetButton=makeButton(resetId,"清空当前地图并重新建图",\'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M7 4V2h10v2h4v2H3V4h4zm-2 4h14l-1 14H6L5 8zm4 2v9h2v-9H9zm4 0v9h2v-9h-2z"/></svg>\');\n' + Path(__file__).with_name('reset_map_inline_confirmation.js').read_text()
s=s.replace(marker,handler+marker,1)
s=s.replace('document.getElementById(loadId)?.remove();','document.getElementById(loadId)?.remove();document.querySelector("#omnifleet-map-reset-confirmation [data-reset-cancel]")?.click();document.getElementById("omnifleet-map-reset-button")?.remove();',1)
bundle.write_text(s)
print('Added map reset toolbar button')
