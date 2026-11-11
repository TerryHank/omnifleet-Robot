"""Sample a displayed RGB region and track its connected HSV color component."""
from collections import deque
import json, time
import cv2
import numpy as np
from std_msgs.msg import String
from rclpy.parameter import Parameter
from rcl_interfaces.msg import Parameter as ParameterMsg, ParameterValue, ParameterType
from rcl_interfaces.srv import SetParameters
from algorithms import COLOR_RANGES

def bbox_iou(a,b):
    x,y,w,h=a;ox,oy,ow,oh=b
    area=max(0,min(x+w,ox+ow)-max(x,ox))*max(0,min(y+h,oy+oh)-max(y,oy))
    return area/(w*h+ow*oh-area) if area else 0.


def sample_color(image, x, y):
    h, w = image.shape[:2]
    x, y = int(np.clip(x,0,w-1)), int(np.clip(y,0,h-1))
    patch=image[max(0,y-2):min(h,y+3),max(0,x-2):min(w,x+3)]
    bgr=np.median(patch.reshape(-1,3),axis=0).astype(np.uint8)
    hue,sat,val=map(int,cv2.cvtColor(bgr.reshape(1,1,3),cv2.COLOR_BGR2HSV)[0,0])
    low,high=hue-10,hue+10
    spans=[(low,high)] if low>=0 and high<=179 else ([(0,high),(180+low,179)] if low<0 else [(low,179),(0,high-180)])
    if sat<40:spans=[(0,179)]
    ranges=[[[a,max(0,sat-60),max(0,val-60)],[b,min(255,sat+60),min(255,val+60)]] for a,b in spans]
    return dict(bgr=bgr.tolist(),hsv=[hue,sat,val],hsv_ranges=ranges,point=[x,y],bbox=None)


def recognize_picked(image, selection, minimum_area):
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV);mask=np.zeros(image.shape[:2],np.uint8)
    for lower,upper in selection['hsv_ranges']:
        mask|=cv2.inRange(hsv,np.asarray(lower,np.uint8),np.asarray(upper,np.uint8))
    kernel=np.ones((3,3),np.uint8)
    mask=cv2.morphologyEx(cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel),cv2.MORPH_CLOSE,kernel)
    contours=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    contours=[c for c in contours if cv2.contourArea(c)>=minimum_area]
    debug=image.copy();detections=[]
    if contours:
        old=selection['bbox'];point=selection['point'] if old is None else [old[0]+old[2]/2,old[1]+old[3]/2]
        contour=max(contours,key=lambda c:(bbox_iou(cv2.boundingRect(c),old) if old is not None else 0.,
                                           cv2.pointPolygonTest(c,tuple(map(float,point)),True)))
        x,y,w,h=cv2.boundingRect(contour);selection['bbox']=[x,y,w,h]
        detections=[dict(**{'class':selection['name']},color=selection.get('source_color',selection['name']),hsv_ranges=selection['hsv_ranges'],
                         confidence=1.,bbox=[x,y,w,h],center=[x+w/2,y+h/2],area=float(cv2.contourArea(contour)))]
        cv2.rectangle(debug,(x,y),(x+w,y+h),(0,255,255),2)
        cv2.putText(debug,'picked color',(x,max(18,y-5)),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,255,255),2)
    return debug,dict(detected=bool(detections),count=len(detections),detections=detections)


