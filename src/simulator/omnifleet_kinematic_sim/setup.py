from glob import glob
from setuptools import find_packages, setup


package_name = "omnifleet_kinematic_sim"


setup(
    name=package_name,
    version="1.0.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="iecme",
    maintainer_email="iecme@example.com",
    description="Serial-free Ackermann chassis simulation.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ackermann_sim_driver = omnifleet_kinematic_sim.ackermann_sim_driver:main",
        ],
    },
)
