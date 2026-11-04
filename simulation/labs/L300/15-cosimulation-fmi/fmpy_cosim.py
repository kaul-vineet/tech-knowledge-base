"""FMPy equivalent (pending-ci / manual): replace the Python room unit with a real FMU and keep the same master.

1. Export the FMU with OpenModelica (Windows PC: official installer; Mac: Docker image, see LEARNING-TOOLS.md):
       omc export_fmu.mos          (or OMEdit: File > Export > FMU)  -> RoomThermal.fmu
2. pip install fmpy==0.3.32, then:  python fmpy_cosim.py RoomThermal.fmu
Without an FMU argument this only checks that FMPy and its FMU2Slave API are importable (what CI runs).
"""
import json
import shutil
import sys

import cosim


class FMURoom:
    """Adapter: FMPy's FMU2Slave behind the same small interface as units.Room (value references by name)."""

    def __init__(self, path):
        from fmpy import extract, read_model_description
        from fmpy.fmi2 import FMU2Slave
        md = read_model_description(path)
        self.vrs = {v.name: v.valueReference for v in md.modelVariables}
        self.dir = extract(path)
        self.fmu = FMU2Slave(guid=md.guid, unzipDirectory=self.dir,
                             modelIdentifier=md.coSimulation.modelIdentifier, instanceName="room")

    def vr(self, name):
        return self.vrs[name]

    def instantiate(self):
        self.fmu.instantiate()

    def setup_experiment(self, start_time=0.0):
        self.fmu.setupExperiment(startTime=start_time)

    def enter_initialization_mode(self):
        self.fmu.enterInitializationMode()

    def exit_initialization_mode(self):
        self.fmu.exitInitializationMode()

    def set_real(self, vrs, values):
        self.fmu.setReal(vrs, values)

    def get_real(self, vrs):
        return self.fmu.getReal(vrs)

    def do_step(self, current_communication_point, communication_step_size):
        self.fmu.doStep(currentCommunicationPoint=current_communication_point,
                        communicationStepSize=communication_step_size)

    def terminate(self):
        self.fmu.terminate()
        self.fmu.freeInstance()
        shutil.rmtree(self.dir, ignore_errors=True)


def api_check():
    import fmpy
    from fmpy.fmi2 import FMU2Slave
    missing = [m for m in ("instantiate", "setupExperiment", "enterInitializationMode", "exitInitializationMode",
                           "setReal", "getReal", "doStep", "terminate", "freeInstance") if not hasattr(FMU2Slave, m)]
    print(f"fmpy {fmpy.__version__}: FMU2Slave API {'complete' if not missing else 'MISSING ' + str(missing)}")
    return not missing


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0 if api_check() else 1)
    for h in (60, 900):
        print(json.dumps(cosim.metrics(cosim.run(h, room=FMURoom(sys.argv[1])))))
