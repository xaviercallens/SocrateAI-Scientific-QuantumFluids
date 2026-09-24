#!/usr/bin/env python3
"""Amendment A3: re-run every trajectory the sum-rule admission excluded, once, to t_end = 4000 (same seed)."""
import json, sys
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_sweep
from sweep import trajectory

if __name__ == "__main__":
    _, excluded = analyze_sweep.load()
    jobs = [(d["e"], d["seed"], False, 4000.0) for d in excluded if d["t_end"] < 4000]
    print("extending:", jobs, flush=True)
    with Pool(8) as pool:
        pool.map(trajectory, jobs, chunksize=1)
