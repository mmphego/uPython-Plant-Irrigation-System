# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import gc
import uos

# uos.dupterm(None, 1) # disable REPL on UART(0)
import ubinascii
import machine
import utime as time

# import webrepl
# webrepl.start()
from wifi import wifi_connect
from mqtt_writer import MQTTWriter
from Logger import LoggingClass

gc.collect()

CONFIG = {
    # WiFI Settings
#    "ssid": "GetUrOwnWiFi",
#    "password": "Livhu300312",
    "ssid": "KATCPT",
    "password": "katCPT#12",
    # MQTT Connection
    "broker": "192.168.1.11",
    "port": 1883,
    "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id()),
}


def setup_wifi():
    wifi_connect(CONFIG["ssid"], CONFIG["password"])


def setup_mqtt():
    client = MQTTWriter(CONFIG["client_id"], CONFIG["broker"], CONFIG["port"])
    return client


if __name__ == "__main__":
    # setup_wifi()
    # client = setup_mqtt()
    # msg = "Hello world"
    # topic = "test"
    # time.sleep(2)
    # client.publish(topic, msg)
    pass