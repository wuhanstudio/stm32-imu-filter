/*
 * Copyright (c) 2006-2021, RT-Thread Development Team
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Change Logs:
 * Date           Author       Notes
 * 2018-11-06     SummerGift   first version
 */

#include <rtthread.h>
#include <rtdevice.h>
#include <board.h>
#include <math.h>
#include <icm20608.h>
#include <stdio.h>

/* defined the LED0 pin: PE7 */
#define LED0_PIN    GET_PIN(E, 7)

// global angle, gyro derived
rt_int16_t accel_x, accel_y, accel_z;
rt_int16_t gyro_x, gyro_y, gyro_z;

double gx = 0, gy = 0, gz = 0;
double gyrX = 0, gyrY = 0, gyrZ = 0;

// For 250 deg/s, check data sheet
double gSensitivity = 131;

double aSensitivity = 16384;

const rt_int32_t TIME_STEP_MS = 100;

int main(void)
{
    double ax, ay;

    /* set LED0 pin mode to output */
    rt_pin_mode(LED0_PIN, PIN_MODE_OUTPUT);

    icm20608_device_t imu = icm20608_init("i2c3");
    if(imu != RT_NULL)
    {
        rt_kprintf("Initialized IMU\n");
    }

    icm20608_calib_level(imu, 500);

    while (1)
    {
        rt_tick_t prevTime = rt_tick_get();

        if (icm20608_get_accel(imu, &accel_x, &accel_y, &accel_z) == RT_EOK)
        {
            if(icm20608_get_gyro(imu, &gyro_x, &gyro_y, &gyro_z) == RT_EOK)
            {
                accel_x = accel_x / aSensitivity;
                accel_y = accel_y / aSensitivity;
                accel_z = accel_z / aSensitivity;

                gyrX = gyro_x / gSensitivity;
                gyrY = gyro_y / gSensitivity;
                gyrZ = gyro_z / gSensitivity;

                // angles based on accelerometer
                ax = atan2(accel_y, accel_z) * 180 / M_PI;                                      // roll
                ay = atan2(-accel_x, sqrt( pow(accel_y, 2) + pow(accel_z, 2))) * 180 / M_PI;    // pitch

                // This is incorrect, many tutorials make this mistake
                // ax = atan2(accel_y, sqrt( pow(accel_x, 2) + pow(accel_z, 2))) * 180 / M_PI;    // roll

                // angles based on gyro (deg/s)
                gx = gx + gyrX * TIME_STEP_MS / 1000;
                gy = gy + gyrY * TIME_STEP_MS / 1000;
                gz = gz + gyrZ * TIME_STEP_MS / 1000;

                // complementary filter
                gx = gx * 0.96 + ax * 0.04;
                gy = gy * 0.96 + ay * 0.04;

                printf("%d %d %d %d %d %d %.4f %.4f %.4f \n", accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, gx, gy, gz);
            }
        };

        while( (rt_tick_get() - prevTime) < rt_tick_from_millisecond(TIME_STEP_MS));
    }
}
