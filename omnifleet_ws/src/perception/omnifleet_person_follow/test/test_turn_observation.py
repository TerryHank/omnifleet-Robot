from std_msgs.msg import Header
from omnifleet_person_follow.body_adapter import body_targets
from omnifleet_person_follow.body_adapter import BodyTrackingAdapter
from std_msgs.msg import String
import json


def test_async_gap_is_distinct_from_a_fresh_observed_gesture_release():
    person=dict(id=7,bbox=[0,0,100,200],confidence=.9)
    assert not body_targets([person],Header(),[],hand_updated=False).targets[0].attributes
    result=body_targets([person],Header(),[],hand_updated=True)
    assert {a.type:a.value for a in result.targets[0].attributes}=={'hand_gesture_observation':-1.}


def test_completed_rotation_releases_visual_lock_for_the_next_gesture():
    bridge=BodyTrackingAdapter.__new__(BodyTrackingAdapter)
    bridge.on_state(String(data=json.dumps(dict(state='TRACKING',track_id=7,rotation_done=True))))
    assert bridge.state=='IDLE' and bridge.track_id is None
