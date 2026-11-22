import numpy as np
from std_msgs.msg import Header
from omnifleet_person_follow.core import classify_hand
from omnifleet_person_follow.body_adapter import body_targets


def okay_points():
    p = np.zeros((21, 3), np.float32)
    p[5], p[17] = [-2, -3, 0], [2, -3, 0]
    for x, (pip, dip, tip) in zip([-2, -1, 1, 2], [(6,7,8), (10,11,12), (14,15,16), (18,19,20)]):
        p[pip], p[dip], p[tip] = [x,-5,0], [x,-7,0], [x,-12,0]
    p[7], p[8], p[4] = [-2,-4,0], [-2,-3,0], [-1.9,-3,0]
    return p


def test_ok_requires_thumb_index_contact_and_three_extended_fingers():
    p = okay_points()
    assert classify_hand(p, p) == 'okay'
    p[4] += [3, 0, 0]
    assert classify_hand(p, p) != 'okay'
    p = okay_points();p[20] = [2,-3,0];p[19] = [2,-4,0]
    assert classify_hand(p, p) != 'okay'


def test_native_gestures_have_official_codes_and_explicit_person_ownership():
    person = dict(id=7, bbox=[0,0,100,200], confidence=.9)
    hand = dict(owner=7, gesture='okay', score=.96, points=np.array([[20,30,0],[40,60,0]]))
    result = body_targets([person], Header(), [hand])
    assert len(result.targets) == 2
    target = result.targets[1]
    assert target.type == 'hand' and target.track_id == 7
    assert {a.type:a.value for a in target.attributes} == {'gesture':11., 'body_track_id':7.}
    assert target.rois[0].rect.width == 20 and target.rois[0].rect.height == 30
    result = body_targets([person], Header(), [{**hand,'gesture':'open_palm'}])
    assert result.targets[1].attributes[0].value == 5.
    for change in [dict(gesture='thumbs_up'), dict(gesture='unknown'), dict(owner=8)]:
        assert len(body_targets([person], Header(), [{**hand, **change}]).targets) == 1
