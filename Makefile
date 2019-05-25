######################################################################
# User configuration
######################################################################
.PHONY: erase flash reset firmware upload check repl bootstrap

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "   erase "
	@echo "   flash "
	@echo "   reset "
	@echo "   firmware "
	@echo "   upload "
	@echo "   check "
	@echo "   repl "
	@echo "   bootstrap ""

# Serial port
# Linux Debian/Ubuntu
PORT=ttyUSB0
SPEED=460800

# Path to programs
# Install with `sudo pip install -U mpfshell esptool`
MPFSHELL=mpfshell --open $(PORT)
ESPTOOL=esptool.py
FIRMWARE=./firmware.bin
FIRMWAREVERSION=esp8266-20190125-v1.10.bin

######################################################################
# End of user config
######################################################################
FILES=boot.py \
	config.json \
	main.py \
	mqtt_writer.py \
	utils.py \
	wifi.py

erase:
	$(ESPTOOL) --port $(PORT) erase_flash

flash: firmware
	$(ESPTOOL) --port /dev/$(PORT) --baud $(SPEED) write_flash --verify --flash_size=detect 0 $(FIRMWARE)
	@sleep 5
	@echo 'Power cycle the device'

reset:
	$(MPFSHELL) --reset

firmware:
	@bash -c "[ -f $(FIRMWARE) ] || wget -O ./firmware.bin http://micropython.org/resources/firmware/"$(FIRMWAREVERSION)

# Upload all
upload:
	for f in $(FILES); \
	do \
		echo installing $$f; \
		$(MPFSHELL) -nc put $$f; \
	done

check:
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

repl:
	$(MPFSHELL) -c repl

bootstrap: erase flash check upload
