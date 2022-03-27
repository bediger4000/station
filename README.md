# Slightly remote atmospheric data collection

BME280 and DS18B20 sensors on a Raspberry Pi 3b+

Don't use a [DHT11](https://github.com/bediger4000/dht11_service) - they suck all around.
Spend a few extra dollars on a BME280.
More accurate, has a wider range, and better, easier to use driver.

## Design

Have a Raspberry Pi in a somewhat water-resistant box outside,
reading atmospheric data
(temperature, relative humidity, barometric pressue)
sensors.
The Raspberry Pi can connect to the house's WiFi network,
so there's need for any cabling.

A server process runs on some suitable Linux machine.
It is addressable by the Raspberry Pi collecting data.
The Raspberry Pi periodically takes sensor readings,
then sends them back to the server process via the local network.

The server process records the data for later use in visualizations,
weather predictions, etc.
No data resides on the Raspberry Pi, since it can get unplugged,
crash or suffer catastrophy like getting wet or iced up.

## Raspberry Pi

I2C has to be turned on for the BME280.
1-wire has to be turned on for the  DS18B20.
Use `raspi-config` to do this.

`/boot/config.txt` has this in it after configuring:
```
dtparam=i2c_arm=on
dtoverlay=w1-gpio
```

I think SPI has to be turned off.

Raspberry Pi robably needs a reboot to work after these changes.

### Sensor connectivity

You can check that the DS18B20 is wired correctly by:

```sh
$ ls -l /sys/bus/w1/devices/
total 0
lrwxrwxrwx 1 root root 0 Mar  1 10:30 28-3c01a8162918 -> ../../../devices/w1_bus_master1/28-3c01a8162918
lrwxrwxrwx 1 root root 0 Mar  1 19:59 w1_bus_master1 -> ../../../devices/w1_bus_master1
```

The "28-3c01a8162918" directory means the kernel detected a DS18B20.

The Linux kernel also loads modules `w1_therm` if it finds a DS18B20.

You can check that the BME280 is wired (mostly) correctly with:

```sh
$ pi@localhost:~ $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- 77                         
```

The "77" is apparently the BME280 I've got.
Other brands will show as "76".
See [station.py](station.py) for a place that must have this number correct.

The "77" will show up even if the GND wire isn't connected,
but the BME280 won't produce any data,
so this isn't a great connectivity test.

## Client

[Code](station.py)

The client requires installing [RPi.bme28](https://pypi.org/project/RPi.bme280/).
The RPi.bme280 library seems reliable.

```sh
$ pip3 install RPi.bme280
```

Install the `smbus2` library:
```sh
$ pip3 install smbus2
```

## Data Saving Server

[Code](server.go)

I wrote the data saving server in Go (v1.17).
It should be portable to almost any Go-supported hardware/OS combo.
It does nothing special, opening a UDP port,
writing data it receives to stdout.

You do NOT want to expose this server to the internet.
Some fool will try to write things to it (DNS queries, etc etc)
and fill up your local storage.
That's why you have to specify an IP address for it to listen to on the command line.

### Build

The data saving server doesn't depend on any 3rd party Go packages.

```sh
$ go build server.go
```

### Run

```sh
$ nohup ./server 10.0.0.1 7689 > data.log 2> server.log &
```

It's possible that a systemd service would be wise,
letting the suitable server keep the data saving server running.
