"""D1 of KINETIC_TDA_PREREG.md: density-only vortex detection = prominence-thresholded minima of |psi|^2,
scored against phase-winding ground truth.  Detector fixed in advance: birth < 0.1 n0, depth > 0.5 n0;
one-to-one matching within 1.0 xi."""
import sys, json
import numpy as np
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, "src")
from quantumfluids.gpe.solver2d import Grid2D, healing_length
from quantumfluids.tda.vortex_persistence import extract_vortices
from quantumfluids.tda.cubical import minima_with_depth

XI = healing_length(1.0); N = 1024; g = Grid2D(n=N, dx=XI / 8); D = "data/generated/kinetic_tda"

def pdist_periodic(a, b, L):
    d = np.abs(a[:, None, :] - b[None, :, :]); d = np.minimum(d, L - d)
    return np.hypot(d[..., 0], d[..., 1])

def minima(psi):
    rho = np.abs(psi) ** 2; rho = rho / rho.mean()
    b, dep, ij = minima_with_depth(rho)
    return b, dep, np.column_stack([ij[:, 1], ij[:, 0]]) * g.dx      # (x, y) like extract_vortices

def score(truth, det, radius=1.0):
    if len(det) == 0 or len(truth) == 0:
        return 0, np.zeros(len(truth), bool)
    C = pdist_periodic(truth, det, g.L) / XI
    r, c = linear_sum_assignment(np.where(C <= radius, C, 1e6))
    ok = C[r, c] <= radius
    hit = np.zeros(len(truth), bool); hit[r[ok]] = True
    return int(ok.sum()), hit

pool = {"tp": 0, "ndet": 0, "ntruth": 0}; nn_all, hit_all = [], []; cache = {}
for t in (5, 10, 20):
    psi = np.load(f"{D}/psi_t{t}.npy")
    truth, _ = extract_vortices(psi, g.dx)
    b, dep, pos = minima(psi); cache[t] = (truth, b, dep, pos)
    det = pos[(b < 0.1) & (dep > 0.5)]
    tp, hit = score(truth, det)
    dtt = pdist_periodic(truth, truth, g.L) / XI; np.fill_diagonal(dtt, np.inf); nn = dtt.min(axis=1)
    nn_all.append(nn); hit_all.append(hit)
    pool["tp"] += tp; pool["ndet"] += len(det); pool["ntruth"] += len(truth)
    print(f"t={t:>2}: truth={len(truth)} detections={len(det)} matched={tp}  precision={tp/max(len(det),1):.3f} recall={tp/len(truth):.3f}")
P, R = pool["tp"] / pool["ndet"], pool["tp"] / pool["ntruth"]
print(f"POOLED precision={P:.3f} (criterion >=0.95: {P >= 0.95})   recall={R:.3f} (criterion >=0.90: {R >= 0.90})")
nn, hit = np.concatenate(nn_all), np.concatenate(hit_all)
for lo, hi in ((0, 1), (1, 2), (2, np.inf)):
    m = (nn >= lo) & (nn < hi)
    print(f"   recall for nearest-neighbour distance in [{lo},{hi}) xi: {hit[m].mean() if m.any() else float('nan'):.3f}  (n={m.sum()})")
print(f"   PREDICTIONS: recall(nn>2 xi) >= 0.97: {hit[nn >= 2].mean() >= 0.97};   recall(nn<1 xi) <= 0.6: {hit[nn < 1].mean() <= 0.6 if (nn < 1).any() else 'no such vortices'}")

psi = np.load(f"{D}/psi_sound_only.npy")
ntruth = len(extract_vortices(psi, g.dx)[0]); b, dep, pos = minima(psi)
ndet = int(((b < 0.1) & (dep > 0.5)).sum())
rho = np.abs(psi) ** 2
print(f"NEGATIVE CONTROL sound-only frame: winding vortices={ntruth} ({'valid' if ntruth == 0 else 'VOID'}), density range [{rho.min()/rho.mean():.2f},{rho.max()/rho.mean():.2f}] n0, "
      f"minima found={len(b)}, detections={ndet}  PASS(==0): {ndet == 0}")

print("SENSITIVITY (reported, not used to choose): rows birth<, cols depth>;  entries precision/recall")
grid = {}
for bt in (0.05, 0.10, 0.15, 0.20, 0.25):
    row = []
    for dt_ in (0.3, 0.4, 0.5, 0.6, 0.7):
        tp = nd = nt = 0
        for t, (truth, b, dep, pos) in cache.items():
            det = pos[(b < bt) & (dep > dt_)]; k, _ = score(truth, det); tp += k; nd += len(det); nt += len(truth)
        row.append(f"{tp/max(nd,1):.2f}/{tp/nt:.2f}"); grid[f"{bt},{dt_}"] = (tp / max(nd, 1), tp / nt)
    print(f"   birth<{bt:.2f}: " + "  ".join(row))
json.dump({"pooled": pool, "precision": P, "recall": R, "grid": grid}, open("exploration/tda/results_d1.json", "w"))
