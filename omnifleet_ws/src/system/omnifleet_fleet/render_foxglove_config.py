#!/usr/bin/env python3
"""Render a Foxglove bridge parameter file from the robot identity."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path


ROBOT_ID_RE = re.compile(r"^robot_[a-z0-9][a-z0-9_-]*$")
TOP_LEVEL_KEY_RE = re.compile(r"(?m)^(/\*\*|[A-Za-z][A-Za-z0-9_]*)\s*:\s*$")
ROBOT_TOKEN_RE = re.compile(r"\brobot_[a-z0-9][a-z0-9_-]*\b")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    robot_id = os.environ.get("OMNIFLEET_ROBOT_ID", "")
    if not ROBOT_ID_RE.fullmatch(robot_id):
        raise SystemExit(f"invalid OMNIFLEET_ROBOT_ID: {robot_id!r}")

    text = args.source.read_text(encoding="utf-8")
    match = TOP_LEVEL_KEY_RE.search(text)
    if not match:
        raise SystemExit(f"no top-level Foxglove parameter key in {args.source}")

    source_id = match.group(1)
    rendered = text.replace(source_id, "/**", 1)
    remaining = sorted(set(ROBOT_TOKEN_RE.findall(rendered)))
    if remaining:
        raise SystemExit(
            "Foxglove config contains another robot identity after rendering: "
            + ", ".join(remaining)
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=args.output.parent, delete=False
    ) as tmp:
        tmp.write(rendered)
        tmp.flush()
        os.fsync(tmp.fileno())
        temporary = Path(tmp.name)
    temporary.chmod(0o644)
    temporary.replace(args.output)
    print(f"{args.output}: {source_id} -> {robot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
