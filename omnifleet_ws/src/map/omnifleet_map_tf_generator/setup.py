from setuptools import setup

setup(
    name='omnifleet_map_tf_generator',
    version='0.1.0',
    packages=['omnifleet_map_tf_generator'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/omnifleet_map_tf_generator']),
        ('share/omnifleet_map_tf_generator', ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools'],
    entry_points={'console_scripts': [
        'mola_realtime_nav_grid.py=omnifleet_map_tf_generator.mola_realtime_nav_grid:main',
    ]},
    description='Map-frame transforms, TF construction and shared-map grid codec.',
    license='Apache-2.0',
)
