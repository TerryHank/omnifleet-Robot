#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

p = Path("/home/iecme/omnifleet_ws/src/system/workspace_support/mola_latest_20260917_ws/manifests/MOLA_LATEST_SOURCE_MANIFEST.json")
d = json.loads(p.read_text())
root = Path("/home/iecme/omnifleet_ws/src/localization/omnifleet_mola")
for repo in d["repositories"]:
    checkout = root / repo["repo"]
    if (checkout / ".git").exists():
        repo["submodules"] = subprocess.run(
            ["git", "-C", str(checkout), "submodule", "status", "--recursive"],
            text=True, capture_output=True
        ).stdout.splitlines()
d["external_build_dependencies"] = {
    "pmc": {
        "commit": "4bbd40ababd8e925c4e1845c509173afe766b443",
        "source": "official CMake pin",
    },
    "xenium": {
        "commit": "1c449ae953ce2a440b0d16c5ed1181d2754860ab",
        "source": "main resolved and frozen at build time",
    },
}
p.write_text(json.dumps(d, indent=2) + "\n")

md = Path("/home/iecme/omnifleet_ws/src/system/workspace_support/mola_latest_20260917_ws/manifests/MOLA_LATEST_SOURCE_MANIFEST.md")
base = md.read_text().split("\n## Fixed submodules and external dependencies", 1)[0].rstrip()
lines = [base, "", "## Fixed submodules and external dependencies", ""]
for repo in d["repositories"]:
    for s in repo.get("submodules", []):
        lines.append(f"- {repo['repo']}: `{s}`")
lines += [
    "- PMC: `4bbd40ababd8e925c4e1845c509173afe766b443`",
    "- Xenium: `1c449ae953ce2a440b0d16c5ed1181d2754860ab`",
]
md.write_text("\n".join(lines) + "\n")
