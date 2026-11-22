#include "app_tracked.h"

#include "app_motion.h"

#include <math.h>

static int16_t Tracked_To_Protocol_Speed(float speed)
{
    if (speed > INT16_MAX) return INT16_MAX;
    if (speed < INT16_MIN) return INT16_MIN;
    return (int16_t)speed;
}

/* V_x: mm/s, V_z: mrad/s. Positive V_z turns left. */
void Tracked_Ctrl(int16_t V_x, int16_t V_y, int16_t V_z, uint8_t adjust)
{
    float linear_speed = V_x;
    float turn_speed;
    int16_t left_speed;
    int16_t right_speed;

    (void)V_y;
    (void)adjust;

    if (V_x == 0 && V_z == 0)
    {
        Motion_Stop(STOP_BRAKE);
        return;
    }

    turn_speed = V_z / 1000.0f * TRACKED_HALF_TRACK_MM;
    if (V_x != 0 && V_z != 0)
    {
        /* Allocate the differential first; use the remaining speed for travel. */
        turn_speed = copysignf(fminf(fabsf(turn_speed), TRACKED_ARC_WHEEL_LIMIT_MM_S),
                               turn_speed);
        const float travel_limit = TRACKED_ARC_WHEEL_LIMIT_MM_S - fabsf(turn_speed);
        linear_speed = copysignf(fminf(fabsf(linear_speed), travel_limit), linear_speed);
    }
    left_speed = Tracked_To_Protocol_Speed(linear_speed - turn_speed);
    right_speed = Tracked_To_Protocol_Speed(linear_speed + turn_speed);

    /* Keep the official motor sign convention; only the tracked-body
       differential inverse kinematics is specific to this chassis. */
    Motion_Set_Speed(right_speed, left_speed, 0, 0);
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
