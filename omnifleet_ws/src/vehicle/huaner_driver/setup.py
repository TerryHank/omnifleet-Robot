from setuptools import setup

setup(
    name="huaner_driver",
    version="0.1.0",
    packages=["huaner_driver"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/huaner_driver"]),
        ("share/huaner_driver", ["package.xml"]),
    ],
    entry_points={"console_scripts": ["huaner_driver = huaner_driver.node:main"]},
)
