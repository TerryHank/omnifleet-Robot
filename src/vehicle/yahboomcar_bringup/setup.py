from setuptools import setup
import os
from glob import glob

package_name = 'yahboomcar_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        #(os.path.join('share','yahboomcar_description','urdf'),glob(os.path.join('urdf','*.*'))),
		#(os.path.join('share','yahboomcar_description','meshes'),glob(os.path.join('meshes','*.*'))),
        (os.path.join('share','yahboomcar_description','rviz'),glob(os.path.join('rviz','*.rviz*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TerryHank',
    maintainer_email='TerryHank@users.noreply.github.com',
    description='ROS 2 driver and bringup utilities for the Yahboom R2 STM32 Ackermann chassis.',
    license='Proprietary',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'patrol_4ROS = yahboomcar_bringup.patrol_4ROS:main',
        'Ackman_driver_R2	= yahboomcar_bringup.Ackman_driver_R2:main',
        'calibrate_linear_R2 = yahboomcar_bringup.calibrate_linear_R2:main',
        'calibrate_angular_R2 = yahboomcar_bringup.calibrate_angular_R2:main',
        'patrol_4ROS_R2 = yahboomcar_bringup.patrol_4ROS_R2:main',
        'patrol_a1_R2 = yahboomcar_bringup.patrol_a1_R2:main',
        'sbus_debug_node = yahboomcar_bringup.sbus_debug_node:main',
        ],
    },
)
