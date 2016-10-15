import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)

#GPIO.output(GPIO.HIGH)

interval = 0.1 # seconds
try:  
    while True:  
        GPIO.output(17, 1)         # set GPIO24 to 1/GPIO.HIGH/True  
        time.sleep(interval)                 # wait   
        if GPIO.input(17):  
            print "LED just about to switch off"  
        GPIO.output(17, 0)         # set GPIO24 to 0/GPIO.LOW/False  
        time.sleep(interval)                 # wait  
        if not GPIO.input(17):  
            print "LED just about to switch on"  
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup() 
