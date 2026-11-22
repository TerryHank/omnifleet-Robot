from pathlib import Path
import json
import time
import cv2
import numpy as np
from mediapipe.framework.formats import rect_pb2
from omnifleet_person_follow.hand_only_detector import HandOnlyDetector
from omnifleet_person_follow.hand_full_gpu import HandFullGpu
from omnifleet_person_follow.core import classify_gesture

root=Path(__file__).parent
cpu=HandOnlyDetector().model
assert cpu.__class__.__name__!='HandFullGpu','Expected the independent CPU reference before deployment'
gpu=HandFullGpu(root/'hand_full_fp32.engine')
tests=[('victory',root/'victory.jpg',754,302,240),('okay',root/'okay.jpg',834,236,240),
       ('background',root/'victory.jpg',392,918,480)]
records=[]
for name,path,cx,cy,size in tests:
    rgb=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
    height,width=rgb.shape[:2]
    request=dict(image=rgb,roi=rect_pb2.NormalizedRect(x_center=cx/width,y_center=cy/height,width=size/width,height=size/height))
    c,g=cpu.process(request),gpu.process(request)
    assert bool(c.landmarks)==bool(g.landmarks),(name,'presence')
    row=dict(test=name,present=bool(g.landmarks))
    if c.landmarks:
        cp=np.asarray([[p.x*width,p.y*height,p.z*width] for p in c.landmarks.landmark])
        gp=np.asarray([[p.x*width,p.y*height,p.z*width] for p in g.landmarks.landmark])
        cw=np.asarray([[p.x,p.y,p.z] for p in c.world.landmark])
        gw=np.asarray([[p.x,p.y,p.z] for p in g.world.landmark])
        error=float(np.abs(cp-gp).max());assert error<.01,(name,error)
        a,b=classify_gesture(cp,cw),classify_gesture(gp,gw)
        assert a==b==name,(name,a,b)
        assert c.side.classification[0].label==g.side.classification[0].label
        row.update(cpu_label=a,gpu_label=b,max_error_px=error)
    records.append(row);print('PASS',row,flush=True)
(root/'gpu-equivalence.json').write_text(json.dumps(records,indent=2))
cpu.close();gpu.close()
