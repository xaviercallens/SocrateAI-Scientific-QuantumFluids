"""Solutions to the exercises of Chapter 2 (Appendix C): every computed number of chapters/sol02.tex.

Run (the module of the programme's virtual environment predates the Adams fix; the build of commit 5db8041 must come first):
  PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/sol02_numbers.py
Writes figures/sol02_numbers.json.  About half a minute of CPU.

Exercise 1 is Lean (book/lean/Sol02_NilpotentInverse.lean and the negative control Sol02_NegativeControl_SignFlip.lean); this
script only checks the ring algebra with sympy and the counterexample in ZMod 27 by integer arithmetic.
Exercise 2  the first box of the chapter's solver section with the Prothero-Robinson right-hand side, lambda = 1e4, rtol 1e-6,
            atol 1e-8, t = 10: right-hand-side calls of both methods; max_steps = 300; the least max_steps with which each finishes.
Exercise 3  N = 16: the wrapped triples at the default cutoff (exhaustive search), the cutoffs for which the engine's cubic term
            equals the literal Galerkin sum for every state, the engine against the transcription of GPGalerkin.nl
            (ch02_compute.lean_nl), the mass rate by Parseval, and the momentum rate of the four wrapped terms in closed form.
"""
import hashlib, itertools, json, math, os, re, sys, time
from pathlib import Path
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
import rusty_sundials                                            # noqa: E402
from rusty_sundials import CvodeSolver                          # noqa: E402
from pgpe import PGPE                                           # noqa: E402
from ch02_compute import lean_nl                                # noqa: E402  (the chapter's literal transcription of GPGalerkin.nl)

OUT = HERE / "sol02_numbers.json"
R = {"script": "book/figures/sol02_numbers.py", "date": time.strftime("%Y-%m-%d %H:%M"), "loadavg_at_start": os.getloadavg()}

# ------------------------------------------------------------------------------------------------ environment and Adams probe
mod = Path(rusty_sundials.__file__)
calls = [0]


def counted(f):
    def g(t, y):
        calls[0] += 1
        return f(t, y)
    return g


calls[0] = 0
_, y = CvodeSolver("adams", 1e-8, 1e-14, 5_000_000).solve(counted(lambda t, y: [-y[0]]), 0.0, [1.0], 10.0)
probe = calls[0]
if probe >= 5000:
    raise SystemExit(f"{mod} has the pre-fix Adams method ({probe} calls on y'=-y); put /mnt/data/xdev-cache/rs_py_5db8041 first")
commit_file = mod.parent / "commit.txt"
R["env"] = {"module": str(mod), "module_sha256": hashlib.sha256(mod.read_bytes()).hexdigest() if mod.suffix == ".so" else None,
            "commit": commit_file.read_text().strip() if commit_file.exists() else None,
            "adams_probe_rhs_calls_y'=-y_t10_rtol1e-8": probe, "adams_probe_relerr": abs(y[0] - math.exp(-10)) / math.exp(-10),
            "numpy": np.__version__, "sympy": sp.__version__}

# ------------------------------------------------------------------------------------------------ Exercise 1 (algebra only)
e = sp.symbols("e")
good = sp.expand((1 + e) * (1 - e + e ** 2) - 1)
bad = sp.expand((1 + e) * (1 - e - e ** 2) - 1)
R["exercise1"] = {"goal_minus_one": str(good), "residual_with_certificate_1_times_h": str(sp.expand((1 + e) * (1 - e + e ** 2) - 1 - (e ** 3 - 0))),
                  "signflip_goal_minus_one": str(bad),
                  "signflip_residual_with_certificate_1_times_h": str(sp.expand(bad - e ** 3)),
                  "signflip_residual_with_best_certificate_(-1)_times_h": str(sp.expand(bad + e ** 3)),
                  "ZMod27_e3": {"e^3 mod 27": (3 ** 3) % 27, "(1+e)(1-e-e^2) mod 27": ((1 + 3) * (1 - 3 - 9)) % 27,
                                "(1+e)(1-e+e^2) mod 27": ((1 + 3) * (1 - 3 + 9)) % 27, "2 e^2 mod 27": (2 * 9) % 27}}

# ------------------------------------------------------------------------------------------------ Exercise 2 (CVODE)
lam = 1e4


def rhs(t, y):
    calls[0] += 1
    return [-lam * (y[0] - math.cos(t)) - math.sin(t)]


def run(method, max_steps):
    calls[0] = 0
    s = CvodeSolver(method, 1e-6, 1e-8, max_steps)
    w0 = time.perf_counter()
    try:
        t, yy = s.solve(rhs, 0.0, [1.0], 10.0)
        return {"status": "ok", "rhs_calls": calls[0], "t": t, "y": yy[0], "err": abs(yy[0] - math.cos(10.0)), "wall_s": time.perf_counter() - w0}
    except Exception as ex:                                      # the module raises with a message
        return {"status": "error", "message": str(ex), "rhs_calls": calls[0], "wall_s": time.perf_counter() - w0}


