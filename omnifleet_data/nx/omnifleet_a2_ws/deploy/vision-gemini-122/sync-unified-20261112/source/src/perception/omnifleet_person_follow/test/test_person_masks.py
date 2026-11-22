import numpy as np
import torch
from omnifleet_person_follow.person_masks import person_masks


def test_native_masks_match_bilinear_crop_and_letterbox_coordinates():
    random=np.random.default_rng(7)
    proto=random.normal(size=(4,8,8)).astype(np.float32)
    rows=np.array([[1.2,2.7,13.5,14.2,.9,0,1.,-.2,.4,.1],
                   [2.,3.,14.,15.,.8,1,1.,1.,1.,1.],
                   [2.,3.,14.,15.,.05,0,1.,1.,1.,1.]],np.float32)
    original=rows.copy()
    boxes,masks=person_masks(rows,proto,(24,32,3),16,.1)
    reference=torch.nn.functional.interpolate(
        (torch.from_numpy(rows[:1,6:])@torch.from_numpy(proto).reshape(4,-1)).reshape(1,1,8,8),
        size=(16,16),mode='bilinear',align_corners=False)[0,0].numpy()>0
    x1,y1,x2,y2=np.ceil(rows[0,:4]).astype(int)
    reference[:y1]=False;reference[y2:]=False;reference[:,:x1]=False;reference[:,x2:]=False
    np.testing.assert_array_equal(masks[0],reference)
    np.testing.assert_allclose(boxes[0,:4],[2.4,1.4,27.,24.],atol=1e-5)
    assert boxes.shape==(1,6)
    np.testing.assert_array_equal(rows,original)


def test_no_person_or_empty_mask_does_not_create_a_detection():
    rows=np.array([[0,0,16,16,.9,1,1]],np.float32)
    boxes,masks=person_masks(rows,np.ones((1,4,4),np.float32),(16,16,3),16,.1)
    assert boxes.shape==(0,6) and masks.shape==(0,16,16)
    rows[0,5]=0
    boxes,masks=person_masks(rows,-np.ones((1,4,4),np.float32),(16,16,3),16,.1)
    assert len(boxes)==len(masks)==0
