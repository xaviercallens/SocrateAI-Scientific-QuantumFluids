"""Turn gated_scan.json + calibration.json into the registered tables (criterion B, bands, physical mapping)."""
import json, numpy as np
sc = json.load(open("gated_scan.json")); cal = json.load(open("calibration.json"))
nus = np.array(sc["nus"]); c = cal["c"]
gB = cal["criterion_B"]["gamma_c"]
gB_lo, gB_hi = cal["criterion_B"]["gamma_c_from_n"][1], cal["criterion_B"]["gamma_c_from_n"][0]   # anchors 320 (smaller gamma_c), 260
labels = ["inf" if d == "inf" else d for d in sc["Ds"]]
Lams = [0.5, 1, 2, 5, 10, 30, 100]
a_B = 0.0529177   # nm, CODATA Bohr radius (assumption-grade constant for the mapping only)

def windows(G, T):
    """return list of (nu_lo, nu_hi) with G<T, log-linear interpolation of crossings; None edges if open."""
    inside = G < T
    ln = np.log(nus); res = []
    start = None
    if inside[0]: start = "open-low"
    cross = []
    for i in range(len(nus)-1):
        if inside[i] != inside[i+1]:
            f = (np.log(T)-np.log(G[i]))/(np.log(G[i+1])-np.log(G[i]))
            cross.append(float(np.exp(ln[i]+f*(ln[i+1]-ln[i]))))
    if not inside.any(): return None
    lo = None if inside[0] else cross[0]
    hi = None if inside[-1] else cross[-1]
    return (lo, hi)

out = dict(gamma_B=gB, tables={})
G_all = {k: np.array(v) for k, v in sc["gamma1"].items()}
# Lambda_c(nu) = (G/gB)^4 ; minimum over the grid
mins = {}
for k, G in G_all.items():
    Lc = (G/gB)**4
    i = int(np.argmin(Lc))
    mins[k] = dict(Lambda_min=float(Lc[i]), at_nu=float(nus[i]), at_edge=bool(i in (0, len(nus)-1)))
out["Lambda_min_over_nu"] = mins
# monotonicity (P4): count sign changes of dG/dnu
mono = {}
for k, G in G_all.items():
    d = np.diff(G)
    mono[k] = dict(monotone_decreasing=bool((d < 0).all()), n_minima=int(((d[:-1] < 0) & (d[1:] > 0)).sum()), argmin_nu=float(nus[int(np.argmin(G))]))
out["monotonicity_P4"] = mono
# windows
for k, G in G_all.items():
    rows = []
    for Lam in Lams:
        row = dict(Lambda=Lam)
        for lab, g in [("B", gB), ("B_anchor320", gB_lo), ("B_anchor260", gB_hi)]:
            T = g*Lam**0.25
            w = windows(G, T)
            row[lab] = None if w is None else dict(nu_lo=w[0], nu_hi=w[1],
                       nr0_lo=None if w[0] is None else w[0]*Lam**2, nr0_hi=None if w[1] is None else w[1]*Lam**2)
        rows.append(row)
    out["tables"][k] = rows
# gate effect at fixed n r0^2 and Lambda (ratio of Lambda_c, independent of gamma_c)
ratio = {}
for k, G in G_all.items():
    ratio[k] = ((G/G_all["dip"])**4).tolist()
out["Lambda_c_ratio_to_dip_vs_nu"] = ratio
# physical mapping (assumptions)
phys = []
for d in [0.7, 1.0, 2.0]:
    for M in [0.5, 1.0, 1.5]:
        for eps in [3.0, 4.5, 6.0]:
            Lam = (d/a_B)*M/eps
            phys.append(dict(d_nm=d, M_me=M, eps=eps, Lambda=Lam))
out["physical_Lambda_assumed"] = phys
out["central"] = dict(d_nm=1.0, M_me=1.0, eps=4.5, Lambda=(1.0/a_B)/4.5)
json.dump(out, open("analysis.json", "w"), indent=1)
# human-readable summary
L = []
L.append(f"gamma_B = {gB:.4f}; c = {c:.4f}")
for k in ["dip", "inf", "20.0", "10.0", "5.0", "3.0", "2.0", "1.5", "1.2"]:
    m = mins[k]; mo = mono[k]
    L.append(f"D/d={k}: Lambda_min={m['Lambda_min']:.3g} at nu={m['at_nu']:.3g} edge={m['at_edge']}; monotone_dec={mo['monotone_decreasing']} n_minima={mo['n_minima']}")
cen = out["central"]["Lambda"]
L.append(f"central Lambda = {cen:.2f}")
for k in ["dip", "inf", "20.0", "10.0", "5.0", "3.0", "2.0", "1.5", "1.2"]:
    L.append(f"--- {k}")
    for r in out["tables"][k]:
        b = r["B"]
        if b is None: L.append(f"  Lambda={r['Lambda']}: no harmonic crystal on grid")
        else: L.append(f"  Lambda={r['Lambda']}: nu in [{b['nu_lo']}, {b['nu_hi']}]  n r0^2 in [{b['nr0_lo']}, {b['nr0_hi']}]")
open("analysis_summary.txt", "w").write("\n".join(L))
print("\n".join(L))
