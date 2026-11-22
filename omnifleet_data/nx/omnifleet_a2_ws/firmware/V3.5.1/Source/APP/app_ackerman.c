#include "app_ackerman.h"
#include "app_motion.h"
#include "app_flash.h"
#include "app_math.h"
#include "app_pid.h"
#include "app.h"


#include "bsp_pwmServo.h"
#include "bsp_usart.h"


static int speed_L_setup = 0;
static int speed_R_setup = 0;

// 小车速度变量
int akm_speed_fb = 0;

// 阿克曼角度相关变量
int akm_servo_angle = 0;
static int16_t akm_servo_target_angle = 0;

// 阿克曼角速度相关变量
float akm_speed_angle = 0;
float akm_angle = 0;

// 阿克曼前轮默认角度，转弯角度以此为相对角度，增加或者减少。
uint16_t g_ackerman_default_angle = AKM_ANGLE_INIT;
static uint8_t g_ackerman_max_steering_angle = AKM_ANGLE_LIMIT_DEFAULT;


static int g_offset_yaw = 0;
static int16_t g_speed_setup = 0;

// REP-103 转向契约：正角左转，负角右转，零角回中。
void Ackerman_Steering(int16_t angle)
{
    akm_servo_target_angle = Math_Limit_int(
        angle, -g_ackerman_max_steering_angle, g_ackerman_max_steering_angle);
    akm_servo_angle = akm_servo_target_angle;
    // 舵机安装方向与 REP-103 逻辑舵角相反；只在 PWM 硬件边界翻转一次。
    PwmServo_Set_Angle(
        AKM_ANGLE_ID,
        Math_Limit_int(Ackerman_Get_Default_Angle() - akm_servo_angle, 0, 180));
}

// 按“正角左转、负角右转”的 REP-103 契约转向，并同步更新左右轮速。
void Ackerman_Steering_with_car(int16_t angle)
{
    Ackerman_Steering(angle);
    akm_angle = akm_servo_angle * AtR;
    speed_L_setup = akm_speed_fb*(1-AKM_WIDTH*tan(akm_angle)/2/AKM_LENGTH);
    speed_R_setup = akm_speed_fb*(1+AKM_WIDTH*tan(akm_angle)/2/AKM_LENGTH);
    speed_L_setup = Math_Limit_int(speed_L_setup, -AKM_MOTOR_MAX_SPEED, AKM_MOTOR_MAX_SPEED);
    speed_R_setup = Math_Limit_int(speed_R_setup, -AKM_MOTOR_MAX_SPEED, AKM_MOTOR_MAX_SPEED);
    Motion_Set_Speed(speed_R_setup, speed_L_setup, 0, 0);
}

// 获取阿克曼前轮舵机转向角度
int16_t Ackerman_Get_Steer_Angle(void)
{
    return akm_servo_angle;
}

// 获取阿克曼前轮舵机默认角度
uint16_t Ackerman_Get_Default_Angle(void)
{
    return g_ackerman_default_angle;
}

// 设置阿克曼前轮舵机默认角度
void Ackerman_Set_Default_Angle(uint16_t angle, uint8_t forever)
{
    if (angle > 180) return;
    g_ackerman_default_angle = angle;
    PwmServo_Set_Angle(AKM_ANGLE_ID, g_ackerman_default_angle);
    if(forever)
    {
        Flash_Set_AKM_Angle(g_ackerman_default_angle);
    }
}

uint8_t Ackerman_Get_Max_Steering_Angle(void)
{
    return g_ackerman_max_steering_angle;
}

int8_t Ackerman_Get_Center_Offset(void)
{
    return (int8_t)((int16_t)g_ackerman_default_angle - AKM_ANGLE_INIT);
}

uint8_t Ackerman_Set_Steering_Config(uint8_t max_angle, int8_t center_offset)
{
    if (max_angle < 1 || max_angle > AKM_ANGLE_LIMIT_MAX) return 0;
    if (center_offset < -AKM_CENTER_OFFSET_LIMIT ||
        center_offset > AKM_CENTER_OFFSET_LIMIT) return 0;

    Motion_Stop(STOP_BRAKE);
    akm_speed_fb = 0;
    g_ackerman_max_steering_angle = max_angle;
    akm_servo_target_angle = 0;
    akm_servo_angle = 0;
    Ackerman_Set_Default_Angle(AKM_ANGLE_INIT + center_offset, 0);
    return 1;
}


void Ackerman_Yaw_Calc(float yaw)
{
    float yaw_offset = PID_Yaw_Calc(yaw);
    g_offset_yaw = yaw_offset * g_speed_setup;

    // 用于调试打印偏差数据
    #if ENABLE_DEBUG_YAW
    static int aaaaaaaaa = 0;
    aaaaaaaaa++;
    if (aaaaaaaaa > 5)
    {
        aaaaaaaaa = 0;
        printf("Yaw Calc:%.5f, %d", yaw_offset, g_offset_yaw);
    }
    #endif

    int speed_L2 = speed_L_setup;
    int speed_R2 = speed_R_setup + g_offset_yaw;
    if (yaw > 0 && g_speed_setup > 0)
    {
        speed_L2 = speed_L_setup + g_offset_yaw;
    }
    else if (yaw < 0 && g_speed_setup > 0)
    {
        speed_R2 = speed_R_setup - g_offset_yaw;
    }
    
    Motion_Set_Speed(speed_R2, speed_L2, 0, 0);
}


