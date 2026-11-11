"""MediaPipe Full palm proposals; landmark inference validates complete hands.

Decode and ROI conventions follow MediaPipe v0.10.18 (Apache-2.0).
"""
import cv2
import numpy as np
from .trt_net import TensorRTNet


class PalmDetector:
    def __init__(self, engine):
        self.net = TensorRTNet(engine, ('Identity', 'Identity_1'))
        self.backend = 'TensorRT FP32 Full palm'
        anchors = []
        for cells, count in [(24, 2), (12, 6)]:
            for y in range(cells):
                for x in range(cells):
                    anchors.extend([((x+.5)/cells, (y+.5)/cells)]*count)
        self.anchors = np.asarray(anchors, np.float32)
        self.detect(np.zeros((192,192,3), np.uint8))

    def detect(self, image):
        height, width = image.shape[:2]
        extent = float(max(height, width))
        corners = cv2.boxPoints(((width/2,height/2),(extent,extent),0.))
        matrix = cv2.getPerspectiveTransform(corners,np.float32([[0,192],[0,0],[192,0],[192,192]]))
        square = cv2.warpPerspective(image,matrix,(192,192),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        tensor = np.ascontiguousarray(square[:,:,::-1].transpose(2,0,1)[None],np.float32)/255.
        self.net.setInput(tensor)
        boxes, logits = self.net.forward(self.net.output_names)
        scores = 1/(1+np.exp(-np.clip(logits[0,:,0],-80,80)))
        # These are proposals, not gesture decisions; Full landmarks retain
        # their existing presence threshold and gesture classification rules.
        keep = scores >= .001
        raw, anchors, scores = boxes[0][keep], self.anchors[keep], scores[keep]
        center, size = raw[:,:2]/192+anchors, raw[:,2:4]/192
        bounds = np.column_stack((center-size/2,center+size/2))
        points = raw[:,4:].reshape(-1,7,2)/192+anchors[:,None,:]
        order = np.argsort(-scores)
        output = []
        offset = np.array([(width-extent)/2,(height-extent)/2])
        while len(order) and len(output) < 8:
            first = order[0]
            low = np.maximum(bounds[first,:2],bounds[order,:2])
            high = np.minimum(bounds[first,2:],bounds[order,2:])
            overlap = np.maximum(high-low,0).prod(1)
            area = np.maximum(bounds[first,2:]-bounds[first,:2],0).prod()
            areas = np.maximum(bounds[order,2:]-bounds[order,:2],0).prod(1)
            matched = overlap/np.maximum(area+areas-overlap,1e-9) > .3
            matched[0] = True
            group = order[matched]
            box = np.average(bounds[group],axis=0,weights=scores[group])*extent+np.tile(offset,2)
            joints = np.average(points[group],axis=0,weights=scores[group])*extent+offset
            axis = joints[2]-joints[0]
            angle = float(np.arctan2(axis[0],-axis[1]))
            h = box[3]-box[1]
            cx = (box[0]+box[2])/2+.5*h*np.sin(angle)
            cy = (box[1]+box[3])/2-.5*h*np.cos(angle)
            output.append(dict(score=float(scores[first]),cx=float(cx),cy=float(cy),
                               size=float(max(box[2]-box[0],h)*2.6),rotation=angle))
            order = order[~matched]
        return output

    def close(self):
        self.net.close()
