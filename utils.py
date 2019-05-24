import json
import time


def current_time():
    year, month, day, hours, mins, secs, _, _ = time.localtime()
    if secs < 10:
        secs = "0" + str(secs)
    if int(mins) < 10:
        mins = "0" + str(mins)
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
