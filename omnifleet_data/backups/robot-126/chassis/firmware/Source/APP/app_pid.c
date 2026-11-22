#include <math.h>

#include "app_pid.h"
#include "app_motion.h"
#include "app_tracked.h"
#include "bsp_motor.h"
#include "bsp_encoder.h"
#include "bsp_usart.h"

#include "app.h"

#define PI      (3.1415926f)


motor_pid_t pid_motor[4];
static float tracked_turn_ff[MOTOR_ID_M2 + 1];
static float tracked_arc_relief[MOTOR_ID_M2 + 1];
static float tracked_arc_applied[MOTOR_ID_M2 + 1];

// YAW偏航角
PID pid_Yaw = {0, 0.4, 0, 0.1, 0, 0, 0};


/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////

// 初始化PID参数
void PID_Param_Init(void)
{
    tracked_turn_ff[MOTOR_ID_M1] = tracked_turn_ff[MOTOR_ID_M2] = 0.0f;
    tracked_arc_relief[MOTOR_ID_M1] = tracked_arc_relief[MOTOR_ID_M2] = 0.0f;
    tracked_arc_applied[MOTOR_ID_M1] = tracked_arc_applied[MOTOR_ID_M2] = 0.0f;
    /* 速度相关初始化参数 */
    for (int i = 0; i < MAX_MOTOR; i++)
    {
        pid_motor[i].target_val = 0.0;
        pid_motor[i].pwm_output = 0.0;
        pid_motor[i].err = 0.0;
        pid_motor[i].err_last = 0.0;
        pid_motor[i].err_next = 0.0;
        pid_motor[i].integral = 0.0;

        pid_motor[i].Kp = PID_DEF_KP;
        pid_motor[i].Ki = PID_DEF_KI;
        pid_motor[i].Kd = PID_DEF_KD;
    }

    pid_Yaw.Proportion = PID_YAW_DEF_KP;
    pid_Yaw.Integral = PID_YAW_DEF_KI;
    pid_Yaw.Derivative = PID_YAW_DEF_KD;
    
    #if PID_ASSISTANT_EN
    float pid_temp[3] = {pid_motor[0].Kp, pid_motor[0].Ki, pid_motor[0].Kd};
    set_computer_value(SEND_P_I_D_CMD, CURVES_CH1, pid_temp, 3);     // 给通道 1 发送 P I D 值
    #endif
}

// 设置PID参数
void PID_Set_Parm(motor_pid_t *pid, float p, float i, float d)
{
    pid->Kp = p; // 设置比例系数 P
    pid->Ki = i; // 设置积分系数 I
    pid->Kd = d; // 设置微分系数 D
}

// 设置PID的目标值
void PID_Set_Target(motor_pid_t *pid, float temp_val)
{
    pid->target_val = temp_val; // 设置当前的目标值
}

// 获取PID目标值
float PID_Get_Target(motor_pid_t *pid)
{
    return pid->target_val; // 设置当前的目标值
}

// 增量式PID计算公式
float PID_Incre_Calc(motor_pid_t *pid, float actual_val)
{
    /*计算目标值与实际值的误差*/
    pid->err = pid->target_val - actual_val;
    /*PID算法实现*/
    pid->pwm_output += pid->Kp * (pid->err - pid->err_next) 
                    + pid->Ki * pid->err 
                    + pid->Kd * (pid->err - 2 * pid->err_next + pid->err_last);
    /*传递误差*/
    pid->err_last = pid->err_next;
    pid->err_next = pid->err;
    
    /*返回PWM输出值*/
    if (Motion_Get_Car_Type() == CAR_SUNRISE)
    {
        if (pid->pwm_output > (MOTOR_MAX_PULSE-MOTOR_SUNRISE_IGNORE_PULSE))
            pid->pwm_output = (MOTOR_MAX_PULSE-MOTOR_SUNRISE_IGNORE_PULSE);
        if (pid->pwm_output < (MOTOR_SUNRISE_IGNORE_PULSE-MOTOR_MAX_PULSE))
            pid->pwm_output = (MOTOR_SUNRISE_IGNORE_PULSE-MOTOR_MAX_PULSE);
    }
    else if (Motion_Get_Car_Type() == CAR_TRACKED)
    {
        float limit = MOTOR_MAX_PULSE;
        if (pid->pwm_output > limit)
            pid->pwm_output = limit;
        if (pid->pwm_output < -limit)
            pid->pwm_output = -limit;
    }
    else
    {
        if (pid->pwm_output > (MOTOR_MAX_PULSE-MOTOR_IGNORE_PULSE))
            pid->pwm_output = (MOTOR_MAX_PULSE-MOTOR_IGNORE_PULSE);
        if (pid->pwm_output < (MOTOR_IGNORE_PULSE-MOTOR_MAX_PULSE))
            pid->pwm_output = (MOTOR_IGNORE_PULSE-MOTOR_MAX_PULSE);
    }
    return pid->pwm_output;
}

