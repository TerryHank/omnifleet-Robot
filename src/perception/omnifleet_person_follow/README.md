## 104单圈旋转（2026-10-23，当前）

3为顺时针一圈、4为逆时针一圈，使用现有/odom航向增量跨±180度连续累计360度，接近终点减速，达到一圈后立即发布零速度。保持同一个3/4不重复启动；异步手部线程尚未返回新结果不视为松手，观察到手势确实改变（例如握拳）后，再做3/4可重新触发；相机自转时的手部出画不作为重新触发条件。相机旋转必然把人转出视野，3/4启动后由里程计独立执行到目标，不因人暂时出画中断；完成后释放感知人物锁，允许新手势。张掌在可见时可中止，面板停止按钮保留，1/2/OK也可切换动作。

1前进、2后退仍保持至张掌或切换。3/4完成后停车，不自动恢复跟随。Fox显示实际累计角度/360°以及旋转完成。底盘仲裁及原有命令过期逻辑保留；旋转命令只根据新的里程计采样刷新，没有改导航/MOLA参数。

验证：47条/5秒的真实/odom输入已读取；纯C++跨角度边界测试、43项隔离实际原生C++检查及88项Python测试通过。隔离检查包含顺逆360后停车、保持不重转、重新触发与掌停，实车物理转角精度尚未现场验收。下面的3/4持续旋转说明为旧版本记录，以本节为准。

## 104单圈旋转（2026-10-23，当前）

3为顺时针一圈、4为逆时针一圈，使用现有/odom航向增量跨±180度连续累计360度，接近终点减速，达到一圈后立即发布零速度。保持同一个3/4不重复启动；异步手部线程尚未返回新结果不视为松手，真实新结果表示放下/未知手势后，再做3/4可重新触发。张掌随时中止，1/2/OK也可切换动作。

1前进、2后退仍保持至张掌或切换。3/4完成后停车，不自动恢复跟随。Fox显示实际累计角度/360°以及旋转完成。底盘仲裁及原有命令过期逻辑保留；旋转命令只根据新的里程计采样刷新，没有改导航/MOLA参数。

验证：47条/5秒的真实/odom输入已读取；纯C++跨角度边界测试、41项隔离实际原生C++检查及87项Python测试通过。隔离检查包含顺逆360后停车、保持不重转、重新触发与掌停，实车物理转角精度尚未现场验收。下面的3/4持续旋转说明为旧版本记录，以本节为准。

## 104数字手势控制（2026-10-23，当前04.09）

同一只识别中的手切换：1（食指）前进、2（食中指V）后退、3（三指）顺时针原地转、4（拇指收起其余四指伸出）逆时针原地转；五指张掌停止并解除锁定。按用户选择，识别后保持动作，直到切换手势或本人张掌；人物丢失沿用原来的停车/丢失窗口处理。OK切回当前距离的自动跟随。

数字命令可从未锁定状态直接锁定做手势的人，不要求先OK；已有锁定时忽略旁人的数字与张掌。1使用既有linear_velocity（当前0.2m/s），2使用既有reverse_max_speed（当前0.25m/s），3/4使用既有angular_velocity（当前0.4rad/s）。数字模式为纯直行/后退/原地转，不使用跟随距离和自动对人转向；底盘输出仍经过既有仲裁。

原生输入gesture字段保留OK=11、Palm=5；数字1-4为104扩展101-104，附带body_track_id。未新增模型，保留TensorRT三模型、CUDA光流和Mask内256点测距。4与停止通过拇指是否展开区分，3支持食中无名三指和拇食中三指两种。

验证：86项Python测试、31项隔离实际C++行为测试通过；旧包30帧检出30次真实手部，28次张掌，未误判成4。旧素材不含完整1-4操作，真人数字手势到实车动作尚未现场验收。切换前备份`/home/iecme/robot_backups/gesture_digits_20261023/before.tar.gz`，后文为早期记录。

## 104视觉性能分段对照（2026-10-23，当前保留CUDA光流）

