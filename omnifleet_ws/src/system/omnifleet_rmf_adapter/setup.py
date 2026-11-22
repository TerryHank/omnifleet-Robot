from glob import glob
from setuptools import setup

setup(
    name='omnifleet_rmf_adapter',
    version='0.1.0',
    packages=['omnifleet_rmf_adapter'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/omnifleet_rmf_adapter']),
        ('share/omnifleet_rmf_adapter', ['package.xml']),
        ('share/omnifleet_rmf_adapter/config', glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={'console_scripts': ['omnifleet = omnifleet_rmf_adapter.launch:main']},
)
