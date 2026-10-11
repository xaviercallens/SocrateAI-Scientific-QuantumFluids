"""Amendment A5: aligned lattice-patch starts for already-run cases.
usage: run_aligned.py <edge-binary> <main_runs_dir> <out_dir> <budget_s> <N> [N ...]     env QF_TABLE_DIR
Starts: 24 (N <= 37) or 12 (N >= 61): orientation 0/30 degrees, offset at the 6 high-symmetry points, spacing x1.0 / x0.94.
Cases = the files present in main_runs_dir for the given N (finished ones only), in the order dip, g3, g10."""
import sys, os, json, time, subprocess, glob
from run_study import case_index, RHO0

def main():
    binary, runs, outd, budget = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    ns = [int(v) for v in sys.argv[5:]]
    os.makedirs(outd, exist_ok=True)
    trap = json.load(open(os.path.join(runs, "trap_k.json")))
    t0 = time.time()
    log = open(os.path.join(outd, "driver_log.txt"), "a")
    for n in ns:
        for k in ("dip", "g3", "g10"):
            for path in sorted(glob.glob(os.path.join(runs, f"{k}_*_N{n}.jsonl"))):
                c = os.path.basename(path)[len(k) + 1:-len(f"_N{n}.jsonl")]
                out = os.path.join(outd, f"{k}_{c}_N{n}.jsonl")
                if os.path.exists(out):
                    continue
                if time.time() - t0 > budget:
                    print("budget exhausted before", k, c, n, file=log, flush=True)
                    continue
                kt = trap[f"{k}_N{n}"]["k"] if c == "trap" else 0.0
                na = 24 if n <= 37 else 12
                tmp = out + ".part"; t1 = time.time()
                r = subprocess.run([binary, k, c, str(n), repr(RHO0), "0", "0", str(case_index(k, c, n)), tmp, repr(kt), "2", str(na)])
                if r.returncode == 0:
                    os.rename(tmp, out)
                print(f"{k} {c} N={n} rc={r.returncode} wall={time.time() - t1:.1f}s aligned={na}", file=log, flush=True)

if __name__ == "__main__":
    main()