// 位置式PID计算方式
float PID_Location_Calc(motor_pid_t *pid, float actual_val)
{
	/*计算目标值与实际值的误差*/
    pid->err = pid->target_val - actual_val;
  
    /* 限定闭环死区 */
    if((pid->err >= -40) && (pid->err <= 40))
    {
        pid->err = 0;
        pid->integral = 0;
    }
    
    /* 积分分离，偏差较大时去掉积分作用 */
    if (pid->err > -1500 && pid->err < 1500)
    {
        pid->integral += pid->err;    // 误差累积

        /* 限定积分范围，防止积分饱和 */
        if (pid->integral > 4000)
            pid->integral = 4000;
        else if (pid->integral < -4000)
            pid->integral = -4000;
    }

	/*PID算法实现*/
    pid->output_val = pid->Kp * pid->err + 
                      pid->Ki * pid->integral + 
                      pid->Kd * (pid->err - pid->err_last);

	/*误差传递*/
    pid->err_last = pid->err;
    
	/*返回当前实际值*/
    return pid->output_val;
}


// PID计算输出值
void PID_Calc_Motor(motor_data_t* motor)
{
    int i;
    const uint8_t tracked = Motion_Get_Car_Type() == CAR_TRACKED;
    /* Hiwonder JGB37 uses 40 permille per r/s of current speed error. */
    const float startup_kp = (40.0f * MOTOR_MAX_PULSE / MOTOR_PWM_DUTY_MAX) / TRACKED_WHEEL_CIRCLE_MM;
    const uint8_t counter_rotating = tracked &&
        ((int32_t)motor->speed_set[MOTOR_ID_M1] * motor->speed_set[MOTOR_ID_M2] < 0);
    const float start_duty_limit = 0.60f * MOTOR_MAX_PULSE;
    // float pid_out[4] = {0};
    // for (i = 0; i < MAX_MOTOR; i++)
    // {
    //     pid_out[i] = PID_Location_Calc(&pid_motor[i], 0);
    //     PID_Set_Motor_Target(i, pid_out[i]);
    // }
    
    for (i = 0; i < MAX_MOTOR; i++)
    {
        if (tracked && motor->speed_set[i] == 0)
        {
            PID_Clear_Motor(i);
            motor->speed_pwm[i] = 0;
        }
        else
        {
            if (counter_rotating && i <= MOTOR_ID_M2)
            {
                const float target = pid_motor[i].target_val;
                const float speed_ratio = fabsf(target) / TRACKED_HALF_TRACK_MM;
                /* Taper friction duty to zero for small speed requests. */
                const float duty = 0.70f * fminf(speed_ratio / 0.35f, 1.0f) +
                                   0.20f * fminf(speed_ratio, 1.0f);
                const float ff = copysignf(duty * MOTOR_MAX_PULSE, target);
                if (tracked_turn_ff[i] == 0.0f || ff * tracked_turn_ff[i] < 0.0f)
                {
                    PID_Clear_Motor(i);
                }
                /* The incremental controller stores the combined output. */
                pid_motor[i].pwm_output += ff - tracked_turn_ff[i];
                tracked_turn_ff[i] = ff;
            }
            else if (i <= MOTOR_ID_M2 && tracked_turn_ff[i] != 0.0f)
            {
                if (tracked_turn_ff[i] * pid_motor[i].target_val < 0.0f)
                    PID_Clear_Motor(i);
                else
                    tracked_turn_ff[i] = 0.0f;
            }
            if (tracked && !counter_rotating && i <= MOTOR_ID_M2)
            {
                const float target = motor->speed_set[i];
                const float other = motor->speed_set[i == MOTOR_ID_M1 ? MOTOR_ID_M2 : MOTOR_ID_M1];
                float relief = 0.0f;
                if (target * other > 0.0f && fabsf(other) > fabsf(target))
                {
                    /* Remove inner-track drive as soon as the differential is requested. */
                    relief = -copysignf((fabsf(other) - fabsf(target)) *
                                       (MOTOR_MAX_PULSE / TRACKED_ARC_WHEEL_LIMIT_MM_S), target);
                }
                if (tracked_arc_relief[i] * target > 0.0f)
                    PID_Clear_Motor(i);
                float delta = relief - tracked_arc_relief[i];
                const float previous_pwm = pid_motor[i].pwm_output;
                if (delta * target < 0.0f && (previous_pwm + delta) * target < 0.0f)
                    delta = previous_pwm * target > 0.0f ? -previous_pwm : 0.0f;
                else if (delta * target > 0.0f && fabsf(delta) > fabsf(tracked_arc_applied[i]))
                    delta = -tracked_arc_applied[i];
                pid_motor[i].pwm_output += delta;
                tracked_arc_applied[i] += delta;
                tracked_arc_relief[i] = relief;
            }
            float pwm = PID_Incre_Calc(&pid_motor[i], motor->speed_mm_s[i]);
            /* Keep the existing startup behavior for straight driving. */
            if (tracked && !counter_rotating && i <= MOTOR_ID_M2 && fabsf(motor->speed_mm_s[i]) < 20.0f &&
                fabsf(pwm) < start_duty_limit)
            {
                pwm += startup_kp * pid_motor[i].err;
                if (pwm > start_duty_limit) pwm = start_duty_limit;
                if (pwm < -start_duty_limit) pwm = -start_duty_limit;
                pid_motor[i].pwm_output = pwm;
            }
            motor->speed_pwm[i] = pwm;
        }
    }
}

