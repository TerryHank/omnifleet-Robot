# Robot workspace layout acceptance

Date: 2026-10-06  
Host: `iecme@10.0.0.198` (`iecme-tank`)  
Workspace: `/home/iecme/omnifleet_ws`

## Latest grouping status

The 39 MOLA-related ROS packages are grouped under
`localization/omnifleet_mola`. The local MOLA metadata directory was copied
there as well (302 files, no `package.xml`). Source hashes/modes/symlinks matched
the pre-move manifest, and the root colcon scan found 68 unique package names.

A fresh clean build finished all 68 packages. Full colcon testing reported 676
tests, 0 errors, 20 failures, and 0 skipped. The 20 failures are existing
lint/copyright checks in `ros_robot_controller`, `ros_robot_controller_msgs`,
and `rslidar_msg`; the two MOLA path-dependent tests now pass. All 16 services
are active after restart. An 8-second read-only probe observed 81 finite odometry
samples, zero endpoint displacement, no `/robot_113/msc/nav_cmd_vel` samples,
and a live 500×500 map. No chassis motion command was sent.

The old build/install trees and a rollback script are outside the workspace at
`/home/iecme/robot_backups/workspace_layout_reorg_20261006/mola-grouping-rollback-20261006/`.
Intermediate zero-byte build artifacts and the failed first `mola_viz` CMake
codemodel are also preserved there for diagnosis.

## Final source tree

The ten source category roots now match the local tree and the category pattern
used by Autoware Universe: `common`, `control`, `localization`, `perception`,
`planning`, `sensing`, `simulator`, `system`, `vehicle`, and `visualization`.
ROS package directories sit under their category root. The active MOLA/MP2P
source is under `localization/omnifleet_mola/<package>`; build/install/log output stays under
`.runtime`.

`colcon --log-base /dev/null list --base-paths .` from the workspace root
returned **68 packages with 68 unique package names**. `.runtime/COLCON_IGNORE`
keeps generated build/install files out of recursive package discovery. A raw
`package.xml` scan sees three nested vendor manifests (`rslidar_msg` ROS1/ROS2
alternatives and the embedded KISS matcher); colcon treats them as content under
their existing source package roots, not as additional workspace packages. The
complete 68-package build passed. The installed prefixes for
`mola_lidar_odometry`, `omnifleet_planner`, and `omnifleet_interfaces` all
resolve below `/home/iecme/omnifleet_ws/install`.

## Retired wrappers and duplicate source tree

After the source move, tests, runtime switch, and backup verification, these
non-source wrappers and the former root `log` directory were removed from the
active workspace:

- `fleet_coordinator_ws`
- `hardware_drivers_ws`
- `mola_latest_20260917_ws`
- `omnifleet_t2_mola_experiments_ws`
- `omnifleet_t2_ws`
- `log`

Each old wrapper's `src` contained zero `package.xml` files. The pre-change
workspace archive outside the active tree contains 30,952 entries and has SHA-256
`7f2d561fe0aafcc111c17751b470480ee492e16d576113403ab455286e852748`.

A separate sibling simulation source tree contained duplicate names
`omnifleet_bringup`, `omnifleet_simulator`, and `omnifleet_description`. No active
service or process referred to it. It was moved intact to
`/home/iecme/robot_backups/workspace_layout_reorg_20261006/retired/omnifleet_multi_point_sim_v1.1.1_20260826`.
Its 1,640-entry file/mode/symlink/hash manifest is
`/home/iecme/robot_backups/workspace_layout_reorg_20261006/external-sim-source-retirement-manifest.json`
(SHA-256 `46dbd0cc155c37517fecffa4ee9184c1a08363f4b5ead8aca25c43d2afb175f0`).
`COLCON_IGNORE` markers in the retired project and robot backup root prevent
recursive discovery of archived package copies.

The workspace root's default colcon inventory command created a new generated
`log/latest_list` directory during verification. That inventory log was removed
afterward; use `--log-base .runtime/log` for normal operations or
`--log-base /dev/null` for read-only inventories. The saved build helper was
updated and `bash -n` passed.

## Runtime and test status

- All 16 Omnifleet systemd services are active after the grouping build.
- Service definitions, active process command lines, and process memory maps
  contain no reference to the removed wrapper paths.
- A final package-prefix audit confirmed all active installed package roots are
  under `.runtime/install`.
- The robot MOLA report separates post-group live evidence from earlier replay,
  map export/reload, and relocalizer smoke checks. No chassis motion command was
  issued.
- Full colcon tests reported **676 tests, 0 errors, 20 failures, 0 skipped**.
  The 20 remaining failures are lint/copyright checks in
  `ros_robot_controller`, `ros_robot_controller_msgs`, and `rslidar_msg`; they
  are listed separately from functional acceptance in
  `../mola_migration/ROBOT_ACCEPTANCE_REPORT.md`.

The existing source-path manifests remain historical provenance records. Root
`README.md` and manifests were synchronized from the local reference tree.
