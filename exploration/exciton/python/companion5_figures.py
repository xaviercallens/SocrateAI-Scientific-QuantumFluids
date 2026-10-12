#!/usr/bin/env python3
"""Figures of paper V (round 1 of the 3D programme, L1, L3, the Bain-path test). Round-2 panels are added by companion5_round2.py.
Writes paper/figs_companion5/fig_round1.{pdf,png}. Reads only committed records."""
import json, os, itertools
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(R, "..", "..", "paper", "figs_companion5"); os.makedirs(OUT, exist_ok=True)
C1, C2, C3, C4, C5, C6 = "#1f4e79", "#c55a11", "#2e7d32", "#7b1fa2", "#616161", "#b8860b"

fig, ax = plt.subplots(2, 3, figsize=(13.2, 7.4))
# (a) A: relative FCC-BCC gap vs parameter
A = json.load(open(f"{R}/three_d/AB/A_summary.json"))["rows"]
for kern, col, lab in (("gauss", C1, r"Gaussian $e^{-ar^2}$"), ("yukawa", C2, r"Yukawa $e^{-kr}/r$")):
    rows = [r for r in A if r["kernel"] == kern]
    p = np.array([r["param"] for r in rows]); g = np.array([(r["E_BCC"] - r["E_FCC"]) / abs(r["E_FCC"]) for r in rows])
    ax[0, 0].plot(p, g, "o-", color=col, label=lab, ms=4)
ax[0, 0].axhline(0, color="k", lw=0.6); ax[0, 0].axvline(np.pi, color=C1, ls=":", lw=0.8); ax[0, 0].axvline(1.7179, color=C2, ls=":", lw=0.8)
ax[0, 0].set_xscale("log"); ax[0, 0].set_yscale("symlog", linthresh=1e-9)
ax[0, 0].set_xlabel("kernel parameter ($a$ or $k$)"); ax[0, 0].set_ylabel(r"$(E_{\rm BCC}-E_{\rm FCC})/|E_{\rm FCC}|$")
ax[0, 0].set_title("(a) A: Bravais winner; crossovers $a^*=\\pi$, $k^*=1.718$", fontsize=10); ax[0, 0].legend(fontsize=8)

# (b) Bain path at alpha = pi, 2.5, 4 (recomputed, same code as AB/bain_selfdual.py)
def bct(t):
    a = (2 / t) ** (1 / 3); c = t * a
    return np.array([[a, 0, 0], [0, a, 0], [a / 2, a / 2, c / 2]])
def theta(B, alpha, Rc=9.0):
    n = int(Rc / np.min(np.linalg.norm(B, axis=1))) + 2; rng = np.arange(-n, n + 1)
    I = np.array(list(itertools.product(rng, rng, rng))); V = I @ B; r2 = (V ** 2).sum(1); r2 = r2[r2 > 1e-12]
    return np.exp(-alpha * r2[r2 < Rc * Rc]).sum()
ts = np.linspace(1, np.sqrt(2), 61)
for alpha, col in ((np.pi, C1), (4.0, C3)):
    v = np.array([theta(bct(t), alpha) for t in ts]); ax[0, 1].plot(ts, (v - v.min()) / v.min(), color=col, label=fr"$\alpha={alpha:.4g}$")
ax[0, 1].axvline(2 ** 0.25, color=C5, ls="--", lw=0.8); ax[0, 1].text(2 ** 0.25, ax[0, 1].get_ylim()[1] * 0.9, " isodual", fontsize=8, color=C5)
ax[0, 1].set_xticks([1, 2 ** 0.25, np.sqrt(2)]); ax[0, 1].set_xticklabels(["BCC\n$t=1$", "$2^{1/4}$", "FCC\n$t=\\sqrt{2}$"])
ax[0, 1].set_ylabel("relative energy above the path minimum"); ax[0, 1].set_title("(b) Bain path: the self-dual lattice is the maximum at $\\alpha=\\pi$", fontsize=10); ax[0, 1].legend(fontsize=8)

# (c) C: success at N=120 (600-cell) and N=24 (24-cell energy)
recs = [json.loads(l) for l in open(f"{R}/three_d/C/records.jsonl")]
refs = json.load(open(f"{R}/three_d/C/reference.json"))["refs"]
kern = ["gauss0.5", "gauss1", "gauss2", "gauss4", "coulomb", "log"]
def frac(N, key):
    out = []
    for k in kern:
        E = np.array([r["E"] for r in recs if r["N"] == N and r["kernel"] == k]); ref = refs[k][key]
        out.append(np.mean(np.abs(E - ref) <= 1e-8 * abs(ref)))
    return np.array(out)
x = np.arange(len(kern)); w = 0.38
ax[0, 2].bar(x - w / 2, frac(120, "E600"), w, color=C1, label="N=120: reach 600-cell (proved optimum)")
ax[0, 2].bar(x + w / 2, frac(24, "E24"), w, color=C2, label="N=24: reach 24-cell energy")
ax[0, 2].axhline(0.9, color="k", ls="--", lw=0.8); ax[0, 2].set_xticks(x); ax[0, 2].set_xticklabels(["g0.5", "g1", "g2", "g4", "Coul", "log"])
ax[0, 2].set_ylabel("fraction of 50 starts"); ax[0, 2].set_title("(c) C: local optimiser on $S^3$ (dashed: gate 0.9)", fontsize=10); ax[0, 2].legend(fontsize=7, loc="upper right")