当前只将BoT-SORT的PyrLK稀疏光流迁到OpenCV CUDA；CPU特征点、RANSAC、Mask解码、手部裁剪旋转、手势规则、Kalman与IoU/评分代价保留。人体分割/手掌/手部21点三个模型保持TensorRT FP16。`perception.py` 状态提供 `gmc_backend`、`optical_flow_ms`、`mask_decode_ms`、`last_hand_preprocess_ms`。

在104用同一旧RGB-D包派生640×480输入、30Hz回放，包含分割/跟踪/真实手部识别/256点深度/原生C++/绘图/JPEG/ROS/网络/Fox实际绘制；同进程CPU→单项GPU→CPU对照，CPU基线28.36/28.11FPS，CUDA光流29.05FPS，已安装代码复测Fox28.84FPS。GPU手势规则/Kalman/IoU代价分别使新鲜完整流程降至约24.83/22.98/27.64FPS，因此没有接入生产。不是所有GPU实现都慢，此结论限本次张量实现和单人负载。

测试使用私有域218/FastDDS/8767端口，所有速度均私有抑制；生产Zenoh首轮积压断连、内存压力段均排除。这些数字不是生产Zenoh或真相机稳定帧率承诺。旧录包没有OK启动动作，计时夹具关闭唤醒条件以连续覆盖深度，但真实手部推理仍运行；生产仍为OK唤醒/本人张掌取消。

分组结果和逐帧记录：`/home/iecme/robot_backups/gpu_pipeline_20261023/REPORT.md`。部署前完整备份为同目录`before.tar.gz`。恢复面板最新控制器读回的跟随距离和六项控制参数；导航/MOLA参数未改。后文包含早期版本记录。

## 104 Body Tracking 手势模式（2026-10-23，当前04.09入口）

`vision_04_09_body_tracking.launch.py` 已启用官方C++手势状态机：OK锁定做手势的人并开始跟随；本人张掌停止并解除锁定，再次OK才能重新跟随。`body_tracking_104.yaml` 的 `activate_wakeup_gesture: 1`，launch的 `auto_follow: false`，手部采用现有MediaPipe 21点 TensorRT FP16引擎和异步线程，不加载人体骨架模型。保留深度16×16采样、连续PD转向、后退控距和现有底盘仲裁。

适配器发送真实手框和官方gesture编码（OK=11、Palm=5），附带所属人体 `body_track_id`；C++仅把手势作用于该人体，原无归属字段的上游消息仍按原逻辑处理。只有实际手部识别结果可触发，不伪造关键点。完整手框需在所属人体框内，与官方无身体关键点时的匹配分支一致。

部署保留当前Fox实际控制器读回的目标2m及六项转向/后退参数，写入本包104配置作为启动值。Fox继续支持热改；手势状态和ID在原04.09面板显示。

验证：84项Python测试、13项隔离原生C++行为测试通过；104 GPU对原有RGB录包30帧检出30次真实21点手部，28次张掌。旧包不含OK动作，实拍OK到张掌的现场运动验收尚未完成。下文为早期版本记录，以本节04.09说明为准。

# OmniFleet 104 官方 TROS C++ 人体跟随

当前生产入口运行 D-Robotics `tros_person_following` 的真实C++组件，上游提交 `202e8c8`。
旧Python状态机不再发送导航任务。手势仍关闭，104已有的YOLO26n-seg TensorRT、ByteTrack、
相机标定、Mask内16×16深度采样及满分辨率Fox图像继续使用。

`/vision/person_follow/tros_targets` 使用官方 `ai_msgs/PerceptionTargets`：真实track_id、ROI、
置信度、厘米制位置及尺寸。没有有效深度时不伪造距离；锁定后高频测距只针对官方选定ID，
未锁定/丢失时轮询候选。官方C++负责观察、选人、跟随、预测、belief search、边缘转向、
目标死区和限频重发；原版使用 `NavigateToPose`，不使用GoalUpdater。

