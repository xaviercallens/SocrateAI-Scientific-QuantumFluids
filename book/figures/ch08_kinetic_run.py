"""Chapter 8: run the CVODE driver (book/rust/ch08_kinetic) on the 2D Landau kinetic equation.
Writes the raw time series to DATA (large/regenerable data: /mnt/data/xdev-cache/book_ch08/kinetic) and the solver
statistics to DATA/stats.json.  Skips runs whose output exists (delete the CSV to redo).
Usage:  python figures/ch08_kinetic_run.py [--only tag]
Machine note: shared 8-core machine, load 8-35 while this was written; wall times in stats.json are NOT benchmarks."""
import sys, json, subprocess, re, os
from pathlib import Path

BIN = Path("/mnt/data/xdev-cache/cargo-target-book8/release/ch08_kinetic")
DATA = Path("/mnt/data/xdev-cache/book_ch08/kinetic"); DATA.mkdir(parents=True, exist_ok=True)
STATS = DATA / "stats.json"
SNAPT = "0,6,12,24"

def ftag(F): return ("m" if F < 0 else "p") + f"{abs(F):g}".replace(".", "_")

def jobs():
    out = []
    # production: BDF, N = 64, rtol 1e-8, atol 1e-10, T = 60, output every 0.1 (units a = q v_F = 1)
    for F in (-0.5, 0.0, 0.5, 1.0, 4.0, 12.0):
        out.append(dict(tag=f"uni_{ftag(F)}", F=F, ic="uniform", N=64, method="bdf", rtol=1e-8, atol=1e-10, T=60, dt=0.1,
                        snaps=SNAPT if F in (0.0, 4.0) else None))
    for F in (-0.5, 0.5, 1.0, 4.0, 12.0):
        out.append(dict(tag=f"kick_{ftag(F)}", F=F, ic="kick", N=64, method="bdf", rtol=1e-8, atol=1e-10, T=60, dt=0.1, snaps=None))
    # solver verification: method and tolerance at F = 0 (exact answer J0) ; Adams at F = 4
    for rt in (1e-6, 1e-8, 1e-10):
        out.append(dict(tag=f"tol_bdf_{rt:g}", F=0.0, ic="uniform", N=64, method="bdf", rtol=rt, atol=rt * 1e-2, T=60, dt=0.1, snaps=None))
    for rt in (1e-6, 1e-8, 1e-10):
        out.append(dict(tag=f"tol_adams_{rt:g}", F=0.0, ic="uniform", N=64, method="adams", rtol=rt, atol=rt * 1e-2, T=60, dt=0.1, snaps=None))
    out.append(dict(tag="uni_p4_adams", F=4.0, ic="uniform", N=64, method="adams", rtol=1e-8, atol=1e-10, T=60, dt=0.1, snaps=None))
    # below the Pomeranchuk bound: F = -2 grows as exp(y t), y = r/sqrt(1-r^2), r = 1 - 1/|F|  (= 1/sqrt(3) at F = -2)
    out.append(dict(tag="uni_m2", F=-2.0, ic="uniform", N=64, method="bdf", rtol=1e-8, atol=1e-10, T=14, dt=0.1, snaps=None))
    # angular resolution: N = 96 at F = 4
    out.append(dict(tag="uni_p4_N96", F=4.0, ic="uniform", N=96, method="bdf", rtol=1e-8, atol=1e-10, T=60, dt=0.1, snaps=None))
    return out

def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    force = "--force" in sys.argv                      # re-run everything with the current binary (overwrites the CSVs)
    stats = json.loads(STATS.read_text()) if STATS.exists() else {}
    for j in jobs():
        if only and not j["tag"].startswith(only): continue
        csv = DATA / f"{j['tag']}.csv"
        if csv.exists() and j["tag"] in stats and not force: continue
        cmd = [str(BIN), "kin", f"{j['F']}", j["ic"], str(j["N"]), j["method"], f"{j['rtol']:g}", f"{j['atol']:g}", str(j["T"]), str(j["dt"]), str(csv)]
        if j["snaps"]: cmd += [j["snaps"], str(DATA / f"{j['tag']}_snap.csv")]
        r = subprocess.run(["nice"] + cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("FAILED", j["tag"], r.stderr[-400:]); stats[j["tag"]] = dict(j, failed=r.stderr[-400:]); continue
        m = re.search(r"steps=(\d+) rhs_evals=(\d+) wall_s=([0-9.]+)", r.stdout)
        stats[j["tag"]] = dict(j, steps=int(m.group(1)), rhs_evals=int(m.group(2)), wall_s=float(m.group(3)), raw=r.stdout.strip().splitlines()[-1])
        print(j["tag"], stats[j["tag"]]["steps"], "steps", stats[j["tag"]]["wall_s"], "s", flush=True)
        STATS.write_text(json.dumps(stats, indent=1))
    STATS.write_text(json.dumps(stats, indent=1))

if __name__ == "__main__":
    main()
