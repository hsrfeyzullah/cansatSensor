#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import smbus
import time
import sys
import csv
import signal

def exit_handler(siglal, frame):
    #C-c is finish
    print("\nExit")
    servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)
    servo.stop()
    GPIO.cleanup()
    sys.exit(0)


class MPU9250:
    #定数宣言
    PWR_MGMT_1 = 0x6B
    INT_PIN_CFG = 0x37
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG1 = 0x1C
    ACCEL_CONFIG2 = 0x1D

    MAG_MODE_POWERDOWN = 0
    MAG_MODE_SERIAL_1 = 1
    MAG_MODE_SERIAL_2 = 2
    MAG_MODE_SINGLE = 3
    MAG_MODE_EX_TRIGER = 4
    MAG_MODE_SELF_TEST = 5

    MAG_ACCESS = False
    MAG_MODE = 0
    MAG_BIT = 14

    offsetRoomTemp = 0
    tempSensitivity = 333.87
    gyroRange = 250
    accelRange = 2
    magRange = 4912

    offsetAccelX = 0.0
    offsetAccelY = 0.0
    offsetAccelZ = 0.0
    offsetGyroX = 0.0
    offsetGyroY = 0.0
    offsetGyroZ = 0.0

    #コンストラクタ
    def __init__(self):
        self.address = 0x68
        self.channel = 1
        self.bus = smbus.SMBus(self.channel)
        self.addrAK8963 = 0x0C 

        #Sensor initialization
        self.resetRegister()
        self.powerWakeUp()

        self.gyroCoefficient = self.gyroRange / float(0x8000)    #dps変換
        self.accelCoefficient = self.accelRange / float(0x8000)  #g変換
        self.magCoefficient16 = self.magRange / 32760.0          #μTに変換する係数(16bit)
        self.magCoefficient14 = self.magRange / 8190.0           #μTに変換する係数(14bit)

       #レジスタを初期設定に戻す
    def resetRegister(self):
        if self.MAG_ACCESS == True:
            self.bus.write_i2c_block_data(self.addrAK8963, 0x0b, [0x01])
        self.bus.write_i2c_block_data(self.address, 0x6b, [0x80])
        self.MAG_ACCESS = False
        time.sleep(0.1)

    #レジスタをセンシング可能な状態にする
    def powerWakeUp(self):
        #PWR_MGMT_1 clear
        self.bus.write_i2c_block_data(self.address, self.PWR_MGMT_1, [0x00])
        time.sleep(0.1)
        #磁気センサ(AK8963)にアクセスできるようにする(BYPASS_EN = 1)
        self.bus.write_i2c_block_data(self.address, self.INT_PIN_CFG, [0x02])
        self.MAG_ACCESS = True
        time.sleep(0.1)
        
    #磁気センサのレジスタ設定
    def setMagRegister(self, _mode, _bit):
        if self.MAG_ACCESS == False:
            #磁気センサへのアクセスが有効になってない場合例外にあげる
            raise Exception('001 Access to a sensor is invalid.')

        _writeData = 0x00

        #測定モードの設定
        if _mode == '8Hz':      #連続測定モード1
            _writeData = 0x02
            self.MAG_MODE = self.MAG_MODE_SERIAL_1
        elif _mode == '100Hz':      #連続測定モード2
            _writeData = 0x06
            self.MAG_MODE = self.MAG_MODE_SERIAL_2
        elif _mode == 'POWER_DOWN':      #powerdownモード
            _writeData = 0x00
            self.MAG_MODE = self.MAG_MODE_POWERDOWN
        elif _mode == 'EX_TRIGER':      #外部トリガ測定モード
            _writeData = 0x04
            self.MAG_MODE = self.MAG_MODE_EX_TRIGER
        elif _mode == 'SELF_TEST':      #セルフテストモード
            _writeData = 0x08
            self.MAG_MODE = self.MAG_MODE_SELF_TEST
        else:                           #単発測定モード
            _writeData = 0x01
            self.MAG_MODE = self.MAG_MODE_SINGLE

        if _bit == '14bit':             #14bit出力
            _writeData = _writeData | 0x00
            self.MAG_BIT = 14
        else:                            #16bit出力
            _writeData = _writeData | 0x10
            self.MAG_BIT = 16

        self.bus.write_i2c_block_data(self.addrAK8963, 0x0A, [_writeData])


    #加速度の測定レンジの設定
    #val = 16, 8, 4, 2(default)
    def setAccelRange(self, val, _calibration = False):
        if val == 16:
            self.accelRange = 16
            _data = 0x18
        elif val == 8:
            self.accelRange = 8
            _data = 0x10
        elif val == 4:
            self.accelRange = 4
            _data = 0x08
        else:
            self.accelRange = 2
            _data = 0x00
        
        self.bus.write_i2c_block_data(self.address, self.ACCEL_CONFIG1, [_data])
        self.accelCoefficient = self.accelRange / float(0x8000)
        time.sleep(0.1)

        #オフセット値をリセット
        self.offsetAccelX = 0
        self.offsetAccelY = 0
        self.offsetAccelZ = 0
        
        if _calibration == True:
            self.calibAccel(1000)
        return

     #キャリブレーションするほうがいいかも
