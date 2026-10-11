"""Gate E-a / E-a2: known answers.  usage: gate_ea.py <edge-binary> <outdir> <out.json>   env QF_TABLE_DIR"""
import sys, os, json, subprocess, numpy as np
from scipy.optimize import basinhopping, brentq, minimize
from edge_ref import pair, energy_force

C = 1.0; K = 1.0
def closed(n):
    if n == 1: return 0.0
    if n == 2:
        x = (3 * C / (16 * K)) ** 0.2; return C / (2 * x) ** 3 + K * x * x
    if n == 3:
        s = (9 * C / K) ** 0.2; return 3 * C / s**3 + 0.5 * K * s * s
    S = 12 + 2 / np.sqrt(3) + 3 / 8; R = (S * C / (2 * K)) ** 0.2
    return S * C / R**3 + 3 * K * R * R


def best_rust(binary, outdir, kid, n, case_idx):
    path = f"{outdir}/ea_{kid}_{n}.jsonl"
    subprocess.run([binary, kid, "trap", str(n), "0.5", "60", "0", str(case_idx), path, repr(K), "2"], check=True)
    best = None
    for l in open(path):
        d = json.loads(l)
        if d["rec"] == "polished" and (best is None or d["e_total"] < best):
            best = d["e_total"]
    return best


def global_opt(kid, n, seed=0):
    phi, dphi = pair(kid)
    def fun(v):
        x = v.reshape(-1, 2)
        e, w, f = energy_force(kid, "trap", n / 0.5, 0.0, K, x)
        return e + w, -f.ravel()
    rng = np.random.default_rng(seed)
    best = np.inf
    for _ in range(40):
        x0 = rng.normal(size=2 * n) * 1.0
        r = basinhopping(lambda v: fun(v)[0], x0, niter=25, T=0.5, stepsize=0.7, seed=int(rng.integers(1e9)),
                         minimizer_kwargs=dict(method="L-BFGS-B", jac=lambda v: fun(v)[1], options=dict(ftol=1e-15, gtol=1e-12, maxiter=2000)))
        best = min(best, r.fun)
    return best


def main():
    binary, outdir, outp = sys.argv[1:4]
    res = {"ea": [], "ea2": []}
    for i, n in enumerate((1, 2, 3, 7)):
        e_r = best_rust(binary, outdir, "r3", n, 100 + i)
        e_c = closed(n)
        row = dict(n=n, rust=e_r, closed=e_c, diff=abs(e_r - e_c) if n == 1 else abs(e_r - e_c) / abs(e_c))
        if n == 7:
            e_g = global_opt("r3", 7)
            row["global_opt"] = e_g; row["rust_minus_opt"] = e_r - e_g; row["opt_vs_closed"] = abs(e_g - e_c) / e_c
            row["pass"] = bool(row["diff"] <= 1e-9 and abs(e_g - e_c) / e_c <= 1e-9 and e_r <= e_g + 1e-9)
        else:
            row["pass"] = bool(row["diff"] <= 1e-9)
        res["ea"].append(row)
    for i, kid in enumerate(("dip", "g3", "g10")):
        phi, dphi = pair(kid)
        g = lambda x: float(2 * dphi(np.array([2 * x]))[0] + 2 * K * x)
        xs = brentq(g, 0.3, 20.0, xtol=1e-14, rtol=1e-14)
        e_ref = float(phi(np.array([2 * xs]))[0]) + K * xs * xs
        e_r = best_rust(binary, outdir, kid, 2, 200 + i)
        res["ea2"].append(dict(kernel=kid, rust=e_r, root=e_ref, rel=abs(e_r - e_ref) / e_ref, pass_=bool(abs(e_r - e_ref) / e_ref <= 1e-9)))
    res["pass"] = bool(all(r["pass"] for r in res["ea"]) and all(r["pass_"] for r in res["ea2"]))
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