配置为 `config/tros_104.yaml`，距离带0.95–1.05米、滞回0.05米。原版过近停车，不主动后退；
没有无深度盲靠近功能。MOLA仍提供map→base_link，相机坐标 `rgbd_view_z_up` 仍位于雷达前5厘米。
控制转换使用最新可用TF，与原版车体位姿及104已有导航一致；输入仍保留图像真实时间戳。

导航仍通过已有 `/navigate_to_pose` 仲裁；原版转向 `/cmd_vel` 经过同一本地底盘仲裁，
不直接发布 `/navigation/cmd_vel_safe`。取消操作仅针对本跟随器的目标，含延迟接受的目标。
切换后延续此前暂停状态；Fox原有按钮改为“开始/恢复官方跟随”和“暂停跟随”，
调用官方 `enable_follow` 服务。`enable_motion=false` 继续保持原有仅识别行为。
`/vision/gesture_follow/status` 的 `controller_backend=tros_person_following_cpp` 标识真实控制器。

切换前Git备份为 `e13959a8b9e58519762166b72bf867a2eb3e6b5b`；车端bundle：
`/home/iecme/robot_backups/tros_cpp_20261022/before-official-tros.bundle`。

参考：[官方跟随节点](https://github.com/D-Robotics/tros_person_following)、
[官方感知消息](https://github.com/D-Robotics/hobot_msgs)。上游README和许可证保留在原包中。

## 旧Python移植实现的历史说明（非当前控制器）

当前104临时使用`config/person_follow.yaml`中的`auto_follow: true`：检测到人体即锁定最居中的可见track_id并跟随，不依赖手势或深度才锁定。
锁定后沿用原ID与现有丢失搜索/连续性重锁；先居中、按需16×16深度、Nav2动态目标；当前目标距离1米。
该模式不加载手掌/手部模型，也不启动手部线程。Fox保留选人和暂停；明确暂停后不会因再次看到人自行恢复。
`auto_follow: false`恢复原手势模式；无需改模型或导航配置。

YOLO26n-seg TensorRT FP16 → ByteTrack（含Kalman）→ 按需原始深度点查询 → 人物三维位置。
MediaPipe手掌/21点手部模型与人物分割区域、手腕位置和track_id关联；104使用同权重TensorRT FP16引擎，未部署引擎时保留OpenCV CUDA。
沿用OpenCV Zoo已有手部模型，在手ROI有效时跳过手掌检测；不加载人体骨架模型或RTMW。

竖拇指锁定/恢复当前人物；张掌暂停并保留ID；剪刀手结束并解除锁定。
锁定后忽略旁人的手势，腕部同时属于多个重叠人体时不将它分配给某一人。
ByteTrack短时丢失保留ID；丢失后按D-Robotics思路主动搜索，并允许结合世界位置与连续运动重锁新ID。
长时间遮挡和出画后重入不等同于可靠ReID。本实现没有新增人体身份识别网络，空间连续性不能保证身份相同。

## 入口与配置

```bash
source /home/iecme/omnifleet_ws/env.bash
cd /home/iecme/omnifleet_ws
ros2 launch omnifleet_person_follow person_follow.launch.py enable_motion:=false
```

原课程入口 `vision_04_08_gesture_person_follow.launch.py` 映射到本包，保留为面板最后案例。
启动时沿用相机常驻服务，RGB保持1536×1280；模型输入512×512，不降低相机源分辨率。
业务参数在本包 `config/person_follow.yaml`；ByteTrack参数在 `config/bytetrack.yaml`。
长期模型位于 `/home/iecme/omnifleet_data/ml_models/omnifleet_vision/vendor/yolo26_person_follow/`。

相机外参由用户2026-10-22确认：居中、同高、水平朝前，位于雷达前0.05m。
本节点发布 `rslidar → rgbd_view_z_up`，复用现有相机工厂RGB/Depth外参。
若实际安装发生变化，应更新本包相机安装参数，不把显示坐标假装为标定测量。

## 话题与实际控制链

- `/vision/gesture_follow/status`：std_msgs/String，JSON状态、人物ID、手势归属、XYZ及分段耗时。
- `/vision/gesture_follow/debug`：sensor_msgs/Image，仅被订阅时发出。
- `/vision/course_gui/course_04_08_gesture_person_follow/debug/compressed`：sensor_msgs/CompressedImage，全分辨率JPEG直接输出。
- `/vision/person_follow/target`：geometry_msgs/PoseStamped，相机光学坐标中的原始深度目标。
- `/vision/person_follow/nav_goal`：geometry_msgs/PoseStamped，map中的跟随候选（识别模式也可查看）。
- `/navigate_to_pose`：已有本机导航仲裁Action，仅在enable_motion=true时提交一次跟随任务。
- `/goal_update`：Humble GoalUpdater目标更新，仅在自己任务有效期间发布。

暂停/结束只取消自己持有的Action，不调用全局停车服务去取消其他任务。
地图目标走Nav2 → local_navigation → `/navigation/cmd_vel_safe` → STM32。
104没有接入Luka或DDSM；不新增或替换全车控制门控。
`enable_motion=false`沿用原案例识别模式，本次不执行物理运动。

## 2026-10-22 主动搜索与误检修正

人体检测`confidence`及ByteTrack新轨迹/高分关联阈值均由0.10/0.25提高至0.50；
图中人物框显示实际分数。阈值不是校准后的正确概率，提高后可能漏掉遮挡或只露出小部分的人物。

丢失后依次尝试预测位置、最后实测位置及历史中的可用观察点，随后按目标离开方向分四段转向扫描。
最多两个观察点，总搜索时长默认30秒；没有三维历史时仍可原地扫描。搜索结束仍保留LOST，等待再次发现或显式手势。
观察点参考现有global costmap，使用已知空闲点；不可用时回溯历史。Nav2仍负责规划、避障和控制权仲裁。
搜索使用有限的普通NavigateToPose；跟随使用GoalUpdater持续更新，二者只取消自己持有的任务，切换时等待取消完成。
搜索到达不是跟随失败，不再因此把状态卡进PAUSED。

同ID恢复同时检查空间连续性；新ID重锁参考原版：置信度至少0.50、2秒窗口内实测位移超过0.20米，
与最后实测/预测位置的距离在丢失前2秒、2–5秒、5秒后分别不超过1.5/3/5米。
多个符合者按分数和距离排序；这会有换错人的可能，并不提供外观ReID保证。
新ID接管后手势归属跟随新ID，旧ID/旁人的手势不会控制当前目标；LOST时竖拇指也可显式重新选择。

正常跟随仍只对锁定人物高频16×16测距；LOST时为重锁候选轮流测距，合计最多10次/秒，未恢复全图配准或点云。
Fox状态包括`confidence_threshold`、`search_phase`、`search_round`、`relock_reason`、`candidate_depth_queries`。
参数`search_timeout`、`search_max_rounds`保存在本包config/person_follow.yaml。

## 当前1米保持、Nav2避障和后退

目标距离按base_link中心到人体实测位置的水平距离计算，保持目标1.00米。
超过1.10米开始靠近，回到1.05米停止；低于0.90米开始后退，回到0.95米停止。
保持期间不追逐中心附近的小幅测距波动。人员突然靠近低于0.90米时，后退不等待世界坐标平滑追上。
人体世界坐标使用0.25秒时间常数平滑，人体移动累计0.15米才更新固定地图目标；
车辆自己移动不会把静止人物的目标绕着人物拖动。相同目标不重复发布，变化目标合并到最高2.5Hz。

人靠近时生成远离人物一侧的约束目标、仍朝向人物，由Nav2规划/MPPI执行后退；没有直接发布底盘速度。
前进切后退时仅取消一次自己的前进任务；后退任务内部仍通过GoalUpdater动态更新，不逐帧取消重发。
后退候选均受远离人物的方向约束，后方没有可用目标时不替换成向人靠近的目标。
跟随BT明确使用FollowPathMPPI、global planner、GoalUpdater和标准代价地图恢复，
移除到达后强制继续运行的包装。Nav2的雷达障碍层、膨胀层与足迹碰撞代价保持使用运行时配置。
若理想目标落入障碍，选择目标距离圆上的可用观察位置；保留可通行膨胀代价，未知区策略交给Nav2。
没有可用目标时等待；障碍可通行后自动恢复，不能保证在受阻时仍恰好1米。
规划执行aborted在2秒后重试，外部cancel不自动夺回控制。

状态新增`person_range_m`、`filtered_person_range_m`、`follow_control_state`（HOLD/FOLLOW/BACKOFF）、
`follow_goal_blocked`、`follow_distance_m`；图中显示距离和模式。
状态携带原图`source_stamp`及实际手部21点，支持录包后同步验证与重放。
原始RGB-D、Nav2路径/代价地图、实际障碍输入、命令和里程计应同时录制，不能只录结果图验证避障。

人物居中采用RGB人体框中心与画面中线的偏差，先通过公共Nav2任务执行原地Spin（不使用平移控制器），
对准后再跟随。角度启动/保持范围为0.12/0.06弧度，避免中心附近反复转动。
人物仍可见、尚无有效深度时不去追历史外推点：先对准，再每次通过Nav2前移0.20米并重新测距；
有有效深度后立即切回1米保持/后退逻辑。接近过程中人物离开视野，会结束当前接近段并转入丢失恢复。
当前按用户要求，人物可见但无有效深度时，先居中再沿其方向每次前移0.20米取深度；不再因旧的近距历史位置一直保持。深度无效时无法知道实际距离，仍由现有Nav2足迹/雷达避障约束前进。
无效深度可能来自反光、遮挡、背光或测距范围，接近不保证恢复深度；雷达避障和现有导航仲裁持续有效。

Fox新增“人物选择→锁定并跟随所选人物”和“暂停跟随”。这是明确的操作者输入，
`lock_source=fox_operator`区别于手势锁定；不会伪造thumbs_up结果。
ROS输入为`/vision/person_follow/control`（std_msgs/String JSON，`op=lock,track_id=...`或`op=pause`）。
手势识别不稳定时可用点选操作继续测试距离、居中和避障，正常手势接口保留。
Windows Fox最终案例同时显示识别图与Z-up导航地图：`/map`、全局/局部costmap、青色候选`/vision/person_follow/nav_goal`、黄色已派发动态目标`/goal_update`及全局/局部规划路径。
地图透明叠层固定按底图、全局、局部顺序绘制；不改变导航地图坐标或代价数据。
`/vision/person_follow/goal_markers`为MarkerArray实时目标显示，使用可靠、瞬态本地QoS；活动点与连线高于地图平面，仅改变显示高度，不改变导航目标坐标。保持时显示“保持1.00m／无移动目标”，暂停时清除目标，标记寿命1秒。Fox隐藏原先可能留存的PoseStamped历史箭头，并显示当前目标的map坐标。
人体检测/新轨迹阈值当前为0.70，未降低手部21点模型的0.80阈值。

## 帧率设计及验收边界

只处理最新RGB帧、QoS队列1、使用同时间戳16UC1原始深度和工厂内外参按需投影；不生成视觉点云。
相机源满分辨率RGB-D已解除1000μs曝光引起的15FPS限制，当前自动曝光上限500μs原生取流约30FPS；不宣称模型FPS等于相机/显示FPS。
直接一次绘图/JPEG，取消原课程的overlay与压缩转发节点，防止重复大图ROS复制。
部署后分别记录人检测/跟踪、手部、深度/TF、JPEG及处理/显示帧率。
软件、静止视频采样、真人动作、Nav2模拟接口和实际底盘运动验收分别记录，不能互相替代。


## 2026-10-22 部署验证

已在104构建/安装；重启后包、引擎与入口仍可用。15项测试通过，包括ID归属、暂停保留ID、
同ID恢复、原始深度单位/掩码、目标暂时丢失不反复取消，以及多次目标更新只发送一个Action。
真实ROS协议另用隔离的无运动模拟服务验证：两次开始（首次/恢复）、27次更新、两次取消。
这些测试没有向实际Nav2提交运动任务，不代表实车导航跟随已验收。

相机安装TF实测可查：rslidar→rgbd_view_z_up为[0.05,0,0]及单位旋转，
map→camera_color_optical_frame、map→base_link均可查询。
显示采用Jetson已有nvjpegenc；同一1536×1280参考图的JPEG对比为OpenCV约14.8ms、nvjpegenc约8.0ms。
手部采集按人物ROI轮换，每帧至多一次手掌检测，已跟踪的手直接复用ROI；
指尖弯曲使用MediaPipe已有的21点3D输出，不增加网络。

真人日志已有拇指锁定、张掌暂停、剪刀手解除ID的记录，但存在unknown及快速手势切换；
一次采样还因电池断电中断，不能据此宣称完成稳定识别、多人误触或实车动作验收。
详细静止/现场帧率记录在交付目录follow_trt_20261022/中，区分有人与空场，不把它们当作同条件加速比。
所有车端测试均enable_motion=false，保留原有导航和定位服务。

RGB识别不等待深度；三维位置异步匹配同时间戳的识别结果与原始深度，保留测量时间戳与融合年龄。


## 2026-10-22 按需查点初版（后续改为下文16×16采样）

当前跟随案例不再订阅整幅配准深度，改用 `/camera/depth/image_raw` 与 `/camera/color/camera_info`。
复用相机SDK配置中的工厂标定；仅在已锁定人物且需要跟随位置时，调用公开RGB点查询函数。
取人物框中心，如中心不在人体分割内则取最近的人体掩码点；只查询该点，不遍历整个人体的深度。
空闲/暂停时不查询。原始深度与RGB结果仍按相同采集时间戳匹配，迟到的原始深度可异步完成查询，
RGB识别不必等待深度到达。返回的XYZ保持在RGB光学坐标系，沿用既有TF转地图坐标。
状态中可查看 depth_query_mode、depth_query_calls、depth_query_ms、depth_query_result。

本次相机SDK14项、跟随包15项测试均通过；现场两路配准图订阅者均为0，
空闲227帧期间查询计数保持0。原始RGB为1536×1280，输入约14.6Hz、显示约11.4Hz；
场景与负载会变化，不把这次数字当作固定保证或同条件准确加速比。
运动输出始终关闭。本次没有重新验收真人手势稳定性或实际导航跟随。

## 当前：锁定人物Mask内16×16稀疏测距

调用SDK的 `rgb_mask_to_depth`：用工厂标定将人物RGB框反投影为原始深度ROI，
在ROI布置16×16网格，最多读取256个实际深度像素，投影回RGB后只保留人物Mask内的点。
使用有效点的深度MAD过滤离群点，XYZ取中位数；没有有效测量时不生成距离。
这不是256次单点查询，不做整幅配准、补洞或点云。

只对当前锁定且可见的人物测距；空闲/暂停时不查询，匹配相同硬件时间戳。
RGB和识别输入分辨率分别保持1536×1280、512×512。
显示绘图与nvjpegenc放在独立进程，待显示队列长度1，忙时替换旧帧；图像与叠加信息必须属于同一帧。
手部后台线程每个处理帧接收最新任务，队列长度1，忙时替换旧任务，不积压。
只消费一次新手势结果，不重放旧命令。实际更新频率受模型执行与整机负载影响。
手部预处理仅旋转最终ROI，保留原始插值及坐标反算；模型仍使用TensorRT FP16。

状态包含 `hand_updated`、`display_async`、`depth_query_calls` 与
`depth_query_result` 中的采样数、Mask有效点数、离群过滤后点数、深度MAD。
相机SDK和跟随包共44项测试通过；真人锁定时的实际帧率、测距耗时另见交付记录。

## 30FPS采集端修复后的历史结果

RGB与深度均保持原分辨率，深度改用原生自动曝光（上限500μs），原生平滑与补洞为Normal。
复用已配置的Ultralytics预测器和CPU ByteTrack输出，避免每帧重新准备预测会话，
以及把CPU轨迹传回GPU再取回CPU。同一张有人物的1536×1280静态图，原方法约50.61ms，
新方法约41.15ms；ID、框、Mask一致。这个数字不是在线相机端到端FPS。
跟随节点单独使用与相机一致的无SHM传输设置，不修改全局ROS或导航传输。
JPEG时间戳名义速率改为30FPS，仍按实际输出发送，不补帧。

当前全链路同时显示深度、进行识别及保留导航时，CPU六核接近满载、GPU约5–6%；
在线识别显示仍约10FPS，尚未达到30FPS，不能把相机恢复30FPS当作识别已达30FPS。
最新相机SDK及跟随包37项测试通过，实际底盘运动保持关闭。

## 2026-10-22 早期实现与现场结果（历史）

104本机的相机到识别进程使用`/dev/shm`共享RGB/16UC1帧对，ROS只发送`/camera/rgbd/local_frame`通知。
帧对在同一文件锁内提交，读取时复制为识别进程自己的数组，保留采集时间戳及硬件帧号。
公开ROS图像和CameraInfo接口继续可用；`use_local_frames: false`可选择原ROS图像输入。
这减少大图ROS序列化，并不表示GPU推理和进程间传输完全没有复制。

人物模型使用TensorRT异步执行；仅解码人物Mask，ByteTrack直接消费CPU结果。
原MediaPipe手掌和21点模型转换为TensorRT FP16，沿用OpenCV Zoo前后处理，后台线程按150ms名义间隔检查手势。
显示进程按需绘制并通过nvjpegenc编码；过时帧直接丢弃，不重放或补帧。深度查询缓存标定矩阵逆。

实际连续锁定ID 1的22.267秒中，处理316帧、测距新增315次，处理14.15FPS、JPEG显示13.88FPS，
输入28.79FPS；全部316帧有有效距离，约1.431–1.458m，每次检查最多256点。
深度查询平均9.03ms、中位3.255ms、P95 34.445ms，包含运行负载造成的等待。
另一段不测距、手部无有效任务的对照可到26.75FPS；不能用它冒充锁定测距帧率。
最高1536×1280 RGB、640×480深度保留，整幅配准和视觉点云未启用。尚未稳定达到30FPS。
所有实测均`enable_motion=false`，未发送导航Action或目标更新；保留导航服务。

## 2026-10-22 完整视觉回放优化

在104上将保存的原始RGB-D帧对按30Hz顺序回放，无插帧；Windows只运行Fox显示。
完整处理包括人物分割、ByteTrack、手掌/21点手势、锁定人物Mask内16×16测距、
TF/世界坐标、跟随目标计算及1536×1280 JPEG质量85显示。底盘运动关闭。
30.055秒测量：处理29.11 FPS、JPEG发布29.11 FPS、实际新手部结果28.81次/秒、
Fox实际绘制26.78 FPS。25.064秒复测：20.19、20.07、19.63、19.07，存在负载波动。
因此已测到接近30FPS的处理能力，但尚不能保证整机并行负载下稳定维持该速度。
44项测试通过；完整计数、分段耗时和限制见e2e30_20261022/REPORT.md交付记录。


## Gemini Pro / official Body Tracking on robot 104 (2026-10-23)

`vision_04_09_body_tracking.launch.py` selects the actual official C++ controller.
Gemini Pro uses the existing Orbbec SDK v1.10.35 and ROS wrapper 1.5.15.
RGB is 640x480 and depth 1280x800, both configured at 30 FPS; observed whole-chain
rates must be measured and must not be inferred from the configured sensor rate.
The camera's factory RGB calibration exists at 640x480 only. The 1920x1080
profile publishes zero RGB intrinsics; it is not used for metric RGB/depth fusion.
Invalid CameraInfo does not enter inverse projection or crash perception.

The existing YOLO26n-seg TensorRT and ByteTrack provide real body ROIs. OpenCV
YuNet CUDA provides measured face ROIs. No face/head ROI is synthesized from a
body box. The original C++ controller retains its face/head prerequisite and
box-based motion rules. It can therefore stop when the face/head is absent,
even if the body is detected. This mode does not use Nav2 or maintain 1 metre.
Movement uses the existing `/cmd_vel` -> local_navigation -> chassis chain.

Native soft filtering and hole filtering are enabled with SDK readback at startup.
`/camera/depth/image_raw` remains the sensor's 16UC1 millimetre output and supplies
the locked person's 16x16 sparse mask query. Independent RGB/depth streams use
nearest-stamp pairing within 50 ms; no hardware synchronization is claimed.
`/camera/depth/image_filtered` is a separate software processed 16UC1 image;
`/camera/depth/image_gray_filtered/compressed` displays it in Foxglove. A 3x3
median smooths small noise and fills only local holes whose measured neighbours
are consistent. Large holes and depth discontinuities are retained.

RGB auto exposure is supported. Depth/IR auto exposure and its maximum are not
supported by this device's SDK properties. Manual depth exposure supports
0..10000 in the SDK's own units; no unverified conversion to microseconds is made.
The native NVIDIA decoder is enabled and reuses its decoder object per stream.


### Depth backoff added to native Body Tracking (2026-10-23)

For the selected native track ID, the existing raw-depth 16x16 mask result is
transformed into base_link. Its XY norm, not camera optical Z, is sent as
`range_base_m` with `range_age_s` in ai_msgs Target attributes. Python never
publishes chassis velocity. Native C++ owns the near-distance override:

- Start straight backoff below 0.90 m; stop once the range reaches 1.00 m.
- Cap backward speed at 0.12 m/s. Keep forward velocity zero through 1.10 m.
- Retain original body/face forward and rotation rules outside that near band.
- A missing face does not prevent reverse with a valid tracked-person depth.
- Suspend reverse when depth or its source frame exceeds 0.35 s; stop on target
  disappearance and reset hysteresis on native target-ID change.
- Preserve the existing chassis arbiter, MOLA and Nav2 settings. This does not
  add Nav2 goal following or replace the original far-distance box controller.

Native status includes range_base_m, distance_mode (ORIGINAL/HOLD/BACKOFF/
WAIT_DEPTH) and target_distance_m. Fox shows these states and the 1 m target.


### Current body-only metric following and hot distance control

The user requested removing the original face/head prerequisite. The 04.09
launch now disables YuNet; only YOLO person segmentation/ByteTrack is needed.
For a locked, visible person, fresh measured base-frame range controls forward,
hold and reverse, without the old box-width/top-of-image forward conditions.
Motion starts outside target +/-0.10m and continues to the target before holding.
Forward speed uses the existing linear_velocity cap (0.2m/s); reverse remains
capped at 0.12m/s. A new person without range is centred first, then approached
at 0.08m/s for a depth measurement. Missing depth after a near-distance hold or
reverse suspends linear motion instead of assuming that the person is farther away.

Continuous steering uses the calibrated person-centre ray in base_link, with
P=3.0, filtered D=0.15, centre deadband 0.025rad and angular envelope +/-1.2rad/s.
Steering remains active while reversing. Positive linear movement waits until
absolute bearing is <=0.15rad, preserving the requested turn-before-approach flow.

Fox provides a slider and numeric target-distance input. Its real request path is
/body_tracking_104/horizon_tracking_RobotCmdVel/set_parameters, parameter
follow_distance (double). The GUI displays target_distance_m from native C++
status as the acknowledgement. This changes forward, hold and reverse thresholds
together. It takes effect during the current run; restarting the case defaults
to 1.0m. MOLA/Nav2 parameters and existing chassis arbitration are retained.


### Response tuning, 2026-10-23

Reverse P is now1.0 with a0.25m/s cap (formerly0.6/0.12m/s). Forward settings,
distance hysteresis and stale-depth behaviour are unchanged. Steering P is1.8,
D is0.35 with a0.8rad/s cap, and derivative filtering weights the current sample
by0.7 (formerly3.0/0.15/1.2rad/s and0.4). The user's active2m target was restored
through the native parameter service before resuming perception. Thirty-two
isolated native ROS checks and a delayed-yaw-plant comparison passed. These are
software checks; the new physical overshoot response still needs field observation.
