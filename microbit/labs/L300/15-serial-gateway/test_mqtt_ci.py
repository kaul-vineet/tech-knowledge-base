"""pending-ci: publish through a real Mosquitto broker with paho-mqtt 2.1.0.

Skipped unless MQTT_BROKER=host:port is set and paho-mqtt is installed
(the CI job "gateway-mqtt" does both). Not run in the authoring sandbox.
"""
import json
import os
import sys
import threading
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BROKER = os.environ.get("MQTT_BROKER")
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


@unittest.skipUnless(BROKER and mqtt, "needs MQTT_BROKER and paho-mqtt (CI job gateway-mqtt)")
class ThroughBroker(unittest.TestCase):
    def test_readings_and_metrics_arrive(self):
        import serial_link
        import solution
        from mqtt_bridge import MqttPublisher
        host, _, port = BROKER.partition(":")
        got, done = [], threading.Event()

        def on_message(client, userdata, msg):
            got.append((msg.topic, json.loads(msg.payload)))
            if msg.topic == "microbit/gateway/metrics" and got[-1][1]["frames_ok"] == 190:
                done.set()

        sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lab15-test-sub")
        sub.on_message = on_message
        sub.connect(host, int(port or 1883), 60)
        sub.subscribe("microbit/#", qos=1)
        sub.loop_start()
        pub = MqttPublisher(host, int(port or 1883))
        try:
            chunks, _ = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)
            solution.run(chunks, pub)
            self.assertTrue(done.wait(10), "final metrics message not received")
        finally:
            pub.close()
            sub.loop_stop()
            sub.disconnect()
        telemetry = [p for t, p in got if t == "microbit/mb1/telemetry"]
        self.assertEqual(len(telemetry), 190)


if __name__ == "__main__":
    unittest.main(verbosity=2)
