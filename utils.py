import json
import ntptime
import machine
import utime

def set_tz(utc_shift=2):
    # Timezone setup
    ntptime.settime()
    rtc = machine.RTC()
    tm = utime.localtime(utime.mktime(utime.localtime()) + (utc_shift*3600))
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    rtc.datetime(tm)

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


class PackageInstaller(object):
    def check_and_install(self):
        try:
            import logging
        except Exception:
            import upip

            pkg = "micropython-logging"
            print("Installing '%s'" % pkg)
            upip.install(pkg)
            import logging

            print("Successfully installed %s" % logging.__name__)
