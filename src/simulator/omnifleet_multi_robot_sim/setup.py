from glob import glob
from setuptools import find_packages, setup


package_name = "omnifleet_multi_robot_sim"


setup(
    name=package_name,
    version="1.1.1",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/rviz", glob("rviz/*")),
        (f"share/{package_name}/config", glob("config/*")),
        (f"share/{package_name}/worlds", glob("worlds/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="iecme",
    maintainer_email="iecme@example.com",
    description="Three-robot Gazebo Classic fleet demonstration and verification.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "fleet_controller = omnifleet_multi_robot_sim.fleet_controller:main",
            "runtime_verifier = omnifleet_multi_robot_sim.runtime_verifier:main",
            "multi_waypoint_verifier = omnifleet_multi_robot_sim.multi_waypoint_verifier:main",
        ],
    },
)
