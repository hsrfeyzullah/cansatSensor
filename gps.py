#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import serial
import time
import csv

class GPS:
    def __init__(self):
        self.ser = serial.Serial('/dev/serial0',9600)
        data = self.ser.readline()

    def parse_gpgga(self, data):
        data = data.split(",")
        dict = {
                "sentence": data[0],
                "current_time": data[1],
                "latitude": data[2],
                "latitude_direction": data[3],
                "longitude": data[4],
                "longitude_direction": data[5],
                "fix_type": data[6],
                "number_of_satellites": data[7],
                "horizontal_precision": data[8],
                "altitude_above_sea": data[9],
                "altitude_uints": data[10],
                "geoidal_separation": data[11],
                "checksum": data[12]
                }
        return dict

    def getGps(self):
        while True:
            data = self.ser.readline()
            if "$GPGGA" in data:
                #print data
                gpsData = self.parse_gpgga(data)
                #print "number of satellites is " + gpsData["number_of_satellites"]
                if int(gpsData["number_of_satellites"]) >= 1:
                    log_data = gpsData["latitude"] + " - " + gpsData["longitude"]
                    return gpsData["latitude"], gpsData["longitude"]
                    #with open("gps.csv", "a") as f:
                    #    writer = csv.writer(f)
                    #    writer.writerow([gpsData["latitude"], gpsData["longitude"]])
if __name__ == "__main__":
    gps = GPS()
    while True:
        data = gps.getGps()
        print data[0] + " , "+ data[1]
