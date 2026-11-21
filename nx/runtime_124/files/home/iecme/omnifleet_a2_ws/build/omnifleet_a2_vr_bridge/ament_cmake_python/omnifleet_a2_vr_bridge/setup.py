from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_a2_vr_bridge',
    version='0.1.0',
    packages=find_packages(
        include=('omnifleet_a2_vr_bridge', 'omnifleet_a2_vr_bridge.*')),
)
