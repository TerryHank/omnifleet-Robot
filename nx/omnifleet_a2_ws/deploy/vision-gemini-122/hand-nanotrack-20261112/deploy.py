from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

home=Path.home();stage=Path(__file__).parent
is_a2=(home/'omnifleet_a2_ws').exists()
if is_a2:
    workspace=home/'omnifleet_a2_ws'
    runtime=workspace/'deploy/vision-gemini-122/from-126.4EV8FJM3/vendor/home/iecme/omnifleet_ws'
    workspaces=[workspace,runtime]
    models=runtime.parent/'omnifleet_data/ml_models/omnifleet_vision/vendor/nanotrack_v2'
    service='omnifleet-a2-vision-follow'
    backup=home/'omnifleet_a2_backups'/('hand-nanotrack-'+time.strftime('%Y%m%d-%H%M%S'))
else:
    workspace=home/'omnifleet_ws';workspaces=[workspace]
    models=home/'omnifleet_data/ml_models/omnifleet_vision/vendor/nanotrack_v2'
    service='omnifleet-t2-vision-demo'
    backup=home/'robot_backups'/('hand-nanotrack-'+time.strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
files=['hand_only_detector.py','hand_nanotrack.py','nanotrack_tracker.py']
mapping={};payload={}
for ws in workspaces:
    package=ws/'src/perception/omnifleet_person_follow/omnifleet_person_follow'
    for name in files:payload[package/name]=(stage/name).read_text()
    p=package/'perception.py';text=p.read_text()
    old='self.hand_only_detector = HandOnlyDetector()'
    assert text.count(old)==1,(p,'constructor changed')
    payload[p]=text.replace(old,"self.hand_only_detector = HandOnlyDetector(str(Path(model_root)/'nanotrack_v2'))")
    for name in files+['perception.py']:
        peers=list((ws/'build/omnifleet_person_follow').rglob(name)) if (ws/'build/omnifleet_person_follow').exists() else []
        if not peers and (ws/'build/omnifleet_person_follow').exists():
            peers=[f.parent/name for f in (ws/'build/omnifleet_person_follow').rglob('perception.py')]
        for peer in peers:
            if not peer.exists() or not peer.samefile(package/name):payload[peer]=payload[package/name]
for path,text in payload.items():compile(text,str(path),'exec')
records=[]
for target in payload:
    row=dict(target=str(target),existed=target.exists())
    if target.exists():
        saved=backup/str(target).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved);row['backup']=str(saved)
    records.append(row)
subprocess.run(['sudo','-n','systemctl','stop',service],check=True)
try:
    for path,text in payload.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    # Keep standalone construction usable on the receiver's existing layout.
    shared=home/'omnifleet_data/ml_models/omnifleet_vision/vendor/nanotrack_v2'
    if not shared.exists():shutil.copytree(models,shared)
    for row in records:row['sha256']=hashlib.sha256(Path(row['target']).read_bytes()).hexdigest()
    (stage/'deployment.json').write_text(json.dumps(dict(backup=str(backup),files=records,models=str(models),service=service),indent=2))
    print('DEPLOYED',service,backup,flush=True)
except Exception:
    for row in reversed(records):
        path=Path(row['target'])
        if row['existed']:shutil.copy2(row['backup'],path)
        elif path.exists():path.unlink()
    raise
finally:subprocess.run(['sudo','-n','systemctl','start',service],check=True)
