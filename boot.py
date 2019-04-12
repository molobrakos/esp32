import webrepl
import machine
import ssd1306
import esp
import esp32
import network
import json
import time


CONFIG="config.json"


def screen():
    i2c = machine.I2C(scl=machine.Pin(4),
                      sda=machine.Pin(5))
    return ssd1306.SSD1306_I2C(128, 64, i2c)


def print_info(oled):
    output = dict(
        freq = machine.freq(),
        flash = esp.flash_size(),
        hall = esp32.hall_sensor(),
        temp = esp32.raw_temperature()
    )

    output = ["%s: %d" % (key, val)
              for key, val in output.items()]

    oled.fill(0)
    for idx, line in enumerate(output):
        print(line)
        oled.text(line, 0, idx * 10)
    oled.show()


def connect(essid, password):
    wlan = network.WLAN(network.STA_IF)
    print("connected", wlan.isconnected())
    print("mac", wlan.config('mac'))
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(essid, password)
        while not wlan.isconnected():
            time.sleep_ms(500)
    print('network config:', wlan.ifconfig())


def read_config():
    with open(CONFIG) as f:
        return json.loads(f.read())


webrepl.start()
print_info(screen())
config = read_config()
connect(**config)
