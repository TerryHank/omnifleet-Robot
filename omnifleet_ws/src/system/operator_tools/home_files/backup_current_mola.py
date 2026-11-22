#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


HOME = Path("/home/iecme")
STAMP = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = HOME / "robot_backups" / f"mola_before_latest_{STAMP}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def run(args, *, check=True):
    return subprocess.run(args, text=True, capture_output=True, check=check)


def copy_file(source: Path, destination: Path):
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=True)
    return True


for directory in (
    "config",
    "runtime",
    "map",
    "navigation_frozen_manifest",
    "interface",
    "manifests",
    "reports",
    "logs",
):
    (BACKUP / directory).mkdir(parents=True, exist_ok=True)

mola_pids = []
for proc in Path("/proc").iterdir():
    if not proc.name.isdigit():
        continue
    try:
        if (proc / "comm").read_text().strip() == "mola-cli":
            mola_pids.append(int(proc.name))
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
if len(mola_pids) != 1:
    raise RuntimeError(f"expected exactly one mola-cli process, got {mola_pids}")
mola_pid = mola_pids[0]
proc = Path("/proc") / str(mola_pid)
cmdline = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode().strip()
environment = {}
for item in (proc / "environ").read_bytes().split(b"\0"):
    if not item or b"=" not in item:
        continue
    key, value = item.split(b"=", 1)
    environment[key.decode(errors="replace")] = value.decode(errors="replace")

write(BACKUP / "runtime" / "mola_pid.txt", f"{mola_pid}\n")
write(BACKUP / "runtime" / "cmdline.txt", cmdline + "\n")
write(BACKUP / "runtime" / "proc_maps.txt", (proc / "maps").read_text())
write(
    BACKUP / "runtime" / "environment.txt",
    "".join(f"{key}={value}\n" for key, value in sorted(environment.items())),
)

status_path = HOME / ".local/share/omnifleet_t2/navigation-stack/status.json"
status = json.loads(status_path.read_text())
write(BACKUP / "config" / "navigation_stack_status.json", json.dumps(status, indent=2))
copy_file(status_path, BACKUP / "config" / "status.json")
if status.get("log"):
    copy_file(Path(status["log"]), BACKUP / "logs" / Path(status["log"]).name)

config_sources = [
    Path(environment.get("MOLA_ODOMETRY_PIPELINE_YAML", "")),
    Path(cmdline.split()[1]) if len(cmdline.split()) > 1 else Path(),
    HOME / "omnifleet_ws/src/system/omnifleet_bringup/launch/mola_localization.launch.py",
    HOME / "omnifleet_ws/src/system/omnifleet_bringup/launch/mola_nav2_unified.launch.py",
    HOME / "omnifleet_ws/src/system/omnifleet_bringup/launch/navigation.launch.py",
    HOME / "omnifleet_fleet/scoped.launch.py",
    HOME / "omnifleet_fleet/env.bash",
    HOME / "omnifleet_fleet/start.sh",
    HOME / "omnifleet_t2_ws/foxglove/nav2_permanent_panel/navigation_restart.py",
    HOME / "omnifleet_t2_ws/foxglove/nav2_permanent_panel/navigation_restart.sh",
    Path("/etc/omnifleet_t2/architecture.env"),
    Path("/etc/omnifleet_msc/agent.json"),
]
copied_configs = []
for source in config_sources:
    if not str(source) or not source.is_file():
        continue
    destination = BACKUP / "config" / source.as_posix().lstrip("/")
    copy_file(source, destination)
    copied_configs.append(str(source))

unit = status.get("unit")
if unit:
    result = run(["systemctl", "--user", "cat", f"{unit}.service"], check=False)
    write(BACKUP / "config" / "active_stack_unit.txt", result.stdout + result.stderr)
result = run(["systemctl", "--user", "list-unit-files", "--no-pager"], check=False)
write(BACKUP / "config" / "user_unit_files.txt", result.stdout)