ex2 = {"problem": "y' = -lam (y - cos t) - sin t, lam = 1e4, y(0) = 1, t in [0, 10], rtol 1e-6, atol 1e-8; exact y = cos t"}
lines = []
for m in ("adams", "bdf"):
    r = run(m, 100000)
    ex2[f"{m}_max_steps_100000"] = r
    lines.append(f"{m:5s} rhs calls {r['rhs_calls']:6d}  error {r['err']:.2e}")
ex2["box_output"] = lines
for m in ("adams", "bdf"):
    ex2[f"{m}_max_steps_300"] = run(m, 300)
# least max_steps with which each method finishes (bisection; max_steps counts internal steps)
for m in ("adams", "bdf"):
    lo, hi = 1, 100000                                            # run(lo) fails or lo = 1, run(hi) succeeds
    if run(m, lo)["status"] == "ok":
        hi = lo
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if run(m, mid)["status"] == "ok":
            hi = mid
        else:
            lo = mid
    ex2[f"{m}_least_max_steps_that_finishes"] = hi
    ex2[f"{m}_at_least_max_steps"] = run(m, hi)
    ex2[f"{m}_at_least_max_steps_minus_1"] = run(m, hi - 1)
# the chapter's stored stiffness scan (Fig. 2.2b) at lam = 1e4, for the comparison
ch = json.loads((HERE / "ch02_numbers.json").read_text())
ex2["chapter_fig_b_rows_lam_1e4"] = [r for r in ch["B_cvode"]["prothero_robinson"]["rows"] if r["lam"] == 1e4]
ex2["chapter_fig_b_rows_lam_1e5"] = [r for r in ch["B_cvode"]["prothero_robinson"]["rows"] if r["lam"] == 1e5]
ex2["chapter_fig_b_rows_lam_1"] = [r for r in ch["B_cvode"]["prothero_robinson"]["rows"] if r["lam"] == 1.0]
R["exercise2"] = ex2

# ------------------------------------------------------------------------------------------------ Exercise 3
N = 16
n1 = np.fft.fftfreq(N, d=1.0 / N).round().astype(int)            # index of each grid wave number, in [-N/2, N/2)


def retained(R2max):
    """integer modes n of the N x N grid with |n|^2 <= R2max (indices as the engine stores them)."""
    return [(a, b) for a in n1 for b in n1 if a * a + b * b <= R2max]


