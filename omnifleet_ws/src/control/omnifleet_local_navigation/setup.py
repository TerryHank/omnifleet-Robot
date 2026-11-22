from setuptools import setup
setup(name="omnifleet_local_navigation",version="0.1.0",packages=["omnifleet_local_navigation"],
data_files=[("share/ament_index/resource_index/packages",["resource/omnifleet_local_navigation"]),("share/omnifleet_local_navigation",["package.xml"])],
entry_points={"console_scripts":["local_navigation=omnifleet_local_navigation.runtime:main"]})
