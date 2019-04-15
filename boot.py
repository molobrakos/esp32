import webrepl
import machine
import ssd1306
import esp
import esp32
import network
import json
import time
import gc
import micropython
import ubinascii


CONFIG="config.json"
HOSTNAME="esp32"
FREQ=80_000_000


def bin2hex(b):
    return ubinascii.hexlify(b, ":").decode()


def dbm2q(dbm):
    if dbm <= -100:
        return 0
    elif dbm >= -50:
        return 100
    else:
        return 2 * (dbm + 100)


class Screen:

    def __init__(self):
        i2c = machine.I2C(scl=machine.Pin(4),
                          sda=machine.Pin(5))
        self.screen = ssd1306.SSD1306_I2C(128, 64, i2c)

    def display_lines(self, lines):
        self.screen.fill(0)
        for idx, line in enumerate(lines):
            print(line)
            self.screen.text(line, 0, idx * 10)
        self.screen.show()


class Network:

    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False)
        self.wlan.active(True)
        self.wlan.disconnect()

    def connect(self, essid="", password=""):
        print("scanning")
        networks = self.wlan.scan()
        for ssid, bssid, _, rssi, auth, hidden in networks:
            print("network: ",
                  ssid.decode("utf-8"),
                  bin2hex(bssid),
                  dbm2q(rssi),
                  "%",
                  "WPA/WPA2-PSK" if auth == 4
                  else "WPA2-PSK" if auth == 3
                  else "WPA-PSK" if auth == 2
                  else "WEP" if auth == 1
                  else "open" if auth == 0
                  else "?",
                  "hidden" if hidden else "visible")

        # FIXME: iterate over found essids, use corresponding key in config
        print("connected", self.is_connected)
        print("mac", self.mac)
        self.wlan.config(dhcp_hostname=HOSTNAME)
        if not self.is_connected:
            print("connecting to network ...", essid)
            self.wlan.connect(essid, password)
            while not self.wlan.isconnected():
                time.sleep_ms(500)
        print("... connected to", essid, "my ip", self.ip)

    @property
    def is_connected(self):
        return self.wlan.isconnected()

    @property
    def mac(self):
        return bin2hex(self.wlan.config('mac'))

    @property
    def ip(self):
        ip, nw, gw, dns = self.wlan.ifconfig()
        return ip


class App:

    def __init__(self):
        with open(CONFIG) as f:
            self.config = json.loads(f.read())
        self.network = Network()
        self.screen = Screen()

    def run(self):
        self.set_frequency()
        self.display_info()
        self.network.connect(**self.config)
        while True:
            self.display_info()
            time.sleep_ms(1000)

    def set_frequency(self):
        print("frequency is", machine.freq() / 1_000_000)
        machine.freq(FREQUENCY)
        print("frequency is", machine.freq() / 1_000_000)

    def display_info(self):
        gc.collect()
        output = dict(
            freq = int(machine.freq() / 1_000_000),
            flash = esp.flash_size(),
            hall = esp32.hall_sensor(),
            temp = int((esp32.raw_temperature() - 32) / 1.8),
            mac = self.network.mac,
            ip = self.network.ip,
            ram = gc.mem_free(),
        )

        output = ["%s: %s" % (key, val)
                  for key, val in output.items()]

        self.screen.display_lines(output)


print("wake reason", machine.wake_reason())

help("modules")
import builtins
dir(builtins)

dir(machine)
dir(esp)
dir(esp32)

App().run()

# machine.deep_sleep(30_000)
