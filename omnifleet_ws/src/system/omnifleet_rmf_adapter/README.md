# WSL多车调度适配器

当前入口支持普通跟随、当前位置编队、单点/多点导航，以及最近车辆或全部车辆的目标调度。旧版“仅两种任务、旧formation已移除”描述不再代表当前模块。

## 任务入口与执行链

Foxglove和网页使用同一个中央HTTP `/state`、`/command`。HTTP命令白名单位于`omnifleet_rmf_adapter/control_http.py`，中央路由位于`central.py`。

| 操作 | 当前行为 |
| --- | --- |
| 跟随领车 | 按选定顺序确定领车和从车，以领车定位、速度和轨迹更新跟随目标；切换或停止由现有交接流程处理 |
| 开始编队 | 保存成员当前位置和相对朝向；目标发给队形中心，联合规划各成员路径，允许局部绕障后归队 |
| 单点导航 | 选定车辆后，在地图发布目标；若目标对象为队形中心，则进入编队任务 |
| 多点导航 | 地图添加航点，列表调整/保存，明确执行后启动；添加或保存航点不应发车 |
| 目标调度 | 最近的合格空闲车辆优先；全部车辆模式依次到达、返回本次出发位置并确认完成后放行下一辆；距离优先，列表顺序其次，已执行车辆不抢占 |
| 通道调度 | 使用A/B标定与互斥资源；当前存在通道配置时禁止启动编队或连续跟随，具体边界见[TRAFFIC_DISPATCH.md](TRAFFIC_DISPATCH.md) |

共享界面的坐标属于`fleet_map`，中央通过有效变换转换到车辆自己的`map`。保留的底层本车接口使用本车坐标；不要把两种坐标直接混用。保存的数据不会在中央重启后自动变成活动任务。

外部`web_goal`经`operator_controls.py`生成Missions内部的`single_goal`或`route_add`；RMF获配任务也可在`rmf_dispatch.py`转换为内部操作。二者不是独立HTTP命令，不应为方便调用直接加入白名单。地图添加多点和发送执行请求是不同操作。

Missions负责业务状态机、队列和车辆客户端调用。`rmf_dispatch.py`把部分请求转换为RMF compose任务，经投标和获配回到Missions；已指定车辆的单点等请求可走现有直接业务路径。`rmf_traffic.py`通过RMF traffic-light接口登记执行路径并处理暂停/恢复；`traffic.py`还管理自定义通道资源。这些路径共用同一执行出口，不能把所有业务统称为原生RMF道路拓扑导航，也不能把RMF说成仅显示状态。

普通导航使用`/navigation/execute`，编队使用`/navigation/formation`，动态目标与路权暂停沿既有FLEET协议传递。本车Nav2负责可行路径和局部控制。RMF Schedule在线、任务获配、交通放行、车端Action成功和轮速停稳各有自己的状态，不能互相替代。

## 配置与许可

当前配置在`config/framework.json`：参考车104，中央Domain42；104/car2、113/car1、111/a2_111分别使用独立Domain104、113、111。接入时读取实际广播配置；111保留Ackermann车型、最小转弯半径等车型差异，不套用差速车原地自转模型。

三车当前保存的`enabled`和`motion_enabled`为true，这仅是配置快照，不表示当前在线或通过全部实车验收。未知车辆默认`motion_enabled=false`。

执行许可链为：配置`motion_enabled` → WSL车辆客户端读取并回报 → 中央检查客户端在线/新鲜且许可确认 → 既有车端allow_fleet/租约/导航执行契约。客户端回报不是另一个独立的车端许可。中央心跳、导航就绪、定位会话、地图配准等现有检查继续生效；此说明没有增加门控或放宽超时。

`/state.execution_requested`、`execution_observed`、`execution_enabled`分别表示配置请求、WSL客户端确认和二者同时成立。顶层`motion_enabled`只是任一有效许可的汇总，不代表每车都具备可执行任务或活动租约。每车阻塞原因看`robots.*.blockers`。

配置中的`map_transform_validated`、`fleet_lease_contract_validated`已删除，发现新车也不再生成这两个无行为字段。运行时地图有效车辆看`maps.valid_robots`及`validation_reasons`，租约看实际导航/客户端状态。实车验收查单独证据，不能从配置标签推断。

## 地图、发现与数据

共享图以`central.reference_robot`为参考，当前为`robot_104`，不是113。其他车辆按与参考的有效会话变换合并地图并补齐未知区域；参考临时离线时可使用缓存参考，定位会话变化会使旧变换失效。多车配准按参考车与待配准成员成对计算并合并结果，并非只支持固定两辆。

共享地图与共享代价图是不同输出：`/fleet/map`和`/fleet/global_costmap/costmap`。车端原生规划/局部控制还有自己的代价图，不把共享膨胀和车端膨胀混称为同一个参数。具体数值读现有配置和车端回报，不在文档写死。

ROS 传输采用 Fast DDS（`rmw_fastrtps_cpp`）。中央角色加载 [fastdds-central.xml](config/fastdds-central.xml)，车辆角色由发现服务根据 [fastdds-client.xml](config/fastdds-client.xml) 和 [路由模板](config/fastdds-router-template.yaml) 生成本车会话。广播接入生成临时 Fast DDS 路由配置；失去新鲜广播后撤下客户端并删除会话。`data/run/discovery/`为空不等于配置损坏。车辆角色要求discovery运行时profile，不作为手动固定连接入口。详见[BROADCAST_DISCOVERY.md](BROADCAST_DISCOVERY.md)。

- `data/connection_status.json`：连接与采样快照；许可聚合以运行中的HTTP `/state`为准。
- `data/map_hub_status.json`：地图状态，不含运动许可；旧缓存中的`motion_enabled:false`没有控制意义。
- `data/fleet_alignment.json`、`registration-job.json`：配准和定位会话记录。
- `data/missions/`：航点、队形、通道等持久数据，保存与执行分离。

停止服务后状态文件不会自动消失。检查服务状态、文件时间和采样新鲜度，不能把旧JSON视作实时车辆状态。

## 源码分工

- `central.py / control_http.py`：状态汇聚、HTTP命令路由、许可和中央周期。
- `discovery.py / discovery_manager.py`：身份广播、冲突检查、临时会话和独立客户端生命周期。
- `missions.py / goal_dispatch.py`：业务状态机、航点队列、派车及往返顺序。
- `formation.py / elastic_trajectory.py / formation_profile.py`：编队、联合轨迹和实际车型约束。
- `rmf_dispatch.py / rmf_traffic.py / traffic.py`：RMF任务桥接、RMF交通与自定义通道资源。
- `control_client.py`：运行在WSL的每车客户端，管理许可配置回读、租约、Action和取消竞态。
- `map_hub.py / registration.py`：共享图、同伴占用与配准。

启动、停止及离线测试命令见[广播发现与接入](BROADCAST_DISCOVERY.md)。当前部署只使用`omnifleet-rmf.target`及广播发现服务；固定104/113的旧unit、静态会话及旧断连脚本已备份后删除。没有实车时只运行离线测试，不用模拟结果冒充物理验收。

仓库内的回归源码见 [test/](test)，测试和实车结果以对应版本的验收记录为准。