#ジャイロの測定レンジの設定(広レンジ→測定粒度が粗い)
    def setGyroRange(self, val, _calibration = False):
        if val == 2000:
            self.gyroRange = 2000
            _data = 0x18
        elif val == 1000:
            self.gyroRange = 1000
            _data = 0x10
        elif val == 500:
            self.gyroRange = 500
            _data = 0x08
        else:
            self.gyroRange = 250
            _data = 0x00
    
        self.bus.write_i2c_block_data(self.address, self.GYRO_CONFIG, [_data])
        self.gyroCoefficient = self.gyroRange / float(0x8000)
        time.sleep(0.1)
        
        #オフセット値をリセット
        self.offsetGyroX = 0
        self.offsetGyroY = 0
        self.offsetGyroZ = 0
        
        if _calibration == True:
            self.calibGyro(1000)
        return

        #キャリブレーションする？
        #Lowpassfilter作る？
    def u2s(self, unsigneddata):
        if unsigneddata & (0x01 << 15):
            return -1 * ((unsigneddata ^ 0xffff) + 1)
        return unsigneddata

    #加速度の取得
    def getAccel(self):
        data = self.bus.read_i2c_block_data(self.address, 0x3B, 6)
        accX = self.accelCoefficient * self.u2s(data[0] << 8 | data[1]) + self.offsetAccelX
        accY = self.accelCoefficient * self.u2s(data[2] << 8 | data[3]) + self.offsetAccelY
        accZ = self.accelCoefficient * self.u2s(data[4] << 8 | data[5]) + self.offsetAccelZ
        return accX, accY, accZ

    #ジャイロ値の取得
    def getGyro(self):
        data = self.bus.read_i2c_block_data(self.address, 0x43, 6)
        gyroX = self.gyroCoefficient * self.u2s(data[0] << 8 | data[1]) + self.offsetGyroX
        gyroY = self.gyroCoefficient * self.u2s(data[2] << 8 | data[3]) + self.offsetGyroY
        gyroZ = self.gyroCoefficient * self.u2s(data[4] << 8 | data[5]) + self.offsetGyroZ
        return gyroX, gyroY, gyroZ

    #   地磁気の取得
    #   ±4800nT (16bit) 
    def getMag(self):
        #磁気センサの例外キャッチ
        if self.MAG_ACCESS == False:
            raise Exception('002 Access to a sensor is invalid.')

        #準備
        if self.MAG_MODE == self.MAG_MODE_SINGLE:
            #単発測定モードは測定終了と同時にパワーダウンするのでもう一度モードを変更する
            if self.MAG_BIT == 14:  #14bit
                _writeData = 0x01
            else:                   #16bit
                _writeData = 0x11
            self.bus.write_i2c_block_data(self.addrAK8963, 0x0A, [_writeData])
            time.sleep(0.01)

        elif self.MAG_MODE == self.MAG_MODE_SERIAL_1 or self.MAG_MODE == self.MAG_MODE_SERIAL_2:
            status = self.bus.read_i2c_block_data(self.addrAK8963, 0x02, 1)
            if(status[0] & 0x02) == 0.02:
                #データオーバーランがあるので再度センシング
                self.bus.read_i2c_block_data(self.addrAK8963, 0x09, 1)

        elif self.MAG_MODE == self.MAG_MODE_EX_TRIGER:

            return
        elif self.MAG_MODE == self.MAG_MODE_POWERDOWN:
            raise Exception('003 Mag sensor power down')

        #ST1レジスタの確認(読み出しが可能か確認)
        status = self.bus.read_i2c_block_data(self.addrAK8963, 0x02, 1)
        while (status[0] & 0x01) != 0x01:
            #dataready状態まで待つ
            time.sleep(0.01)
            status = self.bus.read_i2c_block_data(self.addrAK8963, 0x02, 1)

        #データ読み出し(下位bitが先)
        data = self.bus.read_i2c_block_data(self.addrAK8963, 0x03, 7)
        magX = self.u2s(data[1] << 8 | data[0])
        magY = self.u2s(data[3] << 8 | data[2])
        magZ = self.u2s(data[5] << 8 | data[4])
        st2 = data[6]
        
        #オーバーフローチェック
        if (st2 & 0x80) == 0x80:
            raise Exception('004 Mag sensor over flow')

        #μTへの変換
        if self.MAG_BIT == 16:  #16bit
            magX = magX * self.magCoefficient16 
            magY = magY * self.magCoefficient16
            magZ = magZ * self.magCoefficient16
        else:                   #14bit
            magX = magX * self.magCoefficient14
            magY = magY * self.magCoefficient14
            magZ = magZ * self.magCoefficient14

        return magX, magY, magZ

    #def getTemp(self):
        #data = self.bus.read_i2c_block_data(self.address, 0x65, 2)
        #raw = data[0] << 8 | data[1]
        #return ((raw - self.offsetRoomTemp) / self.tempSensitivity) + 21

    def selfTestMag(self):
        print "start magsensor self test"
        self.setMagRegister('SELF_TEST', '16bit')
        self.bus.write_i2c_block_data(self.addrAK8963, 0x0C, [0x40])
        time.sleep(1.0)
        data = self.getMag()

        print data

        self.bus.write_i2c_block_data(self.addrAK8963, 0x0C, [0x00])
        self.setMagRegister('POWER_DOWN', '16bit')
        time.sleep(1.0)
        print "end mag sensor self test"
        return 

    #加速度のキャリブレーション
    def calibAccel(self, _count = 1000):
        print "Accel calibration start"
        _sum = [0,0,0]

        #データのサンプルをとる
        for i in range(_count):
            _data = self.getAccel()
            _sum[0] += _data[0]
            _sum[1] += _data[1]
            _sum[2] += _data[2]

        self.offsetAccelX = -1.0 * _sum[0] / _count
        self.offsetAccelY = -1.0 * _sum[1] / _count
        self.offsetAccelZ = -1.0 * ((_sum[2] / _count) - 1.0)

        print "Accel calibration ok"
        return self.offsetAccelX, self.offsetAccelY, self.offsetAccelZ
    #ジャイロのキャリブレーション
    def calibGyro(self, _count = 1000):
        print "Gyro calibration start"
        _sum = [0,0,0]

        #データのサンプルをとる
        for i in range(_count):
            _data = self.getGyro()
            _sum[0] += _data[0]
            _sum[1] += _data[1]
            _sum[2] += _data[2]
 
        self.offsetGyroX = -1.0 * _sum[0] / _count
        self.offsetGryoY = -1.0 * _sum[1] / _count
        self.offsetGyroZ = -1.0 * _sum[2] / _count

        print "Gyro calibration ok"
        return self.offsetGyroX, self.offsetGyroY, self.offsetGyroZ
