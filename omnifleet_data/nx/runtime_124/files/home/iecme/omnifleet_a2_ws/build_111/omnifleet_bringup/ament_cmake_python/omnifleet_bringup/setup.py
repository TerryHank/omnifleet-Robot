from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_bringup',
    version='0.3.0',
    packages=find_packages(
        include=('omnifleet_bringup', 'omnifleet_bringup.*')),
)