// PID单独计算一条通道
float PID_Calc_One_Motor(uint8_t motor_id, float now_speed)
{
    if (motor_id >= MAX_MOTOR) return 0; 
    return PID_Incre_Calc(&pid_motor[motor_id], now_speed);
}

// 设置PID参数，motor_id=4设置所有，=0123设置对应电机的PID参数。
void PID_Set_Motor_Parm(uint8_t motor_id, float kp, float ki, float kd)
{
    if (motor_id > MAX_MOTOR) return;

    if (motor_id == MAX_MOTOR)
    {
        for (int i = 0; i < MAX_MOTOR; i++)
        {
            pid_motor[i].Kp = kp;
            pid_motor[i].Ki = ki;
            pid_motor[i].Kd = kd;
        }
        DEBUG("PID Set:%.3f, %.3f, %.3f\n", kp, ki, kd);
    }
    else
    {
        pid_motor[motor_id].Kp = kp;
        pid_motor[motor_id].Ki = ki;
        pid_motor[motor_id].Kd = kd;
        DEBUG("PID Set M%d:%.3f, %.3f, %.3f\n", motor_id+1, kp, ki, kd);
    }
}

// 清除PID数据
void PID_Clear_Motor(uint8_t motor_id)
{
    if (motor_id > MAX_MOTOR) return;
    if (motor_id <= MOTOR_ID_M2)
    {
        tracked_turn_ff[motor_id] = 0.0f;
        tracked_arc_relief[motor_id] = 0.0f;
        tracked_arc_applied[motor_id] = 0.0f;
    }

    if (motor_id == MAX_MOTOR)
    {
        tracked_turn_ff[MOTOR_ID_M1] = tracked_turn_ff[MOTOR_ID_M2] = 0.0f;
        tracked_arc_relief[MOTOR_ID_M1] = tracked_arc_relief[MOTOR_ID_M2] = 0.0f;
        tracked_arc_applied[MOTOR_ID_M1] = tracked_arc_applied[MOTOR_ID_M2] = 0.0f;
        for (int i = 0; i < MAX_MOTOR; i++)
        {
            pid_motor[i].pwm_output = 0.0;
            pid_motor[i].err = 0.0;
            pid_motor[i].err_last = 0.0;
            pid_motor[i].err_next = 0.0;
            pid_motor[i].integral = 0.0;
        }
    }
    else
    {
        pid_motor[motor_id].pwm_output = 0.0;
        pid_motor[motor_id].err = 0.0;
        pid_motor[motor_id].err_last = 0.0;
        pid_motor[motor_id].err_next = 0.0;
        pid_motor[motor_id].integral = 0.0;
    }
}

