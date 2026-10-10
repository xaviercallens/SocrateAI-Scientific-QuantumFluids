"""Chapter 5: a referee for the engine -- the same projected-GPE trajectory integrated by two independent integrators, the
integrating-factor RK4 of the Rust engine `qf_pgpe` and the variable-order Adams method of rusty-SUNDIALS CVODE (Python module
`rusty_sundials`), and the Bogoliubov frequencies read off both.

The projected GPE is an ordinary differential equation for the real vector y = (Re c_k, Im c_k)_{|k| <= k_cut} / N^2
(c_k: fft2 amplitudes).  CVODE integrates it through a Python right-hand side (the numpy engine `pgpe.PGPE.rhs`, the same
equation as the Rust engine; their mode sets are asserted equal).  `CvodeSolver.solve` returns only the end state, so the
record is built by chaining one call per sample interval.

TWO BUILDS OF THE PYTHON MODULE.  The module installed in the project's virtual environment predates a fix of the CVODE Adams
order in the rusty-SUNDIALS tree (the software paper of the engine records the defect: "the Adams order was stuck at one").
`--tag old` runs the small configuration with whatever `rusty_sundials` is first on the path (here: the stale module of the
project's virtual environment, on purpose, for the old/new comparison of the chapter); the production ladder `--tag new` must be
run with the build of the current tree (commit 5db8041 of rusty-SUNDIALS-c3, `cargo build --release -p rusty-sundials-py`, the library
copied to <dir>/rusty_sundials.so) FIRST on PYTHONPATH: /mnt/data/xdev-cache/rs_py_5db8041 (sha256 0bdb1b4a...996d7; the run of this
chapter used a byte-identical copy in the session scratchpad).

    cd book && flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext \
        ../.venv/bin/python figures/ch05_cvode.py --tag new          # N = 16 ladder + the small box + size scaling
    ... env PYTHONPATH=/mnt/data/xdev-cache/qf_ext ../.venv/bin/python figures/ch05_cvode.py --tag old       # small box, old build
"""
import sys, json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PGPE_DIR = HERE.parents[1] / "exploration" / "pgpe"
from ch05_common import *


def cvode_ladder(N, L, T, rtols, g=1.0, dts=0.4, eta=1e-4, seed=3, dt_rk=0.01, atol_over_rtol=1e-3):
    import qf_pgpe
    sys.path.insert(0, str(PGPE_DIR))
    from pgpe import PGPE
    import rusty_sundials
    from rusty_sundials import CvodeSolver
    eng = qf_pgpe.Pgpe(N, L, g, dt_rk, 0.5)
    c0, mask = initial_pulse(eng, N, eta, seed)
    ns = int(round(T / dts)) + 1
    t = np.arange(ns) * dts
    kx, ky = wavevectors(N, L)
    k = np.sqrt(kx ** 2 + ky ** 2)[mask]
    keep = k > 0
    t0 = time.time()
    S_rk, _ = record_condensate_frame(lambda c: eng.run(c, dts), c0, mask, ns, N)
    sec_rk = time.time() - t0
    eng_f = qf_pgpe.Pgpe(N, L, g, dt_rk / 4, 0.5)            # a much finer RK4 run: the engine's own time-step error
    S_rk_fine, _ = record_condensate_frame(lambda c: eng_f.run(c, dts), c0, mask, ns, N)
    py = PGPE(N=N, L=L, g=g, kcut_frac=0.5, dt=dt_rk)
    assert np.array_equal(py.P, mask), "numpy and Rust engines must retain the same modes"
    scale = float(N ** 2)
    counter = {"calls": 0}

    def rhs(_t, y):
        counter["calls"] += 1
        c = py.unpack(np.asarray(y) * scale)
        return (py.pack(py.rhs(c)) / scale).tolist()

    def run_cvode(rtol, atol):
        counter["calls"] = 0
        solver = CvodeSolver("adams", rtol, atol, 10_000_000)
        y = (py.pack(c0) / scale).tolist()
        out = np.empty_like(S_rk)
        t_a = time.time()
        for j in range(ns):
            if j > 0:
                _, y = solver.solve(rhs, (j - 1) * dts, y, j * dts)
            c = py.unpack(np.asarray(y) * scale)
            out[j] = c[mask] * (np.conj(c[0, 0]) / abs(c[0, 0])) / N ** 2
        return out, time.time() - t_a, counter["calls"]

    wb = bog(k[keep], g)
    w_rk = fit_all(t, S_rk[:, keep], split=False)["omega"]
    w_rkf = fit_all(t, S_rk_fine[:, keep], split=False)["omega"]
    amp = np.sqrt(np.mean(np.abs(S_rk_fine[:, keep]) ** 2, axis=0))
    res = dict(N=N, L=L, g=g, T=T, dts=dts, eta=eta, seed=seed, dt_rk=dt_rk, n_modes=int(mask.sum()), n_modes_fitted=int(keep.sum()),
               n_unknowns=int(2 * mask.sum()), distinct_k=sorted({round(float(x), 6) for x in k[keep]}), n_samples=int(ns),
               seconds_rust_rk4=round(sec_rk, 2), rusty_sundials_file=str(rusty_sundials.__file__),
               rk4_vs_bogoliubov_max=float(np.abs(w_rk / wb - 1).max()), rk4_vs_bogoliubov_median=float(np.median(np.abs(w_rk / wb - 1))),
               rk4_dt_vs_dt4_max=float(np.abs(w_rk - w_rkf).max() / wb.min()), ladder=[])
    for rt in rtols:
        S, sec, calls = run_cvode(rt, rt * atol_over_rtol)
        w = fit_all(t, S[:, keep], split=False)["omega"]
        traj = np.abs(S[:, keep] - S_rk_fine[:, keep]) / amp
        res["ladder"].append(dict(rtol=rt, atol=rt * atol_over_rtol, rhs_calls=int(calls), seconds=round(sec, 2),
                                  omega_max_rel_vs_fine_rk4=float(np.max(np.abs(w - w_rkf) / wb)),
                                  omega_median_rel_vs_fine_rk4=float(np.median(np.abs(w - w_rkf) / wb)),
                                  omega_max_rel_vs_bogoliubov=float(np.max(np.abs(w / wb - 1))),
                                  trajectory_max_rel=float(traj.max())))
        print(json.dumps(res["ladder"][-1]), flush=True)
    return res


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    tag = sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "new"
    out = {"tag": tag}
    if quick:
        out["main"] = cvode_ladder(N=8, L=8.0, T=4.0, rtols=(1e-3, 1e-5))
    elif tag == "new":
        out["main"] = cvode_ladder(N=16, L=16.0, T=20.0, rtols=(1e-4, 1e-6, 1e-8, 1e-10))
        out["small"] = cvode_ladder(N=8, L=8.0, T=4.0, rtols=(1e-4, 1e-6, 1e-8))
        out["scaling"] = [cvode_ladder(N=n, L=l, T=2.0, rtols=(1e-6,)) for (n, l) in ((8, 8.0), (16, 16.0), (32, 16.0))]
    else:
        out["small"] = cvode_ladder(N=8, L=8.0, T=4.0, rtols=(1e-4, 1e-6, 1e-8))
    name = "ch05_cvode_quick.json" if quick else f"ch05_cvode_{tag}.json"
    (HERE / name).write_text(json.dumps(out, indent=1))
    print("wrote", name)
