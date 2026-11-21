#!/bin/bash
set -e
root=/home/iecme/.local/share/omnifleet-dispatch-124
export PYTHONPATH="$root/omnifleet-discovery:$PYTHONPATH"
export OMNIFLEET_DISCOVERY_PROFILE="$root/data/run/local-robot-124.json"
mkdir -p "$root/data/run"
python3 - "$root" <<'PY'
from fleet_beacon import settings
from pathlib import Path
import json,sys,time
root=Path(sys.argv[1])
s=settings()
profile={**s,'host':'127.0.0.1','local_namespace':'','onboard_local':True,
         'control_topic':'/navigation/fleet/local_status','compressed_maps':False,
         'fastdds_config':str(root/'omnifleet_rmf_adapter/config/fastdds-client.xml')}
for name,data in [('run/local-robot-124.json',profile),
    ('discovery.json',{'schema':1,'updated_monotonic':time.monotonic(),'robots':{s['robot_id']:profile},'conflicts':[]})]:
    p=root/'data'/name
    tmp=p.with_suffix('.tmp')
    tmp.write_text(json.dumps(data))
    tmp.replace(p)
PY
exec /bin/bash "$root/omnifleet_rmf_adapter/scripts/run.bash" robot_124
