#include "global.h"
#include <math.h>
#include "tim.h"
#include "lwmem_porting.h"
#include "motors_param.h"

/* 全局变量 */
EncoderMotorObjectTypeDef *motors[4];
/* static void packet_handler(struct PacketRawFrame *frame); */

static void motor1_set_pulse(EncoderMotorObjectTypeDef *self, int speed);
static void motor2_set_pulse(EncoderMotorObjectTypeDef *self, int speed);
static void motor3_set_pulse(EncoderMotorObjectTypeDef *self, int speed);
static void motor4_set_pulse(EncoderMotorObjectTypeDef *self, int speed);

void set_motor_param(EncoderMotorObjectTypeDef *motor, int32_t tpc, float rps_limit, float kp, float ki, float kd)
{
    motor->ticks_per_circle = tpc;
    motor->rps_limit = rps_limit;
    motor->pid_controller.kp = kp;
    motor->pid_controller.ki = ki;
    motor->pid_controller.kd = kd;
}

void set_motor_type(EncoderMotorObjectTypeDef *motor, MotorTypeEnum type) {
	switch(type) {
		case MOTOR_TYPE_JGB520:
			set_motor_param(motor, MOTOR_JGB520_TICKS_PER_CIRCLE, MOTOR_JGB520_RPS_LIMIT, MOTOR_JGB520_PID_KP, MOTOR_JGB520_PID_KI, MOTOR_JGB520_PID_KD);
			break;
		case MOTOR_TYPE_JGB37:
			set_motor_param(motor, MOTOR_JGB37_TICKS_PER_CIRCLE, MOTOR_JGB37_RPS_LIMIT, MOTOR_JGB37_PID_KP, MOTOR_JGB37_PID_KI, MOTOR_JGB37_PID_KD);
			break;
		case MOTOR_TYPE_JGA27:
			set_motor_param(motor, MOTOR_JGA27_TICKS_PER_CIRCLE, MOTOR_JGA27_RPS_LIMIT, MOTOR_JGA27_PID_KP, MOTOR_JGA27_PID_KI, MOTOR_JGA27_PID_KD);
			break;
		case MOTOR_TYPE_JGB528:
			set_motor_param(motor, MOTOR_JGB528_TICKS_PER_CIRCLE, MOTOR_JGB528_RPS_LIMIT, MOTOR_JGB528_PID_KP, MOTOR_JGB528_PID_KI, MOTOR_JGB528_PID_KD);
			break;
		default:
			break;
	}
}

void motors_init(void)
{
    for(int i = 0; i < 4; ++i) {
        motors[i] = LWMEM_CCM_MALLOC(sizeof( EncoderMotorObjectTypeDef));
        encoder_motor_object_init(motors[i]);
		motors[i]->ticks_overflow = 60001;
        motors[i]->ticks_per_circle = MOTOR_DEFAULT_TICKS_PER_CIRCLE;
        motors[i]->rps_limit = MOTOR_DEFAULT_RPS_LIMIT;
        motors[i]->pid_controller.set_point = 0.0f;
        motors[i]->pid_controller.kp = MOTOR_DEFAULT_PID_KP;
        motors[i]->pid_controller.ki = MOTOR_DEFAULT_PID_KI;
        motors[i]->pid_controller.kd = MOTOR_DEFAULT_PID_KD;
    }

    /* 马达 1 */
    motors[0]->set_pulse = motor1_set_pulse;
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    __HAL_TIM_ENABLE(&htim1);
    __HAL_TIM_MOE_ENABLE(&htim1);

    /* 编码器 */
    __HAL_TIM_SET_COUNTER(&htim5, 0);
    __HAL_TIM_CLEAR_IT(&htim5, TIM_IT_UPDATE);

    __HAL_TIM_ENABLE(&htim5);
    HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL);


    /* 马达 2 */
    motors[1]->set_pulse = motor2_set_pulse;
    __HAL_TIM_SET_COUNTER(&htim1, 0);
    __HAL_TIM_ENABLE(&htim1);
    __HAL_TIM_MOE_ENABLE(&htim1);

    /* 编码器 */
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    __HAL_TIM_CLEAR_IT(&htim2, TIM_IT_UPDATE);

    __HAL_TIM_ENABLE(&htim2);
    HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);

    /* 马达 3 */
    motors[2]->set_pulse = motor3_set_pulse;
    __HAL_TIM_SET_COUNTER(&htim9, 0);
    __HAL_TIM_ENABLE(&htim9);
    __HAL_TIM_MOE_ENABLE(&htim9);

    /* 编码器 */
    __HAL_TIM_SET_COUNTER(&htim4, 0);
    __HAL_TIM_CLEAR_IT(&htim4, TIM_IT_UPDATE);

    __HAL_TIM_ENABLE(&htim4);
    HAL_TIM_Encoder_Start(&htim4, TIM_CHANNEL_ALL);

    /* 马达 4 */
    motors[3]->set_pulse = motor4_set_pulse;
    __HAL_TIM_SET_COUNTER(&htim10, 0);
    __HAL_TIM_SET_COUNTER(&htim11, 0);
    __HAL_TIM_ENABLE(&htim10);
    __HAL_TIM_ENABLE(&htim11);
    __HAL_TIM_MOE_ENABLE(&htim10);
    __HAL_TIM_MOE_ENABLE(&htim11);

    /* 编码器 */
    __HAL_TIM_SET_COUNTER(&htim3, 0);
    __HAL_TIM_CLEAR_IT(&htim3, TIM_IT_UPDATE);

    __HAL_TIM_ENABLE(&htim3);
    HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);


    // 测速更新定时器
    __HAL_TIM_SET_COUNTER(&htim7, 0);
    __HAL_TIM_CLEAR_IT(&htim7, TIM_IT_UPDATE);
    __HAL_TIM_ENABLE_IT(&htim7, TIM_IT_UPDATE);
    __HAL_TIM_ENABLE(&htim7);

    //packet_register_callback(&packet_controller, PACKET_FUNC_MOTOR, packet_handler);
}

