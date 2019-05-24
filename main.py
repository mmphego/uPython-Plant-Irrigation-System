import gc
import machine
import utime

from utils import current_time, read_config

__all__ = ["MoistureSensor"]


def force_garbage_collect():
    # Not so ideal but someone has to do it
    gc.collect()
    gc.mem_free()


class MoistureSensor(object):
    def __init__(self, adc_pin, config_dict):
        self.adc_pin = adc_pin
        self.sensor_cal = config_dict
        self.setup_adc()

    def setup_adc(self):
        self.adc = machine.ADC(self.adc_pin)

    def average(self, samples):
        return sum(samples, 0.0) / len(samples)

    def read_samples(self, n_samples=10, rate=0.5):
        sampled_adc = []
        for i in range(n_samples):
            sampled_adc.append(self.adc.read())
            utime.sleep(rate)
        force_garbage_collect()
        return sampled_adc

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
            samples = self.read_samples()
            print(samples)
            sampled_adc = self.average(samples)
            print("sampled_adc: %s" % sampled_adc)
            SoilMoistPerc = self.adc_map(
                sampled_adc, self.sensor_cal["wet"], self.sensor_cal["dry"], 0, 100)
            print("Soil Moisture Sensor: %.2f%% \t %s" % (SoilMoistPerc, current_time()))
        except Exception as exc:
            print("Exception: %s", exc)


if __name__ == "__main__":
    config = read_config("config.json")
    moisture_Sensor = MoistureSensor(0, config["moisture_sensor_cal"])
    moisture_Sensor.run()
    force_garbage_collect()
