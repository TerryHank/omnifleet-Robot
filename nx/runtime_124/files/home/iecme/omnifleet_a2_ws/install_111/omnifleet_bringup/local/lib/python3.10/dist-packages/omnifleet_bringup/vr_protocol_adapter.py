"""Compatibility import; implementation belongs to omnifleet_teleop."""
import importlib as _importlib
import sys as _sys

_implementation = _importlib.import_module('omnifleet_teleop.vr_protocol_adapter')
if __name__ == '__main__':
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation
