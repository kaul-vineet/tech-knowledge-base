"""CI only (pending-ci): publish the capstone's stored readings to a real broker (Mosquitto) with
paho-mqtt 2.1.0 through lab 15's MqttPublisher. Skipped unless MQTT_BROKER=host:port is set."""
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
BROKER = os.environ.get("MQTT_BROKER")


@unittest.skipUnless(BROKER, "needs MQTT_BROKER=127.0.0.1:1883 and paho-mqtt (CI job gateway-mqtt)")
class RealBroker(unittest.TestCase):
    def test_publish_capstone_rows(self):
        import build_firmware
        import pipeline
        bridge = pipeline.reuse("L300/15-serial-gateway/mqtt_bridge.py", "l300_mqtt_bridge")
        _, gw, _ = pipeline.run_network(build_firmware.build(), duration_s=60)
        host, _, port = BROKER.partition(":")
        pub = bridge.MqttPublisher(host, int(port or 1883))
        try:
            for row in gw.rows:
                pub.publish("classroom/%s/telemetry" % row["dev"], row, qos=1)
        finally:
            pub.close()
        self.assertGreaterEqual(len(gw.rows), 350)


if __name__ == "__main__":
    unittest.main(verbosity=2)
