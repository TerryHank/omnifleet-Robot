#include <assert.h>
#include "ackermann_chassis.h"
static float left, right;
static int position;
static void capture(void *self, float l, float r, int p)
{
    (void)self;
    left = l;
    right = r;
    position = p;
}
int main(void)
{
    AckermannChassisTypeDef c = {
        .wheel_diameter = 100, .wheelbase = 224.92f, .shaft_length = 213.33f,
        .set_motors = capture
    };
    ackermann_chassis_object_init(&c);
    c.base.set_velocity_radius(&c, 100, 0, false);
    assert(left > 0 && left == right && position == 500);
    c.base.set_velocity_radius(&c, 100, 500, false);
    assert(left > 0 && right > left && position > 500);
    c.base.set_velocity_radius(&c, 100, -500, false);
    assert(right > 0 && left > right && position < 500);
    c.base.set_velocity_radius(&c, -100, -1, false);
    assert(left < right && right < 0 && position >= 375);
    c.base.set_velocity_radius(&c, 0, 500, false);
    assert(left == 0 && right == 0 && position > 500);
    c.base.stop(&c);
    assert(left == 0 && right == 0 && position == 500);
    return 0;
}
