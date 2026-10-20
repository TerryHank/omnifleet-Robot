"""Build the Foxglove-only subscription shutdown backport against the workspace RMW."""
import concurrent.futures
import shlex
import shutil
import subprocess
from pathlib import Path

ws = Path('/home/iecme/omnifleet_ws')
base = ws / 'build/rmw_zenoh_cpp'
work = ws / 'build/foxglove_zenoh_compat'
detail = ws / 'src/system/rmw_zenoh_cpp/src/detail'
sources = work / 'src/detail'
sources.mkdir(parents=True, exist_ok=True)
names = ['rmw_node_data.cpp', 'rmw_subscription_data.cpp']
for name in names:
    shutil.copy2(detail/name, sources/name)
subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i',
                str(Path(__file__).with_name('subscription-shutdown.patch'))], cwd=work, check=True)
flags = dict(line.split(' = ', 1) for line in (base/'CMakeFiles/rmw_zenoh_cpp.dir/flags.make').read_text().splitlines() if ' = ' in line)
arguments = sum([shlex.split(flags[key]) for key in ['CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS']], [])
def compile_source(name):
    obj = work/(name+'.o')
    subprocess.run(['/usr/bin/c++', *arguments, '-I'+str(detail), '-c', str(sources/name), '-o', str(obj)], check=True)
    return name, obj
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    objects = dict(pool.map(compile_source, names))
link = shlex.split((base/'CMakeFiles/rmw_zenoh_cpp.dir/link.txt').read_text())
for i, value in enumerate(link):
    if value.endswith('.o'):
        name = Path(value).name[:-2]
        link[i] = str(objects[name]) if name in objects else str(base/value)
    elif value.endswith('/libzenohc.so'):
        link[i] = str(ws/'src/system/omnifleet_fleet/zenoh-patched-v2/lib/libzenohc.so')
    elif value.startswith('-Wl,-rpath,'):
        link[i] = '-Wl,-rpath,/opt/ros/humble/lib:'+str(ws/'src/system/omnifleet_fleet/zenoh-patched-v2/lib')
link[link.index('-o')+1] = str(work/'librmw_zenoh_cpp.so')
subprocess.run(link, cwd=base, check=True)
print(work/'librmw_zenoh_cpp.so')
