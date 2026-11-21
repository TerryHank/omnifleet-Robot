from setuptools import find_packages, setup

package_name = "omnifleet_hikrobot_rgbd"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml", "README.md"]),
        ("share/" + package_name + "/launch", ["launch/rgbd_camera.launch.py"]),
        ("share/" + package_name + "/config", ["config/mv_dt01snu.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OmniFleet",
    maintainer_email="iecme@example.com",
    description="MV-DT01SNU ROS 2 camera driver using the installed Hikrobot U3V runtime.",
    license="Apache-2.0",
    entry_points={"console_scripts": ["camera_node = omnifleet_hikrobot_rgbd.camera_node:main"]},
)