# (d) C: frustration scan, fraction of starts at the lowest minimum vs N
Ns = sorted({r["N"] for r in recs if r["N"] <= 48})
for k, col in zip(kern, (C1, C2, C3, C4, C5, C6)):
    f = []
    for N in Ns:
        E = np.array([r["E"] for r in recs if r["N"] == N and r["kernel"] == k]); f.append(np.mean(np.abs(E - E.min()) <= 1e-8 * abs(E.min())))
    ax[1, 0].plot(Ns, f, "o-", ms=3, color=col, label=k)
ax[1, 0].set_xlabel("$N$ on $S^3$"); ax[1, 0].set_ylabel("fraction of starts at the lowest minimum"); ax[1, 0].set_title("(d) C: frustration grows and is non-monotone in $N$", fontsize=10); ax[1, 0].legend(fontsize=7, ncol=2)

# (e) D: paired differences of rho_p5 vs the CVT arms
D = json.load(open(f"{R}/three_d/D/summary_d.json"))["paired"]
arms = [("hybrid_vs_cvt20_all", "CVT 20 it."), ("hybrid_vs_cvt40_all", "CVT 40 it.\n(E3 protocol)"), ("hybrid_vs_cvt80_all", "CVT 80 it.\n(cost-matched)")]
m = [D[a]["mean_diff"] for a, _ in arms]; s = [D[a]["se"] for a, _ in arms]
ax[1, 1].bar(range(3), m, yerr=s, color=[C3, C3, C2], capsize=4); ax[1, 1].axhline(0, color="k", lw=0.6)
for i, (a, _) in enumerate(arms): ax[1, 1].text(i, m[i] + (s[i] + 0.004) * np.sign(m[i] or 1), f"wins {D[a]['wins']}/30", ha="center", fontsize=8)
ax[1, 1].set_xticks(range(3)); ax[1, 1].set_xticklabels([l for _, l in arms], fontsize=8); ax[1, 1].set_ylabel(r"$\rho_{p5}$(hybrid) $-$ $\rho_{p5}$(CVT), paired, $\pm$1 s.e.")
ax[1, 1].set_title("(e) D: CM+CVT hybrid vs CVT alone (30 seeds)", fontsize=10)

# (f) L3: wall-spacing scan R(w) and sliding-wall deltas
L = json.load(open(f"{R}/rust/fenris-gated/results_L3/l3_summary.json"))
ws = sorted([k for k in L["g1"] if k.replace(".", "", 1).isdigit()], key=float); Rw = [L["g1"][w]["R"] for w in ws]; ci = np.array([L["g1"][w]["R_ci"] for w in ws]); esc = [L["g1"][w]["n_escaped"] for w in ws]
axf = ax[1, 2]; axf.errorbar([float(w) for w in ws], Rw, yerr=[np.array(Rw) - ci[:, 0], ci[:, 1] - np.array(Rw)], fmt="o-", color=C1, capsize=3, label="defect concentration $R(w)$ (G1)")
for w, r, e in zip(ws, Rw, esc): axf.text(float(w), r + 0.04, f"esc {e}/288", ha="center", fontsize=7)
axf.axhline(1.5, color="k", ls="--", lw=0.8); axf.set_xlabel("wall spacing $w$ (mean node spacing)"); axf.set_ylabel("$R(w)$")
ax2 = axf.twinx(); shapes = ["square", "hexagon", "disc", "rect2", "lshape", "annulus"]
for key, col, lab in (("ungated:0.5", C2, "G2 ungated"), ("gated:0.5:1.5", C4, "G2 gated")):
    g = L["g2"].get(key) or L["g2"].get(next(k for k in L["g2"] if k.startswith(key.split(":")[0])))
    d = [g["shapes"][sname]["all"]["mean_delta"] if sname in g["shapes"] else np.nan for sname in shapes]
    e = [g["shapes"][sname]["all"]["se"] if sname in g["shapes"] else np.nan for sname in shapes]
    ax2.errorbar(0.52 + 0.14 * np.arange(6) + (0.03 if "gated:" in key else 0), d, yerr=e, fmt="s" if "un" in key else "^", ms=4, color=col, capsize=2, ls="none", label=lab)
ax2.axhline(-2, color=C2, ls=":", lw=0.8); ax2.set_ylabel(r"$\Delta$(non-6 nodes), sliding $-$ fixed (G2; gate $-2$)"); ax2.set_ylim(-2.4, 0.8)
axf.set_title("(f) L3: wall spacing (left axis) and sliding walls (right axis)", fontsize=10)
h1, l1 = axf.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); axf.legend(h1 + h2, l1 + l2, fontsize=7, loc="lower left")
plt.tight_layout()
for ext in ("pdf", "png"): plt.savefig(f"{OUT}/fig_round1.{ext}", dpi=160)
print("ok", OUT)
