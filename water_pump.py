from machine import Pin

class WaterPump:
    def __init__(self, pin):
        self.pin = pin
        self.pump_status = False
        self.pump = Pin(self.pin, Pin.OUT)

    def pump_on(self):
        try:
            print("[INFO] Pump ON")
            self.pump_status = True
            self.pump(1)
        except Exception:
            self.pump(0)
            print("[ERROR] Failed turn Pump On!")

    def pump_off(self):
        try:
            print("[INFO] Pump OFF")
            self.pump_status = False
            self.pump(0)
        except Exception:
            self.pump(0)
            print("[ERROR] Failed turn Pump Off!")
