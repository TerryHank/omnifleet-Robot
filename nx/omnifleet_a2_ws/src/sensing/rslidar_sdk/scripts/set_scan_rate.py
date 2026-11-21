#!/usr/bin/env python3
"""Switch the live Airy driver between native full scans and half scans."""
import argparse,re,shutil,subprocess,datetime
from pathlib import Path
from switch_guard import check_stationary,wait_for_fused

p=argparse.ArgumentParser();p.add_argument('hz',type=int,choices=[10,20]);args=p.parse_args()
check_stationary()
config=Path('/home/iecme/omnifleet_a2_ws/src/sensing/rslidar_sdk/config/config.yaml')
backup=Path('/home/iecme/robot_backups/airy_rate_switch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir();shutil.copy2(config,backup/'config.before.yaml')
s=config.read_text()
s,n=re.subn(r'(?m)^(\s*split_frame_mode:)\s*\d+.*$',r'\g<1> '+str(1 if args.hz==10 else 3)+'  # 10 Hz full scan / 20 Hz half scan',s);assert n==1
s,n=re.subn(r'(?m)^(\s*num_blks_split:)\s*\d+.*$',r'\g<1> 900  # Used only for 20 Hz half scans',s);assert n==1
units=['omnifleet-t2-pure-lio-nav2','omnifleet-t2-mola','omnifleet-t2-airy']
subprocess.run(['sudo','systemctl','stop',*units],check=True)
mapfile=Path('/home/iecme/omnifleet_data/maps/experiments/simple_direct/local_map.mm')
if mapfile.exists():shutil.copy2(mapfile,backup/'local_map.before.mm')
config.write_text(s)
subprocess.run(['sudo','systemctl','start','omnifleet-t2-airy','omnifleet-t2-mola'],check=True)
wait_for_fused()
subprocess.run(['sudo','systemctl','start','omnifleet-t2-pure-lio-nav2'],check=True)
print(f'Airy requested {args.hz} Hz; backup={backup}. Verify rslidar_points rate after restart.')
