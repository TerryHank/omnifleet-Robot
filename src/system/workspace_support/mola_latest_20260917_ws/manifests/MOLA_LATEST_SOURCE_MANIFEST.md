# MOLA LATEST SOURCE MANIFEST

Selection: latest stable official tags, anchored at mola 3.2.1; no random develop HEADs.

| Repository | Tag | Commit | Date |
|---|---:|---|---|
| mola | 3.2.1 | `3de167ad809112fcc34097f97071e5b25e2c3a87` | 2026-09-15T19:53:36+02:00 |
| mola_common | 0.6.1 | `d25cf0b4950c47039234586d6dd3e15e6d6f0be0` | 2026-05-17T22:50:02+02:00 |
| mp2p_icp | 2.14.1 | `e41bac069b1e63fbae12b62957edba6363d61e1f` | 2026-09-15T21:01:11+02:00 |
| mola_lidar_odometry | 3.2.0 | `7267828daf83eef47754fc35757a326fef8cb4bf` | 2026-08-21T15:29:54+02:00 |
| mola_state_estimation | 2.4.2 | `c59a3de2cfb4b15985fbe5bce37970e5c465086e` | 2026-06-04T01:02:44+02:00 |
| mola_imu_preintegration | 2.0.0 | `054edd88944cfe582bc752b183163dd2480d39eb` | 2026-09-05T00:18:08+02:00 |
| mola_sm_loop_closure | 1.2.2 | `cc6f30fdc2acb98315c0a10048d2fd40ccc55011` | 2026-06-17T00:00:23+02:00 |
| mola_test_datasets | 0.5.0 | `3d1d930219b8b1187a8d19a4cd70b85258d34308` | 2026-06-16T20:39:15+02:00 |
| mola_academic_datasets | 3.0.0 | `29b0aabc1e2c28722af73bf375d97808a4fbd18a` | 2026-05-12T12:44:43+02:00 |

The build and tests determine whether this stable-tag combination is mutually compatible.

## Fixed submodules and external dependencies

- mola: ` bd14e6830a1474fed9d2d03f5c3b0683d818d540 mola_metric_maps/3rdparty/robin-map (v1.4.1)`
- mola: ` 934c6a5f5ef2355d6df25395d555cb71f790c4e9 mola_viz_imgui/3rdparty/imgui (v1.92.6-docking-28-g934c6a5f5)`
- mola: ` d65a2bef53d32502407de3a4be80f191e2f412d7 mola_viz_imgui/3rdparty/implot (v1.0-6-gd65a2be)`
- mp2p_icp: ` bd14e6830a1474fed9d2d03f5c3b0683d818d540 mp2p_icp_core/3rdparty/robin-map (v1.4.1)`
- mp2p_icp: ` b334d19b667958ed970000073644d911fae17e57 mp2p_icp_viz/3rdparty/imgui (v1.62-7373-gb334d19b6)`
- mola_sm_loop_closure: ` 669fe866b1c612daa3702292571c25dc1bc61c86 third_party/kiss-matcher (v1.0.2-2-g669fe86)`
- mola_sm_loop_closure: ` 64f4096d3010dd569eb0061eaab3b6073428ee8d third_party/robin (v.1.2.7-3-g64f4096)`
- PMC: `4bbd40ababd8e925c4e1845c509173afe766b443`
- Xenium: `1c449ae953ce2a440b0d16c5ed1181d2754860ab`
