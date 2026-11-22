from setuptools import setup

setup(name='omnifleet_terrain_analysis', version='0.1.0', packages=['omnifleet_terrain_analysis'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/omnifleet_terrain_analysis']),
                  ('share/omnifleet_terrain_analysis', ['package.xml', 'README.md'])],
      install_requires=['setuptools'], license='MIT',
      entry_points={'console_scripts':['terrain_mapper=omnifleet_terrain_analysis.terrain_mapper:main', 'depth_dropoff_detector=omnifleet_terrain_analysis.depth_dropoff_detector:main']})
