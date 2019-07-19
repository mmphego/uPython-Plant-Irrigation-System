from machine import Pin
from utime import sleep


class WaterPump:
    def __init__(self, pin, delay_pump_on=2):
        self.pin = pin
        self.delay_pump_on = delay_pump_on
        self._pump = None
        self.pump_status = False

    @property
    def pump(self):
        if not self._pump:
            self._pump = Pin(self.pin, Pin.OUT)
        return self._pump

    def pump_on(self):
        try:
            print("[INFO] Pump ON for %s seconds" % self.delay_pump_on)
            self.pump.on()
            sleep(self.delay_pump_on)
        except Exception:
            print("[ERROR] Failed turn Pump On!")
        finally:
            self.pump_status = True

    def pump_off(self):
        try:
            print("[INFO] Pump OFF after %s seconds" % self.delay_pump_on)
            self.pump.off()
        except Exception:
            print("[ERROR] Failed turn Pump Off!")
        finally:
            self.pump_status = False
