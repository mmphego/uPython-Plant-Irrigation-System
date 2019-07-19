import machine
import utime
from utils import (
    MQTTWriter,
    Slack,
    Ubidots,
    adc_map,
    average,
    current_time,
    force_garbage_collect,
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
        if (isinstance(self.config["Pin_Config"]["Water_Pump_Pin"], int)) and (
            not self._water_pump
        ):
            self._water_pump = WaterPump(
                self.config["Pin_Config"]["Water_Pump_Pin"],
                self.config["water_pump_time"]["delay_pump_on"],
            )
        return self._water_pump

    @property
    def adc(self):
        if (isinstance(self.config["Pin_Config"]["ADC_Pin"], int)) and (not self._adc):
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
        try:
            print("[INFO] Sending message to SLACK")
            self.slack(msg)
            print("[INFO] Message sent...")
        except Exception as exc:
            print("[ERROR] Could not send SLACK message: %s" % str(exc))
        finally:
            print("[INFO] %s" % msg)

    def soil_sensor_check(self):
        try:
            samples = self.read_samples()
            sampled_adc = average(samples)
            self._soilmoistperc = adc_map(
                sampled_adc,
                self.config["moisture_sensor_cal"]["dry"],
                self.config["moisture_sensor_cal"]["wet"],
            )
            self.ubidots.post_request({"soil_moisture": self._soilmoistperc})
            if self._soilmoistperc <= self.config["moisture_sensor_cal"].get(
                "Threshold", 50
            ):
                self._water_me = True
                self.message_send(
                    "[INFO] Soil Moisture Sensor: %.2f%% \t %s"
                    % (self._soilmoistperc, current_time())
                )
            else:
                self._water_me = False
        except Exception as exc:
            print("Exception: %s", exc)
        finally:
            force_garbage_collect()

    def run_timer(self, secs=60):
        print("[INFO] Timer Initialised, callback will be ran every %s seconds!!!" % secs)
        while True:
            self.soil_sensor_check()
            while self._water_me:
                self.message_send(
                    "Note: Automatically watering the plant(s):\t %s" % current_time()
                )
                if not self.water_pump.pump_status:
                    self.water_pump.pump_on()
                    print(
                        "[DEBUG] Setting Pump ON as water is @ %.2f%%"
                        % self._soilmoistperc
                    )
                if self.water_pump.pump_status:
                    print("[DEBUG] Checking Soil Moisture Status...")
                    self.soil_sensor_check()
                    print("[DEBUG] Soil Moisture Percent @ %.2f%%" % self._soilmoistperc)
                self.water_pump.pump_off()
                print(
                    "[DEBUG] Setting Pump OFF as water is @ %.2f%%" % self._soilmoistperc
                )

            utime.sleep(secs)
