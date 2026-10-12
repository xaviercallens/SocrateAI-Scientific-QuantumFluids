#!/usr/bin/env python3
"""Round-2 figure of paper V (F1 homotopy, T1 detector/surrogate, H1 sanity gate). Reads only committed records:
three_d/F1/records_N{120,24}.jsonl, three_d/C/records.jsonl, three_d/T12/{T1_records,T1_basin,T1_controls}.json*, three_d/H1/run.log.
Writes paper/figs_companion5/fig_round2.{pdf,png}. Palette: reference categorical slots 1-3 (validated: CVD dE 9.2; the third
slot is below 3:1 contrast, so every series also carries a marker shape and a legend entry)."""
import json, os, re, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(R, "..", "..", "paper", "figs_companion5"); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, f"{R}/three_d/C")
import run_C as RC
B, O, A = "#2a78d6", "#eb6834", "#1baf7a"
INK2, GRID = "#52514e", "#e4e3df"
plt.rcParams.update({"axes.edgecolor": INK2, "axes.labelcolor": "#0b0b0b", "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})

load = lambda p: [json.loads(l) for l in open(p)]
F120, F24 = load(f"{R}/three_d/F1/records_N120.jsonl"), load(f"{R}/three_d/F1/records_N24.jsonl")
CR = load(f"{R}/three_d/C/records.jsonl")
C6, C24 = RC.cell600(), RC.cell24()
E6 = lambda a: RC.energy(C6, "g", a)

fig, ax = plt.subplots(2, 2, figsize=(11.0, 7.6))

# (a) F1: relative energy excess over E_600(a) along the ladders; C's plain endpoints at the same a
byA = {}
for r in F120:
    for rg in r["homotopy"]["rungs"]:
        byA.setdefault(rg["a"], []).append(rg["E"])
aa = np.array(sorted(byA)); ex = [np.array(byA[a]) / E6(a) - 1 for a in aa]
med = np.array([np.median(e) for e in ex]); lo = np.array([e.min() for e in ex]); hi = np.array([e.max() for e in ex])
ax[0, 0].fill_between(aa, lo, hi, color=B, alpha=0.18, lw=0)
ax[0, 0].plot(aa, med, "-o", color=B, ms=4, lw=2, label=f"homotopy ladders, median and range ({len(F120)} ladders)")
for a, k in ((1.0, "gauss1"), (2.0, "gauss2"), (4.0, "gauss4")):
    e = np.array([c["E"] for c in CR if c["N"] == 120 and c["kernel"] == k]) / E6(a) - 1
    e = np.maximum(e, 1e-13)
    ax[0, 0].plot(a * np.exp(0.04 * np.random.default_rng(0).normal(size=e.size)), e, "s", color=O, ms=4, alpha=0.6,
                  label="C plain L-BFGS endpoints (50 per $a$; at 600-cell drawn at $10^{-13}$)" if a == 1.0 else None)
ax[0, 0].axhline(1e-8, color=INK2, ls="--", lw=0.8); ax[0, 0].text(0.26, 1.4e-8, "F1a tolerance $10^{-8}$", fontsize=8, color=INK2)
ax[0, 0].set_xscale("log"); ax[0, 0].set_yscale("log"); ax[0, 0].set_xticks([0.25, 0.5, 1, 2, 4]); ax[0, 0].set_xticklabels(["0.25", "0.5", "1", "2", "4"]); ax[0, 0].minorticks_off(); ax[0, 0].set_ylim(5e-14, 5e-2)
ax[0, 0].set_xlabel("kernel stiffness $a$ (rungs $0.25\\cdot2^{k/4}$)"); ax[0, 0].set_ylabel("$E/E_{600}(a)-1$")
ax[0, 0].set_title("(a) F1, $N=120$: the ladder follows a non-600-cell branch", fontsize=10); ax[0, 0].legend(fontsize=7.5, loc="upper left")

# (b) F1: success fractions, homotopy vs plain at equal compute vs C plain, N = 24 and N = 120
TOL = 1e-8
def frac(recs, key, Eref, chord=None):
    n = len(recs)
    return sum(abs(r[key]["E"] - Eref) / Eref <= TOL for r in recs) / n if n else np.nan
groups, vals = [], {"homotopy": [], "plain, equal compute": [], "C plain": []}
for N, recs, cell, kmap in ((24, F24, C24, None), (120, F120, C6, None)):
    for a, k in ((1.0, "gauss1"), (2.0, "gauss2"), (4.0, "gauss4")):
        rs = [r for r in recs if r["a_target"] == a]; Eref = RC.energy(cell, "g", a)
        seeds = {r["start"] for r in rs}
        cr = [c for c in CR if c["N"] == N and c["kernel"] == k and c["start"] in seeds]
        groups.append(f"N={N}\na={a:g}\n({len(rs)} seeds)")
        vals["homotopy"].append(frac(rs, "homotopy", Eref)); vals["plain, equal compute"].append(frac(rs, "plain_equal_compute", Eref))
        vals["C plain"].append(sum(abs(c["E"] - Eref) / Eref <= TOL for c in cr) / len(cr))
x = np.arange(len(groups)); w = 0.26
for i, (lab, col, hatch) in enumerate((("homotopy", B, None), ("plain, equal compute", O, "//"), ("C plain", A, ".."))):
    ax[0, 1].bar(x + (i - 1) * w, np.maximum(vals[lab], 0.004), w * 0.9, color=col, hatch=hatch, edgecolor="white", lw=0.5, label=lab)
ax[0, 1].axhline(0.9, color=INK2, ls="--", lw=0.8); ax[0, 1].text(3.55, 0.92, "gate F1a: 45/50", fontsize=8, color=INK2)
ax[0, 1].set_xticks(x); ax[0, 1].set_xticklabels(groups, fontsize=8); ax[0, 1].set_ylim(0, 1.08)
ax[0, 1].set_ylabel("fraction of seeds at the target energy ($10^{-8}$)")
ax[0, 1].set_title("(b) F1: homotopy helps for the 24-cell, not the 600-cell", fontsize=10); ax[0, 1].legend(fontsize=7.5, loc="upper left", bbox_to_anchor=(0.5, 0.82))

# (c) T1: surrogate value vs registered shell mismatch
T1 = load(f"{R}/three_d/T12/T1_records.jsonl"); BA = load(f"{R}/three_d/T12/T1_basin.jsonl")
CT = json.load(open(f"{R}/three_d/T12/T1_controls.json"))
for N, mk in ((2, "o"), (4, "^"), (8, "D")):
    rs = [r for r in T1 if r["N"] == N]
    ax[1, 0].plot([r["M"] for r in rs], [r["shell_mismatch"] for r in rs], mk, color=B, ms=4, alpha=0.6, mfc="none",
                  label=f"random starts, $N={N}$")
for st, mk in (("diamond", "s"), ("SC_2pt", "P")):
    rs = [r for r in BA if r["start"] == st]
    ax[1, 0].plot([r["M"] for r in rs], [r["shell_mismatch"] for r in rs], mk, color=O, ms=5, alpha=0.8,
                  label=f"perturbed {'diamond' if st == 'diamond' else 'SC (2-point cell)'}, $\\varepsilon\\in[10^{{-3}},0.2]$")
pos = [c for c in CT if c.get("surrogate_M") is not None and c["shell_mismatch"] < 1e-20]
ax[1, 0].plot([max(c["surrogate_M"], 1e-30) for c in pos], [max(c["shell_mismatch"], 1e-28) for c in pos], "*", color=A, ms=10,
              label="exact self-dual controls (diamond, SC, isodual bct)")
ax[1, 0].axhline(1e-10, color=INK2, ls="--", lw=0.8); ax[1, 0].text(1e-29, 3e-10, "acceptance $10^{-10}$", fontsize=8, color=INK2)
ax[1, 0].set_xscale("log"); ax[1, 0].set_yscale("log")
ax[1, 0].set_xlabel("surrogate $M$ (Gaussian-family identity, 40 exponents)"); ax[1, 0].set_ylabel("registered 40-shell mismatch")
ax[1, 0].set_title("(c) T1: $M\\approx0$ does not imply self-duality", fontsize=10); ax[1, 0].legend(fontsize=7, loc="center right")

# (d) H1 sanity gate in d = 1: LP value minus E_Z vs beta, admissible or not
log = open(f"{R}/three_d/H1/run.log").read()
EZ = {"d1_alpha1": 0.7726372048266521, "d1_alpha3.14159": 0.08643481121330804}
for tag, col, mk, lab in (("d1_alpha1", B, "o", "$\\alpha=1$"), ("d1_alpha3.14159", O, "s", "$\\alpha=\\pi$")):
    for stage, ms in (("coarse", 4), ("full", 7)):
        pts = re.findall(rf"\[{re.escape(tag)}\] {stage} beta=([\d.]+) \(x([\d.]+)\) bound=([\d.eE+-]+) admissible=(\w+)", log)
        if stage == "full":
            pts = [p for p in pts]
        xs = np.array([float(p[1]) for p in pts]); ys = np.array([float(p[2]) - EZ[tag] for p in pts]) / EZ[tag]
        ok = np.array([p[3] == "True" for p in pts])
        if stage == "coarse":
            ax[1, 1].plot(xs, ys, mk, color=col, ms=ms, mfc="none", label=f"{lab}, coarse scan")
        else:
            if ok.any():  # no empty legend entries
                ax[1, 1].plot(xs[ok], ys[ok], mk, color=col, ms=ms, label=f"{lab}, full, admissible")
            if (~ok).any():
                ax[1, 1].plot(xs[~ok], ys[~ok], "x", color=col, ms=ms, mew=2, label=f"{lab}, full, NOT admissible")
ax[1, 1].axhline(0, color=INK2, lw=0.8); ax[1, 1].axhspan(-1e-8, 1e-8, color=GRID, alpha=0.7, lw=0)
ax[1, 1].text(2.1, 3e-9, "H0 window $\\pm10^{-8}$", fontsize=8, color=INK2)
ax[1, 1].set_yscale("symlog", linthresh=1e-10); ax[1, 1].set_xscale("log"); ax[1, 1].set_xticks([0.35, 0.5, 0.7, 1, 1.5, 2, 3]); ax[1, 1].set_xticklabels(["0.35", "0.5", "0.7", "1", "1.5", "2", "3"]); ax[1, 1].minorticks_off()
ax[1, 1].set_xlabel("$\\beta/(\\alpha/\\pi)$"); ax[1, 1].set_ylabel("(LP value $-E_{\\mathbf{Z}}$)$/E_{\\mathbf{Z}}$  (valid bound: $\\leq 0$)")
ax[1, 1].set_title("(d) H1 sanity gate H0 ($d=1$): failed at $\\alpha=\\pi$", fontsize=10); ax[1, 1].legend(fontsize=7, loc="lower right", ncol=2)

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(f"{OUT}/fig_round2.{ext}", dpi=170)
print("wrote", OUT)
