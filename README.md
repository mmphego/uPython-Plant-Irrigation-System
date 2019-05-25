# ESP8266 MicroPython Demo

MicroPython demo on NodeMCU with ESP8266 (WiFi). Fake temperature data will be posted to API every 10 seconds.

[用 Python 玩硬體：MicroPython 簡介與實作](https://pyliaorachel.github.io/blog/tech/python/2018/07/24/micropython-on-esp8266.html)

## [Setup NodeMCU & Tools](https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html)

1. Install tools
    1. [esptool](https://github.com/espressif/esptool) for communicating with ESP chips: `$ pip install esptool`
    2. [ampy](https://github.com/adafruit/ampy) for serial connection with MicroPython boards: `$ pip install adafruit-ampy`
2. Deploy firmware
    1. Plug in the device
    2. Get port name of device: `$ ls /dev/tty.*`
    3. Download firmware from [MicroPython downloads page](http://micropython.org/download#esp8266)
    4. Deploy: `$ esptool.py --port <port-name> write_flash --flash_size=detect 0 <firmware-file>`

## Usage

1. Create an API for posting data, e.g. Firebase
2. Copy `config.py.template` to `config.py`, replace the placeholders with real values
    1. WiFi SSID and password
    2. API (can replace the whole string with your own url if not using Firebase)
3. Upload code
    1. Get port name of device: `$ ls /dev/tty.*`
    2. Upload code to board: `$ ampy --port <port-name> put boot.py main.py config.py`
4. Reset NodeMCU, i.e. press the reset button, the LED will flash after release; `main.py` will run, data sent at 10 sec interval
5. Check API console for the data posted; the LED will also flash after each data upload

https://blog.miguelgrinberg.com/post/micropython-and-the-internet-of-things-part-ii-hello-micropython
https://electronicsforu.com/resources/software/introduction-micropython