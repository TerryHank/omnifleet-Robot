from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

home=Path.home();workspace=home/'omnifleet_a2_ws'
base=workspace/'deploy/vision-gemini-122';runtime=base/'from-126.4EV8FJM3'
stage=base/'sync-unified-20261112';source=stage/'source'
backup=home/'omnifleet_a2_backups'/('vision-unified-'+time.strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
vendor=runtime/'vendor/home/iecme/omnifleet_ws'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
protected=json.loads((stage/'protected-before.json').read_text())
assert all(digest(Path(p))==sha for p,sha in protected.items()),'Protected configuration changed before commit'

mapping={}
person=source/'src/perception/omnifleet_person_follow'
body=source/'src/perception/body_tracking'
for prefix in [workspace,vendor]:
    for file in (person/'omnifleet_person_follow').glob('*.py'):
        mapping[prefix/'src/perception/omnifleet_person_follow/omnifleet_person_follow'/file.name]=file
    for relative in ['src','include']:
        for file in (body/relative).rglob('*'):
            if file.is_file():mapping[prefix/'src/perception/body_tracking'/file.relative_to(body)]=file
    for name in ['CMakeLists.txt','package.xml']:
        mapping[prefix/'src/perception/body_tracking'/name]=body/name

mapping[vendor/'build/body_tracking/body_tracking']=source/'build/body_tracking/body_tracking'
mapping[runtime/'manager.py']=stage/'manager.py'
camera=vendor/'src/sensing/omnifleet_hikrobot_rgbd/omnifleet_hikrobot_rgbd/local_frames.py'
mapping[camera]=stage/'local_frames.py'
canonical_camera=workspace/'src/sensing/omnifleet_hikrobot_rgbd/omnifleet_hikrobot_rgbd/local_frames.py'
if canonical_camera.parent.exists():mapping[canonical_camera]=stage/'local_frames.py'
model_root=home/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt'
mapping[model_root/'hand_full_fp32.engine']=stage/'hand_full_fp32.engine'
mapping[model_root/'hand_full.onnx']=stage/'hand_full.onnx'
webroots=[runtime/'site',Path('/opt/foxglove-studio-cn-122/site')]
for web in webroots:
    for name in ['vision-follow.html','vision-follow.web.js','vision-reference.js']:
        mapping[web/name]=stage/name

record=[]
for target,origin in mapping.items():
    assert origin.is_file(),origin
    item=dict(target=str(target),source_sha256=digest(origin),existed=target.exists())
    if target.exists():
        saved=backup/str(target).lstrip('/');saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(target,saved);item.update(old_sha256=digest(target),mode=target.stat().st_mode,backup=str(saved))
    record.append(item)
(backup/'manifest-before.json').write_text(json.dumps(record,indent=2))
subprocess.run(['sudo','-n','systemctl','stop','omnifleet-a2-vision-follow'],check=True)
try:
    for target,origin in mapping.items():
        if str(target).startswith('/opt/'):
            subprocess.run(['sudo','-n','install','-m','0644',str(origin),str(target)],check=True)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_name(target.name+'.sync122')
            shutil.copy2(origin,temporary);os.replace(temporary,target)
    assert all(digest(Path(item['target']))==item['source_sha256'] for item in record)
    assert all(digest(Path(p))==sha for p,sha in protected.items()),'Protected configuration changed'
    for item in record:
        path=Path(item['target'])
        if path.suffix=='.py':compile(path.read_text(),str(path),'exec')
    meta=dict(precision='FP32',tf32=False,built_on='122',onnx_sha256=digest(stage/'hand_full.onnx'),
              source_model='MediaPipe hand_landmark_full.tflite 0.10.18',
              source_sha256=digest(home/'omnifleet_ws/.env/hand-runtime/mediapipe/modules/hand_landmark/hand_landmark_full.tflite'))
    (model_root/'hand_full_fp32.json').write_text(json.dumps(meta,indent=2))
    result=dict(backup=str(backup),files=record,protected_configurations=protected,success=True)
    (stage/'deployment.json').write_text(json.dumps(result,indent=2))
    print('COMMITTED',len(record),'FILES',backup,flush=True)
except Exception:
    for item in reversed(record):
        target=Path(item['target'])
        if item['existed']:
            if str(target).startswith('/opt/'):
                subprocess.run(['sudo','-n','cp','-p',item['backup'],str(target)],check=True)
            else:shutil.copy2(item['backup'],target)
        elif target.exists():target.unlink()
    raise
finally:
    subprocess.run(['sudo','-n','systemctl','start','omnifleet-a2-vision-follow'],check=True)
