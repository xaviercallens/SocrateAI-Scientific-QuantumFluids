"""Amendment A6: extra random starts (dip, N = 61, 91) in separate files, new seeds (run index offset = the main stage's count).
usage: run_extra.py <edge-binary> <main_runs_dir> <out_dir> <budget_s>      env QF_TABLE_DIR"""
import sys, os, time, subprocess, json
from run_study import case_index, RHO0, STARTS

EXTRA = {91: 32, 61: 44}
SHAPES = ["disk", "hex", "square", "rect21", "tri", "trap", "rect32", "rect31"]

def main():
    binary, runs, outd, budget = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    os.makedirs(outd, exist_ok=True)
    trap = json.load(open(os.path.join(runs, "trap_k.json")))
    t0 = time.time()
    log = open(os.path.join(outd, "driver_log.txt"), "a")
    for n in (61, 91):
        for c in SHAPES:
            k = "dip"
            if not os.path.exists(os.path.join(runs, f"{k}_{c}_N{n}.jsonl")):
                continue
            out = os.path.join(outd, f"{k}_{c}_N{n}.jsonl")
            if os.path.exists(out):
                continue
            if time.time() - t0 > budget:
                print("budget exhausted before", k, c, n, file=log, flush=True); continue
            kt = trap[f"{k}_N{n}"]["k"] if c == "trap" else 0.0
            nr = EXTRA[n]; off = STARTS[n][0]
            tmp = out + ".part"; t1 = time.time()
            r = subprocess.run([binary, k, c, str(n), repr(RHO0), str(nr), "0", str(case_index(k, c, n)), tmp, repr(kt), "2", "0", str(off)])
            if r.returncode == 0:
                os.rename(tmp, out)
            print(f"{k} {c} N={n} rc={r.returncode} wall={time.time() - t1:.1f}s extra_random={nr} offset={off}", file=log, flush=True)

if __name__ == "__main__":
    main()