class LPS22HB:
    #定数宣言
    WHO_AM_I = 0x0F
    RES_CONF = 0x1A
    CTRL_REG1 = 0x10
    CTRL_REG2 = 0x11
    STATUS_REG =  0x27
    PRESS_OUT_XL = 0x28
    PRESS_OUT_L = 0x29
    PRESS_OUT_H = 0x2A
    TEMP_OUT_L = 0x2B
    TEMP_OUT_H = 0x2C

    #コンストラクタ
    def __init__(self):
        self.address = 0x5C
        self.channel = 1
        self.bus = smbus.SMBus(self.channel)

        #Sensor initialization
        #self.resetRegister()
        self.powerWakeUp()

    def u2s(self, unsigneddata):
        if unsigneddata & 0x800000:
            return (-(unsigneddata ^ 0xffffff) + 1)
        return unsigneddata

        #レジスタをセンシング可能な状態にする
    def powerWakeUp(self):
        #PWR_MGMT_1 clear
        self.bus.write_i2c_block_data(self.address, self.RES_CONF, [0x00])
        time.sleep(0.1)
        #磁気センサ(AK8963)にアクセスできるようにする(BYPASS_EN = 1)
        self.bus.write_i2c_block_data(self.address, self.CTRL_REG1, [0x02])
        self.MAG_ACCESS = True
        time.sleep(0.1)
        
    def readPressure(self):
        self.bus.write_i2c_block_data(self.address, self.CTRL_REG2, [0x01]) #one shot mode のレジスタ

        pressOutH = self.bus.read_i2c_block_data(self.address, self.PRESS_OUT_H)
        pressOutL = self.bus.read_i2c_block_data(self.address, self.PRESS_OUT_L)
        pressOutXL = self.bus.read_i2c_block_data(self.address, self.PRESS_OUT_XL)
        pressOutH = pressOutH[0]  #なんかリスト型配列で出力されるからint型にする
        pressOutL = pressOutL[0]
        pressOutXL = pressOutXL[0]

        value = self.u2s(pressOutH << 16 |pressOutL << 8 |pressOutXL)
        return value / 4096.0

    def readTemp(self):
        #bus.write_i2c_block_data(address, 0x11, [0x01])
        tempOutH = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_H)
        tempOutL = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_L)
        tempOutH = tempOutH[0]  #なんかリスト型配列で出力されるからint型にする
        tempOutL = tempOutL[0]
    
        value = self.u2s(tempOutH << 8 |tempOutL)
        return value / 100.0 

    #WHO AM Iの確認
    def whoami():
        read = self.bus.read_i2c_block_data(self.address, self.WHO_AM_I)
        return read

    #地磁気オフセットかましてないよ
