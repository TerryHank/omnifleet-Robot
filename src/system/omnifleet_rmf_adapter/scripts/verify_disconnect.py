"""Stop/restart only the WSL observer; no robot or RMF task commands."""
import json
from omnifleet_rmf_adapter.state import connection_states
from pathlib import Path
import subprocess
import time

data = Path.home() / 'workspaces/omnifleet_ws/data'
service = 'omnifleet-rmf-robot104.service'


def wait_state(connected, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        report = json.loads((data / 'connection_status.json').read_text())
        state = connection_states(report).get('robot_104')
        if state and state['transport_connected'] is connected:
            return state
        time.sleep(0.2)
    raise AssertionError('Observer state did not change as expected')


wait_state(True, 5)
try:
    subprocess.run(['systemctl', '--user', 'stop', service], check=True, timeout=15)
    offline = wait_state(False, 8)
    assert not offline['dispatch_enabled']
finally:
    subprocess.run(['systemctl', '--user', 'start', service], check=True, timeout=15)
restored = wait_state(True, 15)
result = {'passed': True, 'test': 'wsl_observer_stop_restart',
          'expired_ipc_age_seconds': offline['ipc_age_seconds'],
          'restored_transport_connected': restored['transport_connected'],
          'vehicle_commands_sent': 0, 'vehicle_watchdog_tested': False}
(data / 'evidence_20261014/disconnect.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
