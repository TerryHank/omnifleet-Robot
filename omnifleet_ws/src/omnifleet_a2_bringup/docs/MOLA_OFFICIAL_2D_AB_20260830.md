# MOLA 官方二维输出 A/B（2026-08-30）

所有测试均在独立 ROS 域中回放实车 Airy 点云，只回放
`/rslidar_points` 和 `/tf_static`，避免生产 `/tf` 污染结果；未发送导航目标、
速度或舵角命令。

## 第一轮：未启用 StateEstimationSmoother

同一份 14.43 秒输入包以 0.4 倍速回放。

| 指标 | 现有 MOLA + 平面适配 | MOLA 官方 LO 直接输出 |
| --- | ---: | ---: |
| 样本 | 80 | 81 |
| 最大消息间隔 | 0.3002 s | 0.3002 s |
| 最大绝对 z | 0 | 0.02022 m |
| 最大绝对 roll | 0 | 0.00926 rad |
| 最大绝对 pitch | 0 | 0.00292 rad |
| 地图 frame | `map` | `odom` |
| 位姿 TF | `odom->base_link`，平面、唯一 | `odom->base_link`，含相同 3D 残差、唯一 |

## 第二轮：安装并启用官方 StateEstimationSmoother

远端通过 ROS 2 Humble 软件源安装：

- `ros-humble-mola-state-estimation-smoother=2.4.2-1jammy.20260804.210906`
- `ros-humble-mola-gtsam-factors=2.4.2-1jammy.20260731.185737`

同一份新录制的 17.43 秒 Airy 输入包以 0.4 倍速分别回放。Smoother 使用
官方 `use_state_estimator:=True` 与 `enforce_planar_motion:=True`；纯里程计场景
按官方参数说明设置 `MOLA_LINK_FIRST_POSE_SIGMA=1e-6`。

| 指标 | 现有 MOLA + 平面适配 | 官方 Smoother |
| --- | ---: | ---: |
| 位姿样本 | 159 | 395 |
| 输出话题 | `/odom` | `/state_estimation/pose` |
| 输出 frame | `odom -> base_link` | `map -> base_link` |
| 平均消息间隔 | 约 0.100 s | 0.10009 s |
| 最大消息间隔 | 0.10270 s | 0.10092 s |
| 最大绝对 z | 0 | 0 |
| 最大绝对 roll | 0 | 0 |
| 最大绝对 pitch | 0 | 0 |
| 地图 frame | `map` | `map` |

## 结论

官方 Smoother 已安装且 `enforce_planar_motion` 确实生效，二维精度与连续性
通过测试。但是它遵循 MOLA 官方的直接模式，发布 `map -> base_link` 和
`/state_estimation/pose`，不生成本车当前 Nav2 基线使用的 `/odom` 与
`map -> odom -> base_link` REP-105 链。

上述结论只适用于 Smoother 直接输出方式。生产主线随后改用 MOLA 官方
Simple + REP-105：底盘驱动发布 `/odom` 与 `odom -> base_link`，MOLA BridgeROS2
读取该 TF 并独占发布 `map -> odom`。因此不再需要 `mola_odom_adapter`，也不再
需要静态 `map -> odom`。
