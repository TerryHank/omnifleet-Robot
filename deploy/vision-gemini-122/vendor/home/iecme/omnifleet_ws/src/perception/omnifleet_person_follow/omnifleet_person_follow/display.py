"""Draw and encode exact-frame results outside the inference interpreter."""
import time
from queue import Empty, Full
import cv2
from omnifleet_hikrobot_rgbd.local_frames import LocalFrameReader
from .cuda_wait import blocking_cuda_wait


def display_process(jobs,results,stop,quality):
    cv2.setNumThreads(1)
    blocking_cuda_wait()
    reader,encoder,backend,stale = LocalFrameReader(),None,'nvjpegenc',0
    results.cancel_join_thread()
    try:
        while not stop.is_set():
            try:job=jobs.get(timeout=.2)
            except Empty:continue
            started=time.perf_counter()
            try:
                if job.get('max_age') and time.monotonic() - job['queued_at'] > job['max_age']:
                    stale += 1
                    continue
                pair=reader.read(job['frame'],exact=True)
                if pair is None:
                    stale+=1
                    continue
                canvas,_,sec,nanosec,_=pair
                for track in job['tracks']:
                    x1,y1,x2,y2=map(int,track['bbox'])
                    color=(0,255,0) if track['id']==job['target_id'] else (255,160,0)
                    cv2.rectangle(canvas,(x1,y1),(x2,y2),color,3)
                    cv2.putText(canvas,f"ID {track['id']} {track.get('confidence',0.):.2f}",(x1,max(20,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.8,color,2)
                for points in job['hands']:
                    for x,y,_ in points:cv2.circle(canvas,(int(x),int(y)),3,(0,255,255),-1)
                text=f"{job['state']} ID={job['target_id']} {job['gesture']} {job['inference_ms']:.0f}ms"
                cv2.putText(canvas,text,(24,42),cv2.FONT_HERSHEY_SIMPLEX,.9,(0,255,255),2)
                if job.get('search_phase', 'OFF') != 'OFF':
                    cv2.putText(canvas,job['search_phase'],(24,78),cv2.FONT_HERSHEY_SIMPLEX,.8,(0,255,255),2)
                elif job.get('range_m') is not None:
                    mode='CENTER' if job.get('centering') else job.get('follow_mode','')
                    text=f"{mode} range={job['range_m']:.2f}m target={job.get('follow_distance_m',1.):.2f}m"
                    cv2.putText(canvas,text,(24,78),cv2.FONT_HERSHEY_SIMPLEX,.8,(0,255,255),2)
                elif job.get('follow_mode') in ('VISIBLE_NO_DEPTH','APPROACH_FOR_DEPTH'):
                    text='CENTER / NO DEPTH' if job.get('centering') else 'APPROACH FOR DEPTH'
                    cv2.putText(canvas,text,(24,78),cv2.FONT_HERSHEY_SIMPLEX,.8,(0,255,255),2)
                encoded=None
                if job['jpeg']:
                    if backend=='nvjpegenc':
                        try:
                            if encoder is None:
                                from .jpeg import NvJpegEncoder
                                encoder=NvJpegEncoder(canvas.shape[1],canvas.shape[0],quality)
                            encoded=encoder.encode(canvas)
                        except Exception:
                            backend='opencv'
                    if encoded is None:
                        ok,data=cv2.imencode('.jpg',canvas,[cv2.IMWRITE_JPEG_QUALITY,quality])
                        encoded=data.tobytes() if ok else None
                if job.get('max_age') and time.monotonic() - job['queued_at'] > job['max_age']:
                    stale += 1
                    continue
                value=dict(sec=sec,nanosec=nanosec,frame_id=job['frame_id'],jpeg=encoded,
                    raw=canvas if job['raw'] else None,backend=backend,stale_frames=stale,
                    display_ms=(time.perf_counter()-started)*1000,error='')
            except Exception as error:
                value=dict(error=str(error))
            try:results.put_nowait(value)
            except Full:
                try:results.get_nowait();results.put_nowait(value)
                except (Empty,Full):pass
    finally:
        reader.close()
        if encoder is not None:encoder.close()
