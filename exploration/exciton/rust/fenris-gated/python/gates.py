"""Gates L-a (a4, a5), L-b (b1), L-c, L-d of PREREG.md. Usage: python3 gates.py [all|a|b|c|d] [--fg path]"""
import json, subprocess, sys, os, itertools
import numpy as np
from scipy import special, optimize
sys.path.insert(0, os.path.dirname(__file__))
import geometry as G

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "results")
SCR = "/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-SocrateAI-Scientific-QuantumFluids/a734ac20-b6c3-453c-b3fa-99d9526d3488/scratchpad/fg"
os.makedirs(SCR, exist_ok=True); os.makedirs(RES, exist_ok=True)
FG = "/mnt/data/xdev-cache/fg-target/release/fg"
SPECS = ["ungated:0.5", "gated:0.5:1.5", "gated:0.5:5.0", "yukawa:1.5"]


def run(cmd, **kw):
    env = dict(os.environ, RAYON_NUM_THREADS="1")
    return subprocess.run(cmd, capture_output=True, text=True, env=env, **kw)


def kern(spec, rs, fg=None):
    out = run([fg or FG, "kern", spec] + [repr(float(r)) for r in rs]).stdout.strip().splitlines()
    return np.array([[float(t) for t in l.split() if t not in ("series", "table")] for l in out])


# ---------- independent numpy kernels (scipy.special) ----------
def np_raw(spec, r):
    """(U, U', U'') raw, from scipy.special.k0/k1 (independent of the Rust Bessel code and of the table)."""
    r = np.asarray(r, float)
    p = spec.split(":")
    if p[0] == "ungated":
        d = float(p[1]); s = np.sqrt(r * r + d * d)
        return 1 / r - 1 / s, -1 / r**2 + r / s**3, 2 / r**3 + 1 / s**3 - 3 * r**2 / s**5
    if p[0] == "yukawa":
        k = float(p[1]); e = np.exp(-k * r)
        return e / r, -e * (k * r + 1) / r**2, e * (k * k * r * r + 2 * k * r + 2) / r**3
    d, D = float(p[1]), float(p[2])
    u = np.zeros_like(r); du = np.zeros_like(r); d2u = np.zeros_like(r)
    kmax = int(np.ceil(45 * D / (2 * np.pi * r.min()))) + 2
    for k in range(1, kmax + 1):
        q = 2 * np.pi * k / D
        x = q * r
        m = x < 45
        if not m.any():
            break
        w = 1 - np.cos(2 * np.pi * k * d / D)
        k0, k1 = special.k0(x[m]), special.k1(x[m])
        u[m] += w * k0; du[m] -= w * q * k1; d2u[m] += w * q * q * (k0 + k1 / x[m])
    return 4 / D * u, 4 / D * du, 4 / D * d2u


def rc_of(spec):
    p = spec.split(":")
    return {"ungated": 1e4, "gated": 6 * float(p[2]) if p[0] == "gated" else 0, "yukawa": 20 / float(p[1]) if p[0] == "yukawa" else 0}[p[0]]


def np_pair(spec, r):
    rc = rc_of(spec)
    u, du, d2u = np_raw(spec, r)
    uc, duc, _ = np_raw(spec, np.array([rc]))
    z = r >= rc
    return np.where(z, 0, u - uc[0] - (r - rc) * duc[0]), np.where(z, 0, du - duc[0]), np.where(z, 0, d2u)


def direct_image_U(d, D, r, nmax=200000):
    """Real-space image sum of two grounded planes at z=+-D/2; U_task = (V_ee + V_hh - 2 V_eh)/2."""
    P = 2 * D; h1 = D / 2
    n = np.arange(-nmax, nmax + 1)
    ze, zh = -d / 2, d / 2
    def V(z, z0):
        return (1 / np.sqrt(r * r + (z - z0 - P * n) ** 2) - 1 / np.sqrt(r * r + (z - 2 * h1 + z0 - P * n) ** 2)).sum()
    return 0.5 * (V(ze, ze) + V(zh, zh) - 2 * V(zh, ze))


