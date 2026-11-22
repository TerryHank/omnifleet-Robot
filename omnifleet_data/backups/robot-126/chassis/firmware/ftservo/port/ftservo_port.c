#include "ftservo_port.h"

#include "bsp.h"
#include "bsp_usart.h"
#include "FreeRTOS.h"
#include "task.h"

/* USART3 ISR is the sole producer; the FTServo task is the sole consumer.
 * A 1 Mbps reply arrives much faster than a FreeRTOS tick. Keep every byte
 * in this queue while the synchronous caller yields to other tasks. */
static uint8_t rx_buffer[128];
static volatile uint16_t rx_head;
static volatile uint16_t rx_tail;

void FTServo_PortRxByte(uint8_t byte)
{
    uint16_t next = (rx_head + 1U) & 127U;
    if (next != rx_tail)
    {
        rx_buffer[rx_head] = byte;
        __DMB();
        rx_head = next;
    }
}
void ftUart_Send(uint8_t *nDat, int nLen)
{
    if (nDat != 0 && nLen > 0)
    {
        int sent = 0;
        FTServo_PortFlushRx();
        while (sent < nLen)
        {
            uint32_t guard = 50000U;
            while (USART_GetFlagStatus(USART3, USART_FLAG_TXE) == RESET && guard > 0U)
                --guard;
            if (guard == 0U)
                break;
            USART_SendData(USART3, nDat[sent++]);
        }
    }
}

int ftUart_Read(uint8_t *nDat, int nLen)
{
    int received = 0;
    TickType_t deadline;

    if (nDat == 0 || nLen <= 0)
    {
        return 0;
    }

    deadline = xTaskGetTickCount() + pdMS_TO_TICKS(50);
    while (received < nLen)
    {
        while (rx_head == rx_tail)
        {
            if ((int32_t)(xTaskGetTickCount() - deadline) >= 0)
                break;
            vTaskDelay(1);
        }
        if (rx_head == rx_tail)
            break;
        __DMB();
        nDat[received++] = rx_buffer[rx_tail];
        rx_tail = (rx_tail + 1U) & 127U;
    }
    /* checkHead() reads one byte at a time. Leave subsequent bytes queued. */
    return received;
}

void ftBus_Delay(void)
{
    /* delay_ms() reprograms SysTick, which is also the FreeRTOS tick.  Using
     * it from the FTServo task corrupts scheduling and stops chassis reports. */
    vTaskDelay(pdMS_TO_TICKS(1));
}

void FTServo_PortFlushRx(void)
{
    rx_tail = rx_head;
}

void FTServo_PortSetBaud(uint32_t baudrate)
{
    USART3_Init(baudrate);
    FTServo_PortFlushRx();
}
