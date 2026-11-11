import numpy as np
from std_msgs.msg import Header
from omnifleet_person_follow.core import classify_hand
from omnifleet_person_follow.body_adapter import body_targets


def hand(fingers,thumb=False):
    p=np.zeros((21,3),np.float32)
    p[1,:2],p[2,:2]=(1,-3),(2,-5)
    p[3,:2],p[4,:2]=(2,-7 if thumb else -4),(2,-11 if thumb else -3)
    for up,(pip,dip,tip) in zip(fingers,((6,7,8),(10,11,12),(14,15,16),(18,19,20))):
        x=(pip-12)/3;p[pip,:2]=(x,-5);p[dip,:2]=(x,-7 if up else -4);p[tip,:2]=(x,-12 if up else -3)
    return p


def test_digits_and_palm_are_distinct_in_world_coordinates():
    cases=[([1,0,0,0],False,'one'),([1,1,0,0],False,'victory'),
           ([1,1,1,0],False,'three'),([1,1,0,0],True,'three'),
           ([1,1,1,1],False,'four'),([1,1,1,1],True,'open_palm')]
    rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],np.float32)
    for fingers,thumb,label in cases:
        points=hand(fingers,thumb)
        assert classify_hand(points,points)==label
        assert classify_hand(points,points@rotation.T)==label


def test_digits_use_104_extension_codes_and_keep_body_binding():
    person=dict(id=7,bbox=[0,0,100,200],confidence=.9)
    for label,code in [('one',101),('victory',102),('three',103),('four',104),('open_palm',5),('okay',11)]:
        result=body_targets([person],Header(),[dict(owner=7,gesture=label,score=.99,points=hand([1,1,1,1],True))])
        assert len(result.targets)==2
        attrs={a.type:a.value for a in result.targets[1].attributes}
        assert attrs==dict(gesture=float(code),body_track_id=7.)
