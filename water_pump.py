from machine import Pin
from utime import sleep

class WaterPump:

    def __init__(self, pin, delay_pump_on=5):
        self.pin = pin
        self.delay_pump_on = delay_pump_on
        self._pump = None
        self.pump_status = False

    @property
    def pump(self):
        if not self._pump:
            self._pump = Pin(self.pin, machine.Pin.OUT)
        return self._pump

    def pump_on(self):
        print(f"Pump ON for {self.delay_pump_on}seconds")
        self.pump.high()
        sleep(self.delay_pump_on)
        self.pump_status = True

    def pump_off(self):
        print(f"Pump OFF!")
        self.pump.low()
        self.pump_status = False