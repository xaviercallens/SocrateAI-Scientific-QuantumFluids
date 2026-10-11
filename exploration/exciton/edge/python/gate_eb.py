"""Gate E-b (and planted-bug controls E-d): Rust `evalconf` vs the independent numpy implementation.

usage: gate_eb.py <evalconf-binary> <out.json> [bug 0..4]      env QF_TABLE_DIR
bug 4 = table swap (QF_PLANT_TABLE_SWAP) for kernel g3 only.
"""
import sys, os, json, subprocess, numpy as np
from edge_ref import energy_force, spacing

RHO0 = 0.5; KAPPA = 1e5; KTRAP = 0.3
KERN = ["dip", "g3", "g10", "r3"]
CONT = ["disk", "square", "tri", "hex", "trap"]
NS = [7, 19]
NCONF = 5


def circumradius(cid, area):
    if cid == "disk": return np.sqrt(area / np.pi)
    if cid == "square": return np.sqrt(area / 2.0)
    if cid == "tri": return np.sqrt(4 * area / np.sqrt(3)) / np.sqrt(3)
    if cid == "hex": return np.sqrt(2 * area / (3 * np.sqrt(3)))
    return np.sqrt(area / np.pi)


def make_configs(seed=20261011):
    rng = np.random.default_rng(seed)
    cfgs = []
    for k in KERN:
        for c in CONT:
            for n in NS:
                area = n / RHO0
                R = 1.15 * circumradius(c, area)
                for _ in range(NCONF):
                    x = []
                    while len(x) < n:
                        p = rng.uniform(-R, R, 2)
                        if p @ p <= R * R and all(np.hypot(*(p - q)) > 0.45 * spacing(RHO0) for q in x):
                            x.append(p)
                    cfgs.append((k, c, area, np.array(x)))
    return cfgs


def run_evalconf(binary, cfgs, bug, hess=False):
    lines = []
    for k, c, area, x in cfgs:
        lines.append(f"{k} {c} {area!r} {KAPPA!r} {KTRAP!r} {len(x)} " + " ".join(repr(float(v)) for v in x.ravel()))
    inp = "/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-SocrateAI-Scientific-QuantumFluids/a734ac20-b6c3-453c-b3fa-99d9526d3488/scratchpad/eb_in_%d_%d.txt" % (os.getpid(), bug)
    open(inp, "w").write("\n".join(lines) + "\n")
    env = dict(os.environ)
    if bug == 4: env["QF_PLANT_TABLE_SWAP"] = "1"
    args = [binary, inp, str(bug if bug < 4 else 0)] + (["hess"] if hess else [])
    out = subprocess.run(args, capture_output=True, text=True, env=env, check=True).stdout.strip().split("\n")
    os.remove(inp)
    return out


def main():
    binary, outp = sys.argv[1], sys.argv[2]
    bug = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    cfgs = make_configs()
    if bug == 4:
        cfgs = [c for c in cfgs if c[0] == "g3"]
    out = run_evalconf(binary, cfgs, bug)
    worst = {"e_int": 0.0, "e_wall": 0.0, "force": 0.0}
    rows = []
    for (k, c, area, x), line in zip(cfgs, out):
        v = [float(t) for t in line.split()]
        ei, ew, f = v[0], v[1], np.array(v[2:]).reshape(-1, 2)
        ei0, ew0, f0 = energy_force(k, c, area, KAPPA, KTRAP, x)
        r_i = abs(ei - ei0) / abs(ei0)
        r_w = abs(ew - ew0) / abs(ew0) if abs(ew0) > 0 else abs(ew - ew0) / abs(ei0)
        r_f = np.max(np.abs(f - f0)) / np.max(np.abs(f0))
        rows.append(dict(kernel=k, container=c, n=len(x), r_eint=r_i, r_ewall=r_w, r_force=float(r_f)))
        worst["e_int"] = max(worst["e_int"], r_i); worst["e_wall"] = max(worst["e_wall"], r_w); worst["force"] = max(worst["force"], float(r_f))
    # Hessian vs finite difference of the Rust force
    hess_worst = 0.0; hrows = []
    if bug == 0:
        rng = np.random.default_rng(7)
        hc = []
        for k in ("dip", "g3", "g10"):
            for c in ("disk", "hex"):
                n = 7; area = n / RHO0; R = 1.1 * circumradius(c, area)
                for _ in range(5):
                    x = []
                    while len(x) < n:
                        p = rng.uniform(-R, R, 2)
                        if p @ p <= R * R and all(np.hypot(*(p - q)) > 0.5 * spacing(RHO0) for q in x):
                            x.append(p)
                    hc.append((k, c, area, np.array(x)))
        lines = run_evalconf(binary, hc, 0, hess=True)
        step = 1e-5
        for idx, (k, c, area, x) in enumerate(hc):
            H = np.array([float(t) for t in lines[2 * idx + 1].split()[1:]]).reshape(14, 14).T  # column-major
            fd = np.zeros((14, 14))
            pert = []
            for a in range(14):
                for s in (+1, -1):
                    y = x.ravel().copy(); y[a] += s * step; pert.append((k, c, area, y.reshape(-1, 2)))
            fl = run_evalconf(binary, pert, 0)
            fv = [np.array([float(t) for t in l.split()[2:]]) for l in fl]
            for a in range(14):
                fd[:, a] = -(fv[2 * a] - fv[2 * a + 1]) / (2 * step)   # Hessian = -d f / d x
            err = np.max(np.abs(H - fd)) / np.max(np.abs(H))
            hrows.append(dict(kernel=k, container=c, err=float(err)))
            hess_worst = max(hess_worst, float(err))
    tol = 1e-12
    res = dict(bug=bug, n_configs=len(cfgs), worst=worst, tol=tol, hess_worst=hess_worst,
               pass_energy=(worst["e_int"] <= tol and worst["e_wall"] <= tol), pass_force=(worst["force"] <= tol),
               pass_hessian=(hess_worst <= 1e-6) if bug == 0 else None, rows=rows, hess_rows=hrows)
    res["pass"] = bool(res["pass_energy"] and res["pass_force"] and (res["pass_hessian"] in (True, None)))
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "hess_rows")}, indent=1))


if __name__ == "__main__":
    main()
