#include "global.h"
#include "differential_chassis.h"
#include "mecanum_chassis.h"
#include "ackermann_chassis.h"
#include "encoder_motor.h"
#include "chassis.h"
#include "serial_servo.h"
#include "motors_param.h"

DifferentialChassisTypeDef jetank;
DifferentialChassisTypeDef tank_black;
DifferentialChassisTypeDef ti4wd;
MecanumChassisTypeDef      jetauto;
AckermannChassisTypeDef   jetacker;



static void jetank_set_motors(void* self, float rps_l, float rps_r)
{
    encoder_motor_set_speed(motors[0], rps_r);
    encoder_motor_set_speed(motors[3], -rps_l);
}


static void tankblack_set_motors(void* self, float rps_l, float rps_r)
{
    encoder_motor_set_speed(motors[0], -rps_l);
    encoder_motor_set_speed(motors[1], rps_r);
}

static void ti4wd_set_motors(void* self, float rps_l, float rps_r)
{
    encoder_motor_set_speed(motors[3], rps_r);
    encoder_motor_set_speed(motors[2], rps_r);
    encoder_motor_set_speed(motors[0], -rps_l);
    encoder_motor_set_speed(motors[1], -rps_l);
}

static void jetauto_set_motors(void* self, float rps_lh, float rps_lt, float rps_rh, float rps_rt)
{
    encoder_motor_set_speed(motors[1], rps_lh);
    encoder_motor_set_speed(motors[0], rps_lt);
    encoder_motor_set_speed(motors[2], -rps_rh);
    encoder_motor_set_speed(motors[3], -rps_rt);
}

static void jetacker_set_motors(void *self, float rps_left, float rps_right, int position)
{
    (void)self;
    static int position_last = -1;
    if (position_last != position) {
        PWMServoObjectTypeDef *servo = pwm_servos[2];
        servo->target_duty = 1500 + (position - 500) * 2;
        servo->current_duty = servo->target_duty;
        servo->duty_raw = servo->current_duty + servo->offset;
        servo->duty_raw = servo->duty_raw < 500 ? 500 : (servo->duty_raw > 2500 ? 2500 : servo->duty_raw);
        servo->is_running = false;
        servo->duty_changed = false;
        position_last = position;
    }
    encoder_motor_set_speed(motors[0], rps_left);
    encoder_motor_set_speed(motors[1], -rps_right);
}


/* The final 128 KiB sector stores one committed calibration per 32-bit word.
 * Complemented values reject incomplete programming after power loss.
 * Append-only writes preserve the preceding calibration on an interrupted save. */
#define STEERING_CONFIG_START 0x08060000U
#define STEERING_CONFIG_END   0x08080000U
static uint8_t steering_center_angle = 90;
static uint32_t steering_config_next = STEERING_CONFIG_START;

uint8_t steering_center_get(void)
{
    return steering_center_angle;
}

static void steering_center_apply(uint8_t angle)
{
    PWMServoObjectTypeDef *servo = pwm_servos[2];
    const uint32_t irq = __get_PRIMASK();
    __disable_irq();
    steering_center_angle = angle;
    servo->offset = ((int)angle - 90) * 2000 / 180;
    int duty = servo->current_duty + servo->offset;
    servo->duty_raw = duty < 500 ? 500 : (duty > 2500 ? 2500 : duty);
    __set_PRIMASK(irq);
}

static void steering_center_load(void)
{
    uint8_t angle = 90;
    for (uint32_t address = STEERING_CONFIG_START; address < STEERING_CONFIG_END; address += 4) {
        const uint32_t word = *(const volatile uint32_t *)address;
        if (word == 0xffffffffU) {
            steering_config_next = address;
            steering_center_apply(angle);
            return;
        }
        const uint8_t saved = (uint8_t)word;
        if ((word >> 16) == 0xC741U && saved <= 180 &&
            ((word >> 8) & 0xffU) == ((uint32_t)saved ^ 0xffU))
            angle = saved;
    }
    steering_config_next = STEERING_CONFIG_END;
    steering_center_apply(angle);
}

bool steering_center_save(uint8_t angle)
{
    if (angle > 180) return false;
    if (angle == steering_center_angle) return true;
    if (steering_config_next >= STEERING_CONFIG_END) return false;

    const uint32_t word = 0xC7410000U | (((uint32_t)angle ^ 0xffU) << 8) | angle;
    const uint32_t address = steering_config_next;
    if (HAL_FLASH_Unlock() != HAL_OK) return false;
    const HAL_StatusTypeDef status = HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, address, word);
    HAL_FLASH_Lock();
    /* A failed word is consumed too, so retries never program over partial data. */
    if (*(const volatile uint32_t *)address != 0xffffffffU)
        steering_config_next += 4;
    if (status != HAL_OK || *(const volatile uint32_t *)address != word) return false;
    steering_center_apply(angle);
    return true;
}