class ColorPicker:
    def __init__(self,node):
        self.node=node;self.enabled=bool(node.declare_parameter('enable_click_color',False).value)
        self.frames=deque(maxlen=24);self.selection=None;self.result=None;self.queued=None;self.inflight=False
        if self.enabled:
            controller=str(node.declare_parameter('follow_controller','/course_target_follow').value)
            self.client=node.create_client(SetParameters,controller+'/set_parameters')
            self.sub=node.create_subscription(String,'/vision/color/pick',self.on_pick,10)

    def remember(self,message,image,detections=()):
        if self.enabled:self.frames.append((message.header.stamp.sec+message.header.stamp.nanosec*1e-9,image,detections))

    def on_pick(self,message):
        try:self.queued=json.loads(message.data)
        except (ValueError,TypeError):return
        if not isinstance(self.queued,dict):self.queued=None;return
        if not self.inflight:self.begin()

    def begin(self):
        request,self.queued=self.queued,None
        try:
            if not self.client.service_is_ready():raise ValueError('跟随控制器服务尚未就绪')
            if request.get('op')=='clear':
                self.submit(request,None)
                return
            if self.node.get_parameter('selected_color').value:raise ValueError('已锁定目标，请先清除跟踪')
            if not self.frames:raise ValueError('等待相机RGB图像')
            wanted=float(request.get('stamp',self.frames[-1][0]) or self.frames[-1][0])
            stamp,image,detections=min(self.frames,key=lambda item:abs(item[0]-wanted))
            x=float(request['x'])*image.shape[1]/float(request['width'])
            y=float(request['y'])*image.shape[0]/float(request['height'])
            hits=[d for d in detections if d['bbox'][0]<=x<=d['bbox'][0]+d['bbox'][2] and d['bbox'][1]<=y<=d['bbox'][1]+d['bbox'][3]]
            if request.get('mode')=='box' and not hits:raise ValueError('请点击已显示的颜色检测框')
            if hits:
                target=min(hits,key=lambda d:d['bbox'][2]*d['bbox'][3])
                bx,by,bw,bh=target['bbox'];source=target.get('color',target.get('class'))
                selection=sample_color(image,bx+bw*.5,by+bh*.5)
                if source in COLOR_RANGES:
                    crop=image[int(by):int(by+bh),int(bx):int(bx+bw)]
                    hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);mask=np.zeros(crop.shape[:2],np.uint8)
                    for lo,hi in COLOR_RANGES[source]:mask|=cv2.inRange(hsv,np.asarray(lo,np.uint8),np.asarray(hi,np.uint8))
                    pixels=crop[mask>0]
                    if len(pixels):selection=sample_color(np.median(pixels,axis=0).astype(np.uint8).reshape(1,1,3),0,0)
                selection.update(source_color=source,bbox=list(target['bbox']),point=[x,y])
                if source in COLOR_RANGES:selection['hsv_ranges']=[[list(lo),list(hi)] for lo,hi in COLOR_RANGES[source]]
            else:selection=sample_color(image,x,y)
            selection.update(name='picked_'+format(time.time_ns(),'x'),source_stamp=stamp,frame_delta_ms=(stamp-wanted)*1000)
            self.submit(request,selection)
        except (ValueError,TypeError,KeyError,ZeroDivisionError) as error:
            self.result=dict(id=request.get('id'),success=False,message=str(error))

    def submit(self,request,selection):
        self.inflight=True
        wanted=selection['name'] if selection is not None else '__click_target__'
        future=self.client.call_async(SetParameters.Request(parameters=[ParameterMsg(name='class_filter',
            value=ParameterValue(type=ParameterType.PARAMETER_STRING,string_value=wanted))]))
        future.add_done_callback(lambda f:self.finish(f,request,selection))

    def finish(self,future,request,selection):
        try:
            reply=future.result()
            if not reply.results or not all(result.successful for result in reply.results):raise ValueError('; '.join(result.reason for result in reply.results))
            if self.queued is None:
                self.selection=selection
                wanted=selection['name'] if selection is not None else ''
                result=self.node.set_parameters([Parameter('selected_color',value=wanted)])
                if not all(r.successful for r in result):raise ValueError('; '.join(r.reason for r in result))
                self.result=dict(id=request.get('id'),success=True,selected_color=wanted,op='pick' if selection is not None else 'clear')
                if selection is not None:self.result.update(source_color=selection.get('source_color'),hsv=selection['hsv'],bgr=selection['bgr'])
                else:self.frames.clear()
        except Exception as error:
            self.result=dict(id=request.get('id'),success=False,message=str(error))
        finally:
            self.inflight=False
            if self.queued is not None:self.begin()
