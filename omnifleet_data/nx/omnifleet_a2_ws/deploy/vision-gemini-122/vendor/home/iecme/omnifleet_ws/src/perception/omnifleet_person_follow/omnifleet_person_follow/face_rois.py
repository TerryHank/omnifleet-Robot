"""Measured face ROIs for the native controller's existing face/head input."""
import cv2
import numpy as np


class FaceRois:
    def __init__(self, model):
        targets = cv2.dnn.getAvailableTargets(cv2.dnn.DNN_BACKEND_CUDA)
        cuda = cv2.dnn.DNN_TARGET_CUDA_FP16 in targets
        self.backend = 'OpenCV CUDA FP16' if cuda else 'OpenCV CPU'
        self.detector = cv2.FaceDetectorYN.create(model, '', (320,320), .85, .3, 100,
            cv2.dnn.DNN_BACKEND_CUDA if cuda else cv2.dnn.DNN_BACKEND_OPENCV,
            cv2.dnn.DNN_TARGET_CUDA_FP16 if cuda else cv2.dnn.DNN_TARGET_CPU)

    def detect(self, image, tracks, locked_id):
        if not tracks:
            return 0
        selected = next((t for t in tracks if t['id'] == locked_id), None)
        if selected is None:
            selected = max(tracks, key=lambda t: t['bbox'][2]-t['bbox'][0])
        x0,y0,x1,y1 = map(int, selected['bbox'])
        x0,y0 = max(0,x0),max(0,y0)
        x1,y1 = min(image.shape[1],x1),min(image.shape[0],y1)
        y1 = min(y1, y0+max(1, int((y1-y0)*.6)))
        crop = image[y0:y1,x0:x1]
        if crop.size == 0:
            return 0
        gain = min(320/crop.shape[1],320/crop.shape[0])
        width,height = max(1,round(crop.shape[1]*gain)),max(1,round(crop.shape[0]*gain))
        canvas = np.zeros((320,320,3),np.uint8)
        canvas[:height,:width] = cv2.resize(crop,(width,height))
        _, faces = self.detector.detect(canvas)
        if faces is None:
            return 0
        for face in sorted(faces, key=lambda f: float(f[-1]), reverse=True):
            fx,fy,fw,fh = face[:4]/gain
            if fx < 0 or fy < 0 or fx+fw > crop.shape[1] or fy+fh > crop.shape[0]:
                continue
            selected['face_bbox'] = [x0+fx,y0+fy,x0+fx+fw,y0+fy+fh]
            selected['face_confidence'] = float(face[-1])
            return 1
        return 0
