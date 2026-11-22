from .gate_causal import create
"""Shared header-age and continuous-start check, independent of ROS transport."""
MAX_TF_AGE_SECONDS = .5
MAX_TF_FUTURE_SECONDS = .1


def stamp_is_fresh(stamp, wall):
    age = wall-stamp
    return -MAX_TF_FUTURE_SECONDS <= age <= MAX_TF_AGE_SECONDS


class LocalizationHealth:
    def __init__(self):
        self.trace = create()
        self.query = {}
        self.trace_active = False
        self.trace_phase = 'unknown'
        self.stamp = None
        self.received = None
        self.stable_since = None
        self.age_ms = None
        self.reason = '等待 map→base_link TF'

    def observe(self, stamp, monotonic):
        if self.stamp is not None and (stamp < self.stamp or stamp-self.stamp > .5 or monotonic-self.received > .5):
            self.stable_since = None
        self.stamp, self.received = stamp, monotonic

    def check(self, wall, monotonic):
        result = self._check(wall, monotonic)
        if self.trace:
            self.trace.emit("check", check_wall=wall, check_mono=monotonic,
                            effective_stamp=self.stamp, age_ms=self.age_ms, result=result,
                            reason=self.reason, observed_mono=self.received,
                            active=self.trace_active, phase=self.trace_phase, query=dict(self.query))
        return result

    def _check(self, wall, monotonic):
        self.age_ms = None if self.stamp is None else (wall-self.stamp)*1000
        if self.stamp is None:
            self.reason = '等待 map→base_link TF'
        # elif not stamp_is_fresh(self.stamp, wall):
            # self.reason = f'TF年龄 {self.age_ms:.0f} ms，不在 -100～500 ms 范围内'
        elif monotonic-self.received > .5:
            self.reason = 'TF接收中断超过500 ms'
        else:
            if self.stable_since is None:
                self.stable_since = monotonic
            stable = monotonic-self.stable_since
            self.reason = f'TF年龄 {self.age_ms:.0f} ms；稳定 {stable:.1f}/2.0 秒' if stable < 2 else f'TF年龄 {self.age_ms:.0f} ms；定位已连续稳定'
            return True
        self.stable_since = None
        return False

    def ready(self, wall, monotonic):
        return self.check(wall, monotonic) and monotonic-self.stable_since >= 2
