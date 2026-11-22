#include "app_sbus.h"
#include "protocol.h"
#include "bsp_usart.h"
#include "FreeRTOS.h"
#include "task.h"
#include <string.h>

/* USART2 uses the board inverter and 100000 baud, 8 data bits + even parity, 2 stop bits. */
#define SBUS_TIMEOUT_MS 100U
static volatile uint8_t rx[25], pending[25], ready, rx_index;
static uint16_t channels[16];
static uint8_t failsafe=SBUS_SIGNAL_FAILSAFE, result;
static uint32_t frames, last_frame;

static uint32_t now_ms(void) { return xTaskGetTickCount() * portTICK_RATE_MS; }
static uint16_t age_ms(void) {
    uint32_t age=now_ms()-last_frame;
    return !frames || age>65535U ? 65535U : (uint16_t)age;
}

void SBUS_Reveive(uint8_t value) {
    if (!rx_index && value!=0x0f) return;
    rx[rx_index++]=value;
    if (rx_index==25) { if (rx[24]==0) { memcpy((void*)pending,(const void*)rx,25); ready=1; } rx_index=0; }
}

void SBUS_Handle(void) {
    uint8_t frame[25], received=0;
    taskENTER_CRITICAL();
    if (ready) { memcpy(frame,(const void*)pending,25); ready=0; received=1; }
    taskEXIT_CRITICAL();
    if (received) {
        for (uint8_t ch=0;ch<16;ch++) {
            uint16_t bit=ch*11U, offset=1U+bit/8U;
            uint32_t word=(uint32_t)frame[offset] | ((uint32_t)frame[offset+1]<<8);
            if (offset+2<=22) word|=(uint32_t)frame[offset+2]<<16;
            channels[ch]=(word>>(bit%8U))&0x7ffU;
        }
        failsafe=(frame[23]&8U) ? SBUS_SIGNAL_FAILSAFE : ((frame[23]&4U) ? SBUS_SIGNAL_LOST : SBUS_SIGNAL_OK);
        frames++; last_frame=now_ms();
    }
}

uint8_t SBUS_Set_Mode(uint8_t requested) { return result = (requested != SBUS_MODE_NAVIGATION); }
uint8_t SBUS_Protocol_Allowed(void) { return 1; }

void SBUS_Send_State(void) {
    uint8_t data[48]={0}; uint16_t age=age_ms();
    data[0]=PTO_HEAD; data[1]=PTO_DEVICE_ID-1; data[2]=46; data[3]=FUNC_SBUS_CONTROL;
    data[4]=1; data[5]=SBUS_MODE_NAVIGATION; data[6]=result;
    data[7]=age>SBUS_TIMEOUT_MS ? SBUS_SIGNAL_FAILSAFE : failsafe;
    data[8]=data[7]==SBUS_SIGNAL_OK; data[9]=age; data[10]=age>>8;
    for (uint8_t i=0;i<4;i++) data[11+i]=(uint8_t)(frames>>(8U*i));
    for (uint8_t i=0;i<16;i++) { data[15+i*2]=channels[i]; data[16+i*2]=channels[i]>>8; }
    for (uint8_t i=2;i<47;i++) data[47]+=data[i];
    USART1_Send_ArrayU8(data,sizeof(data));
}
