#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import smbus
import time
import sys
import csv
import signal
import RPi.GPIO as GPIO

import sensor
#import moter
import gps

mpu = sensor.MPU9250()
lps = sensor.LPS22HB()
#servo = moter.SERVO()
#step = moter.STEPPING()
gps = gps.GPS()

def exit_handler(siglal, frame):
    #C-c is finish
    print("\nExit")
    time.sleep(0.5)
    GPIO.cleanup()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, exit_handler)
    #GPIO.setmode(GPIO.BCM)
    mpu.resetRegister()
    mpu.powerWakeUp()
    mpu.setAccelRange(8, True)       #加速度のキャリブレーションon
    mpu.setGyroRange(1000, True)     #ジャイロのキャリブレーションon
    mpu.setMagRegister('100Hz','16bit')
    lps.powerWakeUp()
    startTime = time.time()
    cnt = 0
    while True:
        now = time.time()
        acc = mpu.getAccel()
        gyr = mpu.getGyro()
        mag = mpu.getMag()
        press = lps.readPressure()
        temp = lps.readTemp()
        mag = mpu.getMag()
        gpsData = gps.getGps() 
        """
        for i in range(10):
            step.forward()
            mag = mpu.getMag()
            print "%+8.7f" % mag[0] + " , " + "%+8.7f" % mag[1] + " , " + "%+8.7f" % mag[2]
        """ 
        with open('data_' + str(startTime) + '.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([cnt, press, temp, acc[0], acc[1], acc[2], gyr[0], gyr[1], gyr[2], mag[0], mag[1], mag[2], gpsData[0], gpsData[1]])

        cnt += 1
        sleepTime = 0.1 - (time.time() - now) #処理時間の計測
        if sleepTime < 0.0:
            continue

        time.sleep(sleepTime)

if __name__ == "__main__":
    main()
