# Robot MOLA grouping and runtime acceptance

Date: 2026-10-06  
Host: `iecme@10.0.0.198` (`iecme-tank`)  
Status: **BUILD AND FUNCTIONAL RUNTIME PASS; 20 FULL-SUITE LINT/COPYRIGHT FAILURES REMAIN**

## Source grouping

- The 39 MOLA-related ROS packages now live under
  `/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/<package>`. The group root
  has no `package.xml`, so each ROS package remains independently discoverable.
- The local MOLA source metadata directory is grouped under
  `localization/omnifleet_mola/mola_source_metadata`; its 302 files were copied
  to the robot and SHA-256 checked. It contains no `package.xml`.
- A pre-move manifest covered all 39 robot package roots, 1,983 files, and
  186,080,568 bytes. The post-move tree matched file hashes, modes, and symlink
  targets. The manifest is outside the workspace at
  `/home/iecme/robot_backups/workspace_layout_reorg_20261006/mola-grouping-rollback-20261006/mola-group-source-before.json`
  (SHA-256 `bcd96fac18e5081369a8a281655fa980f7acac27f87996be036a7bc3bd892d26`).
- `colcon --log-base /dev/null list --base-paths .` reports **68 package names,
  68 unique**. All 68 install roots exist under `.runtime/install`.
- 160 source links in `.runtime/install` point into the new group; the final
  audit found no broken links or stale direct `localization/mola_*` targets.
- Two `omnifleet_localization` tests were adjusted to compute the workspace root
  across the new directory level. The MOLA production hash manifest path was
  updated. Runtime algorithms and parameter values were not changed.

## Build and tests

- The full clean build finished all 68 packages successfully.
- MOLA module discovery passed with `mola-cli --list-modules` (exit code 0).
- Full colcon tests: **676 tests, 0 errors, 20 failures, 0 skipped**. All 20
  failures are existing lint/copyright checks in `ros_robot_controller`,
  `ros_robot_controller_msgs`, and `rslidar_msg`. The two path-dependent
  `omnifleet_localization` tests pass after the directory-depth adjustment.
- Prefix checks passed for `mola_lidar_odometry`, `omnifleet_localization`,
  `omnifleet_t2_mola_experiments`, `omnifleet_interfaces`, and
  `omnifleet_navigation_interfaces` under `/home/iecme/omnifleet_ws/install`.
- During recovery from the interrupted build, three zero-byte CMake export files
  were reinstalled, and seven zero-byte object/library/header artifacts for
  `mola_state_estimation_simple` were preserved outside the workspace and
  regenerated. The old pre-group build/install trees remain in the rollback
  directory.

## Runtime check

- All 16 Omnifleet services are active after the rebuild; the temporary runtime
  masks have been removed.
- Live ROS discovery showed MOLA, Nav2 controller/planner/lifecycle nodes, the
  robot driver, and the MOLA map-grid node.
- An eight-second read-only probe received 81 finite odometry samples with zero
  endpoint displacement, no `/robot_113/msc/nav_cmd_vel` samples, and a live
  500×500 occupancy map at 0.1 m resolution.
- No chassis motion command was issued.

## Recovery and limits

The previous build/install trees, interrupted build logs, and rollback script are
outside the active workspace at
`/home/iecme/robot_backups/workspace_layout_reorg_20261006/mola-grouping-rollback-20261006/`.
The old MOLA 3.2 workspace archive remains separately recorded in
`ROBOT_RETIREMENT_RECORD.json`.

The full suite still reports the 20 listed lint/copyright failures. Replay,
map export/reload, and relocalizer smoke evidence was collected before this
directory-only regrouping and was not repeated afterward; the fresh build,
package tests, module discovery, and stationary live probe were repeated.
