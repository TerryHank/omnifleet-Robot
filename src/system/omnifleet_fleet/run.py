#!/usr/bin/env python3
"""Launch the named local component with this robot's native ROS namespace."""
import os,sys
from fleet_scope import ros_args
kind,*args=sys.argv[1:]
if kind=='launch':
    package,filename,*extra=args
    cmd=['ros2','launch','/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/scoped.launch.py',
         'target_package:='+package,'target_launch:='+filename,*extra]
elif kind=='run':
    package,executable,*extra=args
    cmd=['ros2','run',package,executable,*extra,*ros_args()]
elif kind=='python':
    filename,*extra=args
    cmd=['python3',filename,*extra,*ros_args()]
else:raise SystemExit('expected launch, run or python')
os.execvp(cmd[0],cmd)