ChassisTypeDef *chassis = (ChassisTypeDef*)&jetauto;

void chassis_init(void)
{
    diff_chassis_object_init(&jetank);
    jetank.base.chassis_type = CHASSIS_TYPE_JETTANK;
    jetank.correction_factor = JETTANK_CORRECITION_FACTOR;
    jetank.wheel_diameter = JETTANK_WHEEL_DIAMETER;
    jetank.shaft_length = JETTANK_SHAFT_LENGTH;
    jetank.set_motors = jetank_set_motors;

    diff_chassis_object_init(&tank_black);
    tank_black.base.chassis_type = CHASSIS_TYPE_JETTANK;
    tank_black.correction_factor = JETTANK_CORRECITION_FACTOR;
    tank_black.wheel_diameter = JETTANK_WHEEL_DIAMETER;
    tank_black.shaft_length = JETTANK_SHAFT_LENGTH;
    tank_black.set_motors = tankblack_set_motors;

    diff_chassis_object_init(&ti4wd);
    ti4wd.base.chassis_type = CHASSIS_TYPE_TI4WD;
    ti4wd.correction_factor = TI4WD_CORRECITION_FACTOR;
    ti4wd.wheel_diameter = TI4WD_WHEEL_DIAMETER;
    ti4wd.shaft_length = TI4WD_SHAFT_LENGTH;
    ti4wd.set_motors = ti4wd_set_motors;

    mecanum_chassis_object_init(&jetauto);
    jetauto.base.chassis_type = CHASSIS_TYPE_JETAUTO;
    jetauto.correction_factor = JETAUTO_CORRECITION_FACTOR;
    jetauto.wheel_diameter = JETAUTO_WHEEL_DIAMETER;
    jetauto.shaft_length = JETAUTO_SHAFT_LENGTH;
    jetauto.wheelbase = JETAUTO_WHEELBASE;
    jetauto.set_motors = jetauto_set_motors;
		
	ackermann_chassis_object_init(&jetacker);
    jetacker.base.chassis_type = CHASSIS_TYPE_JETACKER;
    jetacker.correction_factor = JETACKER_CORRECITION_FACTOR;
    jetacker.wheel_diameter = JETACKER_WHEEL_DIAMETER;
    jetacker.shaft_length = JETACKER_SHAFT_LENGTH;
    jetacker.wheelbase = JETACKER_WHEELBASE;
    jetacker.set_motors = jetacker_set_motors;
    steering_center_load();

}

void set_chassis_type(uint8_t chassis_type)
{
    switch(chassis_type) {
        case CHASSIS_TYPE_JETAUTO:
            chassis = (ChassisTypeDef*)&jetauto;
            set_motor_type(motors[0], MOTOR_TYPE_JGB520);
            set_motor_type(motors[1], MOTOR_TYPE_JGB520);
            set_motor_type(motors[2], MOTOR_TYPE_JGB520);
            set_motor_type(motors[3], MOTOR_TYPE_JGB520);
            break;
		case CHASSIS_TYPE_JETACKER:
            chassis = (ChassisTypeDef*)&jetacker;
            set_motor_type(motors[0], MOTOR_TYPE_JGB520);
            motors[0]->rps_limit = 9.55f;  /* 3 m/s at 100 mm wheel diameter */
            set_motor_type(motors[1], MOTOR_TYPE_JGB520);
            motors[1]->rps_limit = 9.55f;  /* 3 m/s at 100 mm wheel diameter */
            set_motor_type(motors[2], MOTOR_TYPE_JGB520);
            set_motor_type(motors[3], MOTOR_TYPE_JGB520);
            break;

        case CHASSIS_TYPE_JETTANK:
            chassis = (ChassisTypeDef*)&jetank;
            set_motor_type(motors[0], MOTOR_TYPE_JGB528);
            set_motor_type(motors[1], MOTOR_TYPE_JGB528);
            set_motor_type(motors[2], MOTOR_TYPE_JGB528);
            set_motor_type(motors[3], MOTOR_TYPE_JGB528);
            break;
        case CHASSIS_TYPE_TI4WD:
            chassis = (ChassisTypeDef*)&ti4wd;
            set_motor_type(motors[0], MOTOR_TYPE_JGA27);
            set_motor_type(motors[1], MOTOR_TYPE_JGA27);
            set_motor_type(motors[2], MOTOR_TYPE_JGA27);
            set_motor_type(motors[3], MOTOR_TYPE_JGA27);
			break;
        case CHASSIS_TYPE_TANKBLACK:
            chassis = (ChassisTypeDef*)&tank_black;
            set_motor_type(motors[0], MOTOR_TYPE_JGB37);
            set_motor_type(motors[1], MOTOR_TYPE_JGB37);
            set_motor_type(motors[2], MOTOR_TYPE_JGB37);
            set_motor_type(motors[3], MOTOR_TYPE_JGB37);
			break;
        default:
            break;
    }
}