static void motor1_set_pulse(EncoderMotorObjectTypeDef *self, int speed)
{
    if(speed > 0) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, speed);
    } else if(speed < 0) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, -speed);
    } else {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_4, 0);
    }
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);
}


static void motor2_set_pulse(EncoderMotorObjectTypeDef *self, int speed)
{
    if(speed > 0) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, speed);
    } else if(speed < 0) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, -speed);
    } else {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
    }
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
}

static void motor3_set_pulse(EncoderMotorObjectTypeDef *self, int speed)
{
    HAL_TIM_PWM_Stop(&htim9, TIM_CHANNEL_1);
    HAL_TIM_PWM_Stop(&htim9, TIM_CHANNEL_2);
    if(speed > 0) {
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_2, 0);
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, speed);
    } else if(speed < 0) {
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_2, -speed);
    } else {
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_2, 0);
    }
    HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_2);
}

static void motor4_set_pulse(EncoderMotorObjectTypeDef *self, int speed)
{
    HAL_TIM_PWM_Stop(&htim10, TIM_CHANNEL_1);
    HAL_TIM_PWM_Stop(&htim11, TIM_CHANNEL_1);
    if(speed > 0) {
        __HAL_TIM_SET_COMPARE(&htim10, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim11, TIM_CHANNEL_1, speed);
    } else if(speed < 0) {
        __HAL_TIM_SET_COMPARE(&htim11, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim10, TIM_CHANNEL_1, -speed);
    } else {
        __HAL_TIM_SET_COMPARE(&htim10, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim11, TIM_CHANNEL_1, 0);
    }
    HAL_TIM_PWM_Start(&htim10, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim11, TIM_CHANNEL_1);
}


#pragma pack(1)
typedef struct {
    uint8_t motor_id;
    float speed;
} MotorCtrlCmdUnit;

typedef struct {
    uint8_t cmd;
    uint8_t motor_num;
    MotorCtrlCmdUnit units[];
} MotorMutilCtrlCommandTypeDef;

typedef struct {
    uint8_t cmd;
    uint8_t motor_id;
    float speed;
} MotorSignalCtrlCommandTypeDef;

typedef struct {
    uint8_t cmd;
    uint8_t motor_id;
} MotorSignalStopCommandTypedef;

typedef struct {
    uint8_t cmd;
    uint8_t motor_mask;
} MotorMultiStopCommandTypedef;
#pragma pack()

/**
* @brief 串口命令回调处理
* @param frame 数据帧
* @retval void
*/
/*
static void packet_handler(struct PacketRawFrame *frame)
{

    switch(frame->data_and_checksum[0]) {
        case 0: {
            MotorSignalCtrlCommandTypeDef *mscc = NULL;
            mscc = (MotorSignalCtrlCommandTypeDef *)frame->data_and_checksum;
            motors[mscc->motor_id]->pid_controller.set_point = mscc->speed;
            break;
        }
        case 1: {
            MotorMutilCtrlCommandTypeDef *mmcc = NULL;
            mmcc = (MotorMutilCtrlCommandTypeDef *)frame->data_and_checksum;
            for(int i = 0; i < mmcc->motor_num; ++i) {
                motors[mmcc->units[i].motor_id]->pid_controller.set_point = mmcc->units[i].speed;
            }
            break;
        }
        case 2:  {
            MotorSignalStopCommandTypedef *mssc = NULL;
            mssc = (MotorSignalStopCommandTypedef *)frame->data_and_checksum;
            motors[mssc->motor_id]->pid_controller.set_point = 0;
            break;
        }
        case 3: {
            MotorMultiStopCommandTypedef *mmsc = NULL;
            mmsc = (MotorMultiStopCommandTypedef *)frame->data_and_checksum;
            for(int i = 0; i < 4; ++i) {
                if(mmsc->motor_mask & (0x01 << i)) {
                    motors[i]->pid_controller.set_point = 0;
                }
            }
            break;
        }
        default:
            break;
    }
}

*/


