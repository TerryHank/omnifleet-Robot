from setuptools import setup
setup(name="omnifleet_a2_gateway",version="0.1.0",packages=["omnifleet_a2_gateway"], package_data={"omnifleet_a2_gateway":["ackermann_follow.xml"]},
 data_files=[("share/ament_index/resource_index/packages",["resource/omnifleet_a2_gateway"]),("share/omnifleet_a2_gateway",["package.xml"])],
 entry_points={"console_scripts":["local_navigation=omnifleet_a2_gateway.gateway:main","stop_owned=omnifleet_a2_gateway.stop_owned:main"]})
