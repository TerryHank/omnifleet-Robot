"""Replay real rectified clips through baseline and palm/NanoTrack candidates."""
from pathlib import Path
import collections
import importlib.util
import json
import sys
import tarfile
import time
from types import SimpleNamespace
import cv2
import numpy as np

stage=Path(__file__).parent
a2=(Path.home()/'omnifleet_a2_ws').exists()
workspace=(Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/from-126.4EV8FJM3/vendor/home/iecme/omnifleet_ws' if a2 else Path.home()/'omnifleet_ws')
sys.path.insert(0,str(workspace/'src/perception/omnifleet_person_follow'))
import omnifleet_person_follow
from omnifleet_person_follow.hand_only_detector import HandOnlyDetector as Baseline
from omnifleet_person_follow.trt_net import TensorRTNet
from omnifleet_person_follow.person_masks import person_masks
omnifleet_person_follow.__path__.insert(0,str(stage))

def load(name,path):
    spec=importlib.util.spec_from_file_location('omnifleet_person_follow.'+name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

module=load('palm_candidate',stage/'hand_only_detector.py')
tracker=load('palm_tracker',stage/'hand_nanotrack.py')
module.HandNanoTrack=tracker.HandNanoTrack
candidate_core=load('palm_core_candidate',stage/'core_candidate.py')
module.classify_gesture=candidate_core.classify_gesture
palm_class=module.PalmDetector
module.PalmDetector=lambda _:palm_class(stage/'palm_full_fp32.engine')
Candidate=module.HandOnlyDetector
models=(workspace.parent/'omnifleet_data/ml_models/omnifleet_vision/vendor' if a2 else Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor')
old_stage=stage.parent/'hand-nanotrack-20261112'
person=TensorRTNet(old_stage/'person-raw.engine',('output0','output1'))

def people_in(image):
    height,width=image.shape[:2];gain=min(512/width,512/height)
    resized=cv2.resize(image,(round(width*gain),round(height*gain)))
    left=round((512-resized.shape[1])/2-.1);top=round((512-resized.shape[0])/2-.1)
    padded=cv2.copyMakeBorder(resized,top,512-resized.shape[0]-top,left,512-resized.shape[1]-left,cv2.BORDER_CONSTANT,value=(114,114,114))
    person.setInput(np.ascontiguousarray(padded[:,:,::-1].transpose(2,0,1)[None],np.float32)/255.)
    boxes,prototypes=person.forward(person.output_names)
    decoded,_=person_masks(boxes[0],prototypes[0],image.shape,512,.1)
    return [dict(id=i+1,bbox=box[:4].tolist()) for i,box in enumerate(decoded)]

summary={};results={}
def run_clip(name,samples,cold=False):
    baseline=Baseline();candidate=Candidate(str(models/'nanotrack_v2'))
    if name == 'moving_one':
        baseline.center=(885.4077529907227,641.3044595718384)
        baseline.size=170.88566780090332
        baseline.rotation=.5220776200294495
        baseline.owner=1
    rows=[]
    for file,image,people in samples:
        if cold:baseline.reset();candidate.reset()
        row=dict(file=file)
        for key,obj in [('baseline',baseline),('palm',candidate)]:
            began=time.perf_counter();hands=obj.infer(image,people)
            row[key]=dict(labels=[h['gesture'] for h in hands],ms=(time.perf_counter()-began)*1000,debug=obj.debug)
        rows.append(row)
    baseline.close();candidate.close()
    results[name]=rows
    summary[name]={key:dict(labels=dict(collections.Counter(g for r in rows for g in r[key]['labels'])),median_ms=float(np.median([r[key]['ms'] for r in rows]))) for key in ['baseline','palm']}
    summary[name]['changes']=[dict(file=r['file'],before=r['baseline']['labels'],after=r['palm']['labels']) for r in rows if r['baseline']['labels']!=r['palm']['labels']]
    print(name,json.dumps(summary[name]),flush=True)
    (stage/'chain-results.json').write_text(json.dumps(results,indent=2))
    (stage/'chain-summary.json').write_text(json.dumps(summary,indent=2))

manifest=json.loads((old_stage/'frames/manifest.json').read_text())
for clip in dict.fromkeys(x['clip'] for x in manifest):
    samples=[]
    for entry in [x for x in manifest if x['clip']==clip]:
        image=cv2.imread(str(old_stage/'frames'/entry['file']))
        samples.append((entry['file'],image,people_in(image)))
    run_clip(clip,samples)

cal=json.loads((stage/'rgb-calibration.json').read_text())['color']
k=np.array(cal['k']).reshape(3,3);d=np.array(cal['d']);size=(cal['width'],cal['height'])
nk,_=cv2.getOptimalNewCameraMatrix(k,d,size,0,size,centerPrincipalPoint=True)
maps=cv2.initUndistortRectifyMap(k,d,None,nk,size,cv2.CV_16SC2)
samples=[]
with tarfile.open(stage/'frames.tar.gz') as archive:
    for entry in json.loads((stage/'action-details.json').read_text()):
        data=archive.extractfile(f"rgb-original/{entry['stamp']}.jpg").read()
        image=cv2.remap(cv2.imdecode(np.frombuffer(data,np.uint8),1),*maps,cv2.INTER_LINEAR)
        samples.append((str(entry['second']),image,[dict(id=i+1,bbox=box) for i,box in enumerate(entry['people'])]))
run_clip('side_cold',samples,cold=True)
samples=[]
with tarfile.open(stage/'current-one.tar.gz') as archive:
    for entry in json.loads((stage/'current-one.json').read_text()):
        data=archive.extractfile(entry['file']).read()
        image=cv2.imdecode(np.frombuffer(data,np.uint8),1)
        samples.append((entry['file'],image,entry['people']))
run_clip('moving_one',samples)

candidate=Candidate(str(models/'nanotrack_v2'))
class Dropout:
    def __init__(self,model):self.model=model
    def process(self,request):return SimpleNamespace(landmarks=None,score=0.)
    def reset(self):self.model.reset()
    def close(self):self.model.close()
armed=False
for _,image,people in samples:
    if candidate.infer(image,people):
        candidate.model=Dropout(candidate.model)
        assert not candidate.infer(image,people)
        assert candidate.hand_tracker.active
        armed=True;break
assert armed,'No hand available for dropout check'
candidate.close();person.close()
print('DROPOUT_RETURNS_NO_GESTURE_AND_RETAINS_TRACKING_PASS',flush=True)
