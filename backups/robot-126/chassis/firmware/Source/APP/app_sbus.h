#ifndef __APP_SBUS_H__
#define __APP_SBUS_H__
#include <stdint.h>
#define SBUS_SIGNAL_OK 0
#define SBUS_SIGNAL_LOST 1
#define SBUS_SIGNAL_FAILSAFE 3
#define SBUS_MIDDLE_VALUE 1000
#define SBUS_MODE_NAVIGATION 0
#define SBUS_MODE_PASSTHROUGH 1
void SBUS_Reveive(uint8_t data);
void SBUS_Handle(void);
uint8_t SBUS_Set_Mode(uint8_t mode);
uint8_t SBUS_Protocol_Allowed(void);
void SBUS_Send_State(void);
#endif
