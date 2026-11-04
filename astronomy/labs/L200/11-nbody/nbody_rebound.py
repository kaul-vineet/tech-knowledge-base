"""REBOUND 5.2.2 (GPL-3.0) equivalent of nbody.py (pending-ci). python nbody_rebound.py"""
import numpy as np
import rebound

import nbody as nb


def compare(years=2.0, dt=0.001):
    sim = rebound.Simulation()
    sim.G = nb.G  # same units: au, yr, Msun
    pos, vel = nb.initial_state()
    for m, p, v in zip(nb.MASSES, pos, vel):
        sim.add(m=float(m), x=p[0], y=p[1], z=p[2], vx=v[0], vy=v[1], vz=v[2])
    sim.integrator, sim.dt = "leapfrog", dt
    sim.integrate(years, exact_finish_time=0)  # REBOUND's leapfrog is drift-kick-drift
    ps = sim.particles
    theirs = float(np.hypot(ps[1].x - ps[0].x, ps[1].y - ps[0].y))
    p, _, _, _ = nb.run(nb.step_leapfrog, years=years, dt=dt, com=False)
    return float(np.linalg.norm(p[1] - p[0])), theirs


if __name__ == "__main__":
    ours, theirs = compare()
    print(f"Earth-Sun distance after 2 yr: ours {ours:.6f} au, REBOUND leapfrog {theirs:.6f} au")
