"""Chapter 2 computations (rusty-SUNDIALS + qf-pgpe).  Writes / updates book/figures/ch02_numbers.json.

 A  order test of the IF-RK4 step against CVODE (Adams, rtol 1e-12): the Rust example `cvode_order` re-run and compared with
    the stored data/generated/pgpe/bench/cvode_order.json, and the same test through the Python route (numpy engine + CvodeSolver).
 B  CVODE on two problems with closed-form solutions: harmonic oscillator (ten periods; work-precision for Adams and BDF)
    and Prothero-Robinson y' = -lam (y - cos t) - sin t (cost against stiffness lam); amplitude of the oscillator against time.
 C  exact plane wave of the projected GP equation: numpy IF-RK4, Rust IF-RK4 (qf_pgpe) and CVODE (Adams, BDF) against psi0 exp(-i w t).
 D  the three conserved quantities (norm, energy, momentum) along the integrated flow, for IF-RK4 and CVODE, on the smooth N = 16 state
    used by the registered order test.
 E  the bridge to the Lean library: the engine's projected cubic term against a literal transcription of
    QuantumFluids.GPGalerkin.nl (sum over k1 + k3 = k + k2 in the retained set), the rates of mass and momentum, the effect of the cutoff.

Run:  PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/ch02_compute.py [A B C D E]   (default: all)
      (rs_py_5db8041/rusty_sundials.so = crate rusty-sundials-py of the rusty-SUNDIALS checkout at commit 5db8041, sha256 in the directory;
       rebuild with book/rust/ch02_build_py.sh)
The module `rusty_sundials` that sits in the programme's virtual environment (built 2026-09-26) PREDATES the Adams fix: its Method::Adams is
implicit Euler.  This script refuses to run with it (see check_adams_fix)."""
import json, math, os, subprocess, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RS_ROOT = Path("/home/xavkal/xdev/rusty-SUNDIALS-c3")
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
from pgpe import PGPE
import qf_pgpe
import rusty_sundials
from rusty_sundials import CvodeSolver

OUT = HERE / "ch02_numbers.json"
NUM = json.loads(OUT.read_text()) if OUT.exists() else {}

def save():
    OUT.write_text(json.dumps(NUM, indent=1))

class Counter:
    """wraps a right-hand side f(t, y) and counts the calls (the 'cost' of a CVODE run, machine independent)"""
    def __init__(self, f): self.f, self.n = f, 0
    def __call__(self, t, y): self.n += 1; return self.f(t, y)

def run_cvode(method, rtol, atol, f, y0, tend, t0=0.0, max_steps=5_000_000):
    c = Counter(f); s = CvodeSolver(method, rtol, atol, max_steps)
    w0 = time.perf_counter()
    try:
        _, y = s.solve(c, t0, list(y0), tend); status = "ok"
    except Exception as e:
        y, status = None, str(e)[:80]
    return {"nfe": c.n, "wall_s": time.perf_counter() - w0, "y": y, "status": status}

# ------------------------------------------------------------------------------------------------ environment
def check_adams_fix():
    """Adams on y' = -y, t in [0, 10]: the fixed method (LLNL cvSetAdams, orders 1..12) needs a few hundred right-hand sides at
    rtol 1e-8; the pre-fix method (implicit Euler with a Milne estimate) needs ~2e5."""
    r = run_cvode("adams", 1e-8, 1e-14, lambda t, y: [-y[0]], [1.0], 10.0)
    err = abs(r["y"][0] - math.exp(-10.0)) / math.exp(-10.0)
    ok = r["nfe"] < 5000
    if not ok:
        raise SystemExit(f"rusty_sundials at {rusty_sundials.__file__} has the pre-fix Adams (nfe={r['nfe']}); put a build of the "
                         "current rusty-SUNDIALS (/mnt/data/xdev-cache/rs_py_5db8041, or book/rust/ch02_build_py.sh) first on PYTHONPATH")
    return {"module": rusty_sundials.__file__, "adams_fix_probe_nfe": r["nfe"], "adams_fix_probe_relerr": err}

