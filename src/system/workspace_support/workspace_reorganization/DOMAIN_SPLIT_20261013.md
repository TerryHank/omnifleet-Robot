# OmniFleet 包内职责拆分交付记录

日期：2026-10-13。主机：iecme@192.168.3.113（iecme-tank）。
工作区：`/home/iecme/omnifleet_ws`。

## 九处原目录的最终职责

所有下列相对路径均位于 `/home/iecme/omnifleet_ws/src`。

| 原目录/包 | 保留入口与最终实现位置 |
| --- | --- |
| system/omnifleet_bringup | system 中保留启动编排、doctor 与旧执行入口；底盘/Rosmaster/raw PWM → vehicle/omnifleet_chassis_driver，摄像头/点云过滤 → sensing/omnifleet_sensor_processing，VR → control/omnifleet_teleop |
| system/omnifleet_fleet | system 中保留运行环境、配置和启动/运维入口；命名空间函数 → common/omnifleet_fleet_common，网关/路由等待 → system/omnifleet_transport/runtime，Foxglove脚本 → visualization/omnifleet_fleet_visualization/runtime，时钟守护 → sensing/omnifleet_sensor_processing/scripts，重定位/崩溃捕获 → localization/omnifleet_relocalization |
| system/omnifleet_fleet_coordinator | node/服务/任务编排保留在 system；纯调度 core → planning/omnifleet_fleet_planning/dispatch_core.py |
| system/omnifleet_fleet_interfaces | 整包 → common/omnifleet_fleet_interfaces；服务类型名不变 |
| system/omnifleet_msc | coordinator/core/CLI 的系统编排保留；协议、存储、指标 → common/omnifleet_fleet_common；编队运动学、轨迹、agent → control/omnifleet_fleet_control；栅格规划、traffic、maneuver、任务队列 → planning/omnifleet_fleet_planning；面板/车辆发现/URDF/录制 → visualization/omnifleet_fleet_visualization；共享地图节点 → map/omnifleet_map_tf_generator/shared_map_node.py |
| system/omnifleet_multi_robot_sim | 整包 → simulator/omnifleet_multi_robot_sim |
| system/omnifleet_tutorials | 整包 → perception/omnifleet_tutorials；31个视觉课程及原包名保留 |
| localization/omnifleet_mola/omnifleet_localization | 包入口 → localization/omnifleet_localization；地形/深度落差 → perception/omnifleet_terrain_analysis；轮滑检测 → vehicle/omnifleet_chassis_driver；原生IMU转换库/适配器 → sensing/omnifleet_sensor_processing |
| localization/omnifleet_mola/omnifleet_t2_mola_experiments | 后端/原包入口 → localization/omnifleet_t2_mola_experiments；deskew/缓冲IMU/点云过滤/速度估计 → sensing/omnifleet_sensor_processing；基座-雷达TF → vehicle/omnifleet_chassis_driver；Foxglove栅格偏移 → visualization/omnifleet_fleet_visualization；导航栅格 → map/omnifleet_map_tf_generator；统一MOLA/Nav2编排与就绪/清理脚本 → system/omnifleet_bringup；Nav2 launch/config → planning/omnifleet_fleet_planning |

留在 system 的是实际系统职责，并非未执行移动。MOLA上游源码容器不再混入上述两个业务包。

## 兼容机制

新增8个独立ROS功能包，修改了对应package.xml依赖、ament Python安装和CMake安装/导出规则。
原Python模块是importlib/sys.modules兼容入口，与新模块是同一个对象；没有复制第二份算法。
跨域原生源码、launch/data及松散部署脚本使用相对符号链接保留原入口。原C++执行入口转发到sensing包；原`omnifleet_localization::omnifleet_sensor_conversions`导出目标继续指向新库，原头文件命名空间保留。
服务、包名、ROS接口、原console_scripts及运动保护逻辑保留。
旧源码树整体移动的5处目录没有保留重复包；拆分完成时colcon发现80个包且80个名称唯一。
原许可声明按源码来源保留，混合来源包记录MIT及Apache-2.0。

