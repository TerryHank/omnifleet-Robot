# 小车 VR 协议适配层

## 1. 总体对应关系

~~~
VR
  ├─ UDP DISC 广播       -> 小车 :9100
  ├─ UDP PAIR/控制       -> 小车 192.168.3.104:8888
  ├─ UDP POSE            <- 小车 VR_IP:9000
  └─ TCP JPEG            <- 小车 VR_IP:8090

小车 ROS 2
  ├─ /servo/command       trajectory_msgs/msg/JointTrajectory
  ├─ /servo/joint_states  sensor_msgs/msg/JointState
  ├─ /cmd_vel             geometry_msgs/msg/Twist
  ├─ /odom                nav_msgs/msg/Odometry
  └─ /camera/image/compressed       sensor_msgs/msg/CompressedImage
~~~

## 2. 启动

终端一，启动 USB 摄像头：

~~~
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
ros2 run omnifleet_bringup usb_camera_publisher
~~~

默认读取 /dev/video0，发布 /camera/image/compressed。

终端二，启动协议适配层：

~~~
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
ros2 run omnifleet_bringup vr_protocol_adapter \
  --ros-args \
  -p car_id:=CAR001 \
  -p car_name:=Tracked-Car \
  -p ctrl_port:=8888 \
  -p enable_drive:=false
~~~

enable_drive 为 false 时不会把 SPEED 和 ANGLE 变成底盘运动命令。确认通信和机械安全后才使用 -p enable_drive:=true。

## 3. DISC 设备发现

小车每秒向 255.255.255.255:9100 广播：

~~~
DISC|carId,ctrlPort,matched,pairedVrId,name
~~~

空闲小车的完整报文：

~~~
DISC|CAR001,8888,0,,Tracked-Car\n
~~~

已匹配小车的完整报文：

~~~
DISC|CAR001,8888,1,VR-A1B2C3D4,Tracked-Car\n
~~~

字段：

| 字段 | 示例 | 含义 |
|---|---|---|
| carId | CAR001 | 小车唯一 ID |
| ctrlPort | 8888 | PAIR 和控制指令接收端口 |
| matched | 0 或 1 | 空闲或已匹配 |
| pairedVrId | 空字符串或 VR-A1B2C3D4 | 当前绑定的 VR ID |
| name | Tracked-Car | 显示名称，不能包含逗号 |

## 4. PAIR 一对一匹配

VR 发到小车 192.168.3.104:8888：

~~~
PAIR|VR-A1B2C3D4\n
~~~

成功时小车回到 PAIR 来源 IP 和来源端口：

~~~
PAIR_ACK|CAR001,1,VR-A1B2C3D4\n
~~~

已经被其他 VR 占用时：

~~~
PAIR_ACK|CAR001,0,VR-OTHER\n
~~~

解除匹配：

~~~
UNPAIR|VR-A1B2C3D4\n
~~~

协议没有规定 UNPAIR_ACK；解除成功后 DISC 恢复为：

~~~
DISC|CAR001,8888,0,,Tracked-Car\n
~~~

适配层只接受已绑定 VR 的来源 IP 发来的控制指令。

## 5. UDP 控制报文与 ROS

### 5.1 HEADP 云台俯仰

完整报文：

~~~
HEADP|-15.2\n
~~~

映射：

~~~
HEADP -> ROS /servo/command
joint_names: ["pitch"]
pitch -> 舵机 ID1
~~~

协议角度范围为 -180 到 180 度。当前 ID1 限位为 1067 到 2263，适配层按角度线性换算并限幅。

### 5.2 HEADY 云台偏航

完整报文：

~~~
HEADY|30.0\n
~~~

映射：

~~~
HEADY -> ROS /servo/command
joint_names: ["yaw"]
yaw -> 舵机 ID2
~~~

当前 ID2 限位为 2048 到 4095。

角度转换关系：

~~~
-180 度 -> 下限
   0 度 -> 限位中点
 180 度 -> 上限
~~~

### 5.3 SPEED 底盘速度

完整报文：

~~~
SPEED|0.5\n
~~~

范围为 -1 到 1，映射为：

~~~
/cmd_vel
geometry_msgs/msg/Twist
Twist.linear.x = SPEED
~~~

### 5.4 ANGLE 底盘转向

完整报文：

~~~
ANGLE|-12.0\n
~~~

范围为 -30 到 30 度，当前映射为：

~~~
Twist.angular.z = ANGLE / 30.0 * 2.0
~~~

### 5.5 FIRE 触发

协议规定参数固定为 0：

~~~
FIRE|0\n
~~~

映射为：

~~~
/vr/fire
std_msgs/msg/Bool
data: true
~~~

### 5.6 RESET 复位

完整报文：

~~~
RESET|0\n
~~~

当前处理：

~~~
底盘速度和转向清零
ID1 pitch 回到 1665
ID2 yaw 回到 3071
~~~

