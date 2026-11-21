#!/usr/bin/env python3
"""Order boot clients after the local listener is ready; no dependency on peers."""
import time
from pathlib import Path
deadline=time.monotonic()+30
while time.monotonic()<deadline:
    rows=Path('/proc/net/tcp').read_text().splitlines()[1:]
    if any(row.split()[1].endswith(':1D17') and row.split()[1].split(':')[0] in {'0100007F', '00000000'} and row.split()[3]=='0A' for row in rows):
        raise SystemExit(0)
    time.sleep(.1)
raise SystemExit('Local Zenoh TCP listener did not start')
