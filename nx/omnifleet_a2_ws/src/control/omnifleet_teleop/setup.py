from setuptools import setup

setup(name='omnifleet_teleop', version='0.1.0', packages=['omnifleet_teleop'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/omnifleet_teleop']),
                  ('share/omnifleet_teleop', ['package.xml', 'README.md'])],
      install_requires=['setuptools'], license='MIT',
      entry_points={'console_scripts':['vr_protocol_adapter=omnifleet_teleop.vr_protocol_adapter:main']})
