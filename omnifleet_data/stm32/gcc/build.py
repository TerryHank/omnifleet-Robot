from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re, subprocess, xml.etree.ElementTree as ET

root = Path.cwd()
build = root / "gcc"
project = root / "MDK-ARM"
xml = ET.parse(project / "RosRobotControllerM4.uvprojx")
opts = xml.find(".//Cads/VariousControls")
includes = [(project / p).resolve() for p in opts.findtext("IncludePath").split(";") if "RVDS/" not in p]
includes += [root / "Third_Party", build]
headers = {p.name.lower(): p.name for d in includes if d.is_dir() for p in d.glob("*.h")}
flags = ["-mcpu=cortex-m4", "-mthumb", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard",
         "-Os", "-std=gnu11", "-ffunction-sections", "-fdata-sections", "-fcommon",
         *["-D"+v for v in opts.findtext("Define").split(",")],
         *["-I"+str(d) for d in includes]]
sources = []
for f in xml.findall(".//Groups/Group/Files/File/FilePath"):
    path = (project / f.text.replace("\\", "/")).resolve()
    if path.suffix.lower() != ".c":
        continue
    if "RVDS" in path.parts:
        path = build / path.name
    if not path.exists():
        alt = {p.name.lower():p for p in path.parent.iterdir()}
        path = alt.get(path.name.lower(), path)
    sources.append(path)
def normalize(match):
    name = match[2]
    return match[1] + headers.get(name.lower(), name) + match[3]
for path in set(sources) | {p for d in includes if d.is_dir() for p in d.glob("*.h")}:
    data = path.read_bytes()
    text = data.decode("latin1")
    updated = re.sub(r'(?m)^(\s*#\s*include\s*["<])([^"<>/]+)([">])',normalize,text)
    if updated != text:
        path.write_bytes(updated.encode("latin1"))
def compile_one(item):
    index, source = item
    obj = build / f"{index:03}_{source.stem}.o"
    result = subprocess.run(["arm-none-eabi-gcc", *flags, "-c", str(source), "-o", str(obj)], capture_output=True, text=True, errors="replace")
    return obj, source, result
with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(compile_one, enumerate(sources)))
errors = [(s,r.stderr) for _,s,r in results if r.returncode]
(build / "compile-errors.txt").write_text("\n".join(f"{s}\n{e}" for s,e in errors))
print(f"{len(results)-len(errors)}/{len(results)} C files compiled")
for s,e in errors:
    print(s.relative_to(root), next((x for x in e.splitlines() if "error:" in x),e[:140]))
if errors:
    raise SystemExit(1)
(build / "objects.txt").write_text("\n".join(str(o) for o,_,_ in results))
