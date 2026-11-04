"""tryIt experiments for lesson 4 (run: python try_it.py)."""
import math

import falling as f

# 1. Big step with drag: explicit Euler dt=0.5 s vs RK4 dt=0.001 s.
for name, stepper, dt in (("Euler dt=0.5", f.step_euler, 0.5), ("RK4 dt=0.001", f.step_rk4, 0.001)):
    t, v = f.time_to_ground(stepper, dt, True)
    print(f"{name}: ground at {t:.2f} s, impact {abs(v):.2f} m/s")

# 2. Double the parcel mass (2 kg -> 4 kg).
f.MASS = 4.0
t, v = f.time_to_ground(f.step_rk4, 0.001, True)
print(f"4 kg parcel: terminal velocity {f.terminal_velocity():.2f} m/s (x{f.terminal_velocity() / 18.40:.2f}), ground at {t:.2f} s")
print(f"sqrt(2) = {math.sqrt(2):.3f}")
