"""Chapter 6 -- the Kosterlitz RG flow integrated with CVODE (rusty_sundials.CvodeSolver) and checked against
the statements proved in Lean (lean_src/KTFlow.lean, book/lean/Ch06_KTEscape.lean).

    du/dl = 4 pi^3 y^2,   dy/dl = (2 - pi/u) y,      u = 1/K,   K = 2/pi is the universal stiffness  (n_s lambda_T^2 = 2 pi K = 4).

What is computed (all numbers are written to ch06_flow_numbers.json, trajectories to ch06_flow_data.npz):
  A  a family of trajectories on both sides of the separatrix H = f(pi/2); for those satisfying the hypothesis of the
     Lean theorem `kt_trapped` (u0 < pi/2, H0 > f(pi/2)): max u, monotonicity of u (u_monotone), y^2 <= y0^2
     (kt_fugacity_bounded), the drift of the exact invariant H (kt_invariant) and the limit u* against f(u*) = H0.
  B  invariant drift against rtol and method (Adams, BDF), plus a negative control: a flow with a wrong coefficient
     (5 %) must NOT conserve H.
  C  escape: below the separatrix the Lean theorem `kt_escape_time` bounds the crossing time of u = pi/2 by
     l1 = (pi/2 - u0) / (2 (f(pi/2) - H0)); CVODE crossing times (root-finding on single solves) against the exact quadrature
     l = int_{u0}^{pi/2} du / (2 (f(u) - H0)) and against the Lean bound.  Also two starting points between the exact separatrix
     and the textbook straight line y = (pi/2 - u)/pi^2: the exact theorem says trapped, the linearised one says escape.
  D  the universal jump: K_R = 1/u* against K0 at fixed y0 (invariant root vs CVODE chain to l = 80).
  E  finite box: the flow stopped at l = ln(L/a): rounding of the jump, and the shift of the crossing K(l_L) = 2/pi.
  F  the critical trajectory: n_s lambda^2 (l) - 4 = 2/l + ... along the separatrix; and the essential singularity,
     RG time to leave the critical region ~ pi^2/(4a) with a^2 = (pi/2)(f(pi/2) - H0).
Python-module route: CvodeSolver.solve(rhs, t0, y0, t_out) returns only the end state (it rebuilds the integrator at every call), so
trajectories are sampled by a chain of solve() calls (each restarts CVODE from the previous output point; the drift reported in B
therefore includes the restarts, which is what the user of this binding gets) and end-point quantities use one call.
CH06_QUICK=1 runs a reduced version (smoke test) and writes *_quick files."""
import hashlib, json, math, os, platform, sys, time
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.integrate import quad
import rusty_sundials
from rusty_sundials import CvodeSolver

QUICK = bool(os.environ.get("CH06_QUICK"))
pi = math.pi
OUT = Path(__file__).resolve().parent
UC = pi / 2
A_COEF = 4 * pi ** 3


def check_environment():
    """The rusty_sundials module in the programme's virtual environment (built 2026-09-26) predates the Adams-order fix: its Method::Adams is
    implicit Euler.  Probe: Adams on y' = -y, t in [0, 10], rtol 1e-8, atol 1e-14 must need fewer than 5000 right-hand-side calls (the fixed
    method needs a few hundred; the old one about 2e5).  Refuse to run otherwise.  Records module path, sha256 and the build commit."""
    n = {"c": 0}
    def rhs(t, y):
        n["c"] += 1
        return [-y[0]]
    _, y = CvodeSolver("adams", 1e-8, 1e-14, 5_000_000).solve(rhs, 0.0, [1.0], 10.0)
    err = abs(y[0] - math.exp(-10.0)) / math.exp(-10.0)
    mod = Path(rusty_sundials.__file__).resolve()
    if n["c"] >= 5000:
        raise SystemExit(f"rusty_sundials at {mod} has the pre-fix Adams (nfe={n['c']}); run with PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext")
    commit_file = mod.parent / "commit.txt"
    return dict(module=str(mod), sha256=hashlib.sha256(mod.read_bytes()).hexdigest(), commit=(commit_file.read_text().strip() if commit_file.exists() else "unknown (no commit.txt next to the module)"),
                adams_probe_nfe=n["c"], adams_probe_relerr=err, python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)


