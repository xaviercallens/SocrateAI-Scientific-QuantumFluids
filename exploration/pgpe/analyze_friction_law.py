"""Friction-law campaign analysis (PGPE_FRICTION_LAW_PREREG.md + amendment FL-A1).

    .venv/bin/python exploration/pgpe/analyze_friction_law.py
Reads the base-state JSONs (T, n_s/n) and the pair runs of data/generated/pgpe/transport/fl/, plus the k_cut = pi reference arm
(production_estimates.json), applies the registered estimators (analyze_transport.summarise) and writes
data/generated/pgpe/transport/fl/friction_law_results.json with, per arm: T, rho_n/rho, alpha (energy, regression) with block-jackknife
errors, c = alpha/(rho_n/rho), alpha/T, alpha', eta, the d0 = 8/12 split, the number of runs and how they ended; then the verdicts
FL1, FL2, FL3 and H-T (FL-A1) as fixed in the registration.
"""
import glob, json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"; FL = TR / "fl"
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
from analyze_transport import summarise

ARMS = [  # label, kcut, tag, base (json stem), pair-file prefix
    ("2pi/3, T=0.100", 2.0944, "third", "base_k2.094_N128_e0.55"),
    ("2pi/3, T=0.216", 2.0944, "third", "base_k2.094_N128_e0.60"),
    ("2pi, T=0.127", 6.2832, "fine", "base_k6.283_N256_e0.95"),
    ("2pi, T=0.173", 6.2832, "fine", "base_k6.283_N256_e1.10"),
]


def arm(label, kcut, tag, base):
    jb = json.loads((FL / f"{base}.json").read_text()); T, ns = jb["T"], jb["ns_over_n"]; rn = 1 - ns
    fs = sorted(glob.glob(str(FL / f"FL_{tag}_{base}_antiparallel_d*_s*.npz")))
    if len(fs) < 2:
        return None
    r, info = summarise(fs); out = dict(label=label, kcut=kcut, T=T, rho_n=rn, n_runs=len(fs), ended=[i["ended"] for i in info], base_n_v=jb["n_v"])
    for k in ("alpha_energy", "alpha_regression", "one_minus_alpha_prime", "eta", "msd_exponent"):
        out[k], out[k + "_se"] = r[k], r[k + "_se"]
    out["alpha_prime"] = 1 - r["one_minus_alpha_prime"]
    for k in ("alpha_energy", "alpha_regression"):
        out["c_" + k.split("_")[1]] = r[k] / rn; out["c_" + k.split("_")[1] + "_se"] = r[k + "_se"] / rn
        out[k + "_over_T"] = r[k] / T; out[k + "_over_T_se"] = r[k + "_se"] / T
    for d in (8, 12):
        g = [f for f in fs if f"_d{d}_" in f]
        if len(g) >= 2:
            rr, _ = summarise(g); out[f"d{d}"] = dict(n=len(g), alpha_energy=rr["alpha_energy"], se=rr["alpha_energy_se"])
    return out


def reference_pi():
    pe = json.loads((TR / "production_estimates.json").read_text()); rows = []
    for key, lab in (("e0.60", "pi, T=0.115"), ("e0.70", "pi, T=0.220")):
        e = pe[key]; rn = e["rho_n"]; T = e["T"]
        rows.append(dict(label=lab, kcut=3.1416, T=T, rho_n=rn, n_runs=e["n_runs"], alpha_energy=e["alpha_energy"], alpha_energy_se=e["alpha_energy_se"],
                         alpha_regression=e["alpha_regression"], alpha_regression_se=e["alpha_regression_se"], c_energy=e["alpha_energy"] / rn,
                         c_energy_se=e["alpha_energy_se"] / rn, alpha_energy_over_T=e["alpha_energy"] / T, alpha_energy_over_T_se=e["alpha_energy_se"] / T))
    return rows


def wmean(v, s):
    v, s = np.array(v), np.array(s); w = 1 / s ** 2; m = (w * v).sum() / w.sum()
    return float(m), float(1 / np.sqrt(w.sum())), float(((v - m) ** 2 * w).sum())   # mean, se, chi2


def main():
    arms = [a for a in (arm(*x) for x in ARMS) if a] + reference_pi(); res = {"arms": arms}
    for a in arms:
        print(f"{a['label']:16s} T={a['T']:.3f} rho_n={a['rho_n']:.4f} n={a['n_runs']:2d}  alpha_E={a['alpha_energy']:.5f}+-{a['alpha_energy_se']:.5f}  "
              f"c={a['c_energy']:.3f}+-{a['c_energy_se']:.3f}  alpha/T={a['alpha_energy_over_T']:.4f}+-{a['alpha_energy_over_T_se']:.4f}")
    # FL2: spread of c across the three cutoffs (one value per cutoff: the weighted mean over the arms at that cutoff)
    byk = {}
    for a in arms:
        byk.setdefault(round(a["kcut"], 2), []).append(a)
    cs = {k: wmean([x["c_energy"] for x in v], [x["c_energy_se"] for x in v]) for k, v in byk.items()}
    spread = (max(m for m, _, _ in cs.values()) - min(m for m, _, _ in cs.values())) / np.mean([m for m, _, _ in cs.values()])
    res["FL2"] = dict(c_by_cutoff={str(k): dict(c=m, se=s) for k, (m, s, _) in cs.items()}, spread=float(spread), PASS=bool(spread < 0.20))
    # FL1: within each cutoff with >= 2 temperatures, are the c values consistent (proportionality)
    res["FL1"] = {str(k): dict(n_T=len(v), chi2=cs[k][2], dof=len(v) - 1) for k, v in byk.items() if len(v) >= 2}
    # Born rival: c proportional to k_c, i.e. c(k)/k constant
    born = [(k, m / k, s / k) for k, (m, s, _) in cs.items()]; bm, bs, bchi = wmean([b[1] for b in born], [b[2] for b in born])
    res["Born_rival"] = dict(c_over_k=[b[1] for b in born], chi2=bchi, dof=len(born) - 1, rejected=bool(bchi > 7.8))
    # H-T (post hoc, FL-A1): alpha/T constant across all arms
    m, s, chi = wmean([a["alpha_energy_over_T"] for a in arms], [a["alpha_energy_over_T_se"] for a in arms])
    res["H_T"] = dict(a=m, se=s, chi2=chi, dof=len(arms) - 1, post_hoc=True)
    # c-law (alpha proportional to rho_n with ONE coefficient): same test on c
    mc, sc, chic = wmean([a["c_energy"] for a in arms], [a["c_energy_se"] for a in arms])
    res["one_c"] = dict(c=mc, se=sc, chi2=chic, dof=len(arms) - 1)
    print("FL2:", json.dumps(res["FL2"], indent=0)); print("Born rival:", res["Born_rival"]); print("H-T alpha/T const:", res["H_T"]); print("one c:", res["one_c"])
    (FL / "friction_law_results.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
