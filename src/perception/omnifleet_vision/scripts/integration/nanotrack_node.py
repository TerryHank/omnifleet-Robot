#!/usr/bin/env python3
"""Native OpenCV CUDA NanoTrack for selected objects and detector-seeded tracks."""
from collections import OrderedDict, deque
import json
import time
import sys
import threading

import cv2
import numpy as np
import rclpy
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import Image, RegionOfInterest, CameraInfo
from std_msgs.msg import String

from nanotrack_core import NanoFactory, KcfFactory, HybridTracks, source_stamp
from vision_integration_core import detections_from_payload
from foreground_ros import RosForeground
from omnifleet_hikrobot_rgbd.foreground_tracking import semantic_foreground
sys.path.insert(0,get_package_prefix('omnifleet_vision')+'/lib/omnifleet_vision')
from algorithms import COLOR_RANGES


class NanoTrackNode(Node):
    def __init__(self):
        super().__init__('nanotrack')
        p = lambda name, default:self.declare_parameter(name, default).value
        self.mode = str(p('mode','detections'))
        root = str(p('model_root','/home/iecme/omnifleet_data/ml_models/omnifleet_vision/vendor/nanotrack_v2'))
        self.backend=str(p('tracking_backend','nanotrack'))
        self.factory = KcfFactory() if self.backend=='kcf' else NanoFactory(root, str(p('runtime','auto')), verify_template=self.mode=='roi')
        self.foreground=RosForeground(self,float(p('min_depth',.2)),float(p('max_depth',3.5)))
        self.timeout = float(p('track_timeout',1.))
        self.max_width = int(p('tracking_max_width',640))
        self.cache, self.latest_detection = OrderedDict(), None
        self.depth_values, self.control_value = {}, None
        self.pending_roi, self.manual_tracker, self.manual_id = None, None, 0
        self.source_info = None
        self.foreground_cache,self.color_cache={},{}
        self.foreground_results={}
        self.source_info_topic = str(p('source_info_topic',''))
        if self.source_info_topic:
            self.create_subscription(CameraInfo,self.source_info_topic,self.on_info,QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
        self.output = self.create_publisher(String,str(p('output_topic','/vision/tracks')),1)
        debug = str(p('debug_topic','/vision/tracking/debug'))
        self.debug = self.create_publisher(Image,debug,1) if debug else None
        self.create_subscription(Image,str(p('image_topic','/camera/color/image_raw')),self.on_image,
                                 QoSProfile(depth=1,reliability=ReliabilityPolicy.BEST_EFFORT))
        if self.mode == 'roi':
            self.create_subscription(RegionOfInterest,str(p('roi_topic','/vision/nanotrack/roi')),self.on_roi,QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.VOLATILE))
            self.hybrid = None
        else:
            self.create_subscription(String,str(p('input_topic','/vision/detections')),self.on_detection,1)
            config = str(p('person_tracker_config',get_package_share_directory('omnifleet_person_follow')+'/config/botsort.yaml'))
            self.hybrid = HybridTracks(self.factory,config,self.timeout,foreground=self.observation)
            self.create_subscription(String,'/vision/targets_3d',self.on_depth,1)
            self.create_subscription(String,'/vision/target_follow/status',self.on_control,1)
        self.get_logger().info(f'NanoTrackV2 {self.factory.runtime}; mode={self.mode}; person=BoT-SORT')
        self.frame_lock,self.frame_event=threading.Lock(),threading.Event()
        self.pending_frames=deque(maxlen=16)
        self.last_frame_stamp=float('-inf')
        self.foreground.wake=self.frame_event.set
        self.closed=threading.Event()
        self.worker=threading.Thread(target=self.run,name='foreground-nanotrack',daemon=True)
        self.worker.start()

    def observation(self,image,item,bbox):
        semantic=None
        ranges=item.get('hsv_ranges') or COLOR_RANGES.get(item.get('color'))
        if ranges:
            color_key=(self.foreground.stamp,item['color'])
            semantic=self.color_cache.get(color_key)
            if semantic is None:
                hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
                semantic=np.zeros(hsv.shape[:2],np.uint8)
                for lower,upper in ranges:
                    semantic|=cv2.inRange(hsv,np.asarray(lower,np.uint8),np.asarray(upper,np.uint8))
                semantic=cv2.morphologyEx(semantic,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
                semantic=cv2.morphologyEx(semantic,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
                self.color_cache[color_key]=semantic
        identity=(item.get('class'),item.get('track_id'))
        previous=self.foreground_results.get(identity)
        locked=self.control_value.get('locked_id') if self.control_value else None
        high=self.mode=='roi' or locked is not None and locked==item.get('track_id')
        now=time.monotonic()
        if high or previous is None or now-previous[0]>=.1 or item.get('track_id') is None:
            key=(self.foreground.stamp,tuple(bbox),item.get('color'))
            if key not in self.foreground_cache:self.foreground_cache[key]=self.foreground.query(bbox,semantic)
            result=self.foreground_cache[key]
            description=self.foreground.describe(result)
            if item.get('track_id') is not None:self.foreground_results[identity]=(now,result,description,bbox)
        else:
            _,result,description,old_box=previous
            if result is not None:
                # Propagate a candidate's mask with its visual search box; its
                # measured range keeps the original depth timestamp.
                result=dict(result)
                ox,oy,ow,oh=old_box;nx,ny,nw,nh=bbox
                mx,my,mw,mh=result['mask_box_xywh']
                result['mask_box_xywh']=[nx+(mx-ox)*nw/ow,ny+(my-oy)*nh/oh,mw*nw/ow,mh*nh/oh]
                rx,ry,rw,rh=result['bbox_xywh']
                result['bbox_xywh']=[nx+(rx-ox)*nw/ow,ny+(ry-oy)*nh/oh,rw*nw/ow,rh*nh/oh]
                cx,cy=result['centroid_rgb']
                result['centroid_rgb']=[nx+(cx-ox)*nw/ow,ny+(cy-oy)*nh/oh]
        outline=semantic_foreground(semantic,bbox,self.foreground.rgb_size) if semantic is not None and self.foreground.rgb_size else result
        observed=dict(item,foreground=description)
        observed['bbox']=outline['bbox_xywh'] if outline is not None else bbox
        if outline is not None:observed['center']=list(map(float,outline['centroid_rgb']))
        if len(self.foreground_results)>64:
            self.foreground_results={key:value for key,value in self.foreground_results.items() if now-value[0]<self.timeout}
        # ROI trackers need stable RGB search context. A per-frame depth mask
        # changes the template appearance when samples have holes or arrive late.
        # Foreground geometry remains separate from the selected ROI extent.
        appearance=image if self.mode=='roi' else self.foreground.appearance(image,outline)
        return appearance,observed

    def on_depth(self,message):
        value=json.loads(message.data)
        self.depth_values={item['track_id']:item.get('depth_m') for item in value.get('detections',[]) if 'track_id' in item}

    def on_control(self,message):
        self.control_value=json.loads(message.data)

    def on_info(self,message):
        self.source_info = message

    def on_roi(self, message):
        self.pending_roi = message
        self.manual_tracker = None

    def on_detection(self, message):
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            return
        self.latest_detection = payload
        self.color_selection = payload.get("selected_color", "")

    def on_image(self, message):
        # Keep enough RGB history to pair a depth stream that arrives later.
        # Only one newest matched frame is inferred; stale visual work is dropped.
        with self.frame_lock:self.pending_frames.append(message)
        self.frame_event.set()

    def run(self):
        while not self.closed.is_set():
            self.frame_event.wait(.2)
            with self.frame_lock:
                frames=list(self.pending_frames)
                self.frame_event.clear()
            message=self.foreground.select_frame(frames,self.last_frame_stamp,time.monotonic())
            if message is None:continue
            self.last_frame_stamp=self.foreground.image_stamp(message)
            with self.frame_lock:
                while self.pending_frames and self.foreground.image_stamp(self.pending_frames[0])<=self.last_frame_stamp:
                    self.pending_frames.popleft()
            try:self.process_image(message)
            except Exception as error:self.get_logger().error(f'Foreground tracking frame failed: {error}',throttle_duration_sec=2.)

    def close(self):
        self.closed.set();self.frame_event.set();self.worker.join(timeout=10.)

    def process_image(self, message):
        if message.encoding not in ('rgb8','bgr8'):
            return
        started = time.perf_counter()
        stamp = message.header.stamp.sec + message.header.stamp.nanosec*1e-9
        original = np.ndarray((message.height,message.width,3),dtype=np.uint8,buffer=message.data,strides=(message.step,3,1))
        if message.encoding == 'rgb8':
            original = cv2.cvtColor(original,cv2.COLOR_RGB2BGR)
        scale = min(1., self.max_width/message.width)
        small = cv2.resize(original,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else original
        if self.source_info_topic and self.source_info is None:
            return
        width = self.source_info.width if self.source_info_topic else message.width
        height = self.source_info.height if self.source_info_topic else message.height
        sx,sy = small.shape[1]/width,small.shape[0]/height
        self.foreground.prepare(stamp,(width,height))
        self.foreground_cache.clear();self.color_cache.clear()
        now = time.monotonic()
        if self.mode!='roi':
            self.cache[stamp] = (small.copy(),sx,sy)
            while len(self.cache)>6:self.cache.popitem(last=False)
        tracks = []
        inference_start = time.perf_counter()
        detection_foreground_ms,detection_foreground_calls=0.,0
        if self.mode == 'roi':
            initialized=False
            if self.pending_roi is not None:
                roi,self.pending_roi = self.pending_roi,None
                x,y = min(roi.x_offset,width-2),min(roi.y_offset,height-2)
                w,h = min(roi.width,width-x),min(roi.height,height-y)
                if w>1 and h>1:
                    self.manual_box=[x,y,w,h]
                    self.manual_tracker = self.factory.create(small,[x*sx,y*sy,w*sx,h*sy])
                    self.manual_id += 1
                    initialized=True
            if self.manual_tracker is not None:
                if initialized:
                    x,y,w,h=self.manual_box
                    ok,box=True,[x*sx,y*sy,w*sx,h*sy]
                else:
                    ok,box = self.manual_tracker.update(small)
                if ok:
                    x,y,w,h = box
                    tracks = [dict(track_id=self.manual_id,**{'class':'object'},bbox=[x/sx,y/sy,w/sx,h/sy],
                                   tracker='KCF' if self.backend=='kcf' else 'NanoTrack',
                                   tracking_score=0. if initialized else float(self.manual_tracker.getTrackingScore()))]
                    # Depth may cover only a rim or textured patch. It supplies
                    # range, not the visual target extent or template geometry.
                    _,observed=self.observation(small,{},tracks[0]['bbox'])
                    tracks[0]['center']=[(x+w*.5)/sx,(y+h*.5)/sy]
                    tracks[0]['foreground']=observed['foreground']
                    self.manual_box=tracks[0]['bbox']
        else:
            if self.latest_detection is not None:
                payload,self.latest_detection = self.latest_detection,None
                when = source_stamp(payload,stamp)
                closest = min(self.cache,key=lambda key:abs(key-when))
                frame,dx,dy = self.cache[closest]
                self.foreground.prepare(closest,(width,height))
                self.hybrid.detect(detections_from_payload(payload),frame,dx,dy,now)
                detection_foreground_ms,detection_foreground_calls=self.foreground.elapsed_ms,self.foreground.calls
                self.foreground.prepare(stamp,(width,height))
            tracks = self.hybrid.update(small,sx,sy,now)
            selected = getattr(self, "color_selection", "")
            if selected:
                tracks = [track for track in tracks if track.get("class") == selected]
        inference_ms = (time.perf_counter()-inference_start)*1000.
        payload = dict(stamp=stamp,source_stamp=stamp,frame_id=message.header.frame_id,image_width=width,
                       image_height=height,status='tracking' if tracks else 'target_lost',tracks=tracks,
                       tracker=self.backend if self.mode=='roi' else 'NanoTrack/BoT-SORT',person_tracker='BoT-SORT',runtime=self.factory.runtime,
                       inference_ms=inference_ms,processing_ms=(time.perf_counter()-started)*1000.)
        payload.update(foreground_calls=self.foreground.calls+detection_foreground_calls,foreground_ms=self.foreground.elapsed_ms+detection_foreground_ms,
                       foreground_tracking=True,additional_segmentation_models=0,
                       foreground_depth_ready=self.foreground.depth is not None,foreground_depth_skew_ms=self.foreground.skew_ms)
        if self.mode=='roi':
            payload.update(selected_track_id=self.manual_id if self.manual_tracker is not None else None,
                           tracking_stop_reason=getattr(self.manual_tracker,'stop_reason',''),
                           template_score=getattr(self.manual_tracker,'template_score',None))
        self.output.publish(String(data=json.dumps(payload,separators=(',',':'))))
        if self.debug is not None and self.debug.get_subscription_count():
            debug = original.copy()
            for item in tracks:
                x,y,w,h = map(lambda value:int(round(value)),item['bbox'])
                cv2.rectangle(debug,(x,y),(x+w,y+h),(0,255,255),2)
                text=f"{item['tracker']} ID{item['track_id']} {item.get('class','object')}"
                distance=self.depth_values.get(item['track_id'])
                if distance is not None:text+=f" {distance:.2f}m"
                cv2.putText(debug,text,(x,max(20,y-8)),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,255,255),2)
            if self.control_value is not None:
                cv2.putText(debug,str(self.control_value.get('motion_state',self.control_value.get('reason',''))),(12,26),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,255,255),2)
            output = Image(height=debug.shape[0],width=debug.shape[1],encoding='bgr8',step=debug.shape[1]*3,data=debug.tobytes())
            output.header = message.header
            self.debug.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = NanoTrackNode()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__ == '__main__':main()
