#ifndef __APP_ACKERMAN_H__
#define __APP_ACKERMAN_H__

#include "stdint.h"

// 阿克曼车底盘间距
#define AKM_WIDTH                      (245.400f)   // 毫米 后轮轮距
#define AKM_LENGTH                     (362.296f)   // 毫米 轴距

// 阿克曼小车轮子转一整圈的位移，单位为MM (轮径106mm)
#define AKM_CIRCLE_MM                  (367.74f)

// 舵机ID和初始化角度
#define AKM_ANGLE_ID                   (PWMServo_ID_S1)
#define AKM_ANGLE_INIT                 (90)
#define AKM_ANGLE_LIMIT_DEFAULT        (40)
#define AKM_ANGLE_LIMIT_MAX            (40)
#define AKM_CENTER_OFFSET_LIMIT        (40)


// 阿克曼小车电机最高速度
#define AKM_MOTOR_MAX_SPEED            (2000)


int16_t Ackerman_Get_Steer_Angle(void);
void Ackerman_Steering(int16_t angle);
void Ackerman_Steering_with_car(int16_t angle);
void Ackerman_Ctrl(int16_t V_x, int16_t steering_deg, int16_t V_z, uint8_t adjust);
void Ackerman_State(uint8_t state, uint16_t speed, uint8_t adjust);
uint16_t Ackerman_Get_Default_Angle(void);
void Ackerman_Set_Default_Angle(uint16_t angle, uint8_t forever);
uint8_t Ackerman_Get_Max_Steering_Angle(void);
int8_t Ackerman_Get_Center_Offset(void);
uint8_t Ackerman_Set_Steering_Config(uint8_t max_angle, int8_t center_offset);

void Ackerman_Send_Default_Angle(void);
void Ackerman_Send_Steering_Config(void);

void Ackerman_Yaw_Calc(float yaw);

#endif /* __APP_ACKERMAN_H__ */
