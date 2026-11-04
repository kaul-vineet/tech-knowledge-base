"""Storage + dashboard export for the L400 pipeline (CPython stdlib only).

Store       SQLite (sqlite3, ":memory:" by default). Primary key (dev, seq): a redelivered
            QoS 1 message is ignored = idempotent consumer.
to_csv      rows for Apache Superset's CSV upload (or Orange).
to_prometheus  text exposition format (# HELP / # TYPE / name{labels} value) for a Prometheus
            scrape -> Grafana. Writing the file is local; scraping/Grafana are manual (pending).
"""
import csv
import io
import sqlite3

COLUMNS = ("dev", "seq", "t_sensor", "t_store", "temp", "light", "motion")


class Store:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS readings (dev TEXT, seq INTEGER, t_sensor INTEGER,"
                        " t_store INTEGER, temp INTEGER, light INTEGER, motion INTEGER,"
                        " PRIMARY KEY (dev, seq))")
        self.duplicates = 0

    def add(self, row):
        cur = self.db.execute("INSERT OR IGNORE INTO readings VALUES (?, ?, ?, ?, ?, ?, ?)",
                              tuple(row[c] for c in COLUMNS))   # placeholders, never string formatting
        if cur.rowcount == 0:
            self.duplicates += 1
        return cur.rowcount == 1

    def rows(self, dev=None):
        q = "SELECT %s FROM readings" % ", ".join(COLUMNS)
        args = ()
        if dev is not None:
            q, args = q + " WHERE dev = ?", (dev,)
        return [dict(zip(COLUMNS, r)) for r in self.db.execute(q + " ORDER BY dev, seq", args)]

    def summary(self):
        q = ("SELECT dev, COUNT(*), MAX(seq), MIN(temp), MAX(temp), AVG(light), SUM(motion),"
             " MAX(t_store - t_sensor) FROM readings GROUP BY dev ORDER BY dev")
        keys = ("dev", "rows", "max_seq", "temp_min", "temp_max", "light_avg", "motion", "lat_max_ms")
        return [dict(zip(keys, r)) for r in self.db.execute(q)]


def to_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def to_prometheus(summary, extra=None):
    lines = ["# HELP classroom_readings_total Readings stored per device.",
             "# TYPE classroom_readings_total counter"]
    lines += ['classroom_readings_total{dev="%s"} %d' % (s["dev"], s["rows"]) for s in summary]
    lines += ["# HELP classroom_temp_max_celsius Highest stored temperature per device.",
              "# TYPE classroom_temp_max_celsius gauge"]
    lines += ['classroom_temp_max_celsius{dev="%s"} %d' % (s["dev"], s["temp_max"]) for s in summary]
    for name, value in sorted((extra or {}).items()):
        lines += ["# TYPE %s gauge" % name, "%s %s" % (name, value)]
    return "\n".join(lines) + "\n"
