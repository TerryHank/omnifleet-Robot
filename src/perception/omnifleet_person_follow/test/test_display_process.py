from queue import Queue
import threading
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
from omnifleet_hikrobot_rgbd.local_frames import LocalFrameWriter
from omnifleet_person_follow.display import display_process


def test_display_process_preserves_source_stamp_and_draws_on_own_snapshot():
    writer=LocalFrameWriter((48,64,3),(0,0));stop=threading.Event()
    class Results(Queue):
        def cancel_join_thread(self):pass
        def put_nowait(self,value):
            super().put_nowait(value);stop.set()
    jobs,results=Queue(),Results()
    image=np.zeros((48,64,3),np.uint8)
    try:
        frame=writer.write(image,np.empty((0,0),np.uint16),NS(sec=3,nanosec=27),9)
        jobs.put(dict(frame=frame,tracks=[dict(id=1,bbox=[2,2,30,35])],hands=[],target_id=1,
                      state='TRACKING',gesture='unknown',inference_ms=10.,jpeg=False,raw=True,frame_id='rgb'))
        with patch('omnifleet_person_follow.display.blocking_cuda_wait',return_value=True):
            display_process(jobs,results,stop,85)
        result=results.get_nowait()
        assert not result['error'] and (result['sec'],result['nanosec'])==(3,27)
        assert result['raw'].shape==image.shape and result['raw'].any()
        assert not image.any() and result['jpeg'] is None
    finally:writer.close()
