"""W2 (L = 96 counterflow control) by the registered rule (amendment A1 + PGPE_COUNTERFLOW_PREREG.md).

Per run: 'no stall' if annihilated, or if the late d^2 slope (t in [2000, 4000]) is >= 50 % of the early one
(t in [100, 600]) in magnitude with the same (negative) sign. Verdict on all available W2 runs: SUPPORTED if all
meet it, REFUTED if none does, INCONCLUSIVE otherwise (tie-break: the four-run rule is the same rule applied to four).
Also prints, post hoc and parameter-free, the wind-equation prediction with alpha = 0.0062.
"""
import glob, json, sys
import numpy as np
sys.path.insert(0, "exploration/pgpe")
from analyze_transport import load, pair_separations

L, RHO_N, RHO_S, ALPHA = 96.0, 0.0293, 0.9707, 0.0062


def slope(t, d, a, b):
    m = (t >= a) & (t <= b)
    return float(np.polyfit(t[m], d[m] ** 2, 1)[0]) if m.sum() > 10 else float("nan")


def wind(d0, Lb, rho_n, rho_s, t_end=4000.0, on=True):
    C = 2 * np.pi * rho_s / (rho_n * Lb ** 2); d = d0; out = [d]; dt = 0.5
    for _ in range(int(t_end / dt)):
        d += dt * (-2 * ALPHA * (1 / d - (C * (d0 - d) if on else 0.0))); out.append(max(d, 0.1))
    return np.array(out[::2])


res, crit = {}, []
for f in sorted(glob.glob("data/generated/pgpe/transport/W2_L96_e0.60_dipole_d12_s*.npz")):
    t, R, q, z, meta = load(f); d = pair_separations(R, q, L)[0]
    early, late = slope(t, d, 100, 600), slope(t, d, 2000, 4000)
    ok = meta["ended"] == "annihilated" or (np.isfinite(late) and early < 0 and late < 0 and abs(late) >= 0.5 * abs(early))
    d0 = float(d[100:140].mean()); pw, pf = wind(d0, L, RHO_N, RHO_S), wind(d0, L, RHO_N, RHO_S, on=False)
    dend = float(d[-100:].mean())
    res[f.split("/")[-1]] = dict(ended=meta["ended"], t_end=meta["t_end"], early=early, late=late, meets=bool(ok), d0=d0, d_end=dend,
                                 wind_end=float(pw[-1]), free_end=float(pf[-1]), d_mean_last1000=float(d[t >= 3000].mean()) if t[-1] >= 3999 else None)
    crit.append(ok)
    print(f"{f.split('/')[-1]}: {meta['ended']} t={meta['t_end']:.0f}  d^2 slope early {early:+.4f} late {late:+.4f}  "
          f"-> {'meets' if ok else 'does not meet'};  d(end) {dend:.2f} | wind {pw[-1]:.2f} | free {pf[-1]:.2f}")
verdict = "SUPPORTED" if crit and all(crit) else ("REFUTED" if crit and not any(crit) else "INCONCLUSIVE")
print(f"W2 verdict on {len(crit)} runs ({sum(crit)} meet the rule): {verdict}")
json.dump({"runs": res, "n": len(crit), "n_meet": int(sum(crit)), "verdict": verdict}, open("data/generated/pgpe/transport/W2_result.json", "w"), indent=1)
