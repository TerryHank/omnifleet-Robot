"""Install the palm-to-NanoTrack chain, retaining host-specific configuration."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

stage=Path(__file__).parent
home=Path.home()
target=sys.argv[1]
assert target in ('122','126')
if target=='122':
    ws=home/'omnifleet_a2_ws'
    workspaces=[ws,ws/'deploy/vision-gemini-122/from-126.4EV8FJM3/vendor/home/iecme/omnifleet_ws']
    service='omnifleet-a2-vision-follow'
    backup_root=home/'omnifleet_a2_backups'
else:
    workspaces=[home/'omnifleet_ws']
    service='omnifleet-t2-vision-demo'
    backup_root=home/'robot_backups'
payload={}
for workspace in workspaces:
    package=workspace/'src/perception/omnifleet_person_follow/omnifleet_person_follow'
    for name in ['hand_only_detector.py','palm_detector.py','hand_nanotrack.py','core.py']:
        if name=='core.py':
            text=(package/name).read_text()
            old=' or np.linalg.norm(points[4] - points[5]) > .78 * palm'
            if old in text:
                assert text.count(old)==1,(package/name,'Unexpected digit classifier')
                text=text.replace(old,'')
            else:
                assert 'if axis_length <= 1e-6 or palm <= 1e-6:' in text,(package/name,'Unexpected digit classifier')
        else:text=(stage/name).read_text()
        compile(text,str(package/name),'exec')
        payload[package/name]=text.encode()
        peers=list((workspace/'build/omnifleet_person_follow').rglob(name))
        if not peers:peers=[p.parent/name for p in (workspace/'build/omnifleet_person_follow').rglob('perception.py')]
        for peer in peers:
            if not peer.exists() or not peer.samefile(package/name):payload[peer]=text.encode()
model_folders={home/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt'}
if target=='122':model_folders.add(workspaces[1].parent/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt')
for folder in model_folders:
    for name in ['palm_full.onnx','palm_full.tflite','palm_full_fp32.engine','palm_full_PROVENANCE.json']:
        payload[folder/name]=(stage/name).read_bytes()
backup=backup_root/('hand-palm-'+time.strftime('%Y%m%d-%H%M%S'))
records=[]
for path in payload:
    saved=backup/str(path).lstrip('/')
    if path.exists():
        saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
    records.append(dict(target=str(path),backup=str(saved) if path.exists() else None))
subprocess.run(['sudo','-n','systemctl','stop',service],check=True)
try:
    for path,data in payload.items():
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    for row in records:row['sha256']=hashlib.sha256(Path(row['target']).read_bytes()).hexdigest()
    (stage/'deployment.json').write_text(json.dumps(dict(service=service,backup=str(backup),files=records),indent=2))
except Exception:
    for row in reversed(records):
        if row['backup']:shutil.copy2(row['backup'],row['target'])
        else:Path(row['target']).unlink(missing_ok=True)
    raise
finally:subprocess.run(['sudo','-n','systemctl','start',service],check=True)
print('DEPLOYED',service,backup)
