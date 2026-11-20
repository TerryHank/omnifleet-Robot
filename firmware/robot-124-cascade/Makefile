# Makefile for Rosmaster STM32F103RC Firmware
# Toolchain: arm-none-eabi-gcc

PROJECT = rosmaster
TARGET  = $(PROJECT)

# Toolchain
CC      = arm-none-eabi-gcc
CXX     = arm-none-eabi-g++
AS      = arm-none-eabi-gcc
LD      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
OBJDUMP = arm-none-eabi-objdump
SIZE    = arm-none-eabi-size

# Directories
SRC_DIR     = .
APP_DIR     = Source/APP
BSP_DIR     = Source/BSP
MEMS_DIR    = Source/MEMS
DEBUG_DIR   = Source/DEBUG
TOOL_DIR    = Source/TOOL
FTSERVO_DIR = ftservo/SCSLib
FTSERVO_PORT_DIR = ftservo/port
CMSIS_DIR   = CMSIS
FWLIB_DIR   = FWlib/src
FREERTOS_DIR = FreeRTOS/src
BUILD_DIR   = build

# MCU flags
CPU = -mcpu=cortex-m3
MCU = $(CPU) -mthumb

# Defines
DEFS  = -DSTM32F10X_HD
DEFS += -DUSE_STDPERIPH_DRIVER
DEFS += -DMEMS_20648
DEFS += -DMEMS_WEARABLE_DEVICE
DEFS += -DMEMS_SECONDARY_DEVICE
DEFS += -DMEMS_AUGMENTED_SENSORS

# Compiler flags
CFLAGS  = $(MCU) $(DEFS)
CFLAGS += -Wall -Wextra -Wno-unused-parameter -Wno-missing-field-initializers
CFLAGS += -O2 -g -ffunction-sections -fdata-sections
CFLAGS += -fno-common -fmessage-length=0

# Include paths
INC  = -I$(CMSIS_DIR)
INC += -I$(FWLIB_DIR)/../inc
INC += -I$(BSP_DIR)
INC += -I$(APP_DIR)
INC += -I$(DEBUG_DIR)
INC += -I$(FREERTOS_DIR)/../inc
INC += -I$(MEMS_DIR)
INC += -I$(TOOL_DIR)
INC += -I$(FTSERVO_DIR)
INC += -I$(FTSERVO_PORT_DIR)

# Assembler flags
ASFLAGS = $(MCU) $(DEFS) -Wall -g

# Linker flags
LDFLAGS  = $(MCU) -specs=nano.specs -specs=nosys.specs
LDFLAGS += -T STM32F103RC.ld
LDFLAGS += -Wl,-Map=$(BUILD_DIR)/$(PROJECT).map,--cref
LDFLAGS += -Wl,--gc-sections
LDLIBS = -lm -lc -lnosys

