#include "ackermann_chassis.h"
#include <math.h>

#define PI 3.141592654f
#define MAX_STEERING_RATIO 1.732050808f  /* tan(60 degrees) */

void ackermann_chassis_move(AckermannChassisTypeDef *self, float vx, float radius)
{
    float steering_ratio = radius == 0.0f ? 0.0f : self->wheelbase / radius;
    steering_ratio = fminf(MAX_STEERING_RATIO, fmaxf(-MAX_STEERING_RATIO, steering_ratio));

    const float wheel_difference = steering_ratio * self->shaft_length / (2.0f * self->wheelbase);
    const float rps = vx / (PI * self->wheel_diameter);
    const int position = 500 + (int)(steering_ratio * 187.5f);

    self->set_motors(self, rps * (1.0f - wheel_difference),
                    rps * (1.0f + wheel_difference), position);
}

static void stop(void *self)
{
    ackermann_chassis_move(self, 0.0f, 0.0f);
}

static void set_velocity(void *self, float vx, float vy, float radius)
{
    (void)vy;
    ackermann_chassis_move(self, vx, radius);
}

static void set_velocity_radius(void *self, float linear, float radius, bool swerve)
{
    (void)swerve;
    ackermann_chassis_move(self, linear, radius);
}

void ackermann_chassis_object_init(AckermannChassisTypeDef *self)
{
    self->base.stop = stop;
    self->base.set_velocity = set_velocity;
    self->base.set_velocity_radius = set_velocity_radius;
}