def wraps(Lam):
    """all (k, k1, k2, k3) with k, k1, k2, k3 in Lam, k1 - k2 + k3 = k (mod N) but not equal: the wrapped triples."""
    S = set(Lam); out = []
    for k1 in Lam:
        for k2 in Lam:
            for k3 in Lam:
                sx, sy = k1[0] - k2[0] + k3[0], k1[1] - k2[1] + k3[1]
                kx, ky = ((sx + N // 2) % N) - N // 2, ((sy + N // 2) % N) - N // 2   # representative in [-N/2, N/2), as fftfreq
                if (kx, ky) in S and (kx, ky) != (sx, sy):
                    out.append(((kx, ky), k1, k2, k3, (sx - kx) // N, (sy - ky) // N))
    return out


# the engine's default projector at N = 16 (k_cut = k_max / 2, |k| <= k_cut, floating point as in the engine)
s = PGPE(N=N, L=16.0, g=1.0, kcut_frac=0.5)
NX, NY = np.meshgrid(n1, n1, indexing="ij")
Lam_eng = sorted((int(a), int(b)) for a, b in zip(NX[s.P], NY[s.P]))
Lam4 = sorted(retained(16))
assert Lam_eng == Lam4, "engine projector at N=16 is not |n|^2 <= 16"
w4 = wraps(Lam4)
fed = sorted(set(w[0] for w in w4))
ex3 = {"N": N, "n_retained_default": len(Lam4), "axis_modes_retained": all(m in Lam4 for m in [(4, 0), (-4, 0), (0, 4), (0, -4)]),
       "wrapped_quadruples_default": [dict(k=w[0], k1=w[1], k2=w[2], k3=w[3], wrap=(w[4], w[5])) for w in w4],
       "modes_fed_by_a_wrapped_triple": fed}
# a scan of the cutoff radius: which retained sets are free of wrapped triples
scan = []
for R2 in sorted(set(a * a + b * b for a in range(0, 9) for b in range(0, 9) if a * a + b * b <= 64)):
    Lam = retained(R2)
    if not Lam:
        continue
    nw = len(wraps(Lam)) if R2 <= 32 else None                   # beyond R^2 = 32 the triple loop is slow and wraps are certain
    scan.append(dict(R2=R2, R=math.sqrt(R2), n_modes=len(Lam), n_wrapped_triples=nw, four_R_less_than_N=4 * math.sqrt(R2) < N))
    if R2 > 32:
        break
ex3["cutoff_scan"] = scan
ex3["largest_wrap_free_R2"] = max(r["R2"] for r in scan if r["n_wrapped_triples"] == 0)
ex3["four_times_sqrt13"] = 4 * math.sqrt(13)
# the engine against the literal transcription, random state, two cutoffs: R = 4 (default) and R^2 = 13 (just below)
rng = np.random.default_rng(16)
cases = {}
for tag, frac in (("default_R4", 0.5), ("below_R2_13", math.sqrt(13.5) / 8)):
    se = PGPE(N=N, L=16.0, g=1.0, kcut_frac=frac)
    Lam = np.stack([NX[se.P], NY[se.P]], axis=1)
    A = (rng.normal(size=len(Lam)) + 1j * rng.normal(size=len(Lam))) / np.sqrt(2 * len(Lam))
    a = np.zeros((N, N), dtype=complex); a[se.P] = A
    c = a * N ** 2
    nl_eng = se.nonlin(c) / (-1j * se.g * N ** 2)
    table, B = lean_nl(Lam, A)
    nl_lean = np.zeros((N, N), dtype=complex)
    for (nx, ny), (ix, iy) in zip(Lam, np.argwhere(se.P)):
        nl_lean[ix, iy] = table[nx + B, ny + B]
    diff = np.abs(nl_eng - nl_lean) * se.P
    scale = float(np.abs(nl_lean[se.P]).max())
    differing = [tuple(int(v) for v in Lam[i]) for i, (ix, iy) in enumerate(np.argwhere(se.P)) if diff[ix, iy] > 1e-12 * scale]
    entry = dict(kcut_frac=frac, n_modes=int(se.P.sum()), max_diff_over_max_nl=float(diff.max() / scale), differing_modes=sorted(differing))
    idx = {tuple(int(v) for v in Lam[i]): (ix, iy) for i, (ix, iy) in enumerate(np.argwhere(se.P))}
    amp = {m: a[idx[m]] for m in idx}
    if (4, 0) in idx:
        z = amp[(4, 0)] ** 2 * np.conj(amp[(-4, 0)])
        entry["engine_minus_lean_at_(-4,0)"] = [float((nl_eng - nl_lean)[idx[(-4, 0)]].real), float((nl_eng - nl_lean)[idx[(-4, 0)]].imag)]
        entry["a(4,0)^2 conj a(-4,0)"] = [float(z.real), float(z.imag)]
        entry["closed_form_matches"] = bool(abs((nl_eng - nl_lean)[idx[(-4, 0)]] - z) < 1e-14)
    # rates (the convention of the Lean statements: sum_k p(k) Im(conj a_k G_k), G = omega a + g nl), p(n) = n_x
    kk = 2 * np.pi / se.L; omega = 0.5 * kk ** 2 * (NX ** 2 + NY ** 2)
    for name, nl in (("engine", nl_eng), ("lean", nl_lean)):
        terms = (np.conj(a) * (omega * a + se.g * nl))[se.P]
        p = NX[se.P].astype(float)
        entry[f"mass_rate_{name}"] = float(np.sum(terms.imag)); entry[f"mass_scale_{name}"] = float(np.sum(np.abs(terms)))
        entry[f"momentum_rate_{name}"] = float(np.sum(p * terms.imag)); entry[f"momentum_scale_{name}"] = float(np.sum(np.abs(p) * np.abs(terms)))
    # Parseval on the grid: sum_k conj(a_k) [P FFT(|psi|^2 psi)]_k / N^2 = sum_x |psi(x)|^4 / N^2
    psi = np.fft.ifft2(c)
    lhs = np.sum(np.conj(a) * nl_eng)
    rhs_ = np.sum(np.abs(psi) ** 4) / N ** 2
    entry["parseval_lhs"] = [float(lhs.real), float(lhs.imag)]; entry["parseval_rhs"] = float(rhs_)
    if (4, 0) in idx:
        zz = amp[(4, 0)] ** 2 * np.conj(amp[(-4, 0)]) ** 2
        entry["momentum_rate_closed_form_-8g_Im(a4^2 conj(a-4)^2)"] = float(-8 * se.g * zz.imag)
    cases[tag] = entry
ex3["engine_vs_lean"] = cases
# the wrapped quadruple and an additive weight: p(b) + p(d) - p(a) - p(c) with p = n_x
a_, b_, c_, d_ = (-4, 0), (4, 0), (-4, 0), (4, 0)                  # output a, then k1 = b, k2 = c, k3 = d
ex3["defect_of_additivity_p=n_x"] = (b_[0] + d_[0]) - (a_[0] + c_[0])
R["exercise3"] = ex3

OUT.write_text(json.dumps(R, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
print(json.dumps(R, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))[:9000])
