from setuptools import setup

setup(name='omnifleet_chassis_driver', version='0.1.0', packages=['omnifleet_chassis_driver'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/omnifleet_chassis_driver']),
                  ('share/omnifleet_chassis_driver', ['package.xml', 'README.md'])],
      install_requires=['setuptools'], license='MIT AND Apache-2.0',
      entry_points={'console_scripts':['t2_driver=omnifleet_chassis_driver.omnifleet_t2_driver:main', 'omnifleet-t2-raw-pwm=omnifleet_chassis_driver.raw_pwm_cli:main', 'wheel_slip_detector=omnifleet_chassis_driver.wheel_slip_detector:main', 'base_link_rslidar_tf.py=omnifleet_chassis_driver.base_link_rslidar_tf:main']})
