import os
def robot_id():return os.environ['OMNIFLEET_ROBOT_ID']
def frame(name):return name.lstrip('/')
def topic(name):return '/'+name.lstrip('/')
