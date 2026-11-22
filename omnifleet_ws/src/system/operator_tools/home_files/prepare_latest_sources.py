#!/usr/bin/env python3
import json
import re
from pathlib import Path
import subprocess


WS = Path("/home/iecme/mola_latest_20260917_ws")
SRC = WS / "src"
MANIFESTS = WS / "manifests"
REPORTS = WS / "reports"
for path in (SRC, MANIFESTS, REPORTS):
    path.mkdir(parents=True, exist_ok=True)

selection = {
    "mola": ("3.2.1", "3de167ad809112fcc34097f97071e5b25e2c3a87"),
    "mola_common": ("0.6.1", "d25cf0b4950c47039234586d6dd3e15e6d6f0be0"),
    "mp2p_icp": ("2.14.1", "e41bac069b1e63fbae12b62957edba6363d61e1f"),
    "mola_lidar_odometry": ("3.2.0", "7267828daf83eef47754fc35757a326fef8cb4bf"),
    "mola_state_estimation": ("2.4.2", "c59a3de2cfb4b15985fbe5bce37970e5c465086e"),
    "mola_imu_preintegration": ("2.0.0", "054edd88944cfe582bc752b183163dd2480d39eb"),
    "mola_sm_loop_closure": ("1.2.2", "cc6f30fdc2acb98315c0a10048d2fd40ccc55011"),
    "mola_test_datasets": ("0.5.0", "3d1d930219b8b1187a8d19a4cd70b85258d34308"),
    "mola_academic_datasets": ("3.0.0", "29b0aabc1e2c28722af73bf375d97808a4fbd18a"),
}


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)


for repo, (tag, expected_sha) in selection.items():
    destination = SRC / repo
    url = f"https://github.com/MOLAorg/{repo}.git"
    if not (destination / ".git").exists():
        run(
            [
                "git",
                "clone",
                "--quiet",
                "--recursive",
                "--branch",
                tag,
                "--depth",
                "1",
                url,
                str(destination),
            ]
        )
    actual_sha = run(["git", "rev-parse", "HEAD"], destination).stdout.strip()
    if actual_sha != expected_sha:
        raise RuntimeError(f"{repo}: expected {expected_sha}, got {actual_sha}")

entries = []
for repo, (tag, expected_sha) in selection.items():
    destination = SRC / repo
    commit = run(
        ["git", "show", "-s", "--format=%H%n%cI%n%s", "HEAD"], destination
    ).stdout.splitlines()
    submodules = run(
        ["git", "submodule", "status", "--recursive"], destination
    ).stdout.splitlines()
    packages = []
    for package_xml in destination.rglob("package.xml"):
        text = package_xml.read_text(errors="replace")
        name = re.search(r"<name>([^<]+)</name>", text)
        version = re.search(r"<version>([^<]+)</version>", text)
        packages.append(
            {
                "path": str(package_xml.relative_to(destination)),
                "name": name.group(1) if name else None,
                "version": version.group(1) if version else None,
            }
        )
    entries.append(
        {
            "repo": repo,
            "url": f"https://github.com/MOLAorg/{repo}.git",
            "tag": tag,
            "branch": None,
            "commit": commit[0],
            "commit_date": commit[1],
            "subject": commit[2],
            "packages": sorted(packages, key=lambda item: item["path"]),
            "submodules": submodules,
        }
    )

manifest = {
    "selection_policy": (
        "latest stable semantic-version tag per official repository as of 2026-09-17; "
        "no develop HEAD; compatibility validated by one isolated colcon graph/build/test"
    ),
    "mola_core_anchor": "mola 3.2.1",
    "repositories": entries,
}
(MANIFESTS / "MOLA_LATEST_SOURCE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)

lines = [
    "# MOLA LATEST SOURCE MANIFEST",
    "",
    "Selection: latest stable official tags, anchored at mola 3.2.1; no random develop HEADs.",
    "",
    "| Repository | Tag | Commit | Date |",
    "|---|---:|---|---|",
]
for item in entries:
    lines.append(
        f"| {item['repo']} | {item['tag']} | `{item['commit']}` | {item['commit_date']} |"
    )
lines += [
    "",
    "The build and tests determine whether this stable-tag combination is mutually compatible.",
]
(MANIFESTS / "MOLA_LATEST_SOURCE_MANIFEST.md").write_text(
    "\n".join(lines) + "\n", encoding="utf-8"
)
print(json.dumps({item["repo"]: item["commit"] for item in entries}, indent=2))
