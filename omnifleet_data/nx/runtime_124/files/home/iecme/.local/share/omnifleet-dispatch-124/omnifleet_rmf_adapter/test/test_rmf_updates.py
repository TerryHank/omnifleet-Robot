import asyncio
import json
import queue
from omnifleet_rmf_adapter.rmf_updates import TaskUpdates


def test_receiver_only_forwards_official_task_state_envelopes():
    receiver = TaskUpdates.__new__(TaskUpdates)
    receiver.inbox = queue.Queue()
    task = {'type': 'task_state_update', 'data': {
        'booking': {'id': 'task'}, 'status': 'completed'}}

    async def packets():
        for message in ({'type': 'navigate', 'pose': [0, 0, 0]}, task):
            yield json.dumps(message)

    asyncio.run(receiver.receive(packets(), '/'))
    assert receiver.inbox.get_nowait() == task
    assert receiver.inbox.empty()
