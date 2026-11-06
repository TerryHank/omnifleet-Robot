import json,math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
import numpy as np
from omnifleet_local_navigation.clearance_recovery import ClearanceEscape,planner_cell_cost,planner_blocked,recovery_config

def objectify(value):
    return NS(**{k:objectify(v) for k,v in value.items()}) if isinstance(value,dict) else value

def grid():
    resolution=.05;width=height=40
    values=[]
    for y in range(height):
        for x in range(width):
            wx=-1+(x+.5)*resolution
            values.append(100 if .4<=wx<.45 else 99 if -.2<=wx<.5 else 0)
    return objectify({'header':{'frame_id':'map'},'info':{'width':width,'height':height,'resolution':resolution,
      'origin':{'position':{'x':-1.,'y':-1.},'orientation':{'x':0.,'y':0.,'z':0.,'w':1.}}},'data':values})

class PlannerExitTests(unittest.TestCase):
    def test_global_blocked_local_clear_requires_translation_to_a_free_start(self):
        g=grid();pose=[0.,0.,0.];obstacles=[[0.,.5],[0.,-.5]]
        r=ClearanceEscape(pose,obstacles,[],dict(length=.5,width=.37,padding=.05),.01,0.,'epoch',target_heading=0.,exit_grid=g)
        self.assertIsNone(r.turn_target);self.assertEqual(r.direction,-1)
        self.assertGreaterEqual(r.distance,.2);self.assertTrue(r.planner_clear(r.path[-1]))
        for i,p in enumerate(r.path):
            self.assertNotEqual(planner_cell_cost(g,p),100)
            command=r.command(i*.01/r.speed,p,obstacles,[],[r.direction*r.speed,0.],True,'epoch')
            self.assertNotEqual(r.state,'failed',r.reason)
        self.assertEqual(r.state,'stopping');self.assertEqual(command,[0.,0.])

    def test_updated_global_obstacle_is_not_driven_through(self):
        g=grid();pose=[0.,0.,0.];obstacles=[[0.,.5],[0.,-.5]]
        r=ClearanceEscape(pose,obstacles,[],dict(length=.5,width=.37,padding=.05),.01,0.,'epoch',exit_grid=g)
        end=r.path[-1];ix=math.floor((end[0]+1)/g.info.resolution);iy=20
        g.data[iy*g.info.width+ix]=100
        self.assertFalse(r.certified(end,[-.1,0.],obstacles,[]))

    def test_recorded_global_local_map_mismatch_can_exit(self):
        scenes=json.loads((Path(__file__).parent/'data/recorded-global-exit.json').read_text())
        tested=0
        for scene in scenes:
            g=objectify(scene['global_grid']);pose=scene['pose']
            if not planner_blocked(g,pose):continue
            with self.subTest(time=scene['time']):
                config=recovery_config(scene['config'],scene['local_parameters'])
                r=ClearanceEscape(pose,scene['obstacles'],scene['unknown'],config,scene['resolution'],0.,'epoch',exit_grid=g)
                self.assertTrue(r.planner_clear(r.path[-1]));self.assertLessEqual(r.distance,.8)
                self.assertIsNone(r.turn_target)
                for i,p in enumerate(r.path):
                    command=r.command(i*.01/r.speed,p,scene['obstacles'],scene['unknown'],[r.direction*r.speed,r.direction*r.speed*r.curvature],True,'epoch')
                    self.assertNotEqual(r.state,'failed',r.reason)
                    self.assertLessEqual(abs(command[0]),.1);self.assertLessEqual(abs(command[1]),.1)
                self.assertEqual(r.state,'stopping',r.reason);tested+=1
        self.assertGreater(tested,0,'No blocked-start snapshot was tested')

    def test_recorded_exit_with_speed_gain_and_lateral_drift(self):
        scenes=json.loads((Path(__file__).parent/'data/recorded-global-exit.json').read_text())
        for scene in scenes:
            g=objectify(scene['global_grid']);pose=list(scene['pose'])
            if not planner_blocked(g,pose):continue
            with self.subTest(time=scene['time']):
                config=recovery_config(scene['config'],scene['local_parameters'])
                now=v=w=0.
                for attempt in range(2):
                    r=ClearanceEscape(pose,scene['obstacles'],scene['unknown'],config,scene['resolution'],now,'epoch',exit_grid=g)
                    while r.state=='moving' and now-r.started<r.timeout:
                        command=r.command(now,pose,scene['obstacles'],scene['unknown'],[v,w],True,'epoch')
                        v,w=1.3*command[0],1.3*command[1];lateral=-.06*v+.03*w
                        pose[0]+=.05*(v*math.cos(pose[2])-lateral*math.sin(pose[2]))
                        pose[1]+=.05*(v*math.sin(pose[2])+lateral*math.cos(pose[2]))
                        pose[2]+=.05*w;now+=.05
                    if r.state=='stopping' or not r.replan_allowed:break
                    v=w=0.
                self.assertEqual(r.state,'stopping',r.reason);self.assertTrue(r.planner_clear(pose))

if __name__=='__main__':unittest.main()
