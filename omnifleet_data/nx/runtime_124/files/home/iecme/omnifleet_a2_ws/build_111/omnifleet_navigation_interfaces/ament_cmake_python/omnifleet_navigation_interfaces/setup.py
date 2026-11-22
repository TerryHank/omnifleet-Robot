from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_navigation_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('omnifleet_navigation_interfaces', 'omnifleet_navigation_interfaces.*')),
)
