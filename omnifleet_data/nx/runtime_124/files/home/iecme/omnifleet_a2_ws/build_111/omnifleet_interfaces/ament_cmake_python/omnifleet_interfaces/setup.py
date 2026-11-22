from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_interfaces',
    version='0.3.0',
    packages=find_packages(
        include=('omnifleet_interfaces', 'omnifleet_interfaces.*')),
)
