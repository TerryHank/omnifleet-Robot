# 104 当前导航参数页面：整条路线按钮

已在104正在使用的Foxglove应用包中部署新按钮。现有窗口需Ctrl+R刷新，位置是左侧导航参数搜索框下方「多点路线导航」，在运动数据录制卡片上方。开始按钮发送既有/omnifleet_t2/waypoints/start；停止发送/omnifleet_t2/waypoints/stop。没有自动启动实车导航。

当前航点后台返回0个航点；开始按钮因此禁用，添加航点且导航就绪后启用。保存过的路线未清空或改写。本次发现原后台已在2026-10-14因//navigation/execute非法名称退出；修复无前缀frame=map的路径拼接后，omnifleet-t2-waypoints服务已启动，start有1个订阅者、catalog有1个发布者。

## 修改文件和行号

- `/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel/Nav2PermanentPanel.js`：39行增加catalog/status订阅；1004–1042行路线控制卡片、开始/停止以及状态门控；1052行放到搜索框后；1240–1255行读取路线与后台结果；1270行清理timer和广告。
- `/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/foxglove_extension/omnifleet-t2-semantic-waypoints/src/Nav2PermanentPanel.js`：同步相同源码。
- `/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js`：替换initNav2Builtin函数，部署当前应用。完整bundle和面板源都通过node语法检查。
- `/home/iecme/omnifleet_ws/src/control/omnifleet_local_navigation/omnifleet_local_navigation/client.py`：14–15行，裸map的prefix设为空，避免//navigation/execute及其他双斜杠名称；namespaced frame保持原路由方式。Python编译与实际后台启动验证通过。

## 验证范围

JSDOM行为检查通过：初始化不发布；无航点、未就绪、正在执行时开始禁用；开始/停止使用正确无前缀Empty话题；请求等待时重复点击不重复发送。测试context为模拟发布器，未向实车发送目标。
Foxglove实际运行配置client_topic_whitelist已允许这些既有接口，无需修改桥接配置或重启雷达、MOLA、Nav2。
后台实际catalog读取通过，但没有对用户当前窗口刷新后做截图确认；显示新按钮需要刷新Foxglove窗口。

备份：`/home/iecme/robot_backups/route_button_1791998717611526273`，包含原应用bundle、原面板、原client。
本目录保存源快照和test.cjs。没有修改导航永久参数、航点数据、IMU或融合管线。
