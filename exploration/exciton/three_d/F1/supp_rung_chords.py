"""Supplementary (unregistered, 2026-10-12): one a = 4 ladder (N = 120, C's gauss4 seed, start 0) with the minimum chord and
the distance-spectrum deviation from the 600-cell recorded at EVERY rung, to locate where the homotopy branch departs from the
600-cell. Same optimiser settings as run_F1.py. Output: supp_rung_chords.json."""
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_F1 as F, run_C as R
N, s, kernel = 120, int(sys.argv[1]) if len(sys.argv) > 1 else 0, "gauss4"
seed = 1000 * N + s + 100000 * list(R.KERNELS).index(kernel)
y = np.random.default_rng(seed).normal(size=(N, 4)).ravel()
C6 = R.cell600(); dc = np.sort(np.linalg.norm(C6[:, None] - C6[None], axis=-1)[np.triu_indices(N, 1)])
out = []
for a in F.ladder(4.0):
    c = F.Counter(N, a); res = F.lbfgs(c, y); y = res.x
    X = F.normalise(y, N); d = np.sort(np.linalg.norm(X[:, None] - X[None], axis=-1)[np.triu_indices(N, 1)])
    e6 = R.energy(C6, "g", a)
    out.append(dict(a=a, E=float(res.fun), rel_excess_over_E600=float((res.fun - e6) / e6), nit=int(res.nit), nfev=c.n,
                    min_chord=float(d[0]), spectrum_max_dev_from_600cell=float(np.abs(d - dc).max()), msg=str(res.message)))
    print(out[-1], flush=True)
json.dump(dict(seed=seed, start=s, rungs=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"supp_rung_chords_s{s}.json"), "w"), indent=1)
