# src/utils/metrics.py
import time
import csv
from pathlib import Path

def timeit(fn):
    def wrapper(*a, **k):
        t0 = time.perf_counter()
        res = fn(*a, **k)
        t1 = time.perf_counter()
        return res, t1 - t0
    return wrapper

class CSVLogger:
    def __init__(self, path):
        self.path = Path(path)
        first = not self.path.exists()
        self.f = open(self.path, "a", newline="")
        self.w = csv.writer(self.f)
        if first:
            self.w.writerow(["map","algo","rows","cols","start","goal","cost","length","nodes","time_s","seed","notes"])
            self.f.flush()

    def log(self, rowdict):
        row = [
            rowdict.get("map"),
            rowdict.get("algo"),
            rowdict.get("rows"),
            rowdict.get("cols"),
            rowdict.get("start"),
            rowdict.get("goal"),
            rowdict.get("cost"),
            rowdict.get("length"),
            rowdict.get("nodes"),
            rowdict.get("time_s"),
            rowdict.get("seed"),
            rowdict.get("notes","")
        ]
        self.w.writerow(row)
        self.f.flush()

    def close(self):
        self.f.close()
