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

// Sample Frequency
const rt_int32_t TIME_STEP_MS = 100;

// For 250 deg/s range, check the datasheet
double gSensitivity = 131;

// For 2g range, check the datasheet
double aSensitivity = 16384;

// Raw data from the IMU
rt_int16_t accel_x, accel_y, accel_z;
rt_int16_t gyro_x, gyro_y, gyro_z;

// Predicted Orientation (Gyro)
double gx = 0, gy = 0, gz = 0;

// Predicted Orientation (Acc)
double ax = 0, ay = 0;

double accelX = 0, accelY = 0, accelZ = 0;
double gyrX = 0, gyrY = 0, gyrZ = 0;

int main(void)
{
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
                accelX = accel_x / aSensitivity;
                accelY = accel_y / aSensitivity;
                accelZ = accel_z / aSensitivity;

                gyrX = gyro_x / gSensitivity;
                gyrY = gyro_y / gSensitivity;
                gyrZ = gyro_z / gSensitivity;

                // angles based on accelerometer
                ax = atan2(accelY, accelZ) * 180 / M_PI;                                      // roll
                ay = atan2(-accelX, sqrt( pow(accelY, 2) + pow(accelZ, 2))) * 180 / M_PI;    // pitch

                // This is incorrect, many tutorials make this mistake
                // ax = atan2(accelY, sqrt( pow(accelX, 2) + pow(accelZ, 2))) * 180 / M_PI;    // roll

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
