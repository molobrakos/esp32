PIP_HOME_BIN=$(HOME)/.local/bin

PORT=/dev/ttyUSB0
BAUD=115200

ADDRESS=0x1000
FIRMWARE=esp32-20190125-v1.10.bin

SCREEN_DRIVER=ssd1306.py
SCREEN_DRIVER_URL=https://raw.githubusercontent.com/adafruit/micropython-adafruit-ssd1306/master/$(SCREEN_DRIVER)

PICOCOM=/usr/bin/picocom
ESPTOOL=$(PIP_HOME_BIN)/esptool.py
AMPY_BIN=$(PIP_HOME_BIN)/ampy
AMPY=$(AMPY_BIN) -p $(PORT) -b $(BAUD)

default:
	@echo "help:"
	@echo "make write: write firmware image"
	@echo "make deployt: deploy boot files"
	@echo "make term:  run terminal"

$(PORT):
	test -c $(PORT)

$(ESPTOOL):
	pip install --user esptool

$(PICOCOM):
	sudo apt-get install picocom

$(AMPY_BIN):
	pip install --user adafruit-ampy

$(FIRMWARE):
	curl -LO http://micropython.org/resources/firmware/$@

write: $(FIRMWARE) $(ESPTOOL)
	 $(ESPTOOL) write_flash --compress $(ADDRESS) $(FIRMWARE)

shell:
term: $(PICOCOM)
	$(PICOCOM) $(PORT) -b$(BAUD)

$(SCREEN_DRIVER):
	curl -LO $(SCREEN_DRIVER_URL)

screen: $(SCREEN_DRIVER) | $(PORT)
	$(AMPY) put $(SCREEN_DRIVER)

ls: $(AMPY_BIN) | $(PORT)
	$(AMPY) ls

clean:
	rm -f $(FIRMWARE)

deploy: | $(PORT)
	$(AMPY) put boot.py
	$(AMPY) put config.json
	$(AMPY) put $(SCREEN_DRIVER)