def gate_a(fg=FG):
    out = {}
    # a5: Bessel
    xs = np.logspace(-4, np.log10(40), 400)
    lines = run([fg, "bessel"] + [repr(float(x)) for x in xs]).stdout.strip().splitlines()
    arr = np.array([[float(t) for t in l.split()] for l in lines])
    e0 = np.max(np.abs(arr[:, 1] / special.k0(xs) - 1)); e1 = np.max(np.abs(arr[:, 2] / special.k1(xs) - 1))
    out["a5_bessel_max_rel_err"] = [e0, e1]; out["a5_pass"] = bool(max(e0, e1) <= 1e-13)
    # a4: direct image sum and zero-wavevector integral (gated kernels)
    worst = 0.0; rows = []
    for d, D in [(0.5, 1.5), (0.5, 5.0), (1.0, 3.0), (1.0, 10.0)]:
        rs = [0.05, 0.2, 0.5, 1, 2, 4]
        u = kern(f"gated:{d}:{D}", rs, fg)
        # the engine kernel is shifted-force: compare the RAW series values printed after 'series'
        raw = run([fg, "kern", f"gated:{d}:{D}"] + [repr(float(r)) for r in rs]).stdout.strip().splitlines()
        ser = np.array([float(l.split()[5]) for l in raw])
        for r, s in zip(rs, ser):
            ref = direct_image_U(d, D, r)
            worst = max(worst, abs(s - ref) / (abs(ref) + 1e-3)); rows.append((d, D, r, s, ref))  # amendment A1: floor 1e-11/1e-8
        # int U d^2r = 2 pi d (1 - d/D) via quadrature of the numpy series
        from scipy.integrate import quad
        f = lambda t: 2 * np.pi * t * np_raw(f"gated:{d}:{D}", np.array([t]))[0][0]
        val = 2 * np.pi * 1e-6 + sum(quad(f, a, b, limit=400)[0] for a, b in [(1e-6, 0.1), (0.1, 1), (1, D), (D, 6 * D)])  # amendment A1: + analytic [0,1e-6] piece (U~1/r)
        out.setdefault("a4_integral", []).append([d, D, val, 2 * np.pi * d * (1 - d / D), val / (2 * np.pi * d * (1 - d / D)) - 1])
    out["a4_image_sum_max_rel_err"] = worst
    out["a4_integral_max_rel_err"] = max(abs(x[4]) for x in out["a4_integral"])
    out["a4_pass"] = bool(worst <= 1e-8 and out["a4_integral_max_rel_err"] <= 1e-6)
    return out


# ---------- L-b1 ----------
def lcg_stream(seed):
    s = [seed]
    def f():
        s[0] = (s[0] * 6364136223846793005 + 1442695040888963407) % (1 << 64)
        return ((s[0] >> 11) / float(1 << 53)) * 2.0 - 1.0
    return f


def gate_b1(fg=FG, orig_example="/mnt/data/xdev-cache/fg-target-orig/release/examples/square_patch"):
    l = 12; rnd = lcg_stream(42)
    fixed, free = [], []
    for i in range(l + 1):
        for j in range(l + 1):
            if i in (0, l) or j in (0, l):
                fixed.append((i, j))
            else:
                free.append((i + 0.35 * rnd(), j + 0.35 * rnd()))
    d = SCR + "/b1"; os.makedirs(d, exist_ok=True)
    np.savetxt(d + "/fixed.txt", np.array(fixed, float)); 
    with open(d + "/starts.txt", "w") as f:
        f.write(f"1 {len(free)}\n"); f.writelines(f"{x!r} {y!r}\n" for x, y in free)
    r = run([fg, "run", "yukawa:1.5", d + "/fixed.txt", d + "/starts.txt", d + "/out.txt"])
    txt = open(d + "/out.txt").read().splitlines()
    hdr = txt[0].split()
    mine = np.array([[float(t) for t in l.split()] for l in txt[1:]])
    r2 = run([orig_example, "12", "1.5", d])
    vtk = open(d + "/square_patch_after.vtk").read().split()
    i0 = vtk.index("POINTS") + 3
    npts = int(vtk[vtk.index("POINTS") + 1])
    pts = np.array(vtk[i0:i0 + 3 * npts], float).reshape(npts, 3)[:, :2]
    # original order: all nodes by (i, j); free ones are the interior
    idx = [k for k, (i, j) in enumerate(itertools.product(range(l + 1), range(l + 1))) if not (i in (0, l) or j in (0, l))]
    ref = pts[idx]
    err = np.abs(mine - ref).max()
    return dict(max_abs_coordinate_difference=float(err), fmax_rel_patched=float(hdr[hdr.index("fmax_rel") + 1]),
                converged=int(hdr[hdr.index("converged") + 1]), n_free=len(free),
                pass_=bool(err <= 1e-9 and float(hdr[hdr.index("fmax_rel") + 1]) <= 1e-9))


# ---------- L-c ----------
def energy_np(spec, X, fixed):
    n = len(X)
    iu = np.triu_indices(n, 1)
    e = 0.0
    if n > 1:
        r = np.linalg.norm(X[iu[0]] - X[iu[1]], axis=1); e += np_pair(spec, r)[0].sum()
    r = np.linalg.norm(X[:, None, :] - fixed[None], axis=2).ravel(); e += np_pair(spec, r)[0].sum()
    return e


def grad_np(spec, X, fixed):
    n = len(X); g = np.zeros_like(X)
    for i in range(n):
        D = X[i] - np.vstack([np.delete(X, i, 0), fixed]); r = np.linalg.norm(D, axis=1)
        g[i] = (np_pair(spec, r)[1][:, None] * D / r[:, None]).sum(0)
    return g


