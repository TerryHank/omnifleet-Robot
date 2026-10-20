#!/usr/bin/env python3
"""Keep a signal backtrace for this MOLA process without a resident debugger."""
import os,sys,time
from pathlib import Path

directory=Path('/home/iecme/omnifleet_data/recordings/robot_logs/mola_crashes')
directory.mkdir(parents=True,exist_ok=True)
library=Path('/lib/aarch64-linux-gnu/libSegFault.so')
if not library.is_file():raise RuntimeError('Missing glibc libSegFault crash recorder')
output=directory/f'mola-{time.strftime("%Y%m%d-%H%M%S")}-{os.getpid()}.log'
os.environ['LD_PRELOAD']=str(library)+(':'+os.environ['LD_PRELOAD'] if os.environ.get('LD_PRELOAD') else '')
os.environ['SEGFAULT_OUTPUT_NAME']=str(output)
os.environ['SEGFAULT_USE_ALTSTACK']='1'
os.environ['SEGFAULT_SIGNALS']='segv'
print('MOLA crash backtrace destination: '+str(output),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
