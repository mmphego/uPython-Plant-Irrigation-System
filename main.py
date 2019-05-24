import time
import machine
from boot import read_config
from Logger import LoggingClass


__all__ = ["MoistureSensor"]


class MoistureSensor(LoggingClass):
    def __init__(self, adc_pin, config_dict, sleep=1):
        self.adc_pin = adc_pin
        self.sensor_cal = config_dict
        self.sleep = sleep
        self.setup_adc()

    def setup_adc(self):
        # self.logger.info("Setting up ADC on pin %s", self.adc_pin)
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

    def current_time(self):
        hours = str(time.localtime()[3])
        mins = str(time.localtime()[4])
        secs = str(time.localtime()[5])
        if int(secs) < 10:
            secs = '0' + secs
        if int(mins) < 10:
            mins = '0' + mins
        timestr = "%s:%s:%s" % (hours, mins, secs)
        return timestr

    def run(self):
        try:
            while True:
                SoilMoistPerc = self.adc_map(
                    self.read,
                    self.sensor_cal["wet"],
                    self.sensor_cal["dry"],
                    0, 100
                )
                # self.logger.info("SoilMoist is at %s%", SoilMoistPerc)
                print("ADC Value: %s \t %s" % (SoilMoistPerc,  self.current_time()))
                time.sleep(sleep)
        except Exception:
            machine.reset()

if __name__ == '__main__':
    config = read_config("config.json")
    moisture_Sensor = MoistureSensor(0, config)
    moisture_Sensor.run()