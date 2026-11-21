"""Compare converted palm CPU ONNX and FP32 TensorRT tensors on real crops."""
from pathlib import Path
import json,sys,tarfile
import cv2,numpy as np
r=Path(__file__).parent
ws=(Path.home()/'omnifleet_a2_ws/deploy/vision-gemini-122/from-126.4EV8FJM3/vendor/home/iecme/omnifleet_ws')
sys.path.insert(0,str(ws/'src/perception/omnifleet_person_follow'))
from omnifleet_person_follow.trt_net import TensorRTNet
cpu=cv2.dnn.readNetFromONNX(str(r/'palm_full.onnx'))
gpu=TensorRTNet(r/'palm_full_fp32.engine',('Identity','Identity_1'))
cv2.setNumThreads(1)
cal=json.loads((r/'rgb-calibration.json').read_text())['color']
k=np.array(cal['k']).reshape(3,3);d=np.array(cal['d']);size=(cal['width'],cal['height'])
nk,_=cv2.getOptimalNewCameraMatrix(k,d,size,0,size,centerPrincipalPoint=True)
maps=cv2.initUndistortRectifyMap(k,d,None,nk,size,cv2.CV_16SC2)
records=[]
with tarfile.open(r/'frames.tar.gz') as a:
    for row in json.loads((r/'action-details.json').read_text()):
        if row['second'] not in [132,134,136,138,140]:continue
        data=a.extractfile(f"rgb-original/{row['stamp']}.jpg").read()
        image=cv2.remap(cv2.imdecode(np.frombuffer(data,np.uint8),1),*maps,cv2.INTER_LINEAR)
        x1,y1,x2,y2=row['people'][0];pad=np.clip((y2-y1)*.45,160,320)/2
        x,y,rr,b=max(0,int(x1-pad)),max(0,int(y1-pad)),min(1920,int(x2+pad)),min(1080,int(y2+pad))
        image=image[y:b,x:rr];h,w=image.shape[:2];extent=float(max(h,w))
        matrix=cv2.getPerspectiveTransform(cv2.boxPoints(((w/2,h/2),(extent,extent),0.)),np.float32([[0,192],[0,0],[192,0],[192,192]]))
        square=cv2.warpPerspective(image,matrix,(192,192),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        blob=np.ascontiguousarray(square[:,:,::-1].transpose(2,0,1)[None],np.float32)/255.
        cpu.setInput(blob);gpu.setInput(blob)
        before=cpu.forward(['Identity','Identity_1']);after=gpu.forward(gpu.output_names)
        errors=[float(np.max(np.abs(x-y))) for x,y in zip(before,after)]
        assert max(errors)<.01,(row['second'],errors)
        records.append(dict(second=row['second'],max_absolute_errors=errors))
gpu.close()
(r/'palm-numeric.json').write_text(json.dumps(records,indent=2))
print('PALM_FP32_TENSOR_COMPARISON_PASS',records)
