# uPython-moisture-sensor

**uPython based soil moisture sensor running on an esp8266**

This is a simple [uPython](http://www.micropython.org/) project for a soil moisture sensor connected to a [Wemos D1 esp8266](https://www.wemos.cc/) board that will send a [Slack](slack.com) message to a specific channel every hour with the current moisture level. It uses a Capacitive soil moisture sensor as compared to the resistor soil moisture sensor - for obvious reasons.

![image](assets/soilmoisture.jpg)

## Calibrating the Soil Moisture Sensor

Calibrating the sensor has two parts, the goal is to make sure sensor is functioning properly:
*   Connect up the soil moisture sensor and dip it in a bowl of water and take the reading.
*   Wipe the sensor, and place it on dry surface and take the reading

These readings should be entered in [config.json](config.json) file.

## Setup NodeMCU & Tools

Read the [docs.](https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html)

*   Clone the repo and,
*   Plug in the device to your computer
    **NOTE:** The installation assumes that the port name of device is `/dev/ttyUSB0` else, modify `Makefile` with port name [Hint:`$ ls /dev/tty.*`].
*   Run `make bootstrap`
    This will install `esptool` and `mpfshell` for communicating with ESP chips and for serial connection with MicroPython boards, Eraze and flash the chip with firmware `esp8266-20190125-v1.10.bin` as well as upload the required files to the ESP.

## Setup Slack

I have made a post on how to create a [Slack](slack.com) API for posting data, go [here](http://bit.ly/2K46XP8)
The config goes [here](config.json)

## Oh, Thanks!

By the way... thank you! And if you'd like to [say thanks](https://saythanks.io/to/mmphego)... :)

✨🍰✨

## Contributing/Feedback

Feel free to fork it or send me PR to improve it.
