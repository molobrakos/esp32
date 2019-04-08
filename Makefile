ESPTOOL=$(HOME)/.local/bin/esptool.py
ADDRESS=0x1000
PORT=/dev/ttyUSB0
FIRMWARE=esp32-20190125-v1.10.bin
PICOCOM=/usr/bin/picocom

default:
	@echo "make write: write image"
	@echo "make term:  run terminal"

$(ESPTOOL):
	pip install --user esptool

$(PICOCOM):
	sudo apt-get install picocom

$(FIRMWARE):
	curl -LO http://micropython.org/resources/firmware/$@

write: $(FIRMWARE) $(ESPTOOL)
	 $(ESPTOOL) write_flash --compress $(ADDRESS) $(FIRMWARE)

term: $(PICOCOM)
	$(PICOCOM) $(PORT) -b115200

clean:
	rm -f $(FIRMWARE)
