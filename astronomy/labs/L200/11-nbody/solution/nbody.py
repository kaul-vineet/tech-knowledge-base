"""Build-task SOLUTION. L200 N-body simulation: Euler vs leapfrog, energy conservation, Sun + Earth + Jupiter.

Units: au, years, solar masses, so G = 4 pi^2. Start: circular orbits in one plane, Sun at rest at the origin
(illustrative initial conditions, not an ephemeris).
python nbody.py
"""
import numpy as np

G = 4 * np.pi**2
NAMES = ("Sun", "Earth", "Jupiter")
MASSES = np.array([1.0, 3.003e-6, 9.546e-4])  # solar masses


def initial_state():
    pos = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 5.2026, 0.0]])
    vel = np.array([[0.0, 0.0, 0.0], [0.0, 2 * np.pi, 0.0], [-2 * np.pi / np.sqrt(5.2026), 0.0, 0.0]])  # v = sqrt(GM/r)
    return pos, vel


def to_com_frame(pos, vel, m):
    """Build task (solution): subtract the centre-of-mass position and velocity (barycentric frame)."""
    total = m.sum()
    return pos - m @ pos / total, vel - m @ vel / total  # total momentum becomes zero: the system stops drifting


def accelerations(pos, m):
    d = pos[None, :, :] - pos[:, None, :]  # d[i, j] = r_j - r_i
    r3 = (np.sum(d * d, axis=2) + np.eye(len(m))) ** 1.5  # + eye: avoid 0/0 on the diagonal (d_ii = 0 anyway)
    return G * np.sum(d * (m[None, :, None] / r3[:, :, None]), axis=1)


def energy(pos, vel, m):
    kinetic = 0.5 * np.sum(m * np.sum(vel * vel, axis=1))
    i, j = np.triu_indices(len(m), 1)
    potential = -G * np.sum(m[i] * m[j] / np.linalg.norm(pos[i] - pos[j], axis=1))
    return kinetic + potential


def step_euler(pos, vel, m, dt):
    a = accelerations(pos, m)
    return pos + vel * dt, vel + a * dt  # both updates use the OLD state: energy drifts every orbit


def step_leapfrog(pos, vel, m, dt):
    vel = vel + 0.5 * dt * accelerations(pos, m)  # kick
    pos = pos + dt * vel  # drift
    return pos, vel + 0.5 * dt * accelerations(pos, m)  # kick: symplectic and time-reversible


def run(step, years=12.0, dt=0.001, com=True):
    pos, vel = initial_state()
    if com:
        pos, vel = to_com_frame(pos, vel, MASSES)
    e0 = energy(pos, vel, MASSES)
    com0 = MASSES @ pos / MASSES.sum()
    for _ in range(int(round(years / dt))):
        pos, vel = step(pos, vel, MASSES, dt)
    drift = abs(energy(pos, vel, MASSES) - e0) / abs(e0)
    com_shift = np.linalg.norm(MASSES @ pos / MASSES.sum() - com0)
    return pos, vel, drift, com_shift


def main():
    for name, step in (("Euler", step_euler), ("leapfrog", step_leapfrog)):
        pos, vel, drift, com_shift = run(step)
        r_earth = np.linalg.norm(pos[1] - pos[0])
        print(f"{name:<8} 12 yr, dt=0.001 yr: |dE/E| = {drift:.2e}, Earth-Sun distance {r_earth:.5f} au, "
              f"centre of mass moved {com_shift:.4f} au")
    print(f"Jupiter period from Kepler's third law: {5.2026**1.5:.3f} yr")


if __name__ == "__main__":
    main()
