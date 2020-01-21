######################################################################
# User configuration
######################################################################

# Linux Debian/Ubuntu

# Serial port
PORT=ttyUSB0
SPEED=460800

# Path to programs
MPFSHELL=mpfshell --open $(PORT)
ESPTOOL=esptool.py
FIRMWARE=./firmware.bin
# Get latest version from http://www.micropython.org/download#esp8266
FIRMWAREVERSION=esp8266-20190125-v1.10.bin

######################################################################
# End of user config
######################################################################
FILES=boot.py \
	config.json \
	main.py \
	soil_moisture.py \
	water_pump.py \
	utils.py

.PHONY: erase # : Erase flash on chip
erase:
	$(ESPTOOL) --port /dev/$(PORT) erase_flash
	@sleep 5

.PHONY: flash # : Upload new firmware to chip
flash: firmware
	$(ESPTOOL) --port /dev/$(PORT) --baud $(SPEED) write_flash --flash_size=detect 0 $(FIRMWARE)
	@sleep 10
	@echo 'Power cycle the device'

.PHONY: reset # : Hard reset chip
reset:
	$(MPFSHELL) --reset

.PHONY: install
install:
	@bash -c "if ! command -v esptool.py >/dev/null 2>&1; then python3 -m pip install --user -U esptool;fi"
	@bash -c "if ! command -v mpfshell >/dev/null 2>&1; then python3 -m pip install --user -U mpfshell;fi"

.PHONY: firmware # : Download latest firmware from http://www.micropython.org/download#esp8266
firmware:
	@bash -c "[ -f $(FIRMWARE) ] || wget -O ./firmware.bin http://micropython.org/resources/firmware/"$(FIRMWAREVERSION)

.PHONY: upload_all # : Upload latest firmware"
upload_all:
	for f in $(FILES); do \
		echo installing $$f; \
		$(MPFSHELL) -nc rm $$f > /dev/null 2>&1; \
		$(MPFSHELL) -nc put $$f; \
		echo done installing; \
	done

.PHONY: check # : Compile Python code
check:
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

.PHONY: repl # : Open repl on chip
repl:
	$(MPFSHELL) -c repl

.PHONY: all # :Bootstrap ie erase, flash, and upload
all: install erase flash check upload_all clean

.PHONY: help # : Please use \`make <target>' where <target> is one of
help:
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1 \2/' | expand -t20

.PHONY: clean
clean:
	rm -rf $(FIRMWARE)
	rm -rf *.pyc

.PHONY: test
test:
	ls
