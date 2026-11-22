from pathlib import Path
import importlib.util
import sys
import cv2
import numpy as np

root=Path(__file__).parent
runtime=Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/from-126.4EV8FJM3'
person=runtime/'vendor/home/iecme/omnifleet_ws/src/perception/omnifleet_person_follow'
sys.path.insert(0,str(person))
import omnifleet_person_follow
omnifleet_person_follow.__path__.insert(0,str(root))
from omnifleet_person_follow.hand_only_detector import HandOnlyDetector
from omnifleet_person_follow.hand_geometry import canonical_hand
from omnifleet_person_follow.core import classify_gesture
from mediapipe.framework.formats import rect_pb2
spec=importlib.util.spec_from_file_location('omnifleet_person_follow.gpu_rotated',root/'hand_full_gpu-rotation.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
engine=Path.home()/'omnifleet_data/ml_models/omnifleet_vision/vendor/mediapipe_tensorrt/hand_full_fp32.engine'
gpu=module.HandFullGpu(engine)
image=cv2.imread(str(runtime.parent/'sync-unified-20261112/victory.jpg'))
height,width=image.shape[:2];center=np.array([754.,302.,1.])
for degrees in [0,30,-30,60,-60,90,-90]:
    matrix=cv2.getRotationMatrix2D((width/2,height/2),degrees,1.)
    rotated=cv2.warpAffine(image,matrix,(width,height))
    cx,cy=matrix@center
    result=gpu.process(dict(image=cv2.cvtColor(rotated,cv2.COLOR_BGR2RGB),
        roi=rect_pb2.NormalizedRect(x_center=cx/width,y_center=cy/height,width=240/width,height=240/height,rotation=-np.deg2rad(degrees))))
    assert result.landmarks is not None,degrees
    points=np.asarray([[p.x*width,p.y*height,p.z*width] for p in result.landmarks.landmark])
    world=np.asarray([[p.x,p.y,p.z] for p in result.world.landmark])
    gesture=classify_gesture(points,canonical_hand(world))
    assert gesture=='victory',(degrees,gesture)
    print('ROTATION_PASS',degrees,gesture,flush=True)
gpu.close()
rng=np.random.default_rng(123);points=rng.normal(size=(21,3));reference=canonical_hand(points)
for _ in range(100):
    q,_=np.linalg.qr(rng.normal(size=(3,3)))
    if np.linalg.det(q)<0:q[:,0]*=-1
    transformed=(points@q.T)*rng.uniform(.1,10)+rng.normal(size=3)
    assert np.allclose(canonical_hand(transformed),reference,atol=1e-10)
print('100_CANONICAL_COORDINATE_INVARIANCE_TESTS_PASS',flush=True)
