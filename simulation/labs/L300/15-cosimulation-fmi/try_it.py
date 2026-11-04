"""tryIt experiments for lesson 15 (run: python try_it.py)."""
import cosim
from units import Room, Thermostat

# 1. Sweep the communication step. Predict: where does the loop start to oscillate (theory says ~313 s)?
for h in (180, 240, 300, 360):
    m = cosim.metrics(cosim.run(h))
    print(f"h={h:3d} s: last-hour swing {m['last_hour_swing_C']:.2f} C, heater flips {m['heater_flips']}")


# 2. Gauss-Seidel coupling: step the room FIRST, then give the thermostat the NEW temperature. Predict: stable at 450 s?
def gauss_seidel(h, hours=6.0):
    room, ctrl = Room(), Thermostat()
    for u in (room, ctrl):
        u.instantiate()
        u.setup_experiment(0.0)
    t, records = 0.0, []
    for _ in range(round(hours * 3600 / h)):
        room.set_real([room.vr("heater")], ctrl.get_real([ctrl.vr("heater")]))
        room.do_step(t, h)
        ctrl.set_real([ctrl.vr("T")], room.get_real([room.vr("T")]))  # fresh value: one step less delay
        ctrl.do_step(t, h)
        t += h
        records.append({"t_min": t / 60, "h_s": h, "T_room": room.get_real([room.vr("T")])[0],
                        "heater": ctrl.get_real([ctrl.vr("heater")])[0]})
    return records


for h in (450, 900):
    print(f"Gauss-Seidel h={h} s: {cosim.metrics(gauss_seidel(h))}")
