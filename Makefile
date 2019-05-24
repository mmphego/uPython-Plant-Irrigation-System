.PHONY: help erazer flash upload repl

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  erazer"
	@echo "  flash firmware"
	@echo "  repl"
	@echo "  upload"

erazer:
	@esptool.py --port /dev/ttyUSB0 erase_flash

flash:
	@bash -c "[ -f firmware.bin ] || wget -O ./firmware.bin http://micropython.org/resources/firmware/esp8266-20190125-v1.10.bin"
	@bash -c "[ -f firmware.bin ] && esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 firmware.bin"

repl:
	@mpfshell --open /dev/ttyUSB0

upload:
	@mpfshell -nc "open ttyUSB0; rm boot.py; put boot.py; put config.json; put main.py; put mqtt_writer.py ;put utils.py; put wifi.py;"
	@mpfshell -nc "open ttyUSB0; ls"
