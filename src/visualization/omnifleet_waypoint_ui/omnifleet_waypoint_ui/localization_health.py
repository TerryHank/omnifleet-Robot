"""Shared header-age and continuous-start check, independent of ROS transport."""
class LocalizationHealth:
    def __init__(self):
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
        self.age_ms = None if self.stamp is None else (wall-self.stamp)*1000
        if self.stamp is None:
            self.reason = '等待 map→base_link TF'
        elif not (-100 <= self.age_ms <= 500):
            self.reason = f'TF年龄 {self.age_ms:.0f} ms，不在 -100～500 ms 范围内'
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
