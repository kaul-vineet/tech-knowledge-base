"""buildTask solution (lesson 15): COMM_STEP_S = 60 s. Otherwise identical to the lab file.

L300 co-simulation: a master algorithm couples a room unit and a thermostat unit at fixed communication steps.

Fixed-step Jacobi master: at every communication point read outputs, set inputs, then step both units.
Every step is logged as one JSON line (cosim_log.jsonl) so you can diagnose the run from the log.
python solution/cosim.py   # runs at COMM_STEP_S
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # solution copy: units.py lives in the lab folder
from units import Room, Thermostat  # noqa: E402

COMM_STEP_S = 60  # FIX: well below the stability bound tau ln(K/(K-1)) = 313 s for this loop


def run(h=COMM_STEP_S, hours=6.0, log_path=None, room=None, thermostat=None):
    """Master algorithm. h = communication step in seconds. Returns per-step records."""
    room, ctrl = room or Room(), thermostat or Thermostat()
    for unit in (room, ctrl):
        unit.instantiate()
        unit.setup_experiment(start_time=0.0)
        unit.enter_initialization_mode()
        unit.exit_initialization_mode()
    t, records = 0.0, []
    for _ in range(round(hours * 3600 / h)):
        temp = room.get_real([room.vr("T")])[0]  # 1. read outputs at communication point t
        heater = ctrl.get_real([ctrl.vr("heater")])[0]
        ctrl.set_real([ctrl.vr("T")], [temp])  # 2. exchange: outputs -> inputs
        room.set_real([room.vr("heater")], [heater])
        room.do_step(t, h)  # 3. both units advance from t to t + h with inputs held constant
        ctrl.do_step(t, h)
        records.append({"t_min": round(t / 60, 2), "h_s": h, "T_room": round(temp, 3), "heater": round(heater, 3)})
        t += h
    for unit in (room, ctrl):
        unit.terminate()
    if log_path:
        Path(log_path).write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return records


def metrics(records, setpoint=21.0):
    """Health metrics a monitor can compute from the log: last-hour swing, mean error, heater on/off flips."""
    last = [r for r in records if r["t_min"] > records[-1]["t_min"] - 60]
    temps = [r["T_room"] for r in last]
    flips = sum(abs(a["heater"] - b["heater"]) > 0.5 for a, b in zip(records, records[1:]))
    return {"h_s": records[0]["h_s"], "last_hour_swing_C": round(max(temps) - min(temps), 2),
            "last_hour_mean_error_C": round(sum(abs(x - setpoint) for x in temps) / len(temps), 2),
            "heater_flips": flips}


def main(argv=sys.argv[1:]):
    h = int(argv[0]) if argv else COMM_STEP_S
    path = HERE / f"cosim_log_{h}s.jsonl"
    records = run(h, log_path=path)
    print(json.dumps(metrics(records)))  # structured summary line
    print(f"  {path.name}: {len(records)} lines; last 4:")
    for line in path.read_text(encoding="utf-8").splitlines()[-4:]:
        print("   ", line)


if __name__ == "__main__":
    sys.exit(main())
