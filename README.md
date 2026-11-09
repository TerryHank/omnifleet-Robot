# OmniFleet 单车工作区

- `robot` 以原单车仓库的默认分支为基础，包含车端导航、定位、感知和底盘。
- [`main` 分支](https://github.com/TerryHank/omnifleet_ws/tree/main) 提供中央 RMF 调度、编队和 Web。
- [车端身份广播](src/system/omnifleet_fleet/README.omnifleet.md#车端身份广播) 提供接入中央调度的安装步骤。
- [126 号车底盘备份](backups/robot-126/chassis/README.md) 包含该车驱动、STM32 固件和部署配置。按备份说明恢复 126 的驱动，常规工作区构建使用 `src/vehicle/` 中的驱动。
- [104 号车快照](https://github.com/TerryHank/omnifleet_ws/tree/archive/omnifleet-Robot/104) 保留为独立历史分支。

# Robot 113 source snapshot

Tag: `robot113-source-20261021-015022`. Source: `iecme@192.168.3.113:/home/iecme/omnifleet_ws`.
Snapshot completed (Asia/Shanghai): 2026-10-21T01:50:22.139474+08:00.

The tag contains the complete original snapshot. The source layout is retained under `src/`, alongside workspace `env.bash`.
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
git fetch origin tag robot113-source-20261021-015022
git switch --detach robot113-source-20261021-015022
```

After checking out this tag, start at `src/planning/omnifleet_planner/behavior_trees/` and `src/control/omnifleet_local_navigation/`.
MOLA is under `src/localization/omnifleet_mola/`; MSC under `src/system/omnifleet_msc/`.

Archive SHA256: `ce8f311f95d3e83bf9f13f58b882f1dffd4e45a23f79e5671e0cf0170c2a81e9`.
