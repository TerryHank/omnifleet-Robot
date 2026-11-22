# 104 多点航点添加修复

根因已确认：用户添加第一个航点时，后台save_route尝试创建/var/lib/omnifleet_t2/missions，但服务用户iecme没有该目录父级写权限，触发PermissionError并导致后台退出。先前只验证了服务初始化，未验证真实添加/保存链路，漏掉此问题。

## 改动

- `/home/iecme/omnifleet_ws/src/visualization/omnifleet_waypoint_ui/launch/waypoint_ui.launch.py` 第15行：实机route_file改到`/home/iecme/omnifleet_data/missions/waypoints.json`。
- 同包`omnifleet_waypoint_ui/waypoint_ui_bridge.py`第232行：默认路线文件同步到相同长期数据位置。
- 同文件第688–697行：先将候选列表保存成功，再更新内存中的航点；保存失败时返回添加失败信息，保持后台运行及原路线，不清除待添加名称。
- 创建iecme可写的`/home/iecme/omnifleet_data/missions`。原missions目录不存在，未覆盖或清空已有路线文件。

仅重启omnifleet-t2-waypoints服务。实际参数读回route_file已切换，catalog正常发布，frame_id为map，服务active、PID302662。MOLA、Nav2、驱动和导航永久参数未改。没有发送运动目标。

## 验证

ROS域215、本机通信、FastDDS隔离实例中，用真实/omnifleet_t2/waypoints/add_pose话题连续发入两条PoseStamped。列表和文件均为2个航点；销毁并重建节点后仍恢复2个。
模拟不可写路径，第三条添加返回错误，进程保持运行，列表仍为2，原路线文件逐字节未改。测试通过，没有发布start请求或运动目标。
生产catalog实际读回成功，当前0个航点，用户之前触发崩溃的第一个点未保存，需要重新添加。未把隔离测试点插入生产路线。

备份：`/home/iecme/robot_backups/waypoint_save_1791999526043460142`。
测试结果：`/home/iecme/omnifleet_data/tests/waypoint_save_20261015/result.json`。
本目录保存最终代码快照、patch.py、verify.py和result.json。
