"""Publish the gateway's messages to a real MQTT broker (pending-ci; not run here).

Needs paho-mqtt 2.1.0 (pip install paho-mqtt==2.1.0) and a broker such as
Eclipse Mosquitto on 127.0.0.1:1883. Same publish(topic, payload, qos) interface
as gateway.JsonLinesPublisher, so solution.run() works with either.
API per https://pypi.org/project/paho-mqtt/ (2.x: CallbackAPIVersion.VERSION2).
"""
import json

import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, host="127.0.0.1", port=1883, client_id="microbit-gateway"):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.client.connect(host, port, 60)
        self.client.loop_start()             # background network thread
        self.sent = []

    def publish(self, topic, payload, qos=1):
        info = self.client.publish(topic, json.dumps(payload, sort_keys=True), qos=qos)
        info.wait_for_publish(timeout=5)     # QoS 1: wait for the broker's PUBACK
        self.sent.append({"topic": topic, "qos": qos, "payload": payload})

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