if __name__ == "__main__":
    mpu = MPU9250()
    lps = LPS22HB()
    mpu.resetRegister()
    mpu.powerWakeUp()
    mpu.setAccelRange(8, True)       #加速度のキャリブレーションon
    mpu.setGyroRange(1000, True)     #ジャイロのキャリブレーションon
    mpu.setMagRegister('100Hz','16bit')
    lps.powerWakeUp()
    while True:
        now = time.time()
        acc = mpu.getAccel()
        gyr = mpu.getGyro()
        mag = mpu.getMag()
        press = lps.readPressure()
        temp = lps.readTemp()
        print "%+8.7f" % acc[0] + " ",
        print "%+8.7f" % acc[1] + " ",
        print "%+8.7f" % acc[2] + " ",
        print " | ",
        print "%+8.7f" % gyr[0] + " ",
        print "%+8.7f" % gyr[1] + " ",
        print "%+8.7f" % gyr[2] + " ",
        print " | ",
        print "%+8.7f" % mag[0] + " ",
        print "%+8.7f" % mag[1] + " ",
        print "%+8.7f" % mag[2]
        print ("%+8.7f") % press + " | " + ("%+8.7f") % temp

        """
        with open('magnet.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([mag[0], mag[1], mag[2]])
        """
        sleepTime = 0.1 - (time.time() - now)
        if sleepTime < 0.0:
            continue

        time.sleep(sleepTime)
