# Unified MOLA source and robot acceptance

Status: post-grouping build and functional runtime checks passed on 2026-10-06.
The 39 MOLA-related ROS packages are under
`localization/omnifleet_mola/<package>`; the local MOLA metadata directory is
`localization/omnifleet_mola/mola_source_metadata`. The full robot workspace has
68 packages with 68 unique names and installs to
`/home/iecme/omnifleet_ws/install`.

The clean 68-package build passed. Full colcon testing reported 676 tests, 0
errors, 20 lint/copyright failures, and 0 skipped. All failures are confined to
the existing driver packages `ros_robot_controller`, `ros_robot_controller_msgs`,
and `rslidar_msg`; the two `omnifleet_localization` path tests pass after their
workspace-root calculation was updated for the group directory. See
[ROBOT_ACCEPTANCE_REPORT.md](ROBOT_ACCEPTANCE_REPORT.md) for runtime evidence.

## Source and runtime behavior

The latest implementation and parameters are the baseline. The migration keeps
the old-only optional odometry twist/covariance output, smoother direct
`map -> odom` publication, and bridge wheel-source selection. These features
remain opt-in. Existing production parameter values were compared with the
robot snapshot and preserved. See
[FEATURE_PARAMETER_MATRIX.md](FEATURE_PARAMETER_MATRIX.md).

`latest_env.bash` clears inherited MOLA module paths before setting the canonical
installed package paths. The launcher gives `MOLA_MODULES_LIB_PATH` precedence
over its build-time module path so a deployment cannot load duplicate modules
from an archived build tree. The production service environment and its
systemd loader-path drop-in are versioned here as `robot_mola_env.bash` and
`24-unified-mola-module-path.conf`.

## Validation summary

- Source layout: 68 active package names, 68 unique; all 39 MOLA-related ROS
  packages are under the single group directory.
- Robot build: all 68 packages built successfully after grouping.
- MOLA targeted regression matrix: 20/20 gates passed before grouping; the
  post-group full suite has no functional package failures.
- Full colcon suite: 676 tests, 0 errors, 20 lint/copyright failures, 0 skipped;
  failures are confined to the three driver packages listed above.
- Replay: 2,025 MOLA registrations, zero ICP rejects, 0.78% dropped frames,
  finite timestamped poses/covariance (recorded before the path-only regrouping).
- Post-group stationary live probe: 81 finite odometry samples over eight
  seconds, zero endpoint displacement, and no `/robot_113/msc/nav_cmd_vel`
  samples.
- Map export/reload and relocalizer smoke test passed before regrouping.
- Runtime: all 16 Omnifleet services are active; no chassis motion command was
  sent.

