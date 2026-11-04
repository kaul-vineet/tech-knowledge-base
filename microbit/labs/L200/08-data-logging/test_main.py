import os
import sys
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
sys.path.insert(0, HERE)
from labtest import load_lab, serial  # noqa: E402
import export_csv  # noqa: E402
import log  # noqa: E402  (stub)
import microbit  # noqa: E402


class DataLoggingLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def run_samples(self, readings):
        with serial() as out:
            self.lab.setup()
            state = self.lab.new_state()
            for temp_c, light in readings:
                microbit._inject_temperature(temp_c)
                microbit.display.inject_light_level(light)
                self.lab.step(state)
                microbit.sleep(self.lab.INTERVAL_MS)
        return out.getvalue(), state

    def test_serial_csv(self):
        out, state = self.run_samples([(21, 120), (22, 110)])
        self.assertEqual(out, "time_ms,temp,light\n0,21,120\n1000,22,110\n")
        self.assertEqual(state["rows"], 2)

    def test_log_module_rows_have_timestamp_column(self):
        self.run_samples([(21, 120), (22, 110)])
        self.assertEqual(log.rows, ["Time (seconds),temp,light", "0.00,21,120", "1.00,22,110"])

    def test_full_log_raises_enospc_in_main_lab(self):
        log._set_capacity(40)                   # header (26 bytes) + one row fit
        with self.assertRaises(OSError) as ctx:
            self.run_samples([(21, 120), (22, 110), (23, 100)])
        self.assertEqual(ctx.exception.args[0], 28)

    def test_without_log_module_serial_only(self):
        self.lab.log = None                     # what happens on a V1 board
        out, state = self.run_samples([(20, 5)])
        self.assertEqual(out, "time_ms,temp,light\n0,20,5\n")
        self.assertFalse(state["logging"])


class ExportCsv(unittest.TestCase):
    def test_extract_skips_noise(self):
        lines = ["hello", "time_ms,temp,light\r", "0,21,120\r", "1000,22", "2000,x,1", "3000,23,100"]
        header, rows, skipped = export_csv.extract(lines)
        self.assertEqual(header, ["time_ms", "temp", "light"])
        self.assertEqual(rows, [["0", "21", "120"], ["3000", "23", "100"]])
        self.assertEqual([r for _, _, r in skipped], ["before header", "wrong field count", "not numeric"])

    def test_cli_writes_rfc4180_csv(self):
        tmp = Path(HERE) / "_test_out"
        tmp.mkdir(exist_ok=True)
        try:
            src, dst = tmp / "serial.txt", tmp / "readings.csv"
            src.write_text("time_ms,temp,light\n0,21,120\n1000,22,110\n", encoding="utf-8")
            with serial() as out:
                self.assertEqual(export_csv.main([str(src), str(dst)]), 0)
            self.assertEqual(out.getvalue(), "kept 2 rows, skipped 0\n")
            self.assertEqual(dst.read_bytes(), b"time_ms,temp,light\r\n0,21,120\r\n1000,22,110\r\n")
        finally:
            for p in tmp.iterdir():
                p.unlink()
            tmp.rmdir()


if __name__ == "__main__":
    unittest.main(verbosity=2)
