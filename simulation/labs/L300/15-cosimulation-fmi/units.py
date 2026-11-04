"""Two co-simulation units with an FMI-like interface (names follow FMI 2.0 Co-Simulation: fmi2DoStep etc.).

Each unit owns its state and its own solver; the master only sets inputs, calls do_step and reads outputs
at communication points. This mirrors what FMPy does with a real FMU (FMU2Slave: instantiate, setupExperiment,
enterInitializationMode, exitInitializationMode, setReal/getReal by value reference, doStep, terminate).
"""


class Unit:
    model_description = {}  # variable name -> (value reference, causality), like modelDescription.xml

    def __init__(self, **params):
        self.v = {}  # values by value reference
        self.params = params

    def instantiate(self):
        for name, (vr, _) in self.model_description.items():
            self.v[vr] = float(self.params.get(name, self.start.get(name, 0.0)))

    def setup_experiment(self, start_time=0.0):
        self.time = start_time

    def enter_initialization_mode(self):
        pass

    def exit_initialization_mode(self):
        pass

    def set_real(self, vrs, values):
        for vr, value in zip(vrs, values):
            self.v[vr] = float(value)

    def get_real(self, vrs):
        return [self.v[vr] for vr in vrs]

    def do_step(self, current_communication_point, communication_step_size):
        raise NotImplementedError

    def terminate(self):
        pass

    def vr(self, name):
        return self.model_description[name][0]


class Room(Unit):
    """Thermal room: C dT/dt = heater*Q_max - (T - T_out)/R. Internal solver: RK4 with <= 60 s substeps."""
    model_description = {"heater": (0, "input"), "T": (1, "output"), "T_out": (2, "parameter"),
                         "R": (3, "parameter"), "C": (4, "parameter"), "Q_max": (5, "parameter")}
    start = {"heater": 0.0, "T": 15.0, "T_out": 5.0, "R": 0.008, "C": 450_000.0, "Q_max": 3000.0}  # tau = R*C = 1 h

    def do_step(self, current_communication_point, communication_step_size):
        u, T, T_out, R, C, Q = (self.v[i] for i in range(6))
        f = lambda temp: (u * Q - (temp - T_out) / R) / C  # input u is held constant over the step (ZOH)
        n = max(1, round(communication_step_size / 60))
        h = communication_step_size / n
        for _ in range(n):
            k1 = f(T)
            k2 = f(T + h / 2 * k1)
            k3 = f(T + h / 2 * k2)
            k4 = f(T + h * k3)
            T += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        self.v[1], self.time = T, current_communication_point + communication_step_size


class Thermostat(Unit):
    """PI controller sampled at each communication point; output held until the next one (anti-windup)."""
    model_description = {"T": (0, "input"), "heater": (1, "output"), "setpoint": (2, "parameter"),
                         "Kp": (3, "parameter"), "Ti": (4, "parameter"), "integral": (5, "local")}
    start = {"T": 15.0, "heater": 0.0, "setpoint": 21.0, "Kp": 0.5, "Ti": 1800.0, "integral": 0.0}

    def do_step(self, current_communication_point, communication_step_size):
        T, _, sp, kp, ti, integral = (self.v[i] for i in range(6))
        error = sp - T
        raw = kp * (error + (integral + error * communication_step_size) / ti)
        if 0.0 < raw < 1.0:  # anti-windup: integrate only while the heater is not saturated
            integral += error * communication_step_size
        self.v[1] = min(1.0, max(0.0, kp * (error + integral / ti)))
        self.v[5], self.time = integral, current_communication_point + communication_step_size
