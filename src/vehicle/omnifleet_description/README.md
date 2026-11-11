<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# OmniFleet tracked description

Production geometry:

- collision envelope: 0.50 m long x 0.37 m wide x 0.33 m high;
- track-center separation: 0.33 m;
- `base_footprint` remains on the ground plane;
- `base_link` remains 0.075 m above the ground to preserve the verified 113
  Airy and camera extrinsics.

The production model uses primitive collision geometry and does not depend on
the Ackermann mesh assets migrated from 112.
