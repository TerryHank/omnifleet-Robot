set -e
cd "$(dirname "$0")/.."
flags="-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard"
sed 's/\.fpu softvfp/.fpu fpv4-sp-d16/; 1i .eabi_attribute 28, 1' Core/Startup/startup_stm32f407vetx.s > gcc/startup.S
arm-none-eabi-gcc $flags -c gcc/startup.S -o gcc/startup.o
arm-none-eabi-gcc $flags --specs=nano.specs --specs=nosys.specs -T gcc/flash.ld -Wl,--gc-sections,-Map=gcc/rrc104.map gcc/startup.o @gcc/objects.txt -lm -o gcc/rrc104.elf
arm-none-eabi-size gcc/rrc104.elf
arm-none-eabi-nm gcc/rrc104.elf | grep -E ' (SysTick_Handler|SVC_Handler|PendSV_Handler|host_motor_report|sbus_rx_task_entry|packet_rx_task_entry|packet_tx_task_entry)$'
arm-none-eabi-objcopy -O ihex gcc/rrc104.elf gcc/rrc104.hex
arm-none-eabi-objcopy -O binary gcc/rrc104.elf gcc/rrc104.bin