def f(u): return 2 * u - pi * math.log(u)
def H(u, y): return f(u) - 2 * pi ** 3 * y * y
FC = f(UC)


def make_rhs(a=A_COEF):
    def rhs(l, s):
        u, y = s
        return [a * y * y, (2 - pi / u) * y]
    return rhs


def solver(method, rtol, atol=1e-13):
    return CvodeSolver(method=method, rtol=rtol, atol=atol, max_steps=500000)


def endpoint(u0, y0, l, rtol=1e-10, method="adams", rhs=None, atol=1e-13):
    """One CVODE call from l = 0 to l."""
    _, s = solver(method, rtol, atol).solve(rhs or make_rhs(), 0.0, [u0, y0], l)
    return s


def chain(u0, y0, rtol, method="adams", dl=0.25, lmax=60.0, atol=1e-13, ustop=4.0, ystop=0.5, rhs=None, adaptive=True):
    """Chain of CVODE solves; the output step is min(dl, 0.05 / max(1, |du/dl|)) (fast flows are sampled finely).  Stops at lmax, or when
    u > ustop or |y| > ystop (the flow leaves to the disordered phase; outside the validity of the equations anyway)."""
    rhs = rhs or make_rhs()
    sv = solver(method, rtol, atol)
    l, s = 0.0, [u0, y0]
    L, U, Y = [0.0], [u0], [y0]
    status = "lmax"
    while l < lmax - 1e-12:
        step = dl
        if adaptive:
            step = min(dl, 0.05 / max(1.0, abs(rhs(l, s)[0])))
        l1 = min(l + step, lmax)
        try:
            _, s = sv.solve(rhs, l, s, l1)
        except RuntimeError:
            status = "solver_stop"; break
        l = l1
        L.append(l); U.append(s[0]); Y.append(s[1])
        if s[0] > ustop or abs(s[1]) > ystop:
            status = "left"; break
    return np.array(L), np.array(U), np.array(Y), status


def u_star(u0, y0):
    """The root u* in (0, pi/2] of f(u*) = H(u0, y0): where the trapped flow ends (y -> 0 and H is conserved)."""
    h = H(u0, y0)
    if h < FC: return float("nan")
    if h <= FC + 1e-15: return UC
    return brentq(lambda u: f(u) - h, 1e-9, UC)


def sep_y(u):
    """|y| on the exact separatrix H = f(pi/2)."""
    return math.sqrt(max(f(u) - FC, 0.0) / (2 * pi ** 3))


def lin_sep_y(u):
    """Textbook (linearised at the fixed point) separatrix: |y| = (pi/2 - u)/pi^2."""
    return (UC - u) / pi ** 2


def l_quad(u0, y0, u1):
    """Exact RG time to go from u0 to u1 along the scalar reduction u' = 2 (f(u) - H0)  (Lean: kt_scalar)."""
    h0 = H(u0, y0)
    pts = [UC] if u0 < UC < u1 else None          # the integrand has a narrow peak at pi/2 when H0 is close to f(pi/2)
    return quad(lambda u: 1.0 / (2.0 * (f(u) - h0)), u0, u1, points=pts, epsabs=1e-12, epsrel=1e-12, limit=1000)[0]


def l_bound(u0, y0):
    """Lean kt_escape_time: l1 = (pi/2 - u0) / (2 (f(pi/2) - H0))."""
    return (UC - u0) / (2.0 * (FC - H(u0, y0)))


