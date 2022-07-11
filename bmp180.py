#!/usr/bin/python3

import time
import socket
import sys
import smbus2
from datetime import datetime
 
bus = smbus2.SMBus(1)
# BMP180 address, 0x77
address = 0x77
 
def readTemperature(bus, address):
    data = bus.read_i2c_block_data(address, 0xAA, 22)
     
    # Convert the data
    AC1 = data[0] * 256 + data[1]
    if AC1 > 32767:
        AC1 -= 65535
    AC2 = data[2] * 256 + data[3]
    if AC2 > 32767:
        AC2 -= 65535
    AC3 = data[4] * 256 + data[5]
    if AC3 > 32767:
        AC3 -= 65535
    AC4 = data[6] * 256 + data[7]
    AC5 = data[8] * 256 + data[9]
    AC6 = data[10] * 256 + data[11]
    B1 = data[12] * 256 + data[13]
    if B1 > 32767:
        B1 -= 65535
    B2 = data[14] * 256 + data[15]
    if B2 > 32767:
        B2 -= 65535
    MB = data[16] * 256 + data[17]
    if MB > 32767:
        MB -= 65535
    MC = data[18] * 256 + data[19]
    if MC > 32767:
        MC -= 65535
    MD = data[20] * 256 + data[21]
    if MD > 32767:
        MD -= 65535
     
    time.sleep(0.5)
     
    bus.write_byte_data(address, 0xF4, 0x2E)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(address, 0xF6, 2)
     
    # Convert the data
    temp = data[0] * 256 + data[1]
     
    bus.write_byte_data(address, 0xF4, 0x74)
     
    time.sleep(0.5)
     
    data = bus.read_i2c_block_data(address, 0xF6, 3)
     
    # Convert the data
    pres = ((data[0] * 65536) + (data[1] * 256) + data[2]) / 128
     
    # Callibration for Temperature
    X1 = (temp - AC6) * AC5 / 32768.0
    X2 = (MC * 2048.0) / (X1 + MD)
    B5 = X1 + X2
    cTemp = ((B5 + 8.0) / 16.0) / 10.0
     
    # Calibration for Pressure
    B6 = B5 - 4000
    X1 = (B2 * (B6 * B6 / 4096.0)) / 2048.0
    X2 = AC2 * B6 / 2048.0
    X3 = X1 + X2
    B3 = (((AC1 * 4 + X3) * 2) + 2) / 4.0
    X1 = AC3 * B6 / 8192.0
    X2 = (B1 * (B6 * B6 / 2048.0)) / 65536.0
    X3 = ((X1 + X2) + 2) / 4.0
    B4 = AC4 * (X3 + 32768) / 32768.0
    B7 = ((pres - B3) * (25000.0))
    pressure = 0.0
    if B7 < 2147483648:
        pressure = (B7 * 2) / B4
    else:
        pressure = (B7 / B4) * 2
    X1 = (pressure / 256.0) * (pressure / 256.0)
    X1 = (X1 * 3038.0) / 65536.0
    X2 = ((-7357) * pressure) / 65536.0
    pressure = (pressure + (X1 + X2 + 3791) / 16.0) / 100

    return cTemp, pressure

serverAddressPort = (sys.argv[1], int(sys.argv[2]))
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def send_msg(msg):
    bytesToSend = str.encode(msg)
    try:
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    except Exception as e:
        dt = datetime.now()
        print(dt, e)

output_fmt = '{bp}\t{t1}'

while True:
    temperature, pressure = readTemperature(bus, address)
    send_msg(output_fmt.format(bp="%.3f"%pressure, t1="%.3f"%temperature))
    time.sleep(120)
