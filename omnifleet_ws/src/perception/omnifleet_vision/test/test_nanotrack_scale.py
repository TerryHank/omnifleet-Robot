import numpy as np
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from nanotrack_tracker import NanoTracker


def test_screen_translation_does_not_change_scale_or_relative_prediction():
    outputs=[]
    logits=np.zeros((1,2,16,16),np.float32)
    logits[0,1,8,8]=3.
    regression=np.full((1,4,16,16),20.,np.float32)
    for center in [[100.,100.],[500.,350.]]:
        tracker=NanoTracker.__new__(NanoTracker)
        tracker.center=np.array(center,np.float32)
        tracker.size=np.array([60.,80.],np.float32)
        tracker.image_size=np.array([1024.,768.],np.float32)
        import cv2
        tracker.window=cv2.createHanningWindow((16,16),cv2.CV_32F)
        grid=(np.arange(16,dtype=np.float32)-8)*16+127
        tracker.grid_x,tracker.grid_y=np.meshgrid(grid,grid)
        for _ in range(20):tracker.decode(logits,regression,1.)
        outputs.append((tracker.size.copy(),tracker.center-np.array(center)))
    np.testing.assert_allclose(outputs[0][0],outputs[1][0],atol=1e-5)
    np.testing.assert_allclose(outputs[0][1],outputs[1][1],atol=1e-5)
