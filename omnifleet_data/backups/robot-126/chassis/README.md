# Robot 126 chassis source

- omnifleet_chassis_driver is the ROS 2 package exported from robot 126. Restore it under src/vehicle/omnifleet_chassis_driver.
- firmware is the Yahboom STM32F103RC source for the latest recorded SWD readback. Build entry point: make in firmware, using an arm-none-eabi toolchain.
- zz-yahboom-driver.conf is the active override for omnifleet-t2-chassis.service. 99-omnifleet-t2-chassis.rules creates /dev/omnifleet_t2_stm32.
- The built program corresponding to the verified SWD readback had SHA-256 5407d38e3a9a1bf98f6ff6a445d27ec145e33de978bec935eb408231b690a5b5.
