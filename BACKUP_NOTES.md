# OmniFleet WSL backup — 2026-10-29

Source: `/home/zhangwnag/workspaces/omnifleet_ws` (Ubuntu-22.04).

This private repository is a source and saved-business-data snapshot, not a full WSL disk image. The original workspace was not modified. The nested rmf-web working tree is included as ordinary files, including local modifications and untracked source; its Git history is not embedded. Upstream revision is recorded in BACKUP_MANIFEST.json.

Included: source, configuration, deployment scripts, project documentation, existing backups, data/missions, data/alignment, fleet_alignment.json, robot_names.json, and shared_costmap.json.

Excluded: build/install/log, node_modules, virtual environments, caches, active IPC and session tokens, browser profiles, RMF/Web databases, telemetry and historical evidence directories, and private-key files (including the upstream test.key fixture). Dashboard .env contains build flags and local service URLs, and is preserved.

BACKUP_MANIFEST.json records the original included files and SHA-256 values. The backup root .gitignore intentionally replaces the source version so saved mission/alignment files can be tracked. One relative .pylintrc symlink is backed up as resolved file content; its link target is recorded.

## Restore

Clone into a new ROS 2 Humble workspace on Ubuntu 22.04. Install dependencies from package.xml, Python requirements and frontend lockfiles; rebuild with colcon. The Web runtime and deployed static frontend must be rebuilt separately. Deployment scripts currently contain the original absolute workspace path; adapt those paths if restoring elsewhere. User systemd service definitions are supplied under the source deployment directories; external OS packages, Windows Foxglove sources and robot-side software are outside this backup.

Saved maps, alignment and routes describe their captured localization sessions. Existing motion_enabled values are preserved; cloning does not start services. No build, startup or physical-robot acceptance is claimed for this backup.