## 6. 控制超时

SPEED 和 ANGLE 超过约 200 ms 没有更新时，适配层将速度和转向清零。VR 端应持续发送：

~~~
SPEED|0.5\n
ANGLE|0.0\n
~~~

VR 断开后，小车不会继续保持最后一次速度。

## 7. ROS 舵机接口

控制话题：

~~~
/servo/command
trajectory_msgs/msg/JointTrajectory
~~~

位置使用弧度，速度使用弧度/秒，加速度使用弧度/秒²。

控制 pitch：

~~~
ros2 topic pub --once /servo/command \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: ['pitch'], points: [{positions: [0.0], velocities: [30.0], accelerations: [3.0]}]}"
~~~

控制 yaw：

~~~
ros2 topic pub --once /servo/command \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: ['yaw'], points: [{positions: [0.0], velocities: [30.0], accelerations: [3.0]}]}"
~~~

状态话题：

~~~
/servo/joint_states
sensor_msgs/msg/JointState
~~~

底层 STM32 服务：

~~~
/t2/servo_command
omnifleet_interfaces/srv/ServoCommand
~~~

ROS 轨迹速度和加速度会换算成当前 FTServo 参数并限幅：

~~~
servo_speed = abs(ROS velocity) × 10，范围 0..3400
servo_accel = abs(ROS acceleration) × 10，范围 0..255
~~~

## 8. POSE 遥测

小车向已匹配 VR 的 IP:9000 发送 UDP，建议 20 到 50 Hz。

完整报文格式：

~~~
POSE|x,y,heading,pitch,roll\n
~~~

完整示例：

~~~
POSE|1.200,3.400,90.00,-5.00,2.00\n
~~~

当前来源：

| 字段 | 单位 | ROS 来源 |
|---|---|---|
| x | 米 | /odom.pose.pose.position.x |
| y | 米 | /odom.pose.pose.position.y |
| heading | 度 | /odom.pose.pose.orientation 转 yaw |
| pitch | 度 | 当前暂填 0.00 |
| roll | 度 | 当前暂填 0.00 |

## 9. JPEG 视频

小车作为 TCP 客户端连接：

~~~
VR_IP:8090
~~~

图像来源：

~~~
/camera/image/compressed
sensor_msgs/msg/CompressedImage
~~~

每帧的完整二进制格式：

~~~
4 字节：JPEG 长度，int32，小端序
N 字节：JPEG 原始数据
~~~

发送伪代码：

~~~
jpeg = compressed_image.data
sock.sendall(struct.pack("<i", len(jpeg)))
sock.sendall(jpeg)
~~~

不添加文本分隔符。

## 10. VR 最小联调顺序

监听本机 UDP 9100，等待：

~~~
DISC|CAR001,8888,0,,Tracked-Car
~~~

发送到 192.168.3.104:8888：

~~~
PAIR|VR-A1B2C3D4
~~~

等待：

~~~
PAIR_ACK|CAR001,1,VR-A1B2C3D4
~~~

然后依次测试：

~~~
HEADP|0
HEADY|0
SPEED|0
ANGLE|0
RESET|0
~~~

监听本机 UDP 9000 接收：

~~~
POSE|x,y,heading,pitch,roll
~~~

监听本机 TCP 8090 接收 JPEG。

最后解除匹配：

~~~
UNPAIR|VR-A1B2C3D4
~~~

## 11. ROS 验收命令

~~~
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
ros2 topic list -t | grep -E \
  '(cmd_vel|odom|imu/data_raw|servo|vr/fire)|camera/image/compressed'
~~~

预期话题：

~~~
/cmd_vel              geometry_msgs/msg/Twist
/imu/data_raw         sensor_msgs/msg/Imu
/odom                  nav_msgs/msg/Odometry
/servo/command         trajectory_msgs/msg/JointTrajectory
/servo/joint_states    sensor_msgs/msg/JointState
/vr/fire               std_msgs/msg/Bool
/camera/image/compressed         sensor_msgs/msg/CompressedImage
~~~

检查图像频率：

~~~
ros2 topic hz /camera/image/compressed
~~~

检查舵机状态：

~~~
ros2 topic echo /servo/joint_states
~~~

检查里程计：

~~~
ros2 topic echo /odom
~~~

## 12. 当前实现边界

1. DISC、PAIR、UNPAIR、HEADP、HEADY、SPEED、ANGLE、FIRE、RESET、POSE 和 JPEG 均已有适配代码。
2. enable_drive 默认关闭，避免联调报文意外驱动车辆。
3. 舵机限位使用已经写入的 ID1 和 ID2 限位值。
4. POSE 的 heading 来自 odom；pitch 和 roll 当前暂为 0.00。
6. 原协议的 HEADP 和 HEADY 不携带舵机速度、加速度；适配层使用默认速度和加速度，ROS JointTrajectory 可以额外提供这两个值。
