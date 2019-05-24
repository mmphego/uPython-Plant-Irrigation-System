# This file is executed on every boot (including wake-boot from deepsleep)
import gc
import os
import esp
import machine
import utime

from utils import PackageInstaller, read_config, set_tz
from wifi import disable_wifi_ap, wifi_connect, wifi_disconnect

gc.collect()
esp.osdebug(None)

__all__ = ["InitialSetUp"]


class InitialSetUp(object):
    def __init__(self, config_dict):
        self.config_dict = config_dict

    def setup_wifi(self, disableAP=False):
        if disableAP:
            disable_wifi_ap()

        try:
            print("## Connecting to WiFi")
            wifi_connect(
                self.config_dict["wifi_config"]["ssid"],
                self.config_dict["wifi_config"]["password"],
            )
            print("## Connected to WiFi")
        except Exception:
            print("## Failed to connect to WiFi")
            utime.sleep(5)
            wifi_disconnect()
            machine.reset()


if __name__ == "__main__":
    CONFIG = read_config("config.json")
    run = InitialSetUp(CONFIG)
    run.setup_wifi()  # Connect to WIFI
    set_tz()  # Set timezone
    # run.setup_mqtt() # Connect to MQTT Broker

    # check for dependencies and install if missing
    # pkg_verification = PackageInstaller()
    # pkg_verification.check_and_install()
