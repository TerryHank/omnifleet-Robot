#ifndef FTSERVO_PORT_H
#define FTSERVO_PORT_H

#include <stdint.h>

/*
 * FTServo uses the existing USART3 bus.  The bus remains at the baud rate
 * selected by USART3_Init() in the base application (115200 by default).
 * Do not call the FTServo API concurrently with app_uart_servo commands.
 */
void FTServo_PortFlushRx(void);
void FTServo_PortSetBaud(uint32_t baudrate);
void FTServo_PortRxByte(uint8_t byte);

/* Transport hooks consumed by SCSLib/SCSerail.c. */
void ftUart_Send(uint8_t *nDat, int nLen);
int ftUart_Read(uint8_t *nDat, int nLen);
void ftBus_Delay(void);

#endif
