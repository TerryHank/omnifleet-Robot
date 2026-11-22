#include "app_tracked.h"

#include "app_motion.h"
#include "app_pid.h"
#include "FreeRTOS.h"
#include "task.h"

#include <math.h>

static int16_t requested_speed;
static int16_t requested_yaw_rate;
static float heading_yaw_rate;
static float yaw_rate_integral;
static uint16_t yaw_rate_kp_milli;
static uint16_t yaw_rate_ki_milli;

static int16_t Tracked_To_Protocol_Speed(float speed)
{
    if (speed > INT16_MAX) return INT16_MAX;
    if (speed < INT16_MIN) return INT16_MIN;
    return (int16_t)speed;
}

static void Tracked_Apply_Yaw_Rate(float rate, uint8_t heading_hold)
{
    float linear_speed = requested_speed;
    float turn_speed = rate * TRACKED_HALF_TRACK_MM;
    if (!heading_hold && requested_speed != 0 && requested_yaw_rate != 0)
    {
        turn_speed = copysignf(fminf(fabsf(turn_speed), TRACKED_ARC_WHEEL_LIMIT_MM_S),
                               turn_speed);
        const float travel_limit = TRACKED_ARC_WHEEL_LIMIT_MM_S - fabsf(turn_speed);
        linear_speed = copysignf(fminf(fabsf(linear_speed), travel_limit), linear_speed);
    }
    const int16_t left_speed = Tracked_To_Protocol_Speed(linear_speed - turn_speed);
    const int16_t right_speed = Tracked_To_Protocol_Speed(linear_speed + turn_speed);
    Motion_Set_Speed(right_speed, left_speed, 0, 0);
}

/* V_x: mm/s, V_z: mrad/s. Positive V_z turns left. */
void Tracked_Ctrl(int16_t V_x, int16_t V_y, int16_t V_z, uint8_t adjust)
{
    (void)V_y;
    if (V_x == 0 && V_z == 0)
    {
        Motion_Stop(STOP_BRAKE);
        return;
    }

    taskENTER_CRITICAL();
    const uint8_t hold = adjust && V_z == 0;
    const uint8_t was_held = Motion_Get_Yaw_Adjust();
    const uint8_t changed_direction = (V_x < 0) != (requested_speed < 0);
    if (hold != was_held || changed_direction ||
        (V_z == 0) != (requested_yaw_rate == 0) ||
        (V_z < 0) != (requested_yaw_rate < 0))
    {
        yaw_rate_integral = 0.0f;
    }
    const uint8_t changed = V_x != requested_speed || V_z != requested_yaw_rate ||
                            hold != was_held;
    requested_speed = V_x;
    requested_yaw_rate = V_z;
    if (hold && (!was_held || changed_direction))
    {
        heading_yaw_rate = 0.0f;
        Motion_Set_Yaw_Adjust(1);
    }
    else if (!hold && was_held)
    {
        Motion_Set_Yaw_Adjust(0);
    }
    if (changed)
    {
        Tracked_Apply_Yaw_Rate(V_z * 0.001f, hold);
    }
    taskEXIT_CRITICAL();
}

void Tracked_Yaw_Calc(float yaw)
{
    heading_yaw_rate = PID_Yaw_Calc(yaw);
}

/* Called before the wheel speed PID on each 10 ms speed tick. */
void Tracked_Yaw_Rate_Calc(float measured_rate)
{
    const uint8_t hold = Motion_Get_Yaw_Adjust();
    if (!hold && requested_yaw_rate == 0)
        return;

    const float rate_limit = hold ? 0.5f * fabsf((float)requested_speed) / TRACKED_HALF_TRACK_MM
                                  : TRACKED_ARC_WHEEL_LIMIT_MM_S / TRACKED_HALF_TRACK_MM;
    const float low = !hold && requested_yaw_rate > 0 ? 0.0f : -rate_limit;
    const float high = !hold && requested_yaw_rate < 0 ? 0.0f : rate_limit;
    const float desired = hold ? heading_yaw_rate : requested_yaw_rate * 0.001f;
    const float target = fminf(fmaxf(desired, low), high);
    float output = target;
    if (isfinite(measured_rate))
    {
        const float error = target - measured_rate;
        const float proportional = yaw_rate_kp_milli * 0.001f * error;
        const float next_integral = yaw_rate_integral + yaw_rate_ki_milli * 0.00001f * error;
        const float candidate = target + proportional + next_integral;
        if (!((candidate > high && error > 0.0f) || (candidate < low && error < 0.0f)))
            yaw_rate_integral = next_integral;
        output += proportional + yaw_rate_integral;
    }
    else
    {
        yaw_rate_integral = 0.0f;
    }
    Tracked_Apply_Yaw_Rate(fminf(fmaxf(output, low), high), hold);
}

void Tracked_Reset_Yaw_Rate(void)
{
    requested_speed = 0;
    requested_yaw_rate = 0;
    heading_yaw_rate = 0.0f;
    yaw_rate_integral = 0.0f;
}

void Tracked_Get_Yaw_Rate_PI(uint16_t *kp, uint16_t *ki)
{
    *kp = yaw_rate_kp_milli;
    *ki = yaw_rate_ki_milli;
}

void Tracked_Set_Yaw_Rate_PI(uint16_t kp, uint16_t ki)
{
    taskENTER_CRITICAL();
    yaw_rate_kp_milli = kp;
    yaw_rate_ki_milli = ki;
    yaw_rate_integral = 0.0f;
    taskEXIT_CRITICAL();
}

void Tracked_State(uint8_t state, uint16_t speed, uint8_t adjust)
{
    switch (state)
    {
    case MOTION_STOP:
        Motion_Stop(speed == 0 ? STOP_FREE : STOP_BRAKE);
        break;
    case MOTION_RUN:
        Tracked_Ctrl(speed, 0, 0, adjust);
        break;
    case MOTION_BACK:
        Tracked_Ctrl(-speed, 0, 0, adjust);
        break;
    case MOTION_LEFT:
    case MOTION_SPIN_LEFT:
        Tracked_Ctrl(0, 0, speed * 5, 0);
        break;
    case MOTION_RIGHT:
    case MOTION_SPIN_RIGHT:
        Tracked_Ctrl(0, 0, -speed * 5, 0);
        break;
    case MOTION_BRAKE:
        Motion_Stop(STOP_BRAKE);
        break;
    default:
        Motion_Stop(STOP_BRAKE);
        break;
    }
}
