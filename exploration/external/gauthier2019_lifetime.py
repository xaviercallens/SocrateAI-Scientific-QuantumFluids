#!/usr/bin/env python3
"""Known-answer reproduction on external data: Gauthier et al., Science 364, 1264 (2019), Zenodo 2548958 (CC BY 4.0).

Experimental vortex positions (unsigned, pixels; 512 px = 252.8 um) at 11 hold times (0..10 s) x 10 shots, for
six evaporation depths (condensate fractions 18-75 %). The paper's Fig. 4: the nearest-neighbour distance l/l0
decays exponentially towards the uniform value 1 with a time constant that FALLS as the condensate fraction falls
(thermal friction couples the vortex subsystem to the bath). In the causal-topology chain this is link 3's
lifetime: the protected configuration decays at a rate set by the coupling to the bath.

We recompute l/l0(t) from the raw centroids (l0 = sqrt(0.89 a b / N) as in the paper, 89 % detection region,
a:b = 120:85 um for the FiniteTemp set) and fit l/l0 = 1 + (l/l0(0) - 1) exp(-t/tau). Reported, not tuned.
Data path is where the download landed (lean_src/data/external/...); the owner may move it.
"""
from __future__ import annotations
import json, glob
from pathlib import Path
import numpy as np
import scipy.io as sio
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = [ROOT / "data/external/gauthier2019_zenodo_2548958", ROOT / "lean_src/data/external/gauthier2019_zenodo_2548958"]
D = next(p for p in CANDIDATES if p.exists())
UM_PER_PX = 252.8 / 512.0
EVAP = {"0.9VEvap": 75.3, "1.1VEvap": 67.0, "1.5VEvap": 44.0, "2.0VEvap": 33.0, "2.5VEvap": 26.0, "3.0VEvap": 18.0}  # paper: N_c/N_tot %


def nn_ratio(cent_px: np.ndarray, a_um=60.0, b_um=42.5) -> float:
    p = np.atleast_2d(cent_px) * UM_PER_PX
    n = len(p)
    if n < 2:
        return float("nan")
    d = np.sqrt(((p[:, None, :] - p[None, :, :]) ** 2).sum(-1)); np.fill_diagonal(d, np.inf)
    l = d.min(1).mean(); l0 = np.sqrt(0.89 * a_um * b_um / n)
    return float(l / l0)


def main():
    out = {}
    for sub, frac in EVAP.items():
        f = D / f"exp/Exp_Vortex_Location_Data/FiniteTemp/{sub}/vortexData.mat"
        m = sio.loadmat(f, squeeze_me=True, struct_as_record=False)
        sc = m["single_centroids"]                      # (11 hold times, 10 shots)
        t = np.arange(sc.shape[0], dtype=float)         # seconds
        r = np.array([[nn_ratio(sc[i, j]) for j in range(sc.shape[1])] for i in range(sc.shape[0])])
        rm = np.nanmean(r, 1); rs = np.nanstd(r, 1) / np.sqrt(np.sum(np.isfinite(r), 1))
        try:
            p, cov = curve_fit(lambda tt, r0, tau: 1 + (r0 - 1) * np.exp(-tt / tau), t, rm, p0=[rm[0], 3.0], sigma=rs + 1e-3, maxfev=10000)
            tau, dtau = float(p[1]), float(np.sqrt(cov[1, 1]))
        except Exception:
            tau, dtau = float("nan"), float("nan")
        nv = np.atleast_2d(m["vortex_number"]).mean(1)
        out[sub] = {"cond_frac_pct": frac, "l_over_l0": rm.round(3).tolist(), "sem": rs.round(3).tolist(), "tau_s": tau, "dtau_s": dtau,
                    "l0_ratio_initial": float(rm[0]), "N_v_mean": nv.round(1).tolist()}
        print(f"{sub}: cond {frac:4.1f} %  l/l0(0)={rm[0]:.3f}  l/l0(10s)={rm[-1]:.3f}  tau={tau:.2f}±{dtau:.2f} s  N_v {nv[0]:.1f}->{nv[-1]:.1f}")
    (ROOT / "data/generated/external_gauthier2019_lifetime.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
