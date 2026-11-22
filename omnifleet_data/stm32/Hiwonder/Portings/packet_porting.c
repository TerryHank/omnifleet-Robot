/**
 * @file packet_portting.c
 * @author Lu Yongping (Lucas@hiwonder.com)
 * @brief 串口协议接口实现
 * @version 0.1
 * @date 2023-05-23
 * 
 * @copyright Copyright (c) 2023
 * 
 */
 
#include "global.h"
#include "lwrb.h"
#include "usart.h"
#include "packet.h"
#include "cmsis_os2.h"
#include <stdio.h>
#include "lwmem_porting.h"

#define PACKET_RX_FIFO_BUFFER_SIZE 2048 /* FIFO缓存长度 */
#define PACKET_RX_DMA_BUFFER_SIZE 256 /* 单个DMA缓存长度 */

/* 对外暴露的变量 */
struct PacketController packet_controller; /* 协议控制器实例 */

/* 内部函数 */


static int send_packet(struct PacketController *self, struct PacketRawFrame *frame);

/* 串口控制依赖的外部变量 */
extern osSemaphoreId_t packet_tx_idleHandle;
extern osSemaphoreId_t packet_rx_not_emptyHandle;
extern osMessageQueueId_t packet_tx_queueHandle;

/**
 * @brief 初始化packet 控制器对象
 * @retval void
 */
void packet_init(void)
{
    memset(&packet_controller, 0, sizeof(packet_controller));
    packet_controller.state = PACKET_CONTROLLER_STATE_STARTBYTE1;
    packet_controller.data_index = 0;

    /* DMA 接收缓存初始化 */
		static uint8_t rx_dma_buffer1[PACKET_RX_DMA_BUFFER_SIZE];
		static uint8_t rx_dma_buffer2[PACKET_RX_DMA_BUFFER_SIZE];

    packet_controller.rx_dma_buffers[0] = rx_dma_buffer1;
    packet_controller.rx_dma_buffers[1] = rx_dma_buffer2;
    packet_controller.rx_dma_buffer_size = PACKET_RX_DMA_BUFFER_SIZE;
    packet_controller.rx_dma_buffer_index = 0;

    /* 接收 FIFO 初始化 */
    packet_controller.rx_fifo_buffer  = LWMEM_CCM_MALLOC(PACKET_RX_FIFO_BUFFER_SIZE);
    packet_controller.rx_fifo = LWMEM_CCM_MALLOC(sizeof(lwrb_t)); 
    lwrb_init(packet_controller.rx_fifo, packet_controller.rx_fifo_buffer, PACKET_RX_FIFO_BUFFER_SIZE);

    /* 发送接口 */
    packet_controller.send_packet = send_packet;
}

/**
 * @brief 发送接口
 * @details 实际不会直接进行发送而是将要发送的帧指针压入发送队列，等待发送任务操作硬件完成发送
 *
 * @param self  协议控制器实例
 * @param frame  要发送的帧
 * @return int
 */
static int send_packet(struct PacketController *self, struct PacketRawFrame *frame)
{
    return osMessageQueuePut(packet_tx_queueHandle, &frame, 0, 10);
}

/**
 * @brief 开始串口协议接收
 * @retval void
 */
void USART1_IRQHandler(void)
{
    USART_TypeDef *const uart = huart1.Instance;
    const uint32_t status = uart->SR;
    const uint32_t errors = USART_SR_ORE | USART_SR_FE | USART_SR_NE | USART_SR_PE;
    if (status & (USART_SR_RXNE | errors)) {
        // Reading SR then DR clears receive errors without disabling RXNEIE.
        const uint8_t byte = (uint8_t)uart->DR;
        if ((status & USART_SR_RXNE) && !(status & errors)) {
            lwrb_write(packet_controller.rx_fifo, &byte, 1);
            osSemaphoreRelease(packet_rx_not_emptyHandle);
        }
    }
}

void packet_start_recv(void)
{
    __HAL_UART_CLEAR_OREFLAG(&huart1);
    HAL_NVIC_SetPriority(USART1_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
    __HAL_UART_ENABLE_IT(&huart1, UART_IT_ERR);
    __HAL_UART_ENABLE_IT(&huart1, UART_IT_RXNE);
}

void packet_rx_task_entry(void *argument)
{
    for (;;) {
        osSemaphoreAcquire(packet_rx_not_emptyHandle, osWaitForever);
        packet_recv(&packet_controller);
    }
}

void packet_tx_task_entry(void *argument)
{
    struct PacketRawFrame *frame;
    for (;;) {
        if (osMessageQueueGet(packet_tx_queueHandle, &frame, NULL, osWaitForever) == osOK) {
            HAL_UART_Transmit(&huart1, (uint8_t *)frame, frame->data_length + 5, 30);
            lwmem_free(frame);
        }
    }
}
