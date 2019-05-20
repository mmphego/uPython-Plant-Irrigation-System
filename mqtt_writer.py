# Writer interface over umqtt API.
from umqtt.simple import MQTTClient


class MQTTWriter:
    __variables__ = ("host", "port", "client")

    def __init__(self, client_id, host, port):
        self.host = host
        self.port = port
        self.client = MQTTClient(host, host, port)
        self._connect()

    def _connect(self):
        print("Connecting to %s:%s" % (self.host, self.port))
        self.client.connect()
        print("Connection successful")

    def publish(self, topic, msg, encoder="utf-8"):
        print("Publishing message: %s on topic: %s" % (msg, topic))
        self.client.publish(bytes(topic, encoder), bytes(msg, encoder))
        print("Published Successfully!")
