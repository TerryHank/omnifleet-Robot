import hashlib,json,os,subprocess
from pathlib import Path
root=Path('/home/iecme/robot_backups/fleet_zenoh_20260910');items=[]
for p in Path('/proc').glob('[0-9]*'):
    try:
        maps=(p/'maps').read_text()
        if 'librmw_' not in maps:continue
        args=(p/'cmdline').read_bytes().split(b'\0');env=dict(x.split(b'=',1) for x in (p/'environ').read_bytes().split(b'\0') if b'=' in x)
        libs=sorted({line.split()[-1] for line in maps.splitlines() if 'librmw_' in line or 'libzenohc.so' in line})
        items.append({'pid':int(p.name),'executable':os.fsdecode(args[0]),'script':os.fsdecode(args[1]) if len(args)>1 else '',
                      'rmw':os.fsdecode(env.get(b'RMW_IMPLEMENTATION',b'')),'domain':os.fsdecode(env.get(b'ROS_DOMAIN_ID',b'')),'libraries':libs})
    except (OSError,ValueError):pass
lib=Path('/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/zenoh-patched-v2/lib/libzenohc.so')
result={'robot':os.environ['OMNIFLEET_ROBOT_ID'],'processes':items,'zenoh_library_sha256':hashlib.sha256(lib.read_bytes()).hexdigest() if lib.exists() else None}
result['wrong_rmw']=[p for p in items if 'fastrtps' in ' '.join(p['libraries']) or p['rmw']!='rmw_zenoh_cpp' or p['domain']!='0']
result['unpatched_zenoh']=[p for p in items if any('libzenohc.so' in v and '/omnifleet_fleet/zenoh-patched-v2/' not in v for v in p['libraries'])]
services=json.loads((root/'migrated-services.json').read_text())+['omnifleet-t2-zenoh-router.service']
result['services']={name:subprocess.check_output(['systemctl','show',name,'-p','ActiveState','-p','SubState','-p','MainPID'],text=True).strip().splitlines() for name in services}
(root/'runtime-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='processes'},indent=2))
