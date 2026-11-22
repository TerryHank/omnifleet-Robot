from nav_msgs.msg import OccupancyGrid
from diagnostic_node import grid_summary
m=OccupancyGrid();m.info.width=2;m.info.height=2;m.info.resolution=.1;m.data=[-1,0,50,100]
r=grid_summary(m)
assert (r['unknown'],r['free'],r['occupied_100'],r['intermediate_cost'])==(1,1,1,1)
assert r['coarse_map']['rows']==['+#','?.']
assert 'data' not in r
print('PASS: grid summary separates unknown/free/intermediate/occupied and excludes raw cell arrays')
