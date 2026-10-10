"""Chapter 6 -- the Lean statements about vortex positions, tested on vortex configurations produced by the programme's PGPE runs.

Statements (lean_src/MatchingScreening.lean, lean_src/PairPolarisation.lean; all proved for EVERY configuration):
  M  norm_rho_le_matching_torus :  |rho(k)| <= |k| * sum_i |p_i - m_{sigma i}|   (minimum-image separations, k in the reciprocal lattice 2 pi Z^2 / L),
     for every pairing sigma of the N positive to the N negative vortices; so  |rho(k)| / |k|  <=  W := the optimal matching cost.
  P  rho_polarisation           :  |rho(k) - i sum_i (k.d_i) e^{i k.m_i}|  <=  sum_i (k.d_i)^2     whenever |k.d_i| <= 1 for every pair.
Data: (1) the final fields of the heating ladder (L = 64, 18 runs) and of the finite-size series (L = 32, 15 runs), vortices by the plaquette winding rule of
VortexWinding.lean (exploration/pgpe/observables.vortices);  (2) the saved vortex positions (100 snapshots each, t = 13510..14500) of the six L = 192 runs
of the C4 extension (data/generated/pgpe/r3_C4/analysis/*_samples.npz);  (3) synthetic single dipoles.
Also: the polarisability plateau of PGPE_DIELECTRIC_RESULTS.md (D4), re-derived here from the saved positions with independent code:
  <|rho(k)|^2>/k^2  (mean over shells m^2 in {4,5,8,9,10,13,16})  versus  < sum_i d_i^2 > / 2   (d_i from the optimal matching).
Writes figures/ch06_cert_numbers.json and figures/ch06_cert_data.npz."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
from pgpe import PGPE
from observables import vortices

TWO_PI = 2 * np.pi
SHELLS = {1: [(1, 0), (0, 1)], 2: [(1, 1), (1, -1)], 4: [(2, 0), (0, 2)], 5: [(1, 2), (2, 1), (1, -2), (2, -1)], 8: [(2, 2), (2, -2)],
          9: [(3, 0), (0, 3)], 10: [(1, 3), (3, 1), (1, -3), (3, -1)], 13: [(2, 3), (3, 2), (2, -3), (3, -2)], 16: [(4, 0), (0, 4)]}
PLATEAU = (4, 5, 8, 9, 10, 13, 16)


def split(pos, q):
    """Positive and negative position lists, a charge of modulus m counted m times (a coincident multiple vortex is allowed by the theorem)."""
    a = np.concatenate([np.repeat(pos[q > 0], q[q > 0], axis=0)]) if np.any(q > 0) else np.zeros((0, 2))
    b = np.concatenate([np.repeat(pos[q < 0], -q[q < 0], axis=0)]) if np.any(q < 0) else np.zeros((0, 2))
    return a, b


def optimal_matching(a, b, L):
    d = a[:, None, :] - b[None, :, :]; d -= L * np.round(d / L)
    C = np.hypot(d[..., 0], d[..., 1]); r, c = linear_sum_assignment(C)
    dv = a[r] - b[c]; dv -= L * np.round(dv / L)                 # minimum-image separation of each matched pair
    return float(C[r, c].sum()), dv, a[r], b[c]


def rho(K, a, b):
    """rho(k) = sum_+ e^{i k.p} - sum_- e^{i k.m} for an array of wavevectors K (nk, 2)."""
    return np.exp(1j * (a @ K.T)).sum(0) - np.exp(1j * (b @ K.T)).sum(0)


def lattice_vectors(L, nmax):
    n = np.array([(i, j) for i in range(-nmax, nmax + 1) for j in range(-nmax, nmax + 1) if (i, j) != (0, 0)], float)
    return n, TWO_PI * n / L


def analyse(pos, q, L, nmax=6):
    a, b = split(pos, q)
    if len(a) != len(b) or len(a) == 0:
        return None
    W, dv, pm, mm = optimal_matching(a, b, L)
    n, K = lattice_vectors(L, nmax); kk = np.hypot(K[:, 0], K[:, 1])
    r = rho(K, a, b); bound = np.abs(r) / kk
    k1 = np.isclose(kk, TWO_PI / L)
    out = dict(N=int(len(a)), W=W, bmax=float(bound.max()), tau_max=float(bound.max() / W), bound_k1=float(bound[k1].max()), tau_k1=float(bound[k1].max() / W),
               violations=int(np.sum(bound > W * (1 + 1e-12))), mean_d=float(np.hypot(dv[:, 0], dv[:, 1]).mean()), sum_d2=float((dv ** 2).sum()),
               max_d=float(np.hypot(dv[:, 0], dv[:, 1]).max()))
    # polarisation statement P at the four shortest wavevectors (premise |k.d_i| <= 1 checked)
    Kp = K[k1]; Rr, Bb, rn, prem = [], [], [], []
    for kv in Kp:
        kd = dv @ kv
        T = 1j * np.sum(kd * np.exp(1j * (mm @ kv)))
        rk = rho(kv[None, :], a, b)[0]
        Rr.append(abs(rk - T)); Bb.append(float(np.sum(kd ** 2))); rn.append(abs(rk)); prem.append(bool(np.all(np.abs(kd) <= 1)))
    out.update(P_premise_ok=bool(all(prem)), P_remainder=float(np.mean(Rr)), P_bound=float(np.mean(Bb)), P_rho=float(np.mean(rn)),
               P_holds=bool(all(r_ <= b_ * (1 + 1e-12) for r_, b_, p_ in zip(Rr, Bb, prem) if p_)))
    return out


def load_field_snapshots():
    rows = []
    for prefix, L in (("II_", 64.0), ("III_L32_", 32.0)):
        for f in sorted((ROOT / "data/generated/pgpe/r2").glob(f"{prefix}*_final.npy")):
            c = np.load(f); N = c.shape[0]; s = PGPE(N=N, L=L)
            pos, q = vortices(s, c)
            meta = json.loads(Path(str(f).replace("_final.npy", ".json")).read_text())
            r = analyse(pos.astype(float), q.astype(int), L)
            if r is None:
                continue
            r.update(name=f.stem.replace("_final", ""), L=L, e=meta["e"], T=meta["whole"]["T"], kind="field")
            rows.append(r)
    return rows


def d4_for_run(name, L=192.0):
    z = np.load(ROOT / f"data/generated/pgpe/r3_C4/analysis/{name}_samples.npz", allow_pickle=True)
    dk = TWO_PI / L; acc = {m2: [] for m2 in SHELLS}; sumd2 = []; taus = []; Ws = []; bs = []; viol = 0; prem = []
    for i in range(len(z["t"])):
        pos = np.asarray(z["pos"][i], float); q = np.asarray(z["q"][i], int)
        a, b = split(pos, q)
        if len(a) != len(b) or len(a) == 0:
            continue
        W, dv, pm, mm = optimal_matching(a, b, L); sumd2.append(float((dv ** 2).sum()) / 2); Ws.append(W)
        for m2, vecs in SHELLS.items():
            K = np.array(vecs, float) * dk
            r = rho(K, a, b); acc[m2].append(np.mean(np.abs(r) ** 2) / (m2 * dk ** 2))        # <|rho|^2>/k^2 over the shell vectors
        K1 = np.array(SHELLS[1], float) * dk; b1 = np.abs(rho(K1, a, b)) / dk
        taus.append(float(b1.max() / W)); bs.append(float(b1.max())); viol += int(np.any(b1 > W * (1 + 1e-12)))
    plateau = float(np.mean([np.mean(acc[m2]) for m2 in PLATEAU]))
    per_shell = {m2: float(np.mean(acc[m2])) for m2 in SHELLS}
    return dict(name=name, n_snap=len(sumd2), plateau=plateau, pred=float(np.mean(sumd2)), ratio=plateau / float(np.mean(sumd2)), per_shell=per_shell, tau_k1_mean=float(np.mean(taus)),
                tau_k1_median=float(np.median(taus)), W_mean=float(np.mean(Ws)), W_std=float(np.std(Ws)), bound_k1_mean=float(np.mean(bs)), bound_k1_std=float(np.std(bs)), N_mean=float(np.mean([len(np.asarray(z["q"][i])) for i in range(len(z["t"]))])), violations=viol,
                R_Tv_k1=None)


if __name__ == "__main__":
    res = {}
    rows = load_field_snapshots()
    res["fields"] = rows
    res["fields_summary"] = dict(n=len(rows), violations_total=int(sum(r["violations"] for r in rows)), tau_max_all=float(max(r["tau_max"] for r in rows)),
                                 tau_k1_min=float(min(r["tau_k1"] for r in rows)), tau_k1_max=float(max(r["tau_k1"] for r in rows)),
                                 P_premise_ok=int(sum(r["P_premise_ok"] for r in rows)), P_holds_when_premise=int(sum(r["P_holds"] for r in rows if r["P_premise_ok"])),
                                 P_rel_remainder_median=float(np.median([r["P_remainder"] / r["P_rho"] for r in rows if r["P_premise_ok"]])),
                                 P_rel_bound_median=float(np.median([r["P_bound"] / r["P_rho"] for r in rows if r["P_premise_ok"]])))
    runs = {}
    for name in sorted(f.name.replace("_samples.npz", "") for f in (ROOT / "data/generated/pgpe/r3_C4/analysis").glob("C3_L192_e*_s??_samples.npz")):
        runs[name] = d4_for_run(name); print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in runs[name].items() if k != "per_shell"}, flush=True)
    ref = json.loads((ROOT / "data/generated/pgpe/dielectric/primary_C4.json").read_text())["runs"]
    for name, r in runs.items():
        r["programme_D4_ratio"] = ref[name]["D4_ratio"]; r["programme_R_Tv_k1"] = ref[name]["R_Tv_k1"]; r["programme_box_scale_pair"] = ref[name]["box_scale_pair"]
        r["programme_T"] = ref[name]["T"]; r["programme_K"] = ref[name]["K"]
    res["L192"] = runs
    # synthetic single dipoles in a box of side 64: tightness at k1 parallel to d, and perpendicular
    L = 64.0; syn = []
    for d in (1, 2, 4, 8, 16, 24, 32):
        a = np.array([[d, 0.0]]); b = np.array([[0.0, 0.0]])
        n, K = lattice_vectors(L, 3); kk = np.hypot(K[:, 0], K[:, 1]); r = rho(K, a, b); bound = np.abs(r) / kk
        W = float(d); k1 = np.isclose(kk, TWO_PI / L)
        syn.append(dict(d=d, W=W, bound_k1_max=float(bound[k1].max()), tau_k1=float(bound[k1].max() / W), tau_max=float(bound.max() / W), analytic_tau=float(np.sin(TWO_PI / L * d / 2) / (TWO_PI / L * d / 2))))
    res["synthetic_dipoles_L64"] = syn
    json.dump(res, open(OUT / "ch06_cert_numbers.json", "w"), indent=1, default=float)
    print("fields summary", res["fields_summary"])
    for r in syn: print("dipole", r)
    for name, r in runs.items(): print(name, "D4 ratio mine %.3f programme %.3f | tau_k1 mean %.3f | RTv(k1) prog %.2f box pair %s | violations %d" % (r["ratio"], r["programme_D4_ratio"], r["tau_k1_mean"], r["programme_R_Tv_k1"], r["programme_box_scale_pair"], r["violations"]))
