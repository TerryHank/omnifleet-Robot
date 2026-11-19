"""Scale-normalized One Euro smoothing for live pose coordinates."""
import numpy as np


class PoseSmoothing:
    def __init__(self, min_cutoff, beta):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.timestamp = None

    def update(self, coordinates, timestamp, scale, visible=None):
        points = np.asarray(coordinates)
        valid = np.isfinite(points).all(axis=1)
        if visible is not None:
            valid &= visible
        elapsed = timestamp-self.timestamp if self.timestamp is not None else 0.
        filtered = points.copy()
        velocity = np.zeros_like(points)
        if 0. < elapsed <= .5:
            keep = self.valid & valid
            derivative = (points[keep]-self.raw[keep]) / (elapsed*max(1.,scale))
            speed_alpha = 1-1/(1+2*np.pi*elapsed)
            velocity[keep] = self.velocity[keep] + speed_alpha*(derivative-self.velocity[keep])
            speed = np.linalg.norm(velocity[keep],axis=1)
            cutoff = self.min_cutoff+self.beta*speed
            alpha = (1-1/(1+2*np.pi*elapsed*cutoff))[:,None]
            filtered[keep] = self.filtered[keep]+alpha*(points[keep]-self.filtered[keep])
        self.raw = points.copy()
        self.filtered, self.velocity = filtered, velocity
        self.valid, self.timestamp = valid, timestamp
        return filtered