if __name__ == "__main__":
    t_all = time.time(); res = {"constants": dict(UC=UC, KC=2 / pi, FC=FC, two_pi3=2 * pi ** 3, four_pi3=4 * pi ** 3, nslambda2_crit=4.0), "quick": QUICK}
    res["environment"] = check_environment(); print("environment", res["environment"], flush=True)
    suffix = "_quick" if QUICK else ""
    # ------------------------------------------------------------------ A. the family (Adams, rtol 1e-9)
    fam = []
    u0_list = (0.7, 1.3) if QUICK else (0.5, 0.7, 0.9, 1.1, 1.3, 1.45)
    fr_list = (0.5, 0.97, 1.3) if QUICK else (0.4, 0.8, 0.97, 1.03, 1.3, 1.8)
    lmax_A = 20.0 if QUICK else 60.0
    for u0 in u0_list:
        ys = sep_y(u0)
        for fr in fr_list:
            fam.append((u0, fr * ys))
    for (u0, y0) in ([(UC, 0.004), (1.8, 0.004)] if QUICK else [(UC, 0.004), (UC, 0.012), (1.8, 0.004), (1.8, 0.012), (2.2, 0.004)]):
        fam.append((u0, y0))
    # two starting points between the exact and the linearised separatrix (exact: trapped; linear: escape)
    for u0 in ((0.7,) if QUICK else (0.5, 0.7)):
        ys, yl = sep_y(u0), lin_sep_y(u0)
        fam.append((u0, 0.5 * (ys + yl)))   # midpoint, strictly between the two curves
    portrait = []
    for (u0, y0) in fam:
        L, U, Y, st = chain(u0, y0, 1e-9, "adams", dl=0.25, lmax=lmax_A)
        portrait.append(dict(u0=u0, y0=y0, L=L, U=U, Y=Y, status=st))
    rows = []
    for p in portrait:
        u0, y0, U, Y = p["u0"], p["y0"], p["U"], p["Y"]
        hyp = (u0 < UC) and (H(u0, y0) > FC)
        Hs = np.array([H(a, b) for a, b in zip(U, Y)])
        us = u_star(u0, y0) if hyp else float("nan")
        rows.append(dict(u0=u0, y0=y0, hypothesis=bool(hyp), H0=H(u0, y0), Hmargin=H(u0, y0) - FC, between_exact_and_linear=bool(u0 < UC and lin_sep_y(u0) < y0 < sep_y(u0)),
                         status=p["status"], umax=float(U.max()), monotone=bool(np.all(np.diff(U) >= -1e-12)), ysq_ok=bool(np.all(Y ** 2 <= y0 ** 2 * (1 + 1e-9))),
                         drift=float(np.abs(Hs - Hs[0]).max()), u_end=float(U[-1]), u_star=us, lfinal=float(p["L"][-1]), n_points=int(len(U))))
    res["family"] = rows
    hyp_rows = [r for r in rows if r["hypothesis"]]
    res["n_traj"] = len(rows)
    res["n_hyp"] = len(hyp_rows); res["n_hyp_trapped"] = int(sum(r["umax"] < UC for r in hyp_rows))
    res["n_hyp_monotone"] = int(sum(r["monotone"] for r in hyp_rows)); res["n_hyp_ysq"] = int(sum(r["ysq_ok"] for r in hyp_rows))
    nh = [r for r in rows if r["u0"] < UC and not r["hypothesis"]]
    res["n_below_sep_start_u_lt_uc"] = len(nh); res["n_below_sep_crossed"] = int(sum(r["umax"] >= UC for r in nh))
    res["max_drift_all"] = float(max(r["drift"] for r in rows))
    res["max_drift_hyp"] = float(max(r["drift"] for r in hyp_rows))
    res["max_ustar_error_hyp"] = float(max(abs(r["u_end"] - r["u_star"]) for r in hyp_rows))
    btw = [r for r in rows if r["between_exact_and_linear"]]
    res["between"] = dict(n=len(btw), trapped_by_cvode=int(sum(r["umax"] < UC for r in btw)), rows=btw)
    print("A done", round(time.time() - t_all), "s", {k: res[k] for k in ("n_traj", "n_hyp", "n_hyp_trapped", "n_hyp_monotone", "n_hyp_ysq", "n_below_sep_start_u_lt_uc", "n_below_sep_crossed", "max_drift_hyp", "max_ustar_error_hyp")}, flush=True)
    # ------------------------------------------------------------------ B. invariant drift vs tolerance and method; negative control
    chosen = [(0.6, 0.5), (1.2, 0.9), (1.4, 0.99), (1.0, 0.9), (1.3, 0.999), (0.9, 0.95)]
    methods, rtols, lmax_B = (("adams",), (1e-4, 1e-8), 20.0) if QUICK else (("adams", "bdf"), (1e-4, 1e-6, 1e-8, 1e-10), 40.0)
    if QUICK: chosen = chosen[:2]
    tol = {}; curves = {}
    for method in methods:
        for rtol in rtols:
            dr = []; marg = []; tt = time.time()
            for k, (u0, frac) in enumerate(chosen):
                y0 = frac * sep_y(u0)
                L, U, Y, st = chain(u0, y0, rtol, method, dl=0.5, lmax=lmax_B, adaptive=False)
                Hs = np.array([H(a, b) for a, b in zip(U, Y)])
                dr.append(float(np.abs(Hs - Hs[0]).max())); marg.append(float(UC - U.max()))
                if k == 1: curves[f"{method}_{rtol:g}"] = (L, np.abs(Hs - Hs[0]))
            tol[f"{method}_{rtol:g}"] = dict(method=method, rtol=rtol, max_drift=max(dr), drifts=dr, min_margin=min(marg), seconds=time.time() - tt)
    res["tolerance"] = tol
    # negative control: coefficient 4 pi^3 -> 1.05 * 4 pi^3 in du/dl only: H (computed with the true coefficient) must drift
    dr = []; ctl_curve = None
    for k, (u0, frac) in enumerate(chosen):
        y0 = frac * sep_y(u0)
        L, U, Y, st = chain(u0, y0, 1e-10, "adams", dl=0.5, lmax=lmax_B, rhs=make_rhs(A_COEF * 1.05), adaptive=False)
        Hs = np.array([H(a, b) for a, b in zip(U, Y)]); dr.append(float(np.abs(Hs - Hs[0]).max()))
        if k == 1: ctl_curve = (L, np.abs(Hs - Hs[0]))
    res["control_wrong_coeff_drift"] = dr
    print("B done", round(time.time() - t_all), "s", flush=True)
    # ------------------------------------------------------------------ C. escape below the separatrix: Lean bound vs exact quadrature vs CVODE
    esc = []
    cases = [(0.5, 1.5), (0.8, 1.5)] if QUICK else [(0.5, 1.5), (0.5, 3.0), (0.8, 1.5), (0.8, 4.0), (1.1, 1.5), (1.1, 3.0), (1.3, 1.3), (1.3, 2.0), (1.45, 2.0)]
    for (u0, frac) in cases:
        y0 = frac * sep_y(u0)
        h0 = H(u0, y0); b = l_bound(u0, y0); q = l_quad(u0, y0, UC)
        g = lambda t: endpoint(u0, y0, t, rtol=1e-11)[0] - UC
        lc = brentq(g, 0.0, 1.02 * b, xtol=1e-12, rtol=1e-12)
        esc.append(dict(u0=u0, y0=y0, frac=frac, H0=h0, delta=FC - h0, bound=b, quad=q, cvode=lc, ratio_bound=lc / b, rel_err_cvode_quad=abs(lc - q) / q))
    res["escape"] = esc
    res["escape_all_within_bound"] = bool(all(e["cvode"] <= e["bound"] for e in esc))
    res["escape_max_rel_err"] = float(max(e["rel_err_cvode_quad"] for e in esc))
    print("C done", round(time.time() - t_all), "s", flush=True)
    # ------------------------------------------------------------------ D. universal jump at fixed y0
    y0 = 0.03; K0s = np.linspace(0.40, 1.10, 141); KR_inv = []
    for K0 in K0s:
        u0 = 1 / K0; hh = H(u0, y0)
        KR_inv.append(1 / u_star(u0, y0) if (u0 < UC and hh > FC) else 0.0)
    K0_cv = K0s[::25] if QUICK else K0s[::10]; KR_cv = []; lD = 30.0 if QUICK else 80.0
    for K0 in K0_cv:
        u0 = 1 / K0
        L, U, Y, st = chain(u0, y0, 1e-10, "adams", dl=2.0, lmax=lD, adaptive=False)
        KR_cv.append(float(1 / U[-1]) if st == "lmax" else 0.0)
    u0c = brentq(lambda u: H(u, y0) - FC, 1e-3, UC)
    res["jump"] = dict(y0=y0, K0=K0s.tolist(), KR_inv=KR_inv, K0_cv=K0_cv.tolist(), KR_cv=KR_cv, l_end=lD, K0c=1 / u0c, u0c=u0c, KR_at_threshold=2 / pi)
    sf = [(k0, kr) for k0, kr in zip(K0s, KR_inv) if kr > 0]
    res["jump"]["K0_min_superfluid_grid"] = float(min(k0 for k0, kr in sf)); res["jump"]["KR_at_that_point"] = float(min(kr for k0, kr in sf))
    print("D done", round(time.time() - t_all), "s", flush=True)
    # ------------------------------------------------------------------ E. finite box: stop the flow at l_L = ln(L/a)
    lw = {}
    K0e = np.linspace(0.62, 1.10, 9 if QUICK else 61)
    for LA in ((16, 256) if QUICK else (16, 32, 64, 256, 4096)):
        lL = math.log(LA); vals = []
        for K0 in K0e:
            u0 = 1 / K0
            L, U, Y, st = chain(u0, y0, 1e-11, "adams", dl=lL / 4, lmax=lL, adaptive=False)
            vals.append(float(2 * pi / U[-1]) if st == "lmax" else 0.0)   # n_s lambda^2 = 2 pi K(l_L); 0 if the flow has run away before l_L
        vals = np.array(vals)
        cross = None
        for i in range(len(K0e) - 1, 0, -1):          # scan from the superfluid side (large K0) downwards
            if vals[i] >= 4.0 > vals[i - 1] and vals[i - 1] > 0:
                a, b2 = K0e[i - 1], K0e[i]; va, vb = vals[i - 1], vals[i]
                cross = float(b2 + (a - b2) * (vb - 4.0) / (vb - va)); break
        lw[str(LA)] = dict(LA=LA, lL=lL, nslam2=vals.tolist(), K0_cross=cross)
    res["finite_box"] = dict(K0=K0e.tolist(), y0=y0, runs=lw)
    if not QUICK:   # shift of the crossing of n_s lambda^2 = 4 (in u0 = 1/K0, proportional to T) between L/a = 32 and 64, and each size against the infinite box
        res["finite_box"]["shift_32_to_64_percent"] = 100 * ((1 / lw["32"]["K0_cross"]) / (1 / lw["64"]["K0_cross"]) - 1)
    print("E done", round(time.time() - t_all), "s", flush=True)
    # ------------------------------------------------------------------ F. critical trajectory and the essential singularity
    u0s = 0.6; ys0 = sep_y(u0s)
    crit = []
    for l in ((10, 100) if QUICK else (10, 30, 100, 300, 1000, 3000, 10000)):
        s = endpoint(u0s, ys0, float(l), rtol=1e-12, atol=1e-17)
        n = 2 * pi / s[0]
        crit.append(dict(l=l, u=s[0], y=s[1], nslam2=n, excess_times_l=(n - 4.0) * l, Hdrift=abs(H(s[0], s[1]) - H(u0s, ys0))))
    res["critical"] = crit
    es = []
    u0 = 0.8; ustop = 2.0
    for eps in ((1e-1, 1e-3) if QUICK else (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)):
        y0e = math.sqrt((f(u0) - FC + eps) / (2 * pi ** 3)); h0 = H(u0, y0e)
        a = math.sqrt(0.5 * pi * (FC - h0))
        lq = l_quad(u0, y0e, ustop)
        try:
            lc = brentq(lambda t: endpoint(u0, y0e, t, rtol=1e-11, atol=1e-16)[0] - ustop, 0.0, 1.05 * lq, xtol=1e-10, rtol=1e-10)
        except Exception as e:
            lc = float("nan")
        es.append(dict(eps=eps, a=a, l_quad=lq, l_cvode=lc, asymptote=pi ** 2 / (4 * a), ratio=lq / (pi ** 2 / (4 * a)), l_minus_asym=lq - pi ** 2 / (4 * a)))
    res["essential"] = dict(u0=u0, ustop=ustop, rows=es)
    print("F done", round(time.time() - t_all), "s", flush=True)
    res["seconds_total"] = time.time() - t_all
    save = {}
    for i, p in enumerate(portrait):
        for k in ("L", "U", "Y"): save[f"traj{i}_{k}"] = p[k]
    for k, (L, d) in curves.items(): save[f"drift_{k}_L"] = L; save[f"drift_{k}_d"] = d
    save["ctl_L"], save["ctl_d"] = ctl_curve
    save["n_traj"] = len(portrait); save["traj_hyp"] = np.array([r["hypothesis"] for r in rows]); save["traj_between"] = np.array([r["between_exact_and_linear"] for r in rows])
    np.savez(OUT / f"ch06_flow_data{suffix}.npz", **save)
    json.dump(res, open(OUT / f"ch06_flow_numbers{suffix}.json", "w"), indent=1, default=float)
    print("done", round(res["seconds_total"]), "s")
    for k, v in tol.items(): print(k, v["max_drift"], v["min_margin"], round(v["seconds"], 1))
    print("control", dr)