# Source files
C_SOURCES  = $(CMSIS_DIR)/core_cm3.c
C_SOURCES += $(CMSIS_DIR)/system_stm32f10x.c
C_SOURCES += $(APP_DIR)/main.c
C_SOURCES += $(APP_DIR)/protocol.c
C_SOURCES += $(APP_DIR)/app.c
C_SOURCES += $(APP_DIR)/app_uart_servo.c
C_SOURCES += $(APP_DIR)/app_oled.c
C_SOURCES += $(APP_DIR)/app_bat.c
C_SOURCES += $(APP_DIR)/app_motion.c
C_SOURCES += $(APP_DIR)/app_pid.c
C_SOURCES += $(APP_DIR)/app_flash.c
C_SOURCES += $(APP_DIR)/app_sbus.c
C_SOURCES += $(APP_DIR)/app_rgb.c
C_SOURCES += $(APP_DIR)/app_ackerman.c
C_SOURCES += $(APP_DIR)/app_math.c
C_SOURCES += $(APP_DIR)/app_fourwheel.c
C_SOURCES += $(APP_DIR)/app_mecanum.c
C_SOURCES += $(APP_DIR)/app_tracked.c
C_SOURCES += $(APP_DIR)/app_angle.c
C_SOURCES += $(FTSERVO_DIR)/HLS.c
C_SOURCES += $(FTSERVO_DIR)/SCS.c
C_SOURCES += $(FTSERVO_DIR)/SCSCL.c
C_SOURCES += $(FTSERVO_DIR)/SCSerail.c
C_SOURCES += $(FTSERVO_DIR)/SMS_STS.c
C_SOURCES += $(FTSERVO_PORT_DIR)/ftservo_port.c
C_SOURCES += $(BSP_DIR)/bsp.c
C_SOURCES += $(BSP_DIR)/bsp_beep.c
C_SOURCES += $(BSP_DIR)/bsp_flash.c
C_SOURCES += $(BSP_DIR)/bsp_timer.c
C_SOURCES += $(BSP_DIR)/bsp_usart.c
C_SOURCES += $(BSP_DIR)/bsp_wdg.c
C_SOURCES += $(BSP_DIR)/bsp_io_i2c.c
C_SOURCES += $(BSP_DIR)/bsp_motor.c
C_SOURCES += $(BSP_DIR)/bsp_key.c
C_SOURCES += $(BSP_DIR)/bsp_encoder.c
C_SOURCES += $(BSP_DIR)/bsp_pwmServo.c
C_SOURCES += $(BSP_DIR)/oled_fonts.c
C_SOURCES += $(BSP_DIR)/bsp_ssd1306.c
C_SOURCES += $(BSP_DIR)/bsp_spi.c
C_SOURCES += $(BSP_DIR)/bsp_adc.c
C_SOURCES += $(BSP_DIR)/bsp_can.c
C_SOURCES += $(BSP_DIR)/bsp_rgb.c
C_SOURCES += $(BSP_DIR)/bsp_mpu9250.c
C_SOURCES += $(BSP_DIR)/bsp_mpuiic.c
C_SOURCES += $(FWLIB_DIR)/misc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_adc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_bkp.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_can.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_cec.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_crc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_dac.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_dbgmcu.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_dma.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_exti.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_flash.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_fsmc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_gpio.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_i2c.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_iwdg.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_pwr.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_rcc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_rtc.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_sdio.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_spi.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_tim.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_usart.c
C_SOURCES += $(FWLIB_DIR)/stm32f10x_wwdg.c
C_SOURCES += $(DEBUG_DIR)/yb_debug.c
C_SOURCES += $(FREERTOS_DIR)/croutine.c
C_SOURCES += $(FREERTOS_DIR)/heap_2.c
C_SOURCES += $(FREERTOS_DIR)/list.c
C_SOURCES += $(FREERTOS_DIR)/port.c
C_SOURCES += $(FREERTOS_DIR)/queue.c
C_SOURCES += $(FREERTOS_DIR)/tasks.c
C_SOURCES += $(FREERTOS_DIR)/timers.c
C_SOURCES += $(TOOL_DIR)/tool_pid.c
C_SOURCES += $(MEMS_DIR)/dmp3Default_20648.c
C_SOURCES += $(MEMS_DIR)/icm20948.c
C_SOURCES += $(MEMS_DIR)/inv_mems_augmented_sensors.c
C_SOURCES += $(MEMS_DIR)/inv_mems_base_control.c
C_SOURCES += $(MEMS_DIR)/inv_mems_base_driver.c
C_SOURCES += $(MEMS_DIR)/inv_mems_data_converter.c
C_SOURCES += $(MEMS_DIR)/inv_mems_drv_hook.c
C_SOURCES += $(MEMS_DIR)/inv_mems_interface_mapping.c
C_SOURCES += $(MEMS_DIR)/inv_mems_load_firmware.c
C_SOURCES += $(MEMS_DIR)/inv_mems_mpu_fifo_control.c
C_SOURCES += $(MEMS_DIR)/inv_mems_mpu_selftest.c
C_SOURCES += $(MEMS_DIR)/inv_mems_secondary_transport.c
C_SOURCES += $(MEMS_DIR)/inv_mems_slave_compass.c
C_SOURCES += $(MEMS_DIR)/inv_mems_slave_pressure.c
C_SOURCES += $(MEMS_DIR)/inv_mems_transport.c
C_SOURCES += $(MEMS_DIR)/ml_math_func.c
C_SOURCES += $(MEMS_DIR)/mlmath.c

AS_SOURCES = $(CMSIS_DIR)/startup_stm32f10x_hd.s

# Objects
OBJECTS  = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(AS_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(AS_SOURCES)))

# Build rules
.PHONY: all clean flash

all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(INC) -c $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) $(ASFLAGS) -c $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	$(LD) $(LDFLAGS) $(OBJECTS) -o $@ $(LDLIBS)
	$(SIZE) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
	$(OBJCOPY) -O binary $< $@

clean:
	rm -rf $(BUILD_DIR)

# Flash using OpenOCD
flash:
	@echo "Flashing $(BUILD_DIR)/$(TARGET).hex ..."
	openocd -f interface/stlink.cfg -f target/stm32f1x.cfg \
		-c "program $(BUILD_DIR)/$(TARGET).hex verify reset exit"
