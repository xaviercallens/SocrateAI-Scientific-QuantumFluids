"""Production driver: runs the cases of PREREG.md section 3 in the registered order, skipping finished ones.

usage: run_study.py <edge-binary> <runs_dir> <budget_seconds> [kernel ...]   env QF_TABLE_DIR
"""
import sys, os, json, time, subprocess
from edge_ref import LDA

KERNELS = ["dip", "g3", "g10"]
CONTS = ["disk", "hex", "square", "rect21", "tri", "trap", "rect32", "rect31"]
GRID = {"dip": CONTS, "g3": CONTS, "g10": ["disk", "rect21", "trap"]}
NS = [19, 37, 61, 91]
RHO0 = 0.5
STARTS = {19: (60, 20), 37: (40, 12), 61: (16, 6), 91: (8, 4)}   # (random, patch)


def case_index(k, c, n):
    return (KERNELS.index(k) * len(CONTS) + CONTS.index(c)) * len(NS) + NS.index(n)


# Amendment A4 of PREREG.md: explicit job order (kernel, [shapes], N), used with `plan` as 4th argument
PLAN = [
    ("dip", CONTS, 19), ("g3", CONTS, 19), ("g10", ["disk", "rect21", "trap"], 19),
    ("dip", CONTS, 37), ("g3", CONTS, 37), ("g10", ["disk", "rect21", "trap"], 37),
    ("dip", CONTS, 61),
    ("dip", ["disk", "hex", "square", "rect21", "tri", "trap"], 91),
    ("g3", ["disk", "hex", "square", "rect21", "tri", "trap"], 61),
    ("g10", ["disk", "rect21", "trap"], 61),
    ("dip", ["rect32", "rect31"], 91),
    ("g3", ["rect32", "rect31"], 61),
]


def main():
    binary, runs, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
    use_plan = len(sys.argv) > 4 and sys.argv[4] == "plan"
    kernels = [] if use_plan else (sys.argv[4:] or KERNELS)
    os.makedirs(runs, exist_ok=True)
    t0 = time.time()
    trap_path = os.path.join(runs, "trap_k.json")
    trap = json.load(open(trap_path)) if os.path.exists(trap_path) else {}
    log = open(os.path.join(runs, "driver_log.txt"), "a")
    jobs = []
    if use_plan:
        for k, shapes, n in PLAN:
            for c in shapes:
                jobs.append((k, c, n))
    else:
        for n in NS:                  # N ascending over all kernels of this call (so that every shape gets small N first)
            for k in kernels:
                for c in GRID[k]:
                    jobs.append((k, c, n))
    ldas = {}
    if True:
        for k, c, n in jobs:
            if True:
                out = os.path.join(runs, f"{k}_{c}_N{n}.jsonl")
                if os.path.exists(out):
                    continue
                if time.time() - t0 > budget:
                    print("budget exhausted before", k, c, n, file=log, flush=True)
                    continue
                kt = 0.0
                if c == "trap":
                    key = f"{k}_N{n}"
                    if key not in trap:
                        kk, E, rmax = LDA(k).solve(n, RHO0)
                        trap[key] = dict(k=kk, e_lda=E, rmax=rmax)
                        json.dump(trap, open(trap_path, "w"), indent=1)
                    kt = trap[key]["k"]
                nr, npch = STARTS[n]
                tmp = out + ".part"
                t1 = time.time()
                cmd = [binary, k, c, str(n), repr(RHO0), str(nr), str(npch), str(case_index(k, c, n)), tmp, repr(kt), "2"]
                r = subprocess.run(cmd)
                if r.returncode == 0:
                    os.rename(tmp, out)
                print(f"{k} {c} N={n} rc={r.returncode} wall={time.time() - t1:.1f}s starts={nr}+{npch}", file=log, flush=True)


if __name__ == "__main__":
    main()
