# Import Libraries

import RPi.GPIO as GPIO

import os
import glob
import time

# initilaize OUT
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

#Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module
 
# Finds the correct device file that holds the temperature data
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
# A function that reads the sensors data
def read_temp_raw():
  f = open(device_file, 'r') # Opens the temperature device file
  lines = f.readlines() # Returns the text
  f.close()
  return lines
 
# Convert the value of the sensor into a temperature
def read_temp():
  lines = read_temp_raw() # Read the temperature 'device file'
 
  # While the first line does not contain 'YES', wait for 0.2s
  # and then read the device file again.
  while lines[0].strip()[-3:] != 'YES':
    time.sleep(0.2)
    lines = read_temp_raw()
 
  # Look for the position of the '=' in the second line of the
  # device file.
  equals_pos = lines[1].find('t=')
 
  # If the '=' is found, convert the rest of the line after the
  # '=' into degrees Celsius, then degrees Fahrenheit
  if equals_pos != -1:
    temp_string = lines[1][equals_pos+2:]
    temp_c = float(temp_string) / 1000.0
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_c, temp_f

INTERVAL = 0.01 # seconds
THRESH_LO = 23
THRESH_HI = 27

try:  
    while True:
        t_c, t_f = read_temp()
        if (t_c > THRESH_HI):
            if not GPIO.input(17):
                print t_c, "LED switched on"
                GPIO.output(17, 1)      # set GPIO24 to 1/GPIO.HIGH/True
            else:
                print t_c, 'ON'
        elif (t_c < THRESH_LO):
            if GPIO.input(17):
                print t_c, "LED switched off"
                GPIO.output(17, 0)         # set GPIO24 to 0/GPIO.LOW/False
            else:
                print t_c, 'OFF'
        else:
            print t_c, "in between"
        time.sleep(INTERVAL)                 # wait     
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()
    
# 46 01 4b 46 7f ff 0a 10 85 : crc=85 YES
# 46 01 4b 46 7f ff 0a 10 85 t=20375
