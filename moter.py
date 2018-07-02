#!/usr/bin/python
import sys
import time
import RPi.GPIO as GPIO
import signal


def exit_handler(siglal, frame):
    #C-c is finish
    print("\nExit")
    servo.ChangeDutyCycle(2.5)
    time.sleep(0.5)
    servo.stop()
    GPIO.cleanup()
    sys.exit(0)

class STEPPING:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        """
        aphase = 10 
        aenbl = 9
        bphase = 11
        benbl = 8
        """
        self.steppins = [10, 9, 11, 8]
        self.step_v = 5
        GPIO.setup(self.step_v,GPIO.OUT)
        # Set all pins as output
        for pin in self.steppins:
            print "Setup pins"
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, False)
        GPIO.output(self.steppins[1], True)
        GPIO.output(self.steppins[3], True)
        GPIO.output(self.step_v, False)
        self.WaitTime = 15/float(1000)

    #while True:
    def forward(self):
        GPIO.output(self.step_v, True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[0], True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[2], True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[0], False)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[2], False)
        time.sleep(self.WaitTime)
        GPIO.output(self.step_v, False)

    def reverse(self):
        GPIO.output(self.step_v, True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[2], True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[0], True)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[2], False)
        time.sleep(self.WaitTime)
        GPIO.output(self.steppins[0], False)
        time.sleep(self.WaitTime)
        GPIO.output(self.step_v, False)

class SERVO:
    def __init__(self):
        self.duty = 0
        GPIO.setmode(GPIO.BCM)
        servo_pin = 23 
        GPIO.setup(servo_pin,GPIO.OUT)
        self.servo = GPIO.PWM(servo_pin, 50)
        self.servo.start(0.0)

    def forward(self):
        d = self.duty
        if d > 16:
           d -= 1
        d = d + 1
        dc = ((d + 6) / 10.0) / 20.0 * 100.0
        self.servo.ChangeDutyCycle(dc)
        self.duty = d
        time.sleep(0.05)

    def reverse(self):
        d = self.duty
        if d < 0:
           d += 1
        d = d - 1
        dc = ((d + 6)/ 10.0) / 20.0 * 100.0 # calculate duty
        self.servo.ChangeDutyCycle(dc)
        self.duty = d
        time.sleep(0.05)

def main():
    servo = SERVO()
    step = STEPPING()
    signal.signal(signal.SIGINT, exit_handler)

    #wait = WaitTime * 10.0
    # Start main loop
    while True:
        for i in range(10):
            step.forward()
        for i in range(10):
            servo.forward()
            #time.sleep(1)
        for i in range(10):
            servo.reverse()
            #time.sleep(1)
        for i in range(10):
            step.reverse()
        #time.sleep(1)

if __name__ == "__main__":
    main()
