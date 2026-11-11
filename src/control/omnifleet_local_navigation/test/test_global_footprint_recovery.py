import math
from types import SimpleNamespace as NS
import unittest

from omnifleet_local_navigation.clearance_recovery import grid_body_blocked, grid_start_blocked


class GlobalFootprintRecoveryTests(unittest.TestCase):
    def grid(self, value, yaw=0.):
        data = [0] * 100
        data[5 * 10 + 7] = value
        return NS(data=data, info=NS(width=10, height=10, resolution=.1,
                  origin=NS(position=NS(x=-.5, y=-.5),
                            orientation=NS(x=0., y=0., z=math.sin(yaw/2), w=math.cos(yaw/2)))))

    def test_free_center_with_lethal_cell_at_body_edge_triggers_recovery(self):
        grid = self.grid(100)
        pose = [0., 0., 0.]
        config = dict(length=.5, width=.37, padding=0.)
        self.assertFalse(grid_start_blocked(grid, pose))
        self.assertTrue(grid_body_blocked(grid, pose, config))
        self.assertFalse(grid_body_blocked(grid, [-.2, 0., 0.], config))

    def test_inflation_at_body_edge_is_not_counted_as_lethal_obstacle(self):
        self.assertFalse(grid_body_blocked(self.grid(99), [0., 0., 0.],
                                          dict(length=.5, width=.37, padding=0.)))

    def test_rotated_grid_preserves_full_footprint_collision(self):
        self.assertTrue(grid_body_blocked(self.grid(100, math.pi/2), [-1., 0., math.pi/2],
                                         dict(length=.5, width=.37, padding=0.)))
