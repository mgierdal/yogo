__version__ = 0.9 # test version
__version__ = 1.0 # heat and cool study

# Import Libraries

import RPi.GPIO as GPIO

import os
import glob
import time
import sqlite3 as sql
import datetime

DB = r'record.db'

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
 

def read_temp_raw():
  """ead temp data"""
  f = open(device_file, 'r') # Opens the temperature device file
  lines = f.readlines() # Returns the text
  f.close()
  return lines
 
def read_temp():
  """convert raw readout into a temperature"""
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

def keep_in_range(hi, lo, interval, period, gpio, cursor):
    start_time = datetime.datetime.now()
    ts = datetime.datetime.now()
    while (ts - start_time) > period:
        t_c, t_f = read_temp()
        ts = datetime.datetime.now()
        power_status = GPIO.input(GPIO_PIN)
        if (t_c < lo):
            if power_status == 0:
                #print t_c, "LED switched on", ts
                GPIO.output(gpio, 1)      # set GPIO to 1/GPIO.HIGH/True
            else:
                pass#print t_c, 'ON' if GPIO.input(gpio) == '1' else 'OFF', ts
        elif (t_c > hi):
            if power_status == 1:
                #print t_c, "LED switched off", ts
                GPIO.output(gpio, 0)         # set GPIO to 0/GPIO.LOW/False
            else:
                pass#print t_c, 'ON' if GPIO.input(gpio) == '1' else 'OFF', ts
        else:
            pass#print t_c, "in between", ts
        power_status = GPIO.input(gpio)
        c.execute("INSERT INTO trace VALUES (?,?,?)",(ts, t_c, power_status))
        conn.commit()
        time.sleep(INTERVAL)    # wait 
        
def blink(n, gpio, interval):
    for i in range(n):
        GPIO.output(gpio, 1)
        #print 'blink ):'
        time.sleep(interval)
        GPIO.output(gpio, 0)
        time.sleep(interval)


INTERVAL = 60.0 # seconds
THRESH_LO = 23
THRESH_HI = 27
DROP_DATA = True
GPIO_PIN = 17

start_time = datetime.datetime.now()
heat_period = datetime.timedelta(0, 4.5 *60*60)
cool_period = datetime.timedelta(0, 5.0 *60*60)

conn = sql.connect(DB)
c = conn.cursor()

if DROP_DATA:
    query = 'DROP TABLE IF EXISTS trace'
    c.execute(query)
    # Create table
    query = 'CREATE TABLE trace (timestamp text, temp_c real, power_status integer)'
    c.execute(query)

blink(3, 17, 0.5)

try:  
    #keep_in_range(THRESH_HI, THRESH_LO, INTERVAL, 17, c)
    GPIO.output(GPIO_PIN, 1)
    ts = datetime.datetime.now()
##    while (ts - start_time) < heat_period:
##        if GPIO.input(GPIO_PIN) == 0:
##            GPIO.output(GPIO_PIN, 1)
##            #print 'f',
##        t_c, t_f = read_temp()
##        ts = datetime.datetime.now()
##        power_status = GPIO.input(GPIO_PIN)
##        c.execute("INSERT INTO trace VALUES (?,?,?)",(ts, t_c, power_status))
##        conn.commit()
##        #print '.',
##        time.sleep(INTERVAL) # wait 
    keep_in_range(80, 80, INTERVAL, datetime.timedelta(0, 4 *60*60), 17, c)
    keep_in_range(80, 76, INTERVAL, datetime.timedelta(0, 2 *60*60), 17, c)
    keep_in_range(76, 60, INTERVAL, datetime.timedelta(0, 2 *60*60), 17, c)
except KeyboardInterrupt:      # trap a CTRL+C keyboard interrupt
    pass
finally:
    GPIO.cleanup()
    if conn:
        conn.commit()
        conn.close()
    
# 46 01 4b 46 7f ff 0a 10 85 : crc=85 YES
# 46 01 4b 46 7f ff 0a 10 85 t=20375
