"""Align delayed map poses with wheel odometry in source time."""
from bisect import bisect_left
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

class PoseCompensator:
    def __init__(self, velocity_model_horizon):
        self.history_seconds = 2 * velocity_model_horizon + 1
        self.wheels = []
        self.lidar = None

    def add_wheel(self, stamp, pose):
        if self.wheels and stamp <= self.wheels[-1][0]:
            return
        self.wheels.append((stamp, np.asarray(pose, dtype=float)))
        cutoff = stamp - self.history_seconds
        while len(self.wheels) > 2 and self.wheels[1][0] < cutoff:
            self.wheels.pop(0)

    def add_lidar(self, stamp, pose):
        if self.lidar is None or stamp > self.lidar[0]:
            self.lidar = (stamp, np.asarray(pose, dtype=float))

    def current(self):
        if self.lidar is None or not self.wheels:
            return None
        stamp, localization = self.lidar
        latest_stamp, latest = self.wheels[-1]
        if stamp < self.wheels[0][0] or stamp > latest_stamp:
            return None
        index = bisect_left([t for t, _ in self.wheels], stamp)
        if self.wheels[index][0] == stamp:
            anchor = self.wheels[index][1]
        else:
            before_t, before = self.wheels[index - 1]
            after_t, after = self.wheels[index]
            fraction = (stamp - before_t) / (after_t - before_t)
            rotation = Slerp([before_t, after_t], Rotation.from_quat([before[3:], after[3:]]))([stamp])[0]
            anchor = np.r_[before[:3] + fraction * (after[:3] - before[:3]), rotation.as_quat()]
        map_rotation = Rotation.from_quat(localization[3:])
        correction = map_rotation * Rotation.from_quat(anchor[3:]).inv()
        position = localization[:3] + correction.apply(latest[:3] - anchor[:3])
        rotation = correction * Rotation.from_quat(latest[3:])
        return latest_stamp, np.r_[position, rotation.as_quat()]