source_install = HOME / "mola_3_2_ws/install"
backup_install = BACKUP / "runtime" / "install"
shutil.copytree(source_install, backup_install, symlinks=False)
source_tree = HOME / "mola_3_2_ws/src"
shutil.copytree(source_tree, BACKUP / "runtime" / "source_snapshot", symlinks=False)

loaded_paths = set()
for line in (proc / "maps").read_text().splitlines():
    fields = line.split()
    if len(fields) >= 6 and fields[-1].startswith("/"):
        loaded_paths.add(fields[-1])

key_tokens = (
    "libmp2p",
    "libmola",
    "libmrpt",
    "libtbb",
    "libgtsam",
    "mola-cli",
)
runtime_libraries = []
for raw_path in sorted(loaded_paths):
    if not any(token in raw_path for token in key_tokens):
        continue
    path = Path(raw_path)
    if not path.is_file():
        continue
    build_id = ""
    result = run(["readelf", "-n", str(path)], check=False)
    for line in result.stdout.splitlines():
        if "Build ID:" in line:
            build_id = line.split("Build ID:", 1)[1].strip()
            break
    ldd = run(["ldd", str(path)], check=False)
    ldd_name = hashlib.sha256(str(path).encode()).hexdigest()[:16] + ".ldd.txt"
    write(BACKUP / "runtime" / "ldd" / ldd_name, ldd.stdout + ldd.stderr)
    runtime_libraries.append(
        {
            "path": str(path),
            "realpath": str(path.resolve()),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "build_id": build_id,
            "ldd_file": f"runtime/ldd/{ldd_name}",
        }
    )
write(
    BACKUP / "runtime" / "loaded_libraries.json",
    json.dumps(runtime_libraries, indent=2),
)

