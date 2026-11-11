from glob import glob
from setuptools import setup

setup(name='omnifleet_person_follow', version='0.1.0', packages=['omnifleet_person_follow'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/omnifleet_person_follow']),
                  ('share/omnifleet_person_follow', ['package.xml', 'README.md', 'NOTICE.md']),
                  ('share/omnifleet_person_follow/config', glob('config/*')),
                  ('share/omnifleet_person_follow/launch', glob('launch/*.py'))],
      entry_points={'console_scripts': ['person_follow_node = omnifleet_person_follow.node:main']})
