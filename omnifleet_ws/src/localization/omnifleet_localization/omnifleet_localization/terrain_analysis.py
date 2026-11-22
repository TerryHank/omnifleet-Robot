"""Compatibility import; implementation belongs to omnifleet_terrain_analysis."""
import importlib as _importlib
import sys as _sys

_implementation = _importlib.import_module('omnifleet_terrain_analysis.terrain_analysis')
if __name__ == '__main__':
    _implementation.main()
else:
    _sys.modules[__name__] = _implementation
