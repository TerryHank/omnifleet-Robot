# MOLA 功能与参数迁移对照

状态：机器人和本地参考树已将 MOLA 相关包归入 `localization/omnifleet_mola/<包名>`；机器人根目录扫描为 68 个唯一包名。分组后的 68 包全量构建和路径相关 `omnifleet_localization` 回归通过，16 个服务已恢复。全量 676 项测试中仍有 20 项 lint/copyright failure，均在三个既有驱动包；回放、地图导出/重载和重定位工具证据来自分组前验收，未在本次路径调整后重复。细节见 `ROBOT_ACCEPTANCE_REPORT.md`。

## 包覆盖

| 包 | 旧版 | 新版基准 | 处理 | 仅见于旧快照的文件 |
|---|---|---|---|---|
| kitti_metrics_eval | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_academic_datasets | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_bridge_ros2 | 3.2.0 | 3.2.1 | 新版实现，补齐旧接口 | 0 |
| mola_common | 0.6.1 | 0.6.1 | 之前字节相同，继续共享 | 0 |
| mola_demos | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_georeferencing | 2.4.2 | 2.4.2 | 之前字节相同，继续共享 | 0 |
| mola_gtsam_factors | 2.4.2 | 2.4.2 | 新版实现优先；缺失 API 的历史测试归档 | 2 |
| mola_imu_preintegration | 1.17.1 | 2.0.0 | 新版实现优先 | 0 |
| mola_input_euroc_dataset | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_input_kitti360_dataset | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_input_kitti_dataset | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_input_lidar_bin_dataset | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_input_mulran_dataset | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_input_paris_luco_dataset | 3.0.0 | 3.0.0 | 之前字节相同，继续共享 | 0 |
| mola_input_rawlog | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_input_rosbag2 | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_input_video | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_kernel | 3.2.0 | 3.2.1 | 新版实现，补齐旧接口 | 0 |
| mola_launcher | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_lidar_odometry | 3.2.0 | 3.2.0 | 新版实现优先 | 0 |
| mola_metric_maps | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_msgs | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_pose_list | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_relocalization | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_sm_loop_closure | 无 | 1.2.2 | 新版新增包保留 | 0 |
| mola_state_estimation | 2.4.2 | 2.4.2 | 之前字节相同，继续共享 | 0 |
| mola_state_estimation_simple | 2.4.2 | 2.4.2 | 之前字节相同，继续共享 | 0 |
| mola_state_estimation_smoother | 2.4.2 | 2.4.2 | 新版实现，补齐旧接口 | 10 |
| mola_test_datasets | 无 | 0.5.0 | 新版新增包保留 | 0 |
| mola_traj_tools | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_viz | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_viz_imgui | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mola_yaml | 3.2.0 | 3.2.1 | 新版实现优先 | 0 |
| mp2p_icp | 2.13.1 | 2.14.1 | 新版实现优先 | 0 |
| mp2p_icp_core | 2.13.1 | 2.14.1 | 新版实现优先 | 0 |
| mp2p_icp_viz | 2.13.1 | 2.14.1 | 新版实现优先 | 0 |

## 功能验收矩阵

| 功能 | 候选处理 | 验收证据或门槛 |
|---|---|---|
| 估计速度及 6×6 协方差 | LocalizationUpdate 可选字段；smoother `publish_twist` 默认 false，实验 `smoother_direct` 显式开启 | 68 包 C++ 构建通过；MOLA 定向回归 20 项通过；桥接速度/协方差回归见 `evidence/bridge_twist_regression.json` |
| 直接 map→odom | 从估计器图变量发布；源帧与输出 child 分离；默认关闭 | 禁用/启用/child 覆盖/未知源帧测试通过；运行中 map TF owner 唯一 |
| 新鲜轮速优先 | 时间有效时速度和协方差整体采用轮速；过期/提前超过 0.1s 回退估计；拒绝缓存时间倒退 | C++ 测试覆盖零值、估计、轮速、0.5s/-0.1s 边界和过期回退；桥接回归通过 |
| IMU 采集时间 | ROS bridge 保留输入时间戳的时钟来源，避免不同 ROS clock type 相减 | bridge 重建、odometry 回归和静止传感器采样通过 |
| 新版地图输出 | 保留独立 map executor、流式点云 SensorDataQoS 和导航全程 deskew | 23 帧录包回放、原生地图保存/重载、实时传感器和 500x500 地图导出通过 |
| 生产及四个实验 profile | `simple_direct` / `simple_direct_observation` / `simple_rep105` / `smoother_direct` 保留；加载统一 latest 环境 | 脚本与配置检查通过；机器人生产 `simple_direct` 在线，smoother direct TF 与静态/运动 georeferencing 集成通过 |
| ROS namespace/TF | 保留新版 `robot_113` 输出重映射与 fleet_scope；旧未命名空间的测试预期已更新 | 实时订阅与命名空间通过；map→base_link 只有一个 MOLA owner |
| 数据集/地图导入导出/GNSS/GUI工具 | 35 个旧包全部有新版对应，保留新版新包；脚本和服务采用新版 | 68 包构建、MOLA 定向回归 20 项、原生地图重载和 PGM/YAML 导出、静态/运动 georeferencing 通过；GUI 与全部数据集未逐一实测。全量测试仍有 20 项 vendor lint/copyright failures，见机器人验收报告 |
| 诊断及线程处理 | 新版 CallbackTrace、地图线程和安全退出优先；不恢复旧绝对路径 causal_trace 头文件或默认 crash 前缀 | 全部已注册包测试通过；未单独执行长时间 GUI/线程压力测试 |
| 旧测试 | 有效 map→odom 测试已注册并通过；GTSAM IMU helper 测试引用缺失头文件，移除无效注册；共 11 个不适用历史测试保存在外部归档和 Git 历史 | 依据 CMake 注册和实际测试结果判断，不把未注册测试当成功能证据；全量 676 项结果中剩余 20 项均为三个驱动包的 lint/copyright 检查 |

## 参数链

| 参数 | 环境变量 | 默认 | 消费端 |
|---|---|---|---|
| publish_twist | MOLA_STATE_ESTIMATOR_PUBLISH_TWIST | false | smoother Parameters → spinOnce → LocalizationUpdate → bridge |
| publish_map_to_odom_tf | MOLA_PUBLISH_MAP_TO_ODOM_TF | false | smoother Parameters → publishMapToOdom → bridge source routing |
| map_to_odom_frame_name | MOLA_MAP_TO_ODOM_FRAME | 空 | smoother 源 odometry frame |
| map_to_odom_child_frame | MOLA_MAP_TO_ODOM_CHILD_FRAME | 空，回落到源帧 | smoother 输出 child frame |
| publish_twist_from_latest_odometry | MOLA_PUBLISH_TWIST_FROM_LATEST_ODOM | false | bridge callback cache → OdometryTwist |
| latest_odom_twist_source | MOLA_LATEST_ODOM_TWIST_SOURCE | wheel_odom | bridge 按 sensor label 选择源 |
| latest_odom_twist_max_age | MOLA_LATEST_ODOM_TWIST_MAX_AGE | 0.5 秒 | bridge 按 ROS clock 判定年龄 |

冲突参数和既有算法采用新版。参数差异完整清单见 PARAMETER_DIFF.tsv；文件差异见 SOURCE_DIFF_INVENTORY.tsv。
物理标定、IMU 量纲及当前新版性能调节参数保持现有值，不把旧默认值重新覆盖到新版。
