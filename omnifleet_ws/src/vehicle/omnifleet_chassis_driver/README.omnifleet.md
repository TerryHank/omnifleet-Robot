# omnifleet_chassis_driver

亚博 Rosmaster 履带底盘驱动、原始 PWM 诊断、轮滑检测和辅助 TF。入口和依赖见 [setup.py](setup.py) 与 [package.xml](package.xml)。

126 的 `omnifleet-t2-chassis.service` 运行 `t2_driver`，串口 `/dev/omnifleet_t2_stm32`，左 M2、右 M1。驱动使用本机安全速度，读取 SBUS 通道并处理摇杆优先级。CH5 低挡不接管，中挡限速 0.70 m/s、1.00 rad/s，高挡 1.50 m/s、1.80 rad/s。

[驱动源码](omnifleet_chassis_driver/omnifleet_t2_driver.py) · [原有包说明](README.md)
