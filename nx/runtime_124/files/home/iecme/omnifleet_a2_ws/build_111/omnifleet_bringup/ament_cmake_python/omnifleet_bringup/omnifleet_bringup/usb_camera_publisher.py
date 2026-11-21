"""Compatibility import; implementation belongs to omnifleet_sensor_processing."""
import importlib as _importlib
import sys as _sys

_implementation = _importlib.import_module('omnifleet_sensor_processing.usb_camera_publisher')
if __name__ == '__main__':
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation
