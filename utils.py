import esp
import gc
import json
import machine
import ntptime
import urequests
import utime

from wifi import disable_wifi_ap, wifi_connect, wifi_disconnect


class InitialSetUp(object):
    def __init__(self, config_dict, utc_shift=2):
        self.config_dict = config_dict
        self.utc_shift = utc_shift

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

    def set_tz(self):
        # Timezone setup
        ntptime.settime()
        rtc = machine.RTC()
        tm = utime.localtime(utime.mktime(utime.localtime()) + (self.utc_shift * 3600))
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        rtc.datetime(tm)


class Slack(object):
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
    """
    Ensure that pin RST & D0 are connected!
    """
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
    rtc.alarm(rtc.ALARM0, secs)
    # put the device to sleep
    machine.deepsleep()

