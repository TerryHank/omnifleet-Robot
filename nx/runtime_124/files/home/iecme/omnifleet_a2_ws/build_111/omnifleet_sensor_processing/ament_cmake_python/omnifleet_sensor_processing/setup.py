from setuptools import find_packages
from setuptools import setup

setup(
    name='omnifleet_sensor_processing',
    version='0.1.0',
    packages=find_packages(
        include=('omnifleet_sensor_processing', 'omnifleet_sensor_processing.*')),
)
