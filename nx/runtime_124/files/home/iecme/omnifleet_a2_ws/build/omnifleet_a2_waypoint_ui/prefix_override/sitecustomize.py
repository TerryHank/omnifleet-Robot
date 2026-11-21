import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/iecme/omnifleet_a2_ws/install/omnifleet_a2_waypoint_ui'
