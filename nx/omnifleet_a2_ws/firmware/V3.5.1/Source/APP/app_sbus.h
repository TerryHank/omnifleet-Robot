#ifndef __APP_SBUS_H__
#define __APP_SBUS_H__

#include "stdint.h"

#define SBUS_SIGNAL_OK          0x00
#define SBUS_SIGNAL_LOST        0x01
#define SBUS_SIGNAL_FAILSAFE    0x03
#define ALL_CHANNELS_

#define SBUS_MIDDLE_VALUE       (1000)

void SBUS_Reveive(uint8_t data);
void SBUS_Handle(void);
uint8_t SBUS_Is_Protocol_Control_Enabled(void);

#endif
