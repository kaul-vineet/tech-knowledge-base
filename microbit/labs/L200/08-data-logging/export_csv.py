"""Export the lab's serial CSV (copied from the simulator's serial panel) to a clean .csv file.

Keeps the first `time_ms,...` header and every row that has the same number of
fields, an integer time_ms and numeric values. Everything else is reported and
skipped: "hello" lines, half-received rows, rows mirrored by log.set_mirroring
(their time column is "1.00" seconds, not integer ms). Output follows RFC 4180
(comma, CRLF line ends) via the csv module, so spreadsheets open it directly.

Run:  python3 export_csv.py serial.txt readings.csv     (Windows: py export_csv.py ...)
"""
import csv
import sys
from pathlib import Path

HEADER_PREFIX = "time_ms,"


def extract(lines):
    """Return (header, rows, skipped); skipped = [(line_no, text, reason)]."""
    header, rows, skipped = None, [], []
    for no, line in enumerate(lines, 1):
        text = line.strip()                       # also drops the "\r" of "\r\n"
        if not text:
            continue
        if text.startswith(HEADER_PREFIX):
            if header is None:
                header = text.split(",")
            elif text.split(",") != header:
                skipped.append((no, text, "different header"))
            continue
        if header is None:
            skipped.append((no, text, "before header"))
            continue
        fields = text.split(",")
        if len(fields) != len(header):
            skipped.append((no, text, "wrong field count"))
        elif not fields[0].isdigit():
            skipped.append((no, text, "time_ms not an integer"))
        elif not all(_is_number(f) for f in fields[1:]):
            skipped.append((no, text, "not numeric"))
        else:
            rows.append(fields)
    return header, rows, skipped


def _is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:   # newline="": csv writes CRLF itself
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(__doc__.strip().splitlines()[-1])
        return 2
    lines = Path(args[0]).read_text(encoding="utf-8").splitlines()
    header, rows, skipped = extract(lines)
    if header is None:
        print("no 'time_ms,...' header found")
        return 1
    write_csv(args[1], header, rows)
    print("kept %d rows, skipped %d" % (len(rows), len(skipped)))
    for no, text, reason in skipped:
        print("  line %d skipped (%s): %s" % (no, reason, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
