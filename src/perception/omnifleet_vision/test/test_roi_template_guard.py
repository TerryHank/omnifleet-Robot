from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from nanotrack_node import NanoTrackNode
from test_roi_box_geometry import setup


def test_template_rejection_keeps_original_tracker_and_identity_for_recovery():
    node,message,emitted,created,observed=setup()
    NanoTrackNode.process_image(node,message)
    original=created[0];identity=node.manual_id;reference_box=node.manual_box.copy()
    original.stop_reason='template_mismatch';original.template_score=.2
    original.update=lambda image:(False,[0,0,600,400])
    message.header.stamp.sec+=1
    NanoTrackNode.process_image(node,message)
    assert emitted[-1]['tracks']==[]
    assert emitted[-1]['tracking_stop_reason']=='template_mismatch'
    assert emitted[-1]['selected_track_id']==identity
    assert node.manual_tracker is original and node.manual_box==reference_box
    assert len(observed)==1,'Rejected appearance must not produce depth for another object'
    original.stop_reason='';original.template_score=.95
    original.update=lambda image:(True,reference_box)
    message.header.stamp.sec+=1
    NanoTrackNode.process_image(node,message)
    assert emitted[-1]['tracks'][0]['track_id']==identity
    assert emitted[-1]['tracking_stop_reason']==''
