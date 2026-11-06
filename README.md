# Robot 104 source snapshot

Tag: `robot104-source-20261106-235759`. Source: `iecme@192.168.3.104:/home/iecme/omnifleet_ws`.
Snapshot completed (Asia/Shanghai): 2026-11-06T23:57:59.662348+08:00.

Branch `104` contains this current vehicle source snapshot. Branch `main` retains the existing Robot 113 snapshot. The source layout is retained under `src/`, alongside workspace `env.bash`.
Linux symlinks and executable flags are retained in Git. Windows checkouts can represent symlinks as text; use Linux for restoration.

## Included

Current source/configuration selected from the canonical workspace, plus `env.bash`.
See `BACKUP_MANIFEST.json` for per-file SHA256, modes, symbolic-link targets, exclusions, and redactions.

## Excluded / separate restore requirements

Build/install/log, nested Git histories, dependency caches, virtual environments, node_modules,
desktop distribution binaries, archives, model weights, maps outside src, recordings, credentials,
and historical backup copies. External systemd/configuration, model/map assets and runtime state must be backed up separately.
Some configuration secret values have been replaced with `REDACTED_BACKUP_SECRET`; provision real secrets outside Git.

This is a source backup, not an image of the robot or evidence that rebuilding and real-robot navigation pass.

## Reading

```bash
git fetch origin tag robot104-source-20261106-235759
git switch --detach robot104-source-20261106-235759
```

After checking out this tag, start at `src/planning/omnifleet_planner/behavior_trees/` and `src/control/omnifleet_local_navigation/`.
MOLA is under `src/localization/omnifleet_mola/`; The chassis driver is under `src/vehicle/huaner_driver/`.

Archive SHA256: `0a38566f589f5160d62fe76763695cb0adbad0ff0de6e3c76863848639d1947b`.
