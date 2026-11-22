from unittest.mock import patch
from queue import Queue
import threading
from types import SimpleNamespace
from omnifleet_person_follow.perception import Perception


def pipeline():
    perception = Perception.__new__(Perception)
    perception.gestures_enabled = True
    perception.model_timings = {}
    perception.cuda_blocking_sync = True
    perception.hand_jobs,perception.hand_results = Queue(maxsize=1),Queue(maxsize=1)
    perception.hand_ms,perception.hand_age_ms,perception.hand_error = 0.,None,''
    perception.hand_stop = threading.Event()
    perception.palm=SimpleNamespace(model=SimpleNamespace())
    perception.hand=SimpleNamespace(model=SimpleNamespace())
    return perception


def test_gestures_disabled_runs_people_without_creating_or_using_hand_queues():
    perception=Perception.__new__(Perception)
    perception.gestures_enabled=False
    perception.cuda_blocking_sync=True;perception.model_timings={}
    perception.people=lambda image:[dict(id=7)]
    tracks,hands=perception.infer('image',None)
    assert tracks==[dict(id=7)] and hands==[]
    assert perception.timings['hand_ms']==0 and perception.timings['hand_updated'] is False
    assert not hasattr(perception,'hand_jobs')
    perception.close()


def test_latest_hand_jobs_and_results_are_consumed_once_for_the_same_owner():
    perception=pipeline();body_calls=[];clock=[0.]
    perception.people = lambda image: body_calls.append(image) or [dict(id=7)]
    with patch('omnifleet_person_follow.perception.time.perf_counter',side_effect=lambda:clock[0]):
        assert perception.infer('a',7)[1] == []
        perception.hand_results.put((7,['fresh'],0.,5.,''))
        clock[0]=.05
        assert perception.infer('b',7)[1] == ['fresh']
        clock[0]=.06
        assert perception.infer('c',7)[1] == []
        assert perception.timings['hand_updated'] is False
        assert perception.hand_jobs.get_nowait()[0]=='c'
        clock[0]=.16
        perception.infer('d',7)
        assert perception.hand_jobs.get_nowait()[0]=='d'
        perception.hand_results.put((7,['old-owner'],0.,5.,''))
        assert perception.infer('e',8)[1] == []
    assert body_calls == ['a','b','c','d','e']


def test_slow_hand_model_does_not_block_person_inference():
    perception=pipeline()
    entered,release,finished=threading.Event(),threading.Event(),threading.Event()
    perception.people=lambda image:[dict(id=7)]
    def hands(*args):
        entered.set()
        assert release.wait(2)
        finished.set()
        return ['fresh']
    perception.hands=hands
    perception.hand_worker=threading.Thread(target=perception.hand_run)
    perception.hand_worker.start()
    try:
        assert perception.infer('image',7)[1]==[]
        assert entered.wait(1) and not finished.is_set()
        assert perception.infer('new image',7)[0]==[dict(id=7)]
        release.set()
        result=perception.hand_results.get(timeout=1)
        assert result[0]==7 and result[1]==['fresh']
    finally:
        release.set();perception.close()
