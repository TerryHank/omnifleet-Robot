# RRC Chassis Core

`rrc_chassis_core` is the sole runtime entry point for the Yahboom R2 STM32
chassis. The workspace remains `/home/iecme/stm32_driver_ws` and contains the
driver, wheel odometry, controls, robot description, and STM32 firmware source.

The core runtime owns `/dev/myserial` and publishes:

- `/voltage`
- `/imu/data_raw`
- `/imu/mag`
- `/vel_raw`
- `/wheel/odometry`
- `/joint_states`
- `/edition`

The hardware driver subscribes only to the permanent command mux output
`/cmd_vel`. Command producers must use:

- `/cmd_vel_teleop` for Foxglove/manual control;
- `/cmd_vel_nav_safe` for Nav2 output after collision monitoring;
- `/rrc_safety/zero_cmd` and `/rrc_safety/zero_lock` for the SLAM safety gate.

The mux applies source timeouts and priorities. The hardware driver also
enforces a 0.5 second watchdog and sends zero motion while idle or shutting down.

The systemd service is the normal production entry point:

```bash
sudo systemctl status ackermann-stm32-chassis.service
sudo systemctl restart ackermann-stm32-chassis.service
journalctl -u ackermann-stm32-chassis.service -f
```

Do not start `Ackman_driver_R2` or `base_node_R2` separately while this service
is active because the service exclusively owns the STM32 serial port.
