from collections import deque
from pathlib import Path
from types import SimpleNamespace as NS
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/integration'))
from foreground_ros import RosForeground


def image(value):
    nanoseconds=round(value*1e9)
    return NS(header=NS(stamp=NS(sec=nanoseconds//1_000_000_000,nanosec=nanoseconds%1_000_000_000)))


def source(values,received=5.):
    q=RosForeground.__new__(RosForeground)
    q.depths=deque(map(image,values),maxlen=16);q.depth_received_at=received
    return q


def test_later_depth_wakes_pairing_instead_of_losing_rgb():
    q=source([100.6]);rgb=image(101.)
    assert q.select_frame([rgb],100.5,5.01) is None
    q.depths.append(image(101.))
    assert q.select_frame([rgb],100.5,5.02) is rgb


def test_newest_rgb_does_not_displace_an_older_exact_pair():
    q=source([101.01]);frames=list(map(image,[100.98,101.01,101.3]))
    assert q.select_frame(frames,100.9,5.01) is frames[1]


def test_newest_rgb_uses_a_nearby_past_depth_without_waiting_for_future():
    q=source([101.]);frames=list(map(image,[100.9,101.04]))
    assert q.select_frame(frames,100.8,5.01) is frames[1]


def test_depth_outage_keeps_rgb_tracking_and_does_not_replay_old_frames():
    q=source([101.]);rgb=image(101.4)
    assert q.select_frame([rgb],101.3,5.3) is rgb
    assert q.select_frame([rgb],101.4,5.3) is None


def test_constant_300ms_arrival_delay_is_matched_without_widening_tolerance():
    q=source([]);frames=deque(maxlen=16);last=float('-inf');matched=[]
    for n in range(70):
        rgb=image(100+n/30);frames.append(rgb)
        if n>=9:q.depths.append(image(100+(n-9)/30))
        selected=q.select_frame(list(frames),last,5.)
        if selected is not None:
            last=q.image_stamp(selected)
            if n>=9:matched.append(abs(last-q.image_stamp(q.depths[-1])))
    assert len(matched)>=50 and max(matched)<=.2+1e-9
