"""Rebuild only the keyframe exporter against this workspace's existing MOLA build."""
from pathlib import Path
import os,shlex,subprocess
folder=Path(__file__).resolve().parent;ws=Path.home()/'omnifleet_ws'
reference=ws/'build/mp2p_icp_core/apps/mm2ply';output=ws/'build/omnifleet_alignment_cloud_export';output.mkdir(parents=True,exist_ok=True)
flags={}
for line in (reference/'CMakeFiles/mm2ply.dir/flags.make').read_text().splitlines():
    if line.startswith('CXX_'):
        key,value=line.split('=',1);flags[key.strip()]=shlex.split(value)
subprocess.run(['/usr/bin/c++',*flags['CXX_DEFINES'],*flags['CXX_INCLUDES'],*flags['CXX_FLAGS'],'-c',str(folder/'export_keyframes.cpp'),'-o',str(output/'export.o')],check=True)
link=shlex.split((reference/'CMakeFiles/mm2ply.dir/link.txt').read_text())
link=[str(output/'export.o') if value.endswith('.o') else value for value in link];link[link.index('-o')+1]=str(output/'export-keyframes')
subprocess.run(link,cwd=reference,check=True)
temporary=folder/'export-keyframes.new';temporary.write_bytes((output/'export-keyframes').read_bytes());temporary.chmod(0o755);os.replace(temporary,folder/'export-keyframes')
