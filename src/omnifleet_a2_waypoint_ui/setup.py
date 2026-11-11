from glob import glob
from setuptools import find_packages, setup


package_name = "omnifleet_a2_waypoint_ui"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="TerryHank",
    maintainer_email="terryhank@example.com",
    description="Semantic Foxglove waypoint UI bridge for one OmniFleet robot.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "waypoint_ui_bridge = omnifleet_a2_waypoint_ui.waypoint_ui_bridge:main",
            "semantic_waypoint_panel = omnifleet_a2_waypoint_ui.semantic_waypoint_panel:main",
        ],
    },
)