static volatile uint32_t last_host_command;
static volatile bool host_command_active;

static void host_motor_packet(struct PacketRawFrame *frame)
{
    const uint8_t *data = frame->data_and_checksum;
    const uint8_t length = frame->data_length;
    if (length < 2) return;
    const uint8_t command = data[0];
    if (command == 5 || command == 6) {
        extern bool steering_center_save(uint8_t angle);
        extern uint8_t steering_center_get(void);
        if (length != 2) return;
        const bool success = command == 6 || steering_center_save(data[1]);
        uint8_t reply[] = {'C', 'T', 'R', success ? 0 : 1, steering_center_get()};
        packet_transmit(&packet_controller, PACKET_FUNC_SYS, reply, sizeof(reply));
        return;
    }
    uint8_t count = 0;
    const uint8_t *entries = NULL;
    uint8_t stop_mask = 0;
    float linear_mm_s = 0.0f;
    float radius_mm = 0.0f;
    switch (command) {
    case 0:
        if (length != 6) return;
        count = 1;
        entries = data + 1;
        break;
    case 1:
        count = data[1];
        if (count < 1 || count > 4 || length != 2 + 5 * count) return;
        entries = data + 2;
        break;
    case 2:
        if (length != 2 || data[1] >= 4) return;
        stop_mask = 1U << data[1];
        break;
    case 3:
        if (length != 2) return;
        stop_mask = data[1];
        break;
    case 4:  /* Ackermann center speed and signed turning radius. Zero radius is straight. */
        if (length != 9) return;
        memcpy(&linear_mm_s, data + 1, sizeof(linear_mm_s));
        memcpy(&radius_mm, data + 5, sizeof(radius_mm));
        if (!isfinite(linear_mm_s) || !isfinite(radius_mm)) return;
        break;
    default:
        return;
    }
    float speeds[4];
    for (uint8_t i = 0; i < count; ++i) {
        memcpy(&speeds[i], entries + 5*i + 1, sizeof(float));
        if (entries[5*i] >= 4 || !isfinite(speeds[i])) return;
    }
    uint32_t irq = __get_PRIMASK();
    __disable_irq();
    if (command == 4)
        chassis->set_velocity_radius(chassis, linear_mm_s, radius_mm, false);
    for (uint8_t i = 0; i < count; ++i)
        encoder_motor_set_speed(motors[entries[5*i]], speeds[i]);
    for (uint8_t i = 0; i < 4; ++i)
        if (stop_mask & (1U << i)) encoder_motor_set_speed(motors[i], 0);
    last_host_command = HAL_GetTick();
    host_command_active = true;
    __set_PRIMASK(irq);
    uint8_t ack[] = {'R', 'O', 'S', command};
    packet_transmit(&packet_controller, PACKET_FUNC_SYS, ack, sizeof(ack));
}

void host_motor_init(void)
{
    packet_register_callback(&packet_controller, PACKET_FUNC_MOTOR, host_motor_packet);
}

void host_motor_timeout(void)
{
    if (host_command_active && (uint32_t)(HAL_GetTick() - last_host_command) >= 300U) {
        for (unsigned i = 0; i < 4; ++i)
            encoder_motor_set_speed(motors[i], 0);
        host_command_active = false;
    }
}

void host_motor_report(void)
{
    static uint16_t sequence;
    uint8_t report[88] = {'R','R','C',1};
    const uint16_t seq = sequence++;
    memcpy(report + 4, &seq, sizeof(seq));
    const uint32_t irq = __get_PRIMASK();
    __disable_irq();
    for (unsigned i = 0; i < 4; ++i) {
        const EncoderMotorObjectTypeDef *m = motors[i];
        uint8_t *record = report + 8 + 20*i;
        const int64_t count = m->counter;
        memcpy(record + 4, &m->rps, sizeof(float));
        memcpy(record + 8, &m->current_pulse, sizeof(float));
        memcpy(record + 12, &m->pid_controller.set_point, sizeof(float));
        memcpy(record + 16, &count, sizeof(int32_t));
    }
    __set_PRIMASK(irq);
    packet_transmit(&packet_controller, PACKET_FUNC_SYS, report, sizeof(report));
}
