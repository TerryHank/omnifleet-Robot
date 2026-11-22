from queue import Queue
from omnifleet_person_follow.node import PersonFollowNode


def test_slow_display_keeps_only_latest_frame_without_blocking_inference():
    node = PersonFollowNode.__new__(PersonFollowNode)
    node.display_queue,node.display_dropped = Queue(maxsize=1),0
    node.queue_display('old')
    node.queue_display('latest')
    assert node.display_queue.qsize() == 1
    assert node.display_queue.get_nowait() == 'latest'
    assert node.display_dropped == 1
