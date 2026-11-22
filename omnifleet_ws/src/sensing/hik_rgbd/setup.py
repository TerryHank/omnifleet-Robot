from setuptools import find_packages, setup

setup(
    name="hik_rgbd",
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/hik_rgbd"]),
        ("share/hik_rgbd", ["package.xml", "README.md"]),
        ("share/hik_rgbd/launch", ["launch/hik_rgbd_launch.py"]),
        ("share/hik_rgbd/config", ["config/hik_camera.rviz"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OmniFleet",
    maintainer_email="iecme@example.com",
    description="ROS 2 SDK interface for the existing MV-DT01SNU camera driver.",
    license="Apache-2.0",
    entry_points={"console_scripts": [
        "image_pipeline_all_in_one = hik_rgbd.sdk_node:main",
        "camera_node = hik_rgbd.sdk_node:main",
        "rgbd_visualization = hik_rgbd.visualization_node:main",
    ]},
)
