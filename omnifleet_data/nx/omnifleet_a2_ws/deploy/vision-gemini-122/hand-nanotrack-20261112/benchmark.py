"""Real-video regression and detector-dropout checks, with no ROS publishers."""
from pathlib import Path
import collections
import importlib.util
import json
import sys
import time
from types import SimpleNamespace
import cv2
import numpy as np

root=Path(__file__).parent
if (Path.home()/'omnifleet_a2_ws').exists():
    runtime=Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/from-126.4EV8FJM3'
    person=runtime/'vendor/home/iecme/omnifleet_ws/src/perception/omnifleet_person_follow'
    models=runtime/'vendor/home/iecme/omnifleet_data/ml_models/omnifleet_vision/vendor'
else:
    person=Path.home()/'omnifleet_ws/src/perception/omnifleet_person_follow'
    models=Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor'
sys.path.insert(0,str(person))
import omnifleet_person_follow
from omnifleet_person_follow.hand_only_detector import HandOnlyDetector as Baseline
omnifleet_person_follow.__path__.insert(0,str(root))
rotation_test=len(sys.argv)>1 and sys.argv[1]=='rotation'
spec=importlib.util.spec_from_file_location('omnifleet_person_follow.hand_candidate',root/('hand_only_detector-rotation.py' if rotation_test else 'hand_only_detector.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
Candidate=module.HandOnlyDetector
if rotation_test:
    spec=importlib.util.spec_from_file_location('omnifleet_person_follow.rotated_gpu',root/'hand_full_gpu-rotation.py')
    rotation_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(rotation_module)
    def configure_rotation(obj):
        obj.model.close()
        obj.model=rotation_module.HandFullGpu(Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt/hand_full_fp32.engine')
from omnifleet_person_follow.trt_net import TensorRTNet
from omnifleet_person_follow.person_masks import person_masks

class Dropout:
    def __init__(self,model):self.model=model;self.drop=False
    def process(self,request):
        return SimpleNamespace(landmarks=None,score=0.) if self.drop else self.model.process(request)
    def reset(self):self.model.reset()
    def close(self):self.model.close()

data=(models/'yolo26_person_follow/yolo26n-seg.engine').read_bytes()
metadata=int.from_bytes(data[:4],'little')
if 0<metadata<len(data)-4 and data[4:5]==b'{':
    json.loads(data[4:4+metadata]);data=data[4+metadata:]
raw=root/'person-raw.engine';raw.write_bytes(data)
detector=TensorRTNet(raw,('output0','output1'))
def people_in(image):
    height,width=image.shape[:2];gain=min(512/width,512/height)
    resized=cv2.resize(image,(round(width*gain),round(height*gain)))
    left=round((512-resized.shape[1])/2-.1);top=round((512-resized.shape[0])/2-.1)
    padded=cv2.copyMakeBorder(resized,top,512-resized.shape[0]-top,left,
        512-resized.shape[1]-left,cv2.BORDER_CONSTANT,value=(114,114,114))
    tensor=np.ascontiguousarray(padded[:,:,::-1].transpose(2,0,1)[None],dtype=np.float32)/255.
    detector.setInput(tensor);boxes,prototypes=detector.forward(detector.output_names)
    decoded,_=person_masks(boxes[0],prototypes[0],image.shape,512,.1)
    return [dict(id=i+1,bbox=box[:4].tolist()) for i,box in enumerate(decoded)]
manifest=json.loads((root/'frames/manifest.json').read_text())
output={};dropout_checked=False
for clip in dict.fromkeys(item['clip'] for item in manifest):
    old=Baseline();new=Candidate(str(models/'nanotrack_v2'));missing=Candidate(str(models/'nanotrack_v2'))
    if rotation_test:
        configure_rotation(new);configure_rotation(missing)
    missing.model=Dropout(missing.model)
    rows=[];seen=0;dropped=0
    for item in [x for x in manifest if x['clip']==clip]:
        image=cv2.imread(str(root/'frames'/item['file']))
        people=people_in(image)
        row=dict(file=item['file'])
        for name,obj in [('baseline',old),('nanotrack',new)]:
            began=time.perf_counter();hands=obj.infer(image,people)
            row[name]=dict(labels=[h['gesture'] for h in hands],ms=(time.perf_counter()-began)*1000)
        missing.model.drop=(seen>=3 and dropped<2 and missing.hand_tracker.active and
                            missing.hand_tracker.owner in {p['id'] for p in people})
        if missing.model.drop:dropped+=1
        hands=missing.infer(image,people)
        if missing.model.drop:
            assert not hands,'old command emitted during detector dropout'
            assert missing.hand_tracker.active,'tracking discarded on first landmark dropout'
            dropout_checked=True
        elif hands:seen+=1
        row['dropout']=dict(labels=[h['gesture'] for h in hands],dropped=missing.model.drop,active=missing.hand_tracker.active)
        row['tracker']=new.hand_tracker.status()
        rows.append(row)
    for obj in [old,new,missing]:obj.close()
    changes=[r for r in rows if r['baseline']['labels']!=r['nanotrack']['labels']]
    print(clip,'frames',len(rows),flush=True)
    for name in ['baseline','nanotrack']:
        print(name,collections.Counter(g for r in rows for g in r[name]['labels']),
              'median',round(float(np.median([r[name]['ms'] for r in rows])),2),flush=True)
    print('CHANGES',[(r['file'],r['baseline']['labels'],r['nanotrack']['labels']) for r in changes],flush=True)
    print('DROPOUT',[(r['file'],r['dropout']) for r in rows if r['dropout']['dropped']],flush=True)
    output[clip]=rows
    (root/('benchmark-rotation.json' if rotation_test else 'benchmark.json')).write_text(json.dumps(output,indent=2))
assert dropout_checked,'dropout test never armed'
print('DROPOUT_STOP_AND_POSITION_RETENTION_PASS',flush=True)
