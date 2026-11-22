#ifndef __APP_MOTION_H__
#define __APP_MOTION_H__

#include "stdint.h"


// 205RPM电机，轮子转一整圈，编码器获得的脉冲数=减速比*码盘线数*编码器脉冲（56*11*4）
#define ENCODER_CIRCLE_205           (2464.0f)

// 330RPM电机，轮子转一整圈，编码器获得的脉冲数=减速比*码盘线数*编码器脉冲（30*11*4）
#define ENCODER_CIRCLE_330           (1320.0f)

// 450RPM电机，轮子转一整圈，编码器获得的脉冲数=减速比*码盘线数*编码器脉冲（20*13*4）
#define ENCODER_CIRCLE_450           (1040.0f)

// 550RPM电机，轮子转一整圈，编码器获得的脉冲数=减速比*码盘线数*编码器脉冲（19*11*4）
#define ENCODER_CIRCLE_550           (1340.0f)

// 轮子转一整圈的位移，单位为米
#define DISTANCE_CIRCLE      (0.204203)


// 停止模式，STOP_FREE表示自由停止，STOP_BRAKE表示刹车。
typedef enum _stop_mode {
    STOP_FREE = 0,
    STOP_BRAKE
} stop_mode_t;


typedef enum _motion_state {
    MOTION_STOP = 0,
    MOTION_RUN,
    MOTION_BACK,
    MOTION_LEFT,
    MOTION_RIGHT,
    MOTION_SPIN_LEFT,
    MOTION_SPIN_RIGHT,
    MOTION_BRAKE,

    MOTION_MAX_STATE
} motion_state_t;

typedef enum _motion_source {
    MOTION_SOURCE_NONE = 0,
    MOTION_SOURCE_PROTOCOL,
    MOTION_SOURCE_SBUS
} motion_source_t;


typedef struct _car_data
{
    int16_t Vx;
    int16_t Vy;
    int16_t Vz;
} car_data_t;


typedef enum _car_type
{
    CAR_TYPE_NONE = 0x00,       // 保留
    CAR_TYPE_RESERVED_01 = 0x01,
    CAR_TYPE_RESERVED_02 = 0x02,
    CAR_TYPE_RESERVED_03 = 0x03,
    CAR_FOURWHEEL = 0x04,       // 四轮普通小车
    CAR_ACKERMAN = 0x05,        // 阿克曼小车   R2
    CAR_SUNRISE = 0x06,         // 旭日派小车

    CAR_TYPE_MAX                // 最后一个小车类型，仅作为判断
} car_type_t;


void Motion_Stop(uint8_t brake);
void Motion_Set_Pwm(int16_t Motor_1, int16_t Motor_2, int16_t Motor_3, int16_t Motor_4);
void Motion_Ctrl(int16_t V_x, int16_t V_y, int16_t V_z, uint8_t adjust);
void Motion_Ctrl_State(uint8_t state, uint16_t speed, uint8_t adjust);


void Motion_Get_Encoder(void);
void Motion_Set_Speed(int16_t speed_m1, int16_t speed_m2, int16_t speed_m3, int16_t speed_m4);


void Motion_Handle(void);

void Motion_Get_Speed(car_data_t* car);
void Motion_Yaw_Calc(float yaw);

void Motion_Set_Yaw_Adjust(uint8_t adjust);
uint8_t Motion_Get_Yaw_Adjust(void);

void Motion_Set_Source(motion_source_t source);
motion_source_t Motion_Get_Source(void);

uint8_t Motion_Get_Car_Type(void);
void Motion_Set_Car_Type(car_type_t car_type);
float Motion_Get_Circle_MM(void);
float Motion_Get_APB(void);


void Motion_Get_Motor_Speed(float* speed);


void Motion_Send_Data(void);
void Motion_Send_Ackerman_Motor_State(void);
void Motion_Send_Car_Type(void);


#endif

