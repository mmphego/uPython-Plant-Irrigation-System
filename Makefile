.PHONY: help erazer flash

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  erazer"
	@echo "  flash firmware"
	@echo "  repl"

erazer:
	@esptool.py --port /dev/ttyUSB0 erase_flash

flash:
	@wget http://micropython.org/resources/firmware/esp8266-20190125-v1.10.bin
	@esptool.py --port /dev/ttyUSB0 --help --baud 460800 write_flash --flash_size=detect 0 esp8266-20190125-v1.10.bin

repl:
	@minicom -D /dev/ttyUSB0