// REP-103：V_x 正值前进，V_z 正值左转/逆时针。
// steering_deg 是显式舵角：正角左转，负角右转，并受运行时最大舵角限制。
void Ackerman_Ctrl(int16_t V_x, int16_t steering_deg, int16_t V_z, uint8_t adjust)
{
    int16_t target_servo_angle = akm_servo_target_angle;

    akm_speed_fb = V_x;
    if (steering_deg != 0xff) 
        target_servo_angle = Math_Limit_int(
            steering_deg, -g_ackerman_max_steering_angle, g_ackerman_max_steering_angle);
    if (V_x == 0)
    {
        Motion_Stop(STOP_BRAKE);
        Ackerman_Steering(target_servo_angle);
        DEBUG("akm stop steer:%d\n", akm_servo_angle);
        akm_speed_angle = 0;
        akm_angle = 0;
        return;
    }
    if (target_servo_angle == 0)
    {
        akm_speed_angle = V_z/1000.0f;
        akm_angle = atanf(akm_speed_angle*AKM_LENGTH/akm_speed_fb);
        target_servo_angle = Math_Limit_int(
            akm_angle*RtA,
            -g_ackerman_max_steering_angle,
            g_ackerman_max_steering_angle);
    }

    Ackerman_Steering(target_servo_angle);
    akm_angle = akm_servo_angle * AtR;
    speed_L_setup = akm_speed_fb*(1-AKM_WIDTH*tan(akm_angle)/2/AKM_LENGTH);
    speed_R_setup = akm_speed_fb*(1+AKM_WIDTH*tan(akm_angle)/2/AKM_LENGTH);
    speed_L_setup = Math_Limit_int(speed_L_setup, -AKM_MOTOR_MAX_SPEED, AKM_MOTOR_MAX_SPEED);
    speed_R_setup = Math_Limit_int(speed_R_setup, -AKM_MOTOR_MAX_SPEED, AKM_MOTOR_MAX_SPEED);
    
    Motion_Set_Speed(speed_R_setup, speed_L_setup, 0, 0);
}

// 控制阿克曼小车的运动状态
void Ackerman_State(uint8_t state, uint16_t speed, uint8_t adjust)
{
    g_speed_setup = 0;
    switch (state)
    {
    case MOTION_STOP:
        if (adjust)
        {
            Ackerman_Steering(0);
        }
        Motion_Stop(speed==0?STOP_FREE:STOP_BRAKE);
        akm_speed_fb = 0;
        break;
    case MOTION_RUN:
        g_speed_setup = speed;
        Motion_Set_Yaw_Adjust(adjust);
        Ackerman_Ctrl(speed, 0xff, 0, adjust);
        break;
    case MOTION_BACK:
        g_speed_setup = -speed;
        Motion_Set_Yaw_Adjust(adjust);
        Ackerman_Ctrl(-speed, 0xff, 0, adjust);
        break;
    case MOTION_LEFT:
        Motion_Set_Yaw_Adjust(0);
        Ackerman_Ctrl(speed, 25, 0, adjust);
        break;
    case MOTION_RIGHT:
        Motion_Set_Yaw_Adjust(0);
        Ackerman_Ctrl(speed, -25, 0, adjust);
        break;
    case MOTION_SPIN_LEFT:
        Motion_Set_Yaw_Adjust(0);
        Ackerman_Ctrl(speed, g_ackerman_max_steering_angle, 0, adjust);
        break;
    case MOTION_SPIN_RIGHT:
        Motion_Set_Yaw_Adjust(0);
        Ackerman_Ctrl(speed, -g_ackerman_max_steering_angle, 0, adjust);
        break;
    case MOTION_BRAKE:
        Ackerman_Steering(0);
        Motion_Stop(STOP_BRAKE);
        akm_speed_fb = 0;
        break;
    default:
        Motion_Set_Yaw_Adjust(0);
        break;
    }
}

// 返回当前阿克曼前轮舵机默认角度给主机。
void Ackerman_Send_Default_Angle(void)
{
    #define LEN        7
	uint8_t data_buffer[LEN] = {0};
	uint8_t i, checknum = 0;
	data_buffer[0] = PTO_HEAD;
	data_buffer[1] = PTO_DEVICE_ID-1;
	data_buffer[2] = LEN-2; // 数量
	data_buffer[3] = FUNC_AKM_DEF_ANGLE; // 功能位
	data_buffer[4] = AKM_ANGLE_ID+1;
	data_buffer[5] = g_ackerman_default_angle & 0xff;

	for (i = 2; i < LEN-1; i++)
	{
		checknum += data_buffer[i];
	}
	data_buffer[LEN-1] = checknum;
	USART1_Send_ArrayU8(data_buffer, sizeof(data_buffer));
	#undef LEN
}

void Ackerman_Send_Steering_Config(void)
{
    #define LEN        7
    uint8_t data_buffer[LEN] = {0};
    uint8_t i, checknum = 0;
    data_buffer[0] = PTO_HEAD;
    data_buffer[1] = PTO_DEVICE_ID-1;
    data_buffer[2] = LEN-2;
    data_buffer[3] = FUNC_AKM_STEER_CONFIG;
    data_buffer[4] = Ackerman_Get_Max_Steering_Angle();
    data_buffer[5] = (uint8_t)Ackerman_Get_Center_Offset();

    for (i = 2; i < LEN-1; i++)
    {
        checknum += data_buffer[i];
    }
    data_buffer[LEN-1] = checknum;
    USART1_Send_ArrayU8(data_buffer, sizeof(data_buffer));
    #undef LEN
}

