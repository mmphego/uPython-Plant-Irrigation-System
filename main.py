import time
import machine

from utils import current_time, read_config

__all__ = ["MoistureSensor"]


class MoistureSensor(object):
    def __init__(self, adc_pin, config_dict, sleep=60):
        self.adc_pin = adc_pin
        self.sensor_cal = config_dict
        self.sleep = sleep
        self.setup_adc()

    def setup_adc(self):
        self.adc = machine.ADC(self.adc_pin)

    @property
    def read(self):
        adc_value = float(self.adc.read())
        return adc_value

    def adc_map(self, current_val, fromLow, fromHigh, toLow, toHigh):
        """
        Re-maps a number from one range to another.
        That is, a value of 'fromLow' would get mapped to 'toLow',
        a value of 'fromHigh' to 'toHigh', values in-between to values in-between, etc.

        Does not constrain values to within the range, because out-of-range values are
        sometimes intended and useful.

        y = adc_map(x, 1, 50, 50, 1);

        The function also handles negative numbers well, so that this example

        y = adc_map(x, 1, 50, 50, -100);

        is also valid and works well.

        The adc_map() function uses integer math so will not generate fractions,
        when the math might indicate that it should do so.
        Fractional remainders are truncated, and are not rounded or averaged.

        Parameters
        ----------
        value: the number to map.
        fromLow: the lower bound of the value’s current range.
        fromHigh: the upper bound of the value’s current range.
        toLow: the lower bound of the value’s target range.
        toHigh: the upper bound of the value’s target range.

        Adapted from https://www.arduino.cc/reference/en/language/functions/math/map/
        """

        return (current_val - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow

    def run(self):
        try:
            SoilMoistPerc = self.adc_map(
                self.read, self.sensor_cal["wet"], self.sensor_cal["dry"], 0, 100
            )
            print("Soil Moisture Sensor: %s% \t %s" % (SoilMoistPerc, current_time()))
        except Exception:
            machine.reset()


if __name__ == "__main__":
    config = read_config("config.json")
    pin_adc = 0
    moisture_Sensor = MoistureSensor(pin_adc, config["moisture_sensor_cal"])
    moisture_Sensor.run()
