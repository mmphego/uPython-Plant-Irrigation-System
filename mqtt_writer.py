# Writer interface over umqtt API.
from machine import unique_id
from ubinascii import hexlify
from umqtt.simple import MQTTClient

CLIENT_ID = hexlify(unique_id())


class MQTTWriter:
    __variables__ = ("host", "client")

    def __init__(self, host):
        self.host = host
        self.client = MQTTClient(CLIENT_ID, host)
        self._connect()

    def _connect(self):
        print("Connecting to %s" % (self.host))
        self.client.connect()
        print("Connection successful")

    def publish(self, topic, msg, encoder="utf-8"):
        print("Publishing message: %s on topic: %s" % (msg, topic))
        self.client.publish(bytes(topic, encoder), bytes(msg, encoder))
        print("Published Successfully!")
