"""OpenCV-DNN NanoTrackV2 with size penalties expressed in target-size units.

Reference: OpenCV 4.10 modules/video/src/tracking/tracker_nano.cpp (Apache-2.0),
and HonglinChu/SiamTrackers NanoTrack/nanotrack/tracker/nano_tracker.py.
The installed 4.10 implementation divides predicted size by screen position.
Keep its crop, model, window and learning-rate settings, correcting that ratio.
"""
from pathlib import Path
import cv2
import numpy as np


def size_cal(width, height):
    pad=(width+height)*.5
    return np.sqrt((width+pad)*(height+pad))


class NanoTracker:
    def __init__(self, root, backend, target, verify_template=False):
        self.verify_template=verify_template
        self.template_score=1.
        self.stop_reason=''
        self.backbone=cv2.dnn.readNet(str(Path(root)/'backbone.onnx'))
        self.head=cv2.dnn.readNet(str(Path(root)/'head.onnx'))
        for net in (self.backbone,self.head):
            net.setPreferableBackend(backend);net.setPreferableTarget(target)
        self.window=cv2.createHanningWindow((16,16),cv2.CV_32F)
        grid=(np.arange(16,dtype=np.float32)-8)*16+127
        self.grid_x,self.grid_y=np.meshgrid(grid,grid)
        self.score=0.

    def crop(self, image, size, output_size):
        offset=(size+1)//2
        x,y=int(self.center[0])-offset,int(self.center[1])-offset
        height,width=image.shape[:2]
        left,top=max(0,-x),max(0,-y)
        right,bottom=max(0,x+size-width),max(0,y+size-height)
        if left or top or right or bottom:
            image=cv2.copyMakeBorder(image,top,bottom,left,right,cv2.BORDER_CONSTANT,
                                     value=cv2.mean(image)[:3])
        return cv2.resize(image[y+top:y+top+size,x+left:x+left+size],(output_size,output_size))

    def features(self, image):
        self.backbone.setInput(cv2.dnn.blobFromImage(image,swapRB=True))
        return self.backbone.forward()

    def init(self, image, bbox):
        x,y,width,height=map(float,bbox)
        self.center=np.array([x+width*.5,y+height*.5],np.float32)
        self.size=np.array([width,height],np.float32)
        self.image_size=np.array(image.shape[1::-1],np.float32)
        extent=self.size+.5*self.size.sum()
        crop=self.crop(image,int(np.sqrt(extent.prod())),127)
        self.head.setInput(self.features(crop),'input1')
        self.score=0.
        self.last_box=tuple(map(int,bbox))
        if self.verify_template:
            x,y,w,h=self.last_box
            self.reference=cv2.resize(image[y:y+h,x:x+w],(64,64))
            self.reference_gray=cv2.cvtColor(self.reference,cv2.COLOR_BGR2GRAY)
            self.reference_hist=self.histogram(self.reference)

    @staticmethod
    def histogram(image):
        hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        hist=cv2.calcHist([hsv],[0,1],None,[16,16],[0,180,0,256])
        return cv2.normalize(hist,hist,1.,0.,cv2.NORM_L1)

    def similarity(self, image, box):
        x,y,w,h=box
        patch=cv2.getRectSubPix(image,(max(1,round(w*1.25)),max(1,round(h*1.25))),
                               (float(x+w*.5),float(y+h*.5)))
        patch=cv2.resize(patch,(80,80))
        gray=cv2.cvtColor(patch,cv2.COLOR_BGR2GRAY)
        response=cv2.matchTemplate(gray,self.reference_gray,cv2.TM_CCOEFF_NORMED)
        _,correlation,_,(left,top)=cv2.minMaxLoc(response)
        if self.reference_gray.std()<1e-3:correlation=0.
        matched=patch[top:top+64,left:left+64]
        color=1.-cv2.compareHist(self.reference_hist,self.histogram(matched),cv2.HISTCMP_BHATTACHARYYA)
        return .75*max(0.,float(correlation))+.25*max(0.,float(color))

    def decode(self, classification, regression, scale):
        logits=classification.reshape(2,16,16)
        probability=np.exp(logits-logits.max(axis=0,keepdims=True))
        score=probability[1]/probability.sum(axis=0)
        left,top,right,bottom=regression.reshape(4,16,16)
        width,height=left+right,top+bottom
        scaled_size=self.size*scale
        change=lambda value:np.maximum(value,1./value)
        size_change=change(size_cal(width,height)/size_cal(*scaled_size))
        ratio_change=change((self.size[0]/self.size[1])/(width/height))
        penalty=np.exp(-(ratio_change*size_change-1.)*.055)
        ranked=penalty*score*(1.-.455)+self.window*.455
        index=np.unravel_index(np.argmax(ranked),ranked.shape)
        # Report model evidence, rather than the window-biased ranking value.
        self.score=float(score[index])
        offset=np.array([self.grid_x[index]+(right[index]-left[index])*.5-127,
                         self.grid_y[index]+(bottom[index]-top[index])*.5-127])/scale
        predicted=np.array([width[index],height[index]])/scale
        rate=float(penalty[index]*score[index])*.37
        self.center=np.clip(self.center+offset,0.,self.image_size)
        self.size=np.clip(self.size*(1.-rate)+predicted*rate,10.,self.image_size)
        corner=self.center-self.size*.5
        return tuple(int(value) for value in (*corner,*self.size))

    def update(self, image):
        # Match OpenCV's integer sum before expansion of the search crop.
        extent=self.size+.5*int(self.size.sum())
        size=float(np.sqrt(extent.prod()))
        scale=127./size
        crop=self.crop(image,int(size*255/127),255)
        self.head.setInput(self.features(crop),'input2')
        classification,regression=self.head.forward(['output1','output2'])
        previous_center,previous_size=self.center.copy(),self.size.copy()
        box=self.decode(classification,regression,scale)
        if self.verify_template:
            self.template_score=self.similarity(image,box)
            if self.template_score<.60:
                self.center,self.size=previous_center,previous_size
                self.stop_reason='template_mismatch'
                return False,self.last_box
        self.last_box=box
        self.stop_reason=''
        return True,box

    def getTrackingScore(self):
        return self.score
