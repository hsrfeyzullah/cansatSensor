# cansatSensor
2018年3月加太共同実験のCanSatで使用したライブラリ

* Raspberry Pi で動作させた。後から使用できる場所だけgitに残す。

* cansat_sensor.py→統合

* sensor.py→MPU9250クラスとLPS22Hクラス

    加速度ジャイロ地磁気気温気圧がとれるようになる
    
* gps.py→gpクラス

    GPSを取得できるようになる(CanSat本番では使っていないので、電波受信までの時間は考慮していない。電波の取得自体は確認している。)

* moter.py→servoクラスとsteppinクラス

    サーボモータとステッピングモータの動作