def part_env():
    commit = subprocess.run(["git", "-C", str(RS_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    import hashlib
    sha = hashlib.sha256(Path(rusty_sundials.__file__).read_bytes()).hexdigest() if rusty_sundials.__file__.endswith(".so") else None
    NUM["env"] = {"rusty_sundials_checkout": str(RS_ROOT), "rusty_sundials_commit": commit, "module_sha256": sha, **check_adams_fix(),
                  "loadavg_at_start": os.getloadavg(), "numpy": np.__version__, "date": time.strftime("%Y-%m-%d %H:%M"),
                  "note": "machine shared, load about 7-10: wall times are indicative only, right-hand-side counts are exact"}
    save(); print("env", NUM["env"])

# ------------------------------------------------------------------------------------------------ A
def k2_state(s):
    """the smooth state of the registered order test (crates/qf-pgpe/examples/cvode_order.rs): 1 + 0.15 e^{i(k1 x + 2 k1 y)} + 0.08 e^{i(-2 k1 x + k1 y)}"""
    x = np.arange(s.N) * s.dx; X, Y = np.meshgrid(x, x, indexing="ij"); k1 = 2 * np.pi / s.L
    return 1.0 + 0.15 * np.exp(1j * (k1 * X + 2 * k1 * Y)) + 0.08 * np.exp(1j * (-2 * k1 * X + k1 * Y))

def part_A():
    exe = RS_ROOT / "target" / "release" / "examples" / "cvode_order"
    stored = json.loads((ROOT / "data/generated/pgpe/bench/cvode_order.json").read_text())
    rerun = json.loads(subprocess.run([str(exe)], capture_output=True, text=True, check=True).stdout)
    dts = np.array([p[0] for p in rerun["dt_error"]]); errs = np.array([p[1] for p in rerun["dt_error"]])
    A = {"rust_example": str(exe), "stored_file": "data/generated/pgpe/bench/cvode_order.json", "rerun_identical_to_stored": rerun == stored,
         "n": rerun["n"], "modes": rerun["modes"], "t_end": rerun["t_end"], "cvode_rhs_evals": rerun["cvode_rhs_evals"],
         "cvode_steps": rerun["cvode_steps"], "fitted_order_endpoints_rust": rerun["fitted_order"],
         "dt_error_rust": rerun["dt_error"], "successive_ratios": [float(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]}
    # the same test through the Python route: numpy engine for IF-RK4, CvodeSolver (Adams, 1e-12/1e-14) on s.rhs_real for the reference
    s = PGPE(N=16, L=16.0, g=1.0, dt=0.01)
    c0 = s.modes(k2_state(s)); assert s.n_modes == rerun["modes"]
    cnt = Counter(lambda t, y: list(s.rhs_real(t, y)))
    w0 = time.perf_counter()
    _, yref = CvodeSolver("adams", 1e-12, 1e-14, 2_000_000).solve(cnt, 0.0, s.pack(c0).tolist(), 1.0)
    A["python_route"] = {"cvode_rhs_evals": cnt.n, "wall_s": time.perf_counter() - w0, "dt_error": []}
    yref = np.array(yref)
    for dt in (0.04, 0.02, 0.01, 0.005, 0.0025):
        sd = PGPE(N=16, L=16.0, g=1.0, dt=dt)
        e = float(np.max(np.abs(sd.pack(sd.run(c0, 1.0)) - yref)))
        A["python_route"]["dt_error"].append([dt, e])
    pe = np.array([p[1] for p in A["python_route"]["dt_error"]])
    A["python_route"]["fitted_order_lsq_all5"] = float(np.polyfit(np.log(dts), np.log(pe), 1)[0])
    A["python_route"]["max_rel_difference_of_errors_vs_rust"] = float(np.max(np.abs(pe - errs) / errs))
    A["fitted_order_lsq_all5"] = float(np.polyfit(np.log(dts), np.log(errs), 1)[0])
    NUM["A_order"] = A; save()
    print("A", A["rerun_identical_to_stored"], A["fitted_order_lsq_all5"], A["python_route"]["fitted_order_lsq_all5"],
          A["python_route"]["max_rel_difference_of_errors_vs_rust"])

# ------------------------------------------------------------------------------------------------ B
def part_B():
    B = {}
    TEND = 20 * math.pi
    osc = lambda t, y: [y[1], -y[0]]
    rows = []
    for m in ("adams", "bdf"):
        for k2 in range(6, 25):                       # rtol = 10^{-k2/2}: 1e-3 ... 1e-12, two points per decade
            rt = 10.0 ** (-k2 / 2)
            r = run_cvode(m, rt, rt * 1e-2, osc, [1.0, 0.0], TEND)
            err = amp = None
            if r["y"] is not None:
                err = float(max(abs(r["y"][0] - math.cos(TEND)), abs(r["y"][1] + math.sin(TEND)))); amp = float(math.hypot(*r["y"]) - 1.0)
            rows.append({"method": m, "rtol": rt, "nfe": r["nfe"], "err": err, "amp_minus_1": amp, "wall_s": r["wall_s"], "status": r["status"]})
    B["oscillator"] = {"problem": "x'' = -x, x(0)=1, v(0)=0, t in [0, 20 pi] (ten periods); exact (cos t, -sin t); atol = 1e-2 rtol; err = max-norm at t_end",
                       "tend": TEND, "rows": rows}
    # Prothero-Robinson: stiffness scan at fixed tolerance
    pr_rows = []
    for lam in (1.0, 10.0, 100.0, 1e3, 1e4, 1e5):
        f = lambda t, y, lam=lam: [-lam * (y[0] - math.cos(t)) - math.sin(t)]
        for m in ("adams", "bdf"):
            r = run_cvode(m, 1e-6, 1e-8, f, [1.0], 10.0)
            pr_rows.append({"lam": lam, "method": m, "nfe": r["nfe"], "err": None if r["y"] is None else float(abs(r["y"][0] - math.cos(10.0))),
                            "wall_s": r["wall_s"], "status": r["status"]})
    B["prothero_robinson"] = {"problem": "y' = -lam (y - cos t) - sin t, y(0) = 1, t in [0, 10]; exact y = cos t; rtol 1e-6, atol 1e-8", "rows": pr_rows}
    # amplitude of the oscillator against time (independent solves from t = 0 to each t_k: the API returns the end state only)
    tk = np.linspace(0.0, TEND, 161)[1:]
    amp = {}
    for m in ("adams", "bdf"):
        for rt in (1e-3, 1e-5):
            a = []
            for t in tk:
                r = run_cvode(m, rt, rt * 1e-2, osc, [1.0, 0.0], float(t))
                a.append(None if r["y"] is None else float(math.hypot(*r["y"])))
            amp[f"{m}_{rt:g}"] = a
    B["amplitude_vs_time"] = {"t": tk.tolist(), **amp,
                              "note": "each point is an independent CvodeSolver.solve(rhs, 0, y0, t_k); |(x, v)| = 1 exactly"}
    # the Adams defect, for the record: y' = -y, the fixed method against the numbers of rusty-SUNDIALS docs/CVODE_ADAMS_FIX.md
    dec = []
    for m in ("adams", "bdf"):
        for rt in (1e-4, 1e-6, 1e-8, 1e-10):
            r = run_cvode(m, rt, 1e-14, lambda t, y: [-y[0]], [1.0], 10.0)
            dec.append({"method": m, "rtol": rt, "nfe": r["nfe"], "relerr": float(abs(r["y"][0] - math.exp(-10.0)) / math.exp(-10.0))})
    B["decay_adams_fix"] = {"problem": "y' = -y, t in [0, 10], atol 1e-14, relative error of y(10)", "rows": dec,
                            "unfixed_reference": "docs/CVODE_ADAMS_FIX.md (rusty-SUNDIALS): error x0.316 and steps x3.16 per decade of rtol (implicit Euler)"}
    # the same four runs with the module that sits in the programme's virtual environment (built before the Adams fix)
    snippet = ("import json, math, os, sys\nfrom rusty_sundials import CvodeSolver\nimport rusty_sundials\nout = []\n"
               "for m in ('adams', 'bdf'):\n    for rt in (1e-4, 1e-6, 1e-8, 1e-10):\n        n = [0]\n"
               "        def f(t, y, n=n): n[0] += 1; return [-y[0]]\n"
               "        _, y = CvodeSolver(m, rt, 1e-14, 5000000).solve(f, 0.0, [1.0], 10.0)\n"
               "        out.append({'method': m, 'rtol': rt, 'nfe': n[0], 'relerr': abs(y[0] - math.exp(-10.0)) / math.exp(-10.0)})\n"
               "print(json.dumps({'module': rusty_sundials.__file__, 'mtime': os.path.getmtime(rusty_sundials.__file__), 'rows': out}))\n")
    env = dict(os.environ); env["PYTHONPATH"] = ""
    stale = json.loads(subprocess.run([sys.executable, "-c", snippet], capture_output=True, text=True, env=env, check=True).stdout)
    stale["built"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(stale.pop("mtime")))
    B["decay_stale_venv_module"] = stale
    NUM["B_cvode"] = B; save()
    for r in rows: print("B1", r["method"], f"{r['rtol']:.2e}", r["nfe"], r["err"], r["amp_minus_1"])
    for r in pr_rows: print("B2", r)

# ------------------------------------------------------------------------------------------------ C
def plane_wave_setup(N, L, g, m, n0=1.0):
    s = PGPE(N=N, L=L, g=g, dt=0.01)
    x = np.arange(N) * s.dx; X, Y = np.meshgrid(x, x, indexing="ij")
    k = 2 * np.pi * m / L
    psi0 = np.sqrt(n0) * np.exp(1j * k * X)
    return s, psi0, k, 0.5 * k ** 2 + g * n0

def part_C():
    # C1: the two IF-RK4 engines (numpy, Rust) against the exact solution, N = 32, three steps; and the registered K4 configuration
    N, L, g, m = 32, 16.0, 1.0, 3
    s, psi0, kx, w = plane_wave_setup(N, L, g, m)
    c0 = s.modes(psi0); exact = lambda t: psi0 * np.exp(-1j * w * t)
    TC = 10.0
    C = {"N": N, "L": L, "g": g, "n0": 1.0, "m": m, "k": kx, "omega": w, "k2_over_2": 0.5 * kx ** 2, "t_end": TC, "n_modes": s.n_modes}
    ts = np.linspace(0, TC, 21); series = {}
    for dt in (0.02, 0.01, 0.005):
        sn = PGPE(N=N, L=L, g=g, dt=dt); sr = qf_pgpe.Pgpe(N, L, g, dt)
        cn, cr = c0.copy(), np.ascontiguousarray(c0)
        en, er, nn = [], [], []
        for i, t in enumerate(ts):
            if i > 0:
                cn = sn.run(cn, ts[i] - ts[i - 1]); cr = sr.run(cr, ts[i] - ts[i - 1])
            en.append(float(np.max(np.abs(sn.psi(cn) - exact(t))))); er.append(float(np.max(np.abs(sr.psi(cr) - exact(t)))))
            nn.append(abs(sn.norm(cn) / sn.norm(c0) - 1))
        series[f"dt={dt}"] = {"numpy_err": en, "rust_err": er, "numpy_norm_drift": nn, "rust_minus_numpy_final": float(np.max(np.abs(cr - cn)))}
    C["times"] = ts.tolist(); C["engine_series"] = series
    sf = PGPE(N=N, L=L, g=0.0, dt=0.01); cf = sf.run(sf.modes(psi0), TC)
    srf = qf_pgpe.Pgpe(N, L, 0.0, 0.01); crf = srf.run(np.ascontiguousarray(sf.modes(psi0)), TC)
    ph = psi0 * np.exp(-0.5j * kx ** 2 * TC)
    C["free_g0"] = {"err_numpy_dt0.01": float(np.max(np.abs(sf.psi(cf) - ph))), "err_rust_dt0.01": float(np.max(np.abs(sf.psi(crf) - ph)))}
    # the registered known answer K4 (docs/designs/PGPE_BKT_PREREG.md): N = 64, L = 32, dt = 0.005, t = 10, plane wave; criterion 1e-9 on the phase error
    s4, psi4, k4, w4 = plane_wave_setup(64, 32.0, 1.0, 3)
    s4.set_dt(0.005); c4 = s4.modes(psi4); ex4 = psi4 * np.exp(-1j * w4 * TC)
    r4 = qf_pgpe.Pgpe(64, 32.0, 1.0, 0.005)
    C["K4_registered"] = {"N": 64, "L": 32.0, "dt": 0.005, "t_end": TC, "m": 3, "numpy_err": float(np.max(np.abs(s4.psi(s4.run(c4, TC)) - ex4))),
                          "rust_err": float(np.max(np.abs(r4.psi(r4.run(np.ascontiguousarray(c4), TC)) - ex4))), "criterion": 1e-9}
    print("C engine final errors", {k: (v["numpy_err"][-1], v["rust_err"][-1]) for k, v in series.items()}, C["free_g0"], C["K4_registered"], flush=True)
    # C2: CVODE on the same equation, N = 16 (49 modes, 98 unknowns), plane wave m = 3, t in [0, 10]
    N2, L2 = 16, 16.0
    s2, psi2, k2, w2 = plane_wave_setup(N2, L2, 1.0, 3)
    c2 = s2.modes(psi2); ex2 = psi2 * np.exp(-1j * w2 * TC); y0 = s2.pack(c2).tolist()
    rhs = lambda t, y: list(s2.rhs_real(t, y))
    rows = []
    for meth, rts in (("adams", (1e-4, 1e-6, 1e-8, 1e-10)), ("bdf", (1e-4, 1e-6, 1e-8))):
        for rt in rts:
            r = run_cvode(meth, rt, rt * 1e-2, rhs, y0, TC)
            if r["y"] is not None:
                cc = s2.unpack(np.array(r["y"])); err = float(np.max(np.abs(s2.psi(cc) - ex2))); nrm = float(s2.norm(cc) / s2.norm(c2) - 1)
            else: err = nrm = None
            rows.append({"method": meth, "rtol": rt, "nfe": r["nfe"], "wall_s": r["wall_s"], "err": err, "norm_drift_signed": nrm, "status": r["status"]})
            print("C2", rows[-1], flush=True)
    C["cvode_N16"] = {"N": N2, "L": L2, "m": 3, "k": k2, "omega": w2, "n_modes": s2.n_modes, "t_end": TC, "rows": rows}
    # IF-RK4 on the same N = 16 problem for the cost comparison (4 right-hand sides per step)
    C["engine_N16"] = []
    for dt in (0.02, 0.01, 0.005):
        sd = PGPE(N=N2, L=L2, g=1.0, dt=dt); cc = sd.run(c2, TC)
        C["engine_N16"].append({"dt": dt, "nfe_equivalent": int(round(4 * TC / dt)), "err": float(np.max(np.abs(sd.psi(cc) - ex2))),
                                "norm_drift_signed": float(sd.norm(cc) / sd.norm(c2) - 1)})
    NUM["C_planewave"] = C; save()

# ------------------------------------------------------------------------------------------------ D
def part_D():
    N, L = 16, 16.0
    s = PGPE(N=N, L=L, g=1.0, dt=0.01)
    c0 = s.modes(k2_state(s)); w = s.dx ** 2 / N ** 2
    sc_p = float(np.sum(np.sqrt(s.k2) * np.abs(c0) ** 2) * w)
    inv = lambda c: (s.norm(c), s.energy(c), s.momentum(c))
    n0, e0, p0 = inv(c0)
    TD = 5.0
    D = {"N": N, "L": L, "t_end": TD, "n_modes": s.n_modes, "momentum_scale": sc_p, "initial": {"N": n0, "E": e0, "P": p0.tolist()}, "rows": []}
    # reference: CVODE Adams 1e-12
    ref = run_cvode("adams", 1e-12, 1e-14, lambda t, y: list(s.rhs_real(t, y)), s.pack(c0).tolist(), TD)
    yref = np.array(ref["y"]); D["reference"] = {"method": "adams", "rtol": 1e-12, "nfe": ref["nfe"]}
    def add(label, c, nfe=None, extra=None):
        n1, e1, p1 = inv(c); y = s.pack(c)
        D["rows"].append({"label": label, "nfe": nfe, "dN_over_N_signed": float(n1 / n0 - 1), "dE_over_E_signed": float(e1 / e0 - 1),
                          "dP_over_scale": float(np.max(np.abs(p1 - p0)) / sc_p), "err_vs_reference": float(np.max(np.abs(y - yref))), **(extra or {})})
        print("D", D["rows"][-1], flush=True)
    for dt in (0.02, 0.01, 0.005):
        sd = PGPE(N=N, L=L, g=1.0, dt=dt); add(f"IF-RK4 numpy dt={dt}", sd.run(c0, TD), extra={"engine": "numpy", "dt": dt})
        sr = qf_pgpe.Pgpe(N, L, 1.0, dt); add(f"IF-RK4 Rust dt={dt}", sr.run(np.ascontiguousarray(c0), TD), extra={"engine": "rust", "dt": dt})
    for meth in ("adams", "bdf"):
        for rt in (1e-4, 1e-6, 1e-8, 1e-10):
            r = run_cvode(meth, rt, rt * 1e-2, lambda t, y: list(s.rhs_real(t, y)), s.pack(c0).tolist(), TD)
            if r["y"] is None: D["rows"].append({"label": f"CVODE {meth} rtol={rt:g}", "status": r["status"], "nfe": r["nfe"]}); continue
            add(f"CVODE {meth} rtol={rt:g}", s.unpack(np.array(r["y"])), nfe=r["nfe"], extra={"method": meth, "rtol": rt, "wall_s": r["wall_s"]})
    NUM["D_invariants"] = D; save()

# ------------------------------------------------------------------------------------------------ E
def lean_nl(Lam, A):
    """Literal transcription of QuantumFluids.GPGalerkin.nl on Z^2:
         nl psi k = sum over k1, k2, k3 in Lam with k1 + k3 = k + k2 of
                    psi k1 * conj(psi k2) * psi k3        (no wrap-around)
       Lam: (m, 2) integer array of modes, A: (m,) amplitudes psi.
       Returns (table, B) with table[kx + B, ky + B] = nl psi (kx, ky)."""
    m = len(Lam)
    B = 3 * int(np.abs(Lam).max()) + 1               # sums reach 3 R
    size = 2 * B + 1
    re = np.zeros(size * size)
    im = np.zeros(size * size)
    for i in range(m):                               # k1 = Lam[i]
        k = Lam[i] - Lam[:, None, :] + Lam[None, :, :]       # k1 - k2 + k3
        idx = ((k[..., 0] + B) * size + (k[..., 1] + B)).ravel()
        v = (A[i] * np.conj(A)[:, None] * A[None, :]).ravel()
        re += np.bincount(idx, weights=v.real, minlength=size * size)
        im += np.bincount(idx, weights=v.imag, minlength=size * size)
    return (re + 1j * im).reshape(size, size), B


def lean_dens_sq(Lam, A):
    """sum_q |A_q|^2 with A_q = sum_{a - b = q} psi a conj(psi b)  (QuantumFluids.GPGalerkin.pairing_eq_sum, right-hand side)"""
    m = len(Lam); B = 2 * int(np.abs(Lam).max()); size = 2 * B + 1
    re = np.zeros(size * size); im = np.zeros(size * size)
    for i in range(m):
        q = Lam[i][None, :] - Lam
        idx = (q[:, 0] + B) * size + (q[:, 1] + B); v = A[i] * np.conj(A)
        re += np.bincount(idx, weights=v.real, minlength=size * size); im += np.bincount(idx, weights=v.imag, minlength=size * size)
    return float(np.sum(np.abs(re + 1j * im) ** 2))

def bridge_case(N, L, g, f, interior_only, seed):
    s = PGPE(N=N, L=L, g=g, kcut_frac=f)
    n1 = np.fft.fftfreq(N, d=1.0 / N).round().astype(int); NX, NY = np.meshgrid(n1, n1, indexing="ij")
    Lam = np.stack([NX[s.P], NY[s.P]], axis=1)
    rng = np.random.default_rng(seed)
    A = (rng.normal(size=len(Lam)) + 1j * rng.normal(size=len(Lam))) / np.sqrt(2 * len(Lam))
    extreme = (np.abs(Lam[:, 0]) == N // 4) & (Lam[:, 1] == 0) | (np.abs(Lam[:, 1]) == N // 4) & (Lam[:, 0] == 0)
    if interior_only: A[extreme] = 0.0
    # <<< engine_vs_lean
    a = np.zeros((N, N), dtype=complex)
    a[s.P] = A                  # psi_k, the units of the Lean statement
    c = a * N ** 2              # the engine's unnormalized FFT amplitudes
    # the engine's cubic term, in the units of nl:
    nl_eng = s.nonlin(c) / (-1j * g * N ** 2)
    # >>> engine_vs_lean
    table, B = lean_nl(Lam, A)
    nl_lean = np.zeros((N, N), dtype=complex); ij = np.argwhere(s.P)
    for (nx, ny), (ix, iy) in zip(Lam, ij): nl_lean[ix, iy] = table[nx + B, ny + B]
    scale = float(np.abs(nl_lean[s.P]).max()); diff = np.abs(nl_eng - nl_lean) * s.P
    # rates  d/dt sum_k p(k)|a_k|^2 = sum_k p(k) 2 Im( conj(a_k) G_k ),  G_k = omega_k a_k + g nl_k,  omega_k = |k|^2/2 (k = 2 pi n / L)
    kk = 2 * np.pi / L; omega = 0.5 * kk ** 2 * (NX ** 2 + NY ** 2)
    out = {}
    for tag, nlx in (("lean_nl", nl_lean), ("engine", nl_eng)):
        terms = (np.conj(a) * (omega * a + g * nlx))[s.P]                 # conj(a_k) G_k
        pk = (NX[s.P]).astype(float)                                      # p(n) = n_x : an additive map Z^2 -> R
        sc_m = float(np.sum(np.abs(terms))); sc_p = float(np.sum(np.abs(pk) * np.abs(terms)))
        out[tag] = {"mass_rate_over_scale": float(abs(np.sum(terms.imag)) / sc_m), "momentum_rate_over_scale": float(abs(np.sum(pk * terms.imag)) / sc_p)}
    Q = np.sum(np.conj(a[s.P]) * nl_lean[s.P])
    return {"f": f, "interior_only": interior_only, "n_modes": int(len(Lam)), "R_index": float(f * N / 2), "max_abs_diff_over_max_nl": float(diff.max() / scale),
            "n_modes_differing_1e-12": int((diff > 1e-12 * scale).sum()), "rates": out, "Q_lean": [float(Q.real), float(Q.imag)],
            "sum_dens_sq": lean_dens_sq(Lam, A), "Lam": Lam.tolist(), "log10_reldiff": [float(np.log10(max(diff[ix, iy] / scale, 1e-17))) for ix, iy in ij],
            "seed": seed, "n_extreme_modes_zeroed": int(extreme.sum()) if interior_only else 0}

def drift_series(N, L, f, e=0.6, dt=0.01, T=20, seed=3):
    s = PGPE(N=N, L=L, g=1.0, kcut_frac=f, dt=dt)
    c = s.random_state(1.0, e, np.random.default_rng(seed)); w = s.dx ** 2 / N ** 2
    sc_p = float(np.sum(np.sqrt(s.k2) * np.abs(c) ** 2) * w); n0, e0, p0 = s.norm(c), s.energy(c), s.momentum(c)
    rows = []
    for t in range(T + 1):
        if t > 0: c = s.run(c, 1.0)
        rows.append([float(t), float(abs(s.norm(c) / n0 - 1)), float(abs(s.energy(c) / e0 - 1)), float(np.max(np.abs(s.momentum(c) - p0)) / sc_p)])
    return {"f": f, "n_modes": s.n_modes, "dt": dt, "e_target": e, "momentum_scale": sc_p, "rows_t_dN_dE_dP": rows}

def part_E():
    N, L, g = 32, 16.0, 1.0
    E = {"N": N, "L": L, "g": g, "cases": {}}
    for key, (f, io) in {"half_interior": (0.5, True), "half_full": (0.5, False), "twothirds_full": (2 / 3, False)}.items():
        w0 = time.perf_counter(); E["cases"][key] = bridge_case(N, L, g, f, io, seed=1); E["cases"][key]["wall_s"] = time.perf_counter() - w0
        cs = E["cases"][key]
        print("E", key, cs["n_modes"], f"diff={cs['max_abs_diff_over_max_nl']:.2e}", cs["n_modes_differing_1e-12"], cs["rates"], cs["Q_lean"], cs["sum_dens_sq"], flush=True)
    E["drift"] = {"half": drift_series(N, L, 0.5), "twothirds": drift_series(N, L, 2 / 3)}
    NUM["E_bridge"] = E; save()
    for k, v in E["drift"].items(): print("E drift", k, v["rows_t_dN_dE_dP"][10], v["rows_t_dN_dE_dP"][20])

if __name__ == "__main__":
    parts = sys.argv[1:] or ["env", "A", "B", "C", "D", "E"]
    part_env()
    for p in parts:
        if p == "env": continue
        {"A": part_A, "B": part_B, "C": part_C, "D": part_D, "E": part_E}[p]()
    print("wrote", OUT)
