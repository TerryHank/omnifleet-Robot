"""Compatibility import; implementation belongs to omnifleet_chassis_driver."""
import importlib as _importlib
import sys as _sys

_implementation = _importlib.import_module('omnifleet_chassis_driver.raw_pwm_cli')
if __name__ == '__main__':
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation
