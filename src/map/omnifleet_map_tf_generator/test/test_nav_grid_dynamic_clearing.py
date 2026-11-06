import ast
import math
import os
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
import numpy as np


SOURCE = Path(os.environ.get('GRID_SOURCE', str(Path(__file__).resolve().parents[1] /
              'omnifleet_map_tf_generator' / 'mola_realtime_nav_grid.py')))
tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
scope = {'math': math, 'np': np}
functions = [f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == 'select_grid_points']
functions += [f for c in tree.body if isinstance(c, ast.ClassDef) and c.name == 'RealtimeNavGrid'
              for f in c.body if isinstance(f, ast.FunctionDef) and f.name == 'mark_free_ray']
exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), scope)


def message(points):
    xyz = np.asarray(points, dtype='<f4').reshape((-1, 3))
    return NS(fields=[NS(name=k, offset=i*4, datatype=7) for i,k in enumerate(['x','y','z'])],
              is_bigendian=False, point_step=12, row_step=len(xyz)*12, height=1,
              width=len(xyz), data=xyz.tobytes())


def polar(distance, angle):
    a = math.radians(angle)
    return [.05+distance*math.cos(a), .05+distance*math.sin(a), .2]


class Grid:
    def __init__(self, width=120):
        self.width = self.height = width
        self.grid = [-1]*(width*width)

    def index(self, point):
        return math.floor(point[1]/.1)*self.width+math.floor(point[0]/.1)

    def apply(self, points):
        rays, occupied = scope['select_grid_points'](message(points), .05, .05, 0., 0., .1,
                                                      self.width, self.height)
        self._current_occupied = set(occupied.tolist())
        for cell in rays:
            scope['mark_free_ray'](self, (0,0), cell)
        for index in occupied:
            self.grid[index] = 100
        return rays


class GridClearing(unittest.TestCase):
    def test_removed_box_in_same_degree_bin_is_cleared(self):
        box, fixed, background = polar(2.,10.9), polar(3.,10.1), polar(5.,10.9)
        grid = Grid(); grid.apply([box,fixed])
        self.assertEqual(grid.grid[grid.index(box)],100)
        grid.apply([fixed,background])
        self.assertEqual(grid.grid[grid.index(box)],0)
        self.assertEqual(grid.grid[grid.index(fixed)],100)
        self.assertEqual(grid.grid[grid.index(background)],100)

    def test_normal_observed_removal_still_clears(self):
        old, fixed, background = [1.05,.05,.2], [1.05,.55,.2], [3.05,.05,.3]
        grid = Grid(); grid.apply([old,fixed]); grid.apply([background,fixed])
        self.assertEqual(grid.grid[grid.index(old)],0)
        self.assertEqual(grid.grid[grid.index(fixed)],100)

    def test_current_foreground_protects_occluded_history(self):
        old, foreground, far = [3.05,.05,.2], [1.05,.05,.2], [5.05,.05,.3]
        grid = Grid(); grid.apply([old]); grid.apply([foreground,far])
        self.assertEqual(grid.grid[grid.index(old)],100)
        self.assertEqual(grid.grid[grid.index(foreground)],100)
        self.assertEqual(grid.grid[grid.index(far)],100)

    def test_ceiling_or_floor_return_does_not_erase_low_obstacle(self):
        for z in [2.,-.5]:
            grid=Grid(); old=[2.05,.05,.2]; grid.apply([old]); grid.apply([[5.05,.05,z]])
            self.assertEqual(grid.grid[grid.index(old)],100)

    def test_far_background_clears_only_to_existing_eight_metre_limit(self):
        grid=Grid(); old=[2.05,.05,.2]; grid.apply([old]); grid.apply([[10.05,.05,.2]])
        self.assertEqual(grid.grid[grid.index(old)],0)
        self.assertEqual(grid.grid[grid.index([9.55,.05,.2])],-1)

    def test_background_outside_map_still_clears_visible_inside_segment(self):
        grid=Grid(60); old=[5.05,.05,.2]; grid.apply([old]); grid.apply([[8.05,.05,.2]])
        self.assertEqual(grid.grid[grid.index(old)],0)

    def test_current_return_outside_marking_range_does_not_erase_that_obstacle(self):
        grid=Grid(); current=[7.05,.05,.2]
        grid.grid[grid.index(current)]=100
        grid.apply([current])
        self.assertEqual(grid.grid[grid.index(current)],100)

    def test_duplicate_endpoint_cells_need_only_one_ray(self):
        grid=Grid(); rays=grid.apply([[.615,.625,.2],[.625,.615,.2]]*10000)
        self.assertEqual(len(rays),1)
        self.assertEqual(grid.grid[6*grid.width+6],100)

    def test_empty_scan_does_not_erase_unobserved_history(self):
        grid=Grid(); grid.apply([[2.05,.05,.2]]); before=list(grid.grid)
        self.assertEqual(grid.apply([]),[])
        self.assertEqual(grid.grid,before)


if __name__ == '__main__':
    unittest.main()