install_files = []
for path in sorted(backup_install.rglob("*")):
    if path.is_file():
        install_files.append(
            {
                "path": str(path.relative_to(backup_install)),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
write(
    BACKUP / "runtime" / "install_manifest.json",
    json.dumps(install_files, indent=2),
)

package_versions = []
for package_xml in sorted(source_tree.rglob("package.xml")):
    text = package_xml.read_text(errors="replace")
    import re

    name = re.search(r"<name>([^<]+)</name>", text)
    version = re.search(r"<version>([^<]+)</version>", text)
    package_versions.append(
        {
            "path": str(package_xml),
            "name": name.group(1) if name else None,
            "version": version.group(1) if version else None,
            "sha256": sha256(package_xml),
        }
    )
write(
    BACKUP / "runtime" / "source_packages.json",
    json.dumps(package_versions, indent=2),
)

map_path = Path(environment.get("MOLA_LOAD_MM", ""))
if not map_path.is_file():
    raise RuntimeError(f"active MOLA map missing: {map_path}")
backup_map = BACKUP / "map" / map_path.name
copy_file(map_path, backup_map)
map_manifest = {
    "source": str(map_path),
    "backup": str(backup_map),
    "size": map_path.stat().st_size,
    "sha256_source": sha256(map_path),
    "sha256_backup": sha256(backup_map),
}
write(BACKUP / "map" / "map_manifest.json", json.dumps(map_manifest, indent=2))
copy_file(
    HOME / "robot_backups/tf_budget_20260916/p2plane/icplog_layers.txt",
    BACKUP / "map" / "map_layer_class_evidence.txt",
)

navigation_candidates = set()
for pattern in (
    "/opt/ros/humble/lib/libnav2*.so*",
    "/opt/ros/humble/lib/nav2_*/*",
    "/opt/ros/humble/share/nav2_*/*.xml",
    "/opt/ros/humble/share/nav2_*/*.yaml",
    "/opt/ros/humble/share/nav2_*/*.yml",
    "/opt/ros/humble/share/nav2_*/launch/*.py",
):
    import glob

    navigation_candidates.update(Path(item) for item in glob.glob(pattern))

for root in (
    HOME / "omnifleet_t2_ws/src",
    HOME / "omnifleet_t2_ws/install",
    HOME / "omnifleet_ws/src/system/omnifleet_bringup",
    HOME / "omnifleet_ws/install/omnifleet_bringup",
    HOME / "omnifleet_fleet",
):
    if not root.exists():
        continue
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        lower = str(path).lower()
        if any(
            token in lower
            for token in (
                "nav2",
                "navigation",
                "continuous_route",
                "output_gate",
                "safety",
                "waypoint",
                "msc",
                "scoped.launch",
            )
        ):
            navigation_candidates.add(path)

for pattern in (
    "/etc/zenoh/**/*",
    "/etc/omnifleet_msc/**/*",
    "/home/iecme/.config/zenoh/**/*",
):
    import glob

    navigation_candidates.update(Path(item) for item in glob.glob(pattern, recursive=True))

navigation_files = []
for path in sorted(navigation_candidates):
    try:
        if not path.is_file():
            continue
        navigation_files.append(
            {
                "path": str(path),
                "realpath": str(path.resolve()),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    except (FileNotFoundError, PermissionError):
        continue

nav_packages = [
    "nav2_controller",
    "nav2_planner",
    "nav2_bt_navigator",
    "nav2_costmap_2d",
    "nav2_map_server",
    "nav2_lifecycle_manager",
    "omnifleet_navigation_policy",
    "omnifleet_waypoint_ui",
    "omnifleet_msc",
]
package_prefixes = {}
for package in nav_packages:
    result = run(["ros2", "pkg", "prefix", package], check=False)
    package_prefixes[package] = result.stdout.strip() if result.returncode == 0 else None

nav_manifest = {
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "ros_domain_id": environment.get("ROS_DOMAIN_ID"),
    "rmw_implementation": environment.get("RMW_IMPLEMENTATION"),
    "package_prefixes": package_prefixes,
    "files": navigation_files,
}
nav_root = BACKUP / "navigation_frozen_manifest"
write(nav_root / "NAVIGATION_FROZEN_MANIFEST.json", json.dumps(nav_manifest, indent=2))
nav_md = [
    "# NAVIGATION FROZEN MANIFEST",
    "",
    f"- ROS_DOMAIN_ID: `{nav_manifest['ros_domain_id']}`",
    f"- RMW_IMPLEMENTATION: `{nav_manifest['rmw_implementation']}`",
    f"- Hashed files: {len(navigation_files)}",
    "",
    "## Package prefixes",
    "",
]
nav_md += [f"- `{key}`: `{value}`" for key, value in package_prefixes.items()]
nav_md += ["", "The JSON file is the canonical before-switch manifest."]
write(nav_root / "NAVIGATION_FROZEN_MANIFEST.md", "\n".join(nav_md) + "\n")

backup_manifest = {
    "backup": str(BACKUP),
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "mola_pid": mola_pid,
    "command": cmdline,
    "active_unit": unit,
    "active_operation": status.get("operation"),
    "source_install": str(source_install),
    "backup_install": str(backup_install),
    "install_file_count": len(install_files),
    "loaded_library_count": len(runtime_libraries),
    "copied_configs": copied_configs,
    "map": map_manifest,
}
write(
    BACKUP / "CURRENT_MOLA_BACKUP_MANIFEST.json",
    json.dumps(backup_manifest, indent=2),
)
manifest_md = [
    "# CURRENT MOLA BACKUP MANIFEST",
    "",
    f"- Backup: `{BACKUP}`",
    f"- MOLA PID captured: `{mola_pid}`",
    f"- Active unit: `{unit}`",
    f"- Runtime install copied with symlinks dereferenced: `{backup_install}`",
    f"- Runtime files: `{len(install_files)}`",
    f"- Loaded key libraries recorded: `{len(runtime_libraries)}`",
    f"- Map SHA256: `{map_manifest['sha256_source']}`",
    f"- Navigation frozen files: `{len(navigation_files)}`",
    "",
    "Rollback does not depend on downloading the old release.",
]
write(BACKUP / "CURRENT_MOLA_BACKUP_MANIFEST.md", "\n".join(manifest_md) + "\n")
write(HOME / "robot_backups" / "mola_before_latest_CURRENT", str(BACKUP) + "\n")
print(BACKUP)
