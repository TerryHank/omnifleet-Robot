> 2026-11-06清理说明：本文提及的 `/home/iecme/robot_backups/` 历史副本已从104删除，不能作为当前可用回退路径；原日期的验证结论仅代表当时状态。

# 本车 ROS 接口与运行入口

104、113 分别使用 ROS_DOMAIN_ID=104、113，车辆身份由 OMNIFLEET_ROBOT_ID 保留。
本车话题、服务、Action、TF 均不加车辆前缀，例如 /map、/tf、/cmd_vel、/navigate_to_pose，坐标系为 map、base_link、rslidar。
安全速度链为 /navigation/nav_cmd_vel → local_navigation → /navigation/cmd_vel_safe → 底盘。
旧 Domain 0 双车网关已退役，旧入口明确拒绝启动，不能把两车裸名话题合并到同一通信域。
Foxglove 使用 /etc/omnifleet_t2/foxglove.yaml 的 /** 参数根；永久 Nav2 参数位于 src/planning/omnifleet_planner/config/nav2_t2.yaml。
本次修改前的文件及旧部署说明保存在 /home/iecme/robot_backups/unprefixed_interfaces_20261016/originals。
历史迁移报告、原始录制和回退资料保留原始内容，不作为当前启动配置。
