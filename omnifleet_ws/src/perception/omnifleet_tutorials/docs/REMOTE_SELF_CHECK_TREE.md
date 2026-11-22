# OmniFleet T2 远端自检树

目标主机：`iecme@192.168.3.113`。

## 1. 硬件底座

```bash
ssh iecme@192.168.3.113
readlink -f /dev/omnifleet_t2_stm32
systemctl is-active omnifleet-t2-chassis.service omnifleet-t2-airy.service
```

预期串口解析到一个真实 `ttyUSB*`，两个服务均为 `active`。

## 2. ROS 底盘反馈

```bash
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/hardware_drivers_ws/install/setup.bash
source /home/iecme/omnifleet_ws/omnifleet_t2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 topic echo /vel_raw --once
ros2 topic echo /odom --once
ros2 topic info /cmd_vel -v
ros2 run tf2_ros tf2_echo odom base_link
```

底盘驱动必须持续发布速度反馈、`/odom` 和 `odom -> base_link`。排查时先确认
`/cmd_vel` 的发布者和订阅者数量，不通过增加第二个速度发布节点来绕过问题。

## 3. 手动导航

```bash
cd /home/iecme/omnifleet_ws/omnifleet_t2_ws
ros2 launch omnifleet_bringup production.launch.py \
  backend:=mola map_id:=active \
  map_dir:=/home/iecme/omnifleet_data/maps \
  start_description:=false
```

随后检查：

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
ros2 topic echo /map --field info --once
ros2 run tf2_ros tf2_echo map odom
```

三项 Nav2 生命周期均应为 `active`，且 `/map`、`map -> odom`、
`odom -> base_link` 连续可用。

## 4. 停止手动导航

在启动导航的终端按 `Ctrl+C`。若使用 systemd 临时启动过，则执行：

```bash
sudo systemctl stop omnifleet-t2-navigation.service
```

该导航服务应始终保持 `disabled`，不随开机自动运行。