## 验证与边界

- 候选及生产路径下17个受影响包构建成功；元数据补充后的6包构建成功。
- 55项源码等价检查通过；Python只改职责对应的导入路径，原生源码/启动脚本内容保留。
- 27个旧模块导入与新模块身份相同，安装后的实现resolve到生产src中的新功能域。
- 28个旧ROS可执行入口存在且可执行；新8包在生产ament索引中可查。
- Airy IMU旋转C++测试通过；MOLA、统一MOLA/Nav2和运动学仿真3个原入口的`--show-args`通过，不启动硬件节点。
- 128项离线契约/MSC回归：118通过；10项失败与拆分前完全相同，新增失败0。
- 另有2个仿真测试因原有布局/脚本缺失，基线和迁移后同样未收集；未用伪造资源或删除断言来制造全通过。
- 失效安装链接为0；源码移动引起的87处生成链接已改指新路径。
- systemctl记录的状态、MainPID与启动时间相同；17个服务active。VR adapter在操作前已failed，本轮不修复其既有故障。

验证结论：**PASS_STATIC / PENDING_LIVE_VALIDATION**。
本轮没有重启服务、运行真实SLAM/导航测试节点或发送运动命令。长驻进程仍保留已加载版本；本轮不宣称重启后、真实传感器或实车导航验收。

## 证据与恢复

完整证据目录：`/home/iecme/robot_backups/domain_split_20261013_134749`。

- `source-before.tar.gz`：九处原目录及原map工具包的完整迁移前源码。
- `runtime-before.tar.gz`、`build-before/`：涉及包的原build/install及移动前构建缓存。
- `manifest.json`、`deployment.json`：源码移动、兼容入口、变更文件和生成链接。
- `packages-before.tsv`、`packages-after.tsv`：72→80唯一包发现记录。
- `candidate-build.log`、`production-build.log`、`metadata-build.log`：构建证据。
- `candidate-source-verification.json`、`production-source-verification.json`、`installation-verification.json`：等价、安装、接口、服务连续性。
- `before-tests.xml`、`candidate-tests.xml`、`production-tests.xml`：同一离线回归的迁移前后记录。
- 原`config/production_hashes.sha256`保留为历史清单；当前规范实现的哈希另存`localization/omnifleet_t2_mola_experiments/config/domain_split_hashes.sha256`。

恢复前需先核对本轮之后的修改。按manifest恢复原目录结构，再恢复涉及包的build/install或重新构建；不要把源代码恢复当作运行时恢复，也不要整树覆盖其他包。

## 最终引用适配复核

在源码抽取之外，补充适配16处当前引用文件：系统Coordinator/Core/CLI与任务Node直接引用新功能域；原ROS执行脚本直接导入新实现；Foxglove导航重启助手改用system/omnifleet_bringup中的cleanup实现；MOLA校验脚本使用新定位业务包路径，并对历史清单做路径映射；仿真测试的description路径归入vehicle。

最后一次可执行代码/systemd引用审计中，移走的5处包目录没有遗留当前文件访问。仅MOLA校验脚本的2个历史路径翻译字典键保留旧字符串，这是历史manifest解析规则。

引用适配后的4个关联包再次构建成功。128项离线回归仍为118通过、原有10失败，新增失败0。27个旧模块和28个旧ROS执行入口仍通过；服务状态/PID/启动时间仍与迁移前一致。

原C++导出目标另通过独立下游消费验证：`find_package(omnifleet_localization)`、旧头文件include、链接`omnifleet_localization::omnifleet_sensor_conversions`、调用旋转函数均通过。记录在`legacy-cpp-probe.log`。

补充引用变更备份：`reference-before/`。文件和哈希清单：`reference-adaptation.json`。最终审计：`final-reference-audit.log`。本轮只交付上述九处目录的职责拆分与引用适配，后端安装/试运行不属于这份交付结论。
