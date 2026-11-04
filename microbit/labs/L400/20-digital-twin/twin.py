"""Lab 20 - digital twin of the classroom sensor network: drift check (BEFORE).

The twin (twin_model.py) predicts, per device and 30-reading window, two things the gateway can see:
  lat   the share of readings that needed a radio retransmission (from the link-loss model)
  temp  the reading minus the room model (from the thermal model + the board's calibrated offset)
and turns predicted vs observed into z-scores (observed - predicted, in model standard deviations).
This version alarms on ANY single window with |z| > Z_LIMIT. A tight limit catches drift earlier, but
every noisy window is a false alarm; the twin has no memory, so slow drift hides inside the noise.
"""
import json

import twin_model

Z_LIMIT = 2.0


class Twin:
    def __init__(self, params):
        self.params = params                 # calibrated per device: loss, offset, temp_sd
        self.alarms, self.log = [], []

    def update(self, dev, obs):
        """Feed one observed window; return the alarms it raised."""
        z = twin_model.z_scores(self.params, dev, obs)
        raised = []
        for signal in ("lat", "temp"):
            if abs(z[signal]) > Z_LIMIT:     # memoryless threshold on one window
                raised.append({"t": obs["t"], "dev": dev, "alarm": "DRIFT_" + signal.upper(),
                               "z": round(z[signal], 1)})
        self.log.append(json.dumps({"t": obs["t"], "dev": dev, "z_lat": round(z["lat"], 2),
                                    "z_temp": round(z["temp"], 2)}))
        self.alarms += raised
        return raised
