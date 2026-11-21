from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_a2_planner',
    version='0.3.0',
    packages=find_packages(
        include=('omnifleet_a2_planner', 'omnifleet_a2_planner.*')),
)
