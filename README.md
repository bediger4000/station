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
The Raspberry Pi can connect to the house's WiFi network.

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

Probably needs a reboot to work.

## Client

[Code](station.py)

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

```sh
$ go build server.go
```

### Run

```sh
$ nohup ./server 10.0.0.1 7689 > data.log 2> server.log &
```

It's possible that a systemd service would be wise,
letting the suitable server keep the data saving server running.
