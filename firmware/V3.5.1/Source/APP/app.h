#ifndef __APP_H__
#define __APP_H__

#include "stdio.h"

#include "config.h"
#include "yb_debug.h"
#include "protocol.h"

#include "tool_pid.h"

#define MOTION_WATCHDOG_DEFAULT_TIMEOUT_MS 1000U
#define MOTION_WATCHDOG_MIN_TIMEOUT_MS     100U
#define MOTION_WATCHDOG_MAX_TIMEOUT_MS     5000U

void App_Init(void);
void App_Loop(void);
void App_Start_FreeRTOS(void);

void App_Delay_ms(uint16_t ms);
void App_Send_Version(void);

void App_Motion_Command_Heartbeat(void);
void App_Motion_Command_Watchdog_Handle(void);
uint8_t App_Set_Motion_Command_Watchdog_Timeout(uint16_t timeout_ms);
void App_Get_Motion_Command_Watchdog_Status(uint16_t *timeout_ms,
	uint16_t *elapsed_ms, uint8_t *armed, uint8_t *stopped,
	uint16_t *trigger_count);

void Set_Auto_Report(uint16_t enable);


void App_Set_OLED_Flag(uint8_t flag);
void App_Clear_Yaw(void);
void App_Test_Mode_Init(void);
uint8_t App_FreeRTOS_Enable(void);

#endif
