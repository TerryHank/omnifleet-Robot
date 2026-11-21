"""Preserve source time for selected velocity callbacks on ROS Humble."""
import time
from rclpy.executors import SingleThreadedExecutor, await_or_execute


def with_source_time(callback):
    callback.with_source_time = True
    return callback


def velocity_command_time(message, info, timeout=.35):
    """Return the command's monotonic origin, or None when it is too old."""
    now = time.monotonic()
    # A zero command must always be able to stop, even without valid metadata.
    if message.linear.x == 0. and message.angular.z == 0.:
        return now
    source = info.get('source_timestamp', 0) if isinstance(info, dict) else getattr(info, 'source_timestamp', 0)
    age = (time.time_ns() - source) / 1e9
    if source <= 0 or not -.05 <= age < timeout:
        return None
    return now - max(0., age)


class SourceTimeExecutor(SingleThreadedExecutor):
    def _take_subscription(self, sub):
        if not getattr(sub.callback, 'with_source_time', False):
            return super()._take_subscription(sub)
        with sub.handle:
            return sub.handle.take_message(sub.msg_type, sub.raw)

    async def _execute_subscription(self, sub, sample):
        if not getattr(sub.callback, 'with_source_time', False):
            return await super()._execute_subscription(sub, sample)
        if sample is not None:
            await await_or_execute(sub.callback, *sample)
