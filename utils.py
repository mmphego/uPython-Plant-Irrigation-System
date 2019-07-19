import gc
import json

import esp
import machine
import network
import ntptime
import urequests
import usocket
import utime
from ubinascii import hexlify
from umqtt.simple import MQTTClient


class WiFi:
    """
    Connect to the WiFi.
    Based on the example in the micropython documentation.
    """

    def __init__(self, essid, password):
        self.essid = essid
        self.password = password

    def wifi_connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print("connecting to network '%s'..." % self.essid)
            wlan.connect(self.essid, self.password)
            # connect() appears to be async - waiting for it to complete
            while not wlan.isconnected():
                print("[DEBUG] Waiting for connection...")
                utime.sleep(5)
            print(
                "[INFO] WiFi connect successful, network config: %s"
                % repr(wlan.ifconfig())
            )
        else:
            # Note that connection info is stored in non-volatile memory. If
            # you are connected to the wrong network, do an explicity disconnect()
            # and then reconnect.
            print(
                "[INFO] WiFi already connected, network config: %s"
                % repr(wlan.ifconfig())
            )

    def wifi_disconnect(self):
        # Disconnect from the current network. You may have to
        # do this explicitly if you switch networks, as the params are stored
        # in non-volatile memory.
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            print("[DEBUG] Disconnecting...")
            wlan.disconnect()
        else:
            print("[ERROR] WiFi not connected.")

    def disable_wifi_ap(self):
        # Disable the built-in access point.
        wlan = network.WLAN(network.AP_IF)
        wlan.active(False)
        print("[INFO] Disabled access point, network status is %s" % wlan.status())


class InitialSetUp:
    def __init__(self, config_dict, utc_shift=2):
        self.utc_shift = utc_shift
        self.setup_wifi = WiFi(
            config_dict["wifi_config"]["ssid"], config_dict["wifi_config"]["password"]
        )

    def wifi_config(self, disableAP=False):
        if disableAP:
            self.setup_wifi.disable_wifi_ap()

        try:
            print("[INFO] Connecting to WiFi")
            self.setup_wifi.wifi_connect()
            print("[INFO] Connected to WiFi")
        except Exception:
            print("[ERROR] Failed to connect to WiFi")
            utime.sleep(5)
            self.setup_wifi.wifi_disconnect()
            machine.reset()

    def set_tz(self):
        # Timezone setup
        ntptime.settime()
        rtc = machine.RTC()
        tm = utime.localtime(utime.mktime(utime.localtime()) + (self.utc_shift * 3600))
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        rtc.datetime(tm)


class Slack:
    def __init__(self, app_id, secret_id, token):
        """
        Get an "incoming-webhook" URL from your slack account.
        @see https://api.slack.com/incoming-webhooks
        eg: https://hooks.slack.com/services/<app_id>/<secret_id>/<token>
        """
        self._url = "https://hooks.slack.com/services/%s/%s/%s" % (
            app_id,
            secret_id,
            token,
        )

    def slack_it(self, msg):
        """ Send a message to a predefined slack channel."""
        headers = {"content-type": "application/json"}
        data = '{"text":"%s"}' % msg
        resp = urequests.post(self._url, data=data, headers=headers)
        return "Message Sent" if resp.status_code == 200 else "Failed to sent message"


class MQTTWriter:
    """Writer interface over umqtt API."""

    __variables__ = ("host", "client")
    __flag = False

    def __init__(self, host):
        self.host = host
        if self.host:
            self.client = MQTTClient(
                client_id=hexlify(machine.unique_id()), server=self.host
            )
            self.check_ip_up()
            self._connect()

    def check_ip_up(self):
        try:
            s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.host, 1883))
            print("[INFO] Host %s is UP!" % self.host)
            self.__flag = True
        except Exception:
            print("[ERROR] Host %s is DOWN!" % self.host)
            utime.sleep(1)
        finally:
            s.close()

    def _connect(self):
        print("[INFO] Connecting to %s" % (self.host))
        if self.__flag:
            self.client.connect()
            print("[INFO] Connection successful")
        else:
            print("[ERROR] Cannot connect to host:%s" % self.host)

    def publish(self, topic="", msg="", encoder="utf-8"):
        print("[INFO] Publishing message: %s on topic: %s" % (msg, topic))
        if self.__flag:
            self.client.publish(bytes(topic, encoder), bytes(msg, encoder))
            print("[INFO] Published Successfully!")
        else:
            print("[ERROR] Failed to Publish the message, Link is not UP!")


class Ubidots:
    def __init__(self, TOKEN, device_label):
        self.url = "https://things.ubidots.com/api/v1.6/devices/{}?token={}".format(
            device_label, TOKEN
        )

    def post_request(self, payload):
        """Creates the headers for the HTTP requests and Makes the HTTP requests"""
        print("[DEBUG] Uploading Payload: %s" % payload)
        assert isinstance(payload, dict)

        status = 400
        attempts = 0
        while status >= 400 and attempts <= 5:
            req = urequests.post(url=self.url, json=payload)
            status = req.status_code
            attempts += 1
            utime.sleep(1)
            print("[DEBUG] Sending data to Ubidots...")

        # Processes results
        if status == 200:
            print("[INFO] Request made properly, Updated Ubidots with %s." % payload)
            return True
        else:
            print(
                "[ERROR] Could not send data after 5 attempts, please check "
                "your token credentials and internet connection."
            )
            return False


def force_garbage_collect():
    # Not so ideal but someone has to do it
    gc.collect()
    gc.mem_free()


def current_time():
    year, month, day, hours, mins, secs, _, _ = utime.localtime()
    hours = "0" + str(hours) if hours < 10 else hours
    secs = "0" + str(secs) if secs < 10 else secs
    mins = "0" + str(mins) if mins < 10 else secs
    datetime = "%s-%s-%s %s:%s:%s" % (year, month, day, hours, mins, secs)
    return datetime


def read_config(filename):
    with open(filename) as _f:
        config = json.load(_f)
    assert isinstance(config, dict)
    return config


def enter_deep_sleep(secs):
    # For some weird reason, my Wemos D1 does not wake up from deepsleep
    """
    Ensure that pin RST & D0 are connected!
    """
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after Xseconds, waking the device
    sleep_timeout = secs * 1000
    rtc.alarm(rtc.ALARM0, sleep_timeout)
    print("Sleep for %d sec" % sleep_timeout)
    # put the device to sleep
    machine.deepsleep()


def adc_map(current_val, from_Low, from_High, to_Low=0, to_High=100):
    """
    Re-maps a number from one range to another.
    That is, a value of 'from_Low' would get mapped to 'to_Low',
    a value of 'from_High' to 'to_High', values in-between to values in-between, etc.

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
    from_Low: the lower bound of the value’s current range.
    from_High: the upper bound of the value’s current range.
    to_Low: the lower bound of the value’s target range.
    to_High: the upper bound of the value’s target range.

    Adapted from https://www.arduino.cc/reference/en/language/functions/math/map/
    """

    return (current_val - from_Low) * (to_High - to_Low) / (from_High - from_Low) + to_Low


def average(samples):
    ave = sum(samples, 0.0) / len(samples)
    return ave if ave > 0 else 0
