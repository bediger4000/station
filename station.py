#!/usr/bin/python3

from time import sleep
import bme280
import glob
import smbus2
import socket
import sys

device_dirs = glob.glob('/sys/bus/w1/devices/28-*')
if len(device_dirs) < 1:
    print("no DS18B20 device directory found")

file_name = device_dirs[0]+"/w1_slave"

serverAddressPort = (sys.argv[1], int(sys.argv[2]))
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def send_msg(msg):
    bytesToSend = str.encode(msg)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

def ds18b20_temp():

    try:
        fin = open(file_name, "r")
    except FileNotFoundError:
        print("Couldn't find thermometer file ", file_name)
        return -41.00
    except:
        print("Problem opening thermometer file ", file_name)
        return -42.00

    lines = fin.readlines()
    fin.close()

    for line in lines:
        idx = line.find("t=")
        if idx >= 0:
            strrep = line[idx+2:]
            temp = float(strrep)/1000.
            return temp
 
    return -40.00

port = 1
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

output_fmt = '{rh}\t{bp}\t{t1}\t{t2}'

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature
    temperature2 = ds18b20_temp()
    send_msg(output_fmt.format(rh="%.3f"%humidity, bp="%.3f"%pressure, t1="%.3f"%ambient_temperature, t2="%.3f"%temperature2))
    sleep(120)

