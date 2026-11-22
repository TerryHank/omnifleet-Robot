from pathlib import Path
import importlib.util
import sys
sys.path.insert(0,str(Path.home()/'omnifleet_ws/.env/hand-runtime'))
import cv2
import numpy as np
from mediapipe.framework.formats import rect_pb2

root=Path(__file__).parent
runtime=Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/from-126.4EV8FJM3'
sys.path.insert(0,str(runtime/'vendor/home/iecme/omnifleet_ws/src/perception/omnifleet_person_follow'))
import omnifleet_person_follow
omnifleet_person_follow.__path__.insert(0,str(root))
from omnifleet_person_follow.core import classify_gesture
from omnifleet_person_follow.hand_geometry import canonical_hand
spec=importlib.util.spec_from_file_location('omnifleet_person_follow.multi_gpu',root/'hand_full_gpu-multiview.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
gpu=module.HandFullGpu(Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt/hand_full_fp32.engine')
records=[]
for name,cx,cy in [('okay',834,236),('victory',754,302)]:
    image=cv2.imread(str(runtime.parent/f'sync-unified-20261112/{name}.jpg'))
    height,width=image.shape[:2]
    for angle in [0,30,-30,60,-60,90,-90]:
        matrix=cv2.getRotationMatrix2D((width/2,height/2),angle,1.)
        rotated=cv2.warpAffine(image,matrix,(width,height))
        x,y=matrix@np.array([cx,cy,1.])
        result=gpu.process(dict(image=cv2.cvtColor(rotated,cv2.COLOR_BGR2RGB),roi=rect_pb2.NormalizedRect(x_center=x/width,y_center=y/height,width=240/width,height=240/height,rotation=-np.deg2rad(angle))))
        assert result.landmarks is not None,(name,angle,'missing')
        points=np.asarray([[p.x*width,p.y*height,p.z*width] for p in result.landmarks.landmark])
        world=canonical_hand([[p.x,p.y,p.z] for p in result.world.landmark])
        label=classify_gesture(points,world)
        assert label==name,(name,angle,label)
        records.append((name,angle,label))
gpu.close()
print('14_OK_AND_TWO_FINGER_ROTATIONS_PASS',records)
