import machine
import utime

from utils import (
    adc_map,
    average,
    current_time,
    force_garbage_collect,
    MQTTWriter,
    Slack,
    Ubidots,
)

from water_pump import WaterPump


class MoistureSensor(object):
    def __init__(self, config_dict):
        """
        Sensor calibration
        ######################
        This was determined by placing the sensor in&out of water, and reading the ADC value
        Note: That this values might be unique to individual sensors, ie your mileage may vary
        dry air = 841 (0%) eq 0v ~ 0
        water = 470 (100%) eq 3.3v ~ 1023
        Expects a dict:
            config_dict = {"moisture_sensor_cal": {"dry": 841, "wet": 470}
        """
        self.config = config_dict
        self._adc = None
        self._mqtt = None
        self._slack = None
        self._ubidots = None
        self._water_me = False
        self._water_pump = None

    @property
    def ubidots(self):
        if (self.config["ubidots"]["token"]) and (not self._ubidots):
            self._ubidots = Ubidots(
                self.config["ubidots"]["token"], self.config["ubidots"]["device"]
            )
        return self._ubidots

    @property
    def water_pump(self):
        if (self.config["Pin_Config"]["Water_Pump_Pin"]) and (not self._water_pump):
            self._water_pump = WaterPump(self.config["Pin_Config"]["Water_Pump_Pin"])
        return self._water_pump

    @property
    def adc(self):
        if (self.config["Pin_Config"]["ADC_Pin"]) and (not self._adc):
            self._adc = machine.ADC(self.config["Pin_Config"]["ADC_Pin"])
        return self._adc

    @property
    def slack(self):
        """Slack message init"""
        if (self.config["slack_auth"].get("app_id")) and (not self._slack):
            self._slack = Slack(
                self.config["slack_auth"]["app_id"],
                self.config["slack_auth"]["secret_id"],
                self.config["slack_auth"]["token"],
            )
        return self._slack.slack_it

    @property
    def mqtt(self):
        if (self.config["MQTT_config"].get("Host")) and (not self._mqtt):
            self._mqtt = MQTTWriter(self.config["MQTT_config"]["Host"])
        return self._mqtt

    def read_samples(self, n_samples=10, rate=0.5):
        sampled_adc = []
        for i in range(n_samples):
            sampled_adc.append(self.adc.read())
            utime.sleep(rate)
        force_garbage_collect()
        return sampled_adc

    def message_send(self, msg):
        self.slack(msg)
        print(msg)

    def soil_sensor_check(self):
        try:
            samples = self.read_samples()
            sampled_adc = average(samples)
            SoilMoistPerc = adc_map(
                sampled_adc,
                self.config["moisture_sensor_cal"]["dry"],
                self.config["moisture_sensor_cal"]["wet"],
            )
            self.ubidots.post_request({"soil_moisture": SoilMoistPerc})
            if SoilMoistPerc <= self.config["moisture_sensor_cal"].get("Threshold", 50):
                self.message_send(
                    "Soil Moisture Sensor: %.2f%% \t %s" % (SoilMoistPerc, current_time())
                )
                self._water_me = True
            else:
                self._water_me = False
        except Exception as exc:
            print("Exception: %s", exc)
        finally:
            force_garbage_collect()

    def run_timer(self, secs=60):
        while True:
            self.soil_sensor_check()
            while self._water_me:
                self.message_send(
                    "Automatically watering the plant(s): %s" % current_time()
                )
                if not self.water_pump.pump_status:
                    self.water_pump.pump_on()
                if self.water_pump.pump_status:
                    self.soil_sensor_check()
                self.water_pump.pump_off()

            utime.sleep(secs)
        print("Timer Initialised, callback will be ran every %s seconds!!!" % secs)
