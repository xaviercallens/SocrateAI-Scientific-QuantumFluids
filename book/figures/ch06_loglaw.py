"""Chapter 6 -- the Coulomb gas inside the solver: the energy of an imprinted vortex-antivortex pair in a uniform two-dimensional
condensate (rusty-SUNDIALS `qf-pgpe`, Python extension `qf_pgpe`), against the point-vortex energy on the torus.

Units hbar = m = 1, mean density n = 1, g n = 1 (healing length xi = 1), box side L.  For a neutral pair of separation d << L the plane law is

        E_pair(d) - E_uniform = 2 pi (hbar^2 n / m) ln(d / a) + 2 E_core ,

and on the torus (zero-winding sector, which is what a single-valued phase requires) it becomes

        Delta E(d) = pi * H_WM(d) + 2 pi^2 d^2 / L^2 + C ,       C = 2 pi ln(L / (2 pi a)) + 2 E_core   (one constant per box),

where H_WM is the Weiss-McWilliams pair energy of kappa = +-1 point vortices on the torus (box rescaled to 2 pi; exploration/pgpe/vortex_thermometer.py),
and 2 pi^2 d^2 / L^2 is the kinetic energy of the uniform counterflow  v = 2 pi d / L^2  that the imprint adds so that the phase has no winding around
the box (a dipole of moment d would otherwise leave circulation -2 pi d / L around the other cycle).  The excess energy is read from the engine's own
`energy` of the imprinted field (norm restored by the imprint): no time stepping, no temperature.  The imprint (periodic theta-function phase, Bernoulli
density) is not the relaxed vortex, so C contains a core-mismatch energy; what is tested is the d-dependence, and the dependence of C on L
(C(2L) - C(L) = 2 pi ln 2 = 4.355 if the coupling is 2 pi hbar^2 n / m).
Writes figures/ch06_loglaw_numbers.json.   Run:  PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch06_loglaw.py"""
import json, sys, time
from pathlib import Path
import numpy as np
import qf_pgpe
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "exploration" / "pgpe"))
from vortex_thermometer import h_pair                      # Weiss-McWilliams eq. (12), box side 2 pi

OUT = Path(__file__).resolve().parent
TWO_PI = 2 * np.pi


def model(d, L):
    """pi H_WM(d) + 2 pi^2 d^2 / L^2  (without the constant)."""
    d = np.asarray(d, float)
    return np.pi * h_pair(d * TWO_PI / L, np.zeros_like(d)) + 2 * np.pi ** 2 * d ** 2 / L ** 2


def run(N, L, ds):
    s = qf_pgpe.Pgpe(N, L)
    c0 = s.uniform(); E0 = s.energy(c0); N0 = s.norm(c0)
    rows = []
    for d in ds:
        x0, y0 = L / 2 + 0.25 * s.dx, L / 2 + 0.25 * s.dx     # off-grid centre: vortices sit at plaquette centres
        pos = np.array([[x0 + d / 2, y0], [x0 - d / 2, y0]]); q = np.array([1, -1])
        c = s.imprint_v2(c0, pos, q)
        dp, dq = s.detect(c)
        sep = None
        if len(dq) == 2 and dq.sum() == 0:
            a = dp[dq > 0][0]; b = dp[dq < 0][0]; v = a - b; v -= L * np.round(v / L); sep = float(np.hypot(*v))
        rows.append(dict(d_imprint=float(d), d_detected=sep, n_detected=int(len(dq)), dE=float(s.energy(c) - E0), norm_rel_err=float(abs(s.norm(c) - N0) / N0)))
    return rows, E0


def fit(rows, L, dmin):
    d = np.array([r["d_detected"] for r in rows]); E = np.array([r["dE"] for r in rows])
    m = d >= dmin
    mod = model(d, L)
    C = float(np.mean(E[m] - mod[m])); res = E[m] - mod[m] - C
    return dict(dmin=dmin, n_points=int(m.sum()), d_range=(float(d[m].min()), float(d[m].max())), dE_range=(float(E[m].min()), float(E[m].max())), C=C,
                rms=float(np.sqrt(np.mean(res ** 2))), max_abs=float(np.max(np.abs(res))))


def free_slope(rows, a, b):
    d = np.array([r["d_detected"] for r in rows]); E = np.array([r["dE"] for r in rows]); m = (d >= a) & (d <= b)
    p = np.polyfit(np.log(d[m]), E[m], 1)
    return dict(window=(a, b), n_points=int(m.sum()), slope=float(p[0]), slope_over_2pi=float(p[0] / TWO_PI))


if __name__ == "__main__":
    t0 = time.time(); out = {}
    cfg = {64.0: (128, [2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28]), 128.0: (256, [4, 6, 8, 12, 16, 24, 32, 40, 48, 56])}
    for L, (N, ds) in cfg.items():
        rows, E0 = run(N, L, ds)
        key = f"L{int(L)}"
        out[key] = dict(N=N, L=L, dx=L / N, E_uniform=E0, rows=rows, fits={f"dmin{dm}": fit(rows, L, dm) for dm in (4.0, 6.0, 8.0)},
                        slopes={"d4_8": free_slope(rows, 4.0, 8.0), "d3_10": free_slope(rows, 3.0, 10.0)})
        print(f"L={L}: E_uniform={E0}")
        for r in rows:
            dd = r["d_detected"]; print("  d=%5.1f detected %6.3f dE=%9.4f model=%9.4f  norm_err=%.1e" % (r["d_imprint"], dd, r["dE"], float(model(dd, L)), r["norm_rel_err"]))
        for k, v in out[key]["fits"].items(): print("  fit", k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
    for dm in ("dmin4.0", "dmin6.0", "dmin8.0"):
        out.setdefault("C_difference", {})[dm] = out["L128"]["fits"][dm]["C"] - out["L64"]["fits"][dm]["C"]
    out["two_pi_ln2"] = float(TWO_PI * np.log(2))
    print("C(128) - C(64):", out["C_difference"], " vs 2 pi ln 2 =", out["two_pi_ln2"])
    import hashlib, os
    mod = Path(qf_pgpe.__file__).resolve()
    out["environment"] = dict(qf_pgpe_module=str(mod), sha256=hashlib.sha256(mod.read_bytes()).hexdigest(), mtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(mod))),
                              note="module as found in /mnt/data/xdev-cache/qf_ext (the path FACTS.md section 5 prescribes); the commit it was built from is not recorded; the HEAD of the rusty-SUNDIALS-c3 worktree on 2026-10-10 is 5db8041 (committed 2026-10-09 21:23, before the mtime above)")
    out["seconds"] = time.time() - t0
    out["note"] = "units hbar = m = 1, n = 1, g = 1; imprint_v2 of qf_pgpe (periodic phase, Bernoulli density); energies from Pgpe.energy at fixed norm"
    json.dump(out, open(OUT / "ch06_loglaw_numbers.json", "w"), indent=1, default=float)
