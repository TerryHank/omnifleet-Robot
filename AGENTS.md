# OmniFleet 126 工作区约定

适用 `/home/iecme/omnifleet_ws`。先读 [本机配置](README.workspace.md) 和 [源码索引](src/README.md)，进入子项目后遵循其 `AGENTS.md`。

## 源码与配置

- 源码按 `src/<功能域>/<包>` 组织，新增包参数放在对应 `config/`。维护 [Nav2 永久参数](src/planning/omnifleet_planner/config/nav2_t2.yaml) 与 [本机导航配置](src/control/omnifleet_local_navigation/config/local-navigation.json) 的实际启动和保存路径。
- 部署前备份并保留本机身份、硬件配置和面板已保存参数。涉及包移动时，先核对兼容导入、执行入口、安装软链接及 CMake、setup、systemd 的消费者，再验证迁移。
- 长期数据放 `/home/iecme/omnifleet_data`。保留模型、地图、录包、视频、标定、源码和回退资料，清理限定在已确认并授权的范围。
- 凭据与业务参数分开。文档、聊天日志和 Git 备份只引用凭据位置。维护包说明时保留上游 README 和许可证。

## 运行与验证

- `local_navigation` 负责底盘控制仲裁，是 `/navigation/cmd_vel_safe` 的唯一发布者。通过现有控制入口处理导航、摇杆和车队请求。
- 服务重启前检查现有任务和运动状态。机器人或舵机运动需明确授权及对应停止路径。
- 验证记录区分源码、构建、运行、离线测试和实车结果。部署后核对实际生效的参数与入口。
