#ifndef __APP_TRACKED_H__
#define __APP_TRACKED_H__

#include "stdint.h"

/* OmniFleet T2: JGB37 motor, 54 mm drive wheel, 330 mm track-center separation. */
#define TRACKED_WHEEL_DIAMETER_MM       (54.0f)
#define TRACKED_WHEEL_CIRCLE_MM         (169.6460f)
#define TRACKED_TRACK_WIDTH_MM          (330.0f)
#define TRACKED_HALF_TRACK_MM           (165.0f)
/* Reserve steering headroom below the measured full-duty ground speed. */
#define TRACKED_ARC_WHEEL_LIMIT_MM_S    (460.0f)
#define TRACKED_ENCODER_CIRCLE          (1980.0f)

void Tracked_Ctrl(int16_t V_x, int16_t V_y, int16_t V_z, uint8_t adjust);
void Tracked_State(uint8_t state, uint16_t speed, uint8_t adjust);

#endif /* __APP_TRACKED_H__ */