def gate_c(fg=FG, nstart=60, nnp=400):
    sh = G.Shape("square", 5.0)
    fixed = sh.boundary
    d = SCR + "/c"; os.makedirs(d, exist_ok=True)
    np.savetxt(d + "/fixed.txt", fixed)
    out = {}
    for spec in SPECS:
        for nf in (3, 7):
            rng = np.random.default_rng(777000 + nf)
            starts = sh.sample(nstart * nf, rng).reshape(nstart, nf, 2)
            with open(d + "/starts.txt", "w") as f:
                f.write(f"{nstart} {nf}\n")
                for s in starts:
                    f.writelines(f"{x!r} {y!r}\n" for x, y in s)
            run([fg, "run", spec, d + "/fixed.txt", d + "/starts.txt", d + "/out.txt"])
            lines = open(d + "/out.txt").read().splitlines()
            eng = []; k = 0
            while k < len(lines):
                h = lines[k].split(); P = np.array([[float(t) for t in l.split()] for l in lines[k + 1:k + 1 + nf]]); k += 1 + nf
                if int(h[3]) == 1 and sh.inside(P).all():
                    eng.append(float(h[h.index("energy") + 1]))
            # independent numpy search
            rng = np.random.default_rng(555000 + nf)
            npe = []
            for s in sh.sample(nnp * nf, rng).reshape(nnp, nf, 2):
                res = optimize.minimize(lambda v: energy_np(spec, v.reshape(-1, 2), fixed),
                                        s.ravel(), jac=lambda v: grad_np(spec, v.reshape(-1, 2), fixed).ravel(),
                                        method="L-BFGS-B", options=dict(gtol=1e-12, ftol=1e-15, maxiter=20000, maxcor=30))
                P = res.x.reshape(-1, 2)
                if sh.inside(P).all() and np.abs(grad_np(spec, P, fixed)).max() < 1e-8:
                    npe.append(res.fun)
            bh = optimize.basinhopping(lambda v: energy_np(spec, v.reshape(-1, 2), fixed), sh.sample(nf, rng).ravel(), niter=200,
                                       minimizer_kwargs=dict(method="L-BFGS-B", jac=lambda v: grad_np(spec, v.reshape(-1, 2), fixed).ravel(),
                                                             options=dict(gtol=1e-12, ftol=1e-15)), seed=1)
            if sh.inside(bh.x.reshape(-1, 2)).all():
                npe.append(bh.fun)
            def distinct(v, tol=1e-7):
                out = []
                for e in sorted(v):
                    if not out or abs(e - out[-1]) > tol * abs(out[-1]): out.append(e)
                return out
            de, dn = distinct(eng), distinct(npe)
            matched = all(any(abs(e - m) <= 1e-7 * abs(m) for m in dn) for e in de)
            best_eq = bool(de and dn and abs(de[0] - dn[0]) <= 1e-7 * abs(dn[0]))
            out[f"{spec}|N{nf}"] = dict(engine_converged_inside=len(eng), engine_distinct=de[:10], n_engine_distinct=len(de),
                                        numpy_inside=len(npe), numpy_distinct=dn[:10], n_numpy_distinct=len(dn),
                                        best_engine=de[0] if de else None, best_numpy=dn[0] if dn else None,
                                        best_equal=best_eq, every_engine_minimum_matched=bool(matched),
                                        pass_=bool(best_eq and matched))
    return out


def gate_f(fg=FG):
    """L-f (amendment A2): final energies independent of the CVODE tolerances (1e-6/1e-9 vs 1e-2/1e-5), N_free ~ 30."""
    sh = G.fit_shape("square", 30)
    d = SCR + "/f"; os.makedirs(d, exist_ok=True)
    np.savetxt(d + "/fixed.txt", sh.boundary)
    ns = 4
    with open(d + "/starts.txt", "w") as f:
        f.write(f"{ns} {sh.n_free}\n")
        for s in range(ns):
            f.writelines(f"{x!r} {y!r}\n" for x, y in sh.sample(sh.n_free, np.random.default_rng(31000 + s)))
    out = {}
    for spec in SPECS:
        E = {}
        for tag, rt, at in (("tight", "1e-6", "1e-9"), ("loose", "1e-2", "1e-5")):
            run([fg, "run", spec, d + "/fixed.txt", d + "/starts.txt", d + "/o.txt", "1e-9", rt, at])
            E[tag] = [float(l.split()[l.split().index("energy") + 1]) for l in open(d + "/o.txt") if l.startswith("start")]
        rel = [abs(a - b) / abs(a) for a, b in zip(E["tight"], E["loose"])]
        out[spec] = dict(E_tight=E["tight"], E_loose=E["loose"], max_rel_diff=max(rel))
    out["pass_"] = bool(all(v["max_rel_diff"] <= 1e-6 for v in out.values() if isinstance(v, dict)))
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    fg = FG
    if "--fg" in sys.argv: fg = sys.argv[sys.argv.index("--fg") + 1]
    res = {}
    if which in ("all", "a"): res["L-a_a4_a5"] = gate_a(fg)
    if which in ("all", "b"): res["L-b1"] = gate_b1(fg)
    if which in ("all", "c"): res["L-c"] = gate_c(fg)
    if which in ("all", "f"): res["L-f"] = gate_f(fg)
    tag = os.path.basename(os.path.dirname(os.path.dirname(fg))) if "--fg" in sys.argv else "main"
    json.dump(res, open(f"{RES}/gates_{which}_{tag}.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
