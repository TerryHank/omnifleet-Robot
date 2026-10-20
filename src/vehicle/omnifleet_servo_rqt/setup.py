from setuptools import setup

package_name = 'omnifleet_servo_rqt'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'rqt_gui_py.plugin': [
            'FTServo Panel = omnifleet_servo_rqt.servo_plugin:ServoPlugin',
        ],
    },
)