// 设置PID目标速度，单位为：mm/s
void PID_Set_Motor_Target(uint8_t motor_id, float target)
{
    if (motor_id > MAX_MOTOR) return;

    if (motor_id == MAX_MOTOR)
    {
        for (int i = 0; i < MAX_MOTOR; i++)
        {
            pid_motor[i].target_val = target;
        }
    }
    else
    {
        pid_motor[motor_id].target_val = target;
    }
}

// 返回PID结构体数组
motor_pid_t* Pid_Get_Motor(void)
{
    return pid_motor;
}


/* 串口发送PID数据到主控上，index=1~5，1~4表示四路电机，5表示YAW */
void PID_Send_Parm_Active(uint8_t index)
{
    #define LEN        12
	uint8_t data_buffer[LEN] = {0};
	uint8_t i, checknum = 0;
    if (index > 0 && index < 6)
    {
        data_buffer[0] = PTO_HEAD;
        data_buffer[1] = PTO_DEVICE_ID-1;
        data_buffer[2] = LEN-2; // 数量
        data_buffer[3] = FUNC_SET_MOTOR_PID; // 功能位
        data_buffer[4] = index;
        if (index == 5)
        {
            data_buffer[3] = FUNC_SET_YAW_PID; // 功能位
            data_buffer[5] = (int32_t)(pid_Yaw.Proportion * 1000) & 0xff;
            data_buffer[6] = ((int32_t)(pid_Yaw.Proportion * 1000) >> 8) & 0xff;
            data_buffer[7] = (int32_t)(pid_Yaw.Integral * 1000) & 0xff;
            data_buffer[8] = ((int32_t)(pid_Yaw.Integral * 1000) >> 8) & 0xff;
            data_buffer[9] = (int32_t)(pid_Yaw.Derivative * 1000) & 0xff;
            data_buffer[10] = ((int32_t)(pid_Yaw.Derivative * 1000) >> 8) & 0xff;
        }
        else
        {
            data_buffer[5] = (int32_t)(pid_motor[index-1].Kp * 1000) & 0xff;
            data_buffer[6] = ((int32_t)(pid_motor[index-1].Kp * 1000) >> 8) & 0xff;
            data_buffer[7] = (int32_t)(pid_motor[index-1].Ki * 1000) & 0xff;
            data_buffer[8] = ((int32_t)(pid_motor[index-1].Ki * 1000) >> 8) & 0xff;
            data_buffer[9] = (int32_t)(pid_motor[index-1].Kd * 1000) & 0xff;
            data_buffer[10] = ((int32_t)(pid_motor[index-1].Kd * 1000) >> 8) & 0xff;
        }
        for (i = 2; i < LEN-1; i++)
        {
            checknum += data_buffer[i];
        }
        data_buffer[LEN-1] = checknum;
        USART1_Send_ArrayU8(data_buffer, sizeof(data_buffer));
    }
}

/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////



// 重置偏航角的目标值
void PID_Yaw_Reset(float yaw)
{
	pid_Yaw.SetPoint = yaw;
    pid_Yaw.SumError = 0;
    pid_Yaw.LastError = 0;
    pid_Yaw.PrevError = 0;
}

// 计算偏航角的输出值
float PID_Yaw_Calc(float NextPoint)
{
	float dError, Error;
	Error = pid_Yaw.SetPoint - NextPoint;			// 偏差
	pid_Yaw.SumError += Error;						// 积分
	dError = pid_Yaw.LastError - pid_Yaw.PrevError; // 当前微分
	pid_Yaw.PrevError = pid_Yaw.LastError;
	pid_Yaw.LastError = Error;

	double omega_rad = pid_Yaw.Proportion * Error			 // 比例项
					   + pid_Yaw.Integral * pid_Yaw.SumError // 积分项
					   + pid_Yaw.Derivative * dError;		 // 微分项

	if (omega_rad > PI / 6)
		omega_rad = PI / 6;
	if (omega_rad < -PI / 6)
		omega_rad = -PI / 6;
	return omega_rad;
}

// 设置偏航角PID的参数
void PID_Yaw_Set_Parm(float kp, float ki, float kd)
{
    pid_Yaw.Proportion = kp;
    pid_Yaw.Integral = ki;
    pid_Yaw.Derivative = kd;
}

