#!/usr/bin/env python3
"""Figures and number macros of paper/qf_pgpe_software.tex, from data on disk.
    .venv/bin/python exploration/pgpe/bench_engines.py single|scaling ...        (data/generated/pgpe/bench/{engines,scaling}.json)
    cargo run --release -p qf-pgpe --example cvode_order > data/generated/pgpe/bench/cvode_order.json
    .venv/bin/python paper/make_figures_software.py   -> paper/figures/sw_*.pdf, paper/sw_numbers.tex"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]; B = ROOT / "data/generated/pgpe/bench"; FIG = ROOT / "paper/figures"; FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "legend.fontsize": 7.5, "figure.dpi": 150})
COL = {"rust": "#b23a2e", "numpy": "#1f5fa8", "scipy-1": "#6aa0d8", "torch-1": "#2a7f4f", "torch-4": "#7fbf9a", "scipy-4": "#9bbbe0"}
LAB = {"rust": "qf-pgpe (Rust, 1 thread)", "numpy": "numpy (pocketfft)", "scipy-1": "scipy.fft (1 worker)", "scipy-4": "scipy.fft (4 workers)", "torch-1": "torch CPU (1 thread)", "torch-4": "torch CPU (4 threads)"}
eng = json.loads((B / "engines.json").read_text()); rows = eng["results"]
by = {}
for r in rows:
    by.setdefault(r["engine"], {})[r["n"]] = r["us_per_step_best"]
Ns = sorted(by["rust"])
nums = {}
LET = {64: "A", 128: "B", 256: "C", 512: "D"}   # TeX control sequences cannot contain digits

# ---- Fig. 1: per-step time and speed-up -----------------------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9))
for e in ("rust", "numpy", "scipy-1", "torch-1", "torch-4"):
    if e in by:
        ax[0].loglog(Ns, [by[e][n] / 1000 for n in Ns], "o-", color=COL[e], ms=3.5, lw=1.1, label=LAB[e])
ax[0].minorticks_off(); ax[0].set_xticks(Ns); ax[0].set_xticklabels([str(n) for n in Ns]); ax[0].set_xlabel(r"grid points per side $N$"); ax[0].set_ylabel("time per IF-RK4 step (ms)"); ax[0].legend(frameon=False, fontsize=7)
base = {"numpy": "numpy", "torch-1": "best Python baseline"}
sp_np = [by["numpy"][n] / by["rust"][n] for n in Ns]
best_py = [min(by[e][n] for e in by if e != "rust" and not e.startswith("rust")) / by["rust"][n] for n in Ns]
ax[1].semilogx(Ns, sp_np, "o-", color=COL["numpy"], ms=3.5, label="vs numpy"); ax[1].semilogx(Ns, best_py, "s-", color=COL["torch-1"], ms=3.5, label="vs the fastest Python engine")
ax[1].axhline(1, color="#666", lw=0.7, ls=":"); ax[1].set_xlabel(r"$N$"); ax[1].set_ylabel("speed-up of qf-pgpe"); ax[1].legend(frameon=False); ax[1].set_ylim(0, max(sp_np) * 1.2)
ax[1].minorticks_off(); ax[1].set_xticks(Ns); ax[1].set_xticklabels([str(n) for n in Ns])
fig.tight_layout(); fig.savefig(FIG / "sw_fig1_performance.pdf"); plt.close(fig)
for n, a, b in zip(Ns, sp_np, best_py):
    nums[f"SpNumpy{LET[n]}"] = f"{a:.1f}"; nums[f"SpBest{LET[n]}"] = f"{b:.1f}"; nums[f"RustMs{LET[n]}"] = f"{by['rust'][n] / 1000:.2f}"; nums[f"NumpyMs{LET[n]}"] = f"{by['numpy'][n] / 1000:.2f}"
nums["MaxChecksumDiff"] = f"{max(r['checksum_rel_diff_vs_rust'] for r in rows):.0e}"

# ---- Fig. 2: order against CVODE and the G0 bias --------------------------------------------------------------------------
co = json.loads((B / "cvode_order.json").read_text()); dts = np.array([x[0] for x in co["dt_error"]]); er = np.array([x[1] for x in co["dt_error"]])
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
ax[0].loglog(dts, er, "o-", color=COL["rust"], ms=4, label="IF-RK4 step of qf-pgpe"); ax[0].loglog(dts, er[0] * (dts / dts[0]) ** 4, "k:", lw=0.9, label=r"$\propto\Delta t^4$")
ax[0].set_xlabel(r"time step $\Delta t$"); ax[0].set_ylabel("global error against CVODE (max over modes)"); ax[0].legend(frameon=False)
eta = np.array([0, 5e-4, 1e-3, 2e-3]); aE = np.array([0.0200, 0.0183, 0.0163, 0.0156]) / 0.02; aR = np.array([0.0200, 0.0198, 0.0194, 0.0194]) / 0.02
ax[1].plot(eta * 1e3, aE, "o-", color=COL["rust"], label=r"energy estimator"); ax[1].plot(eta * 1e3, aR, "s-", color=COL["torch-1"], label="regression estimator"); ax[1].axhline(1, color="#666", lw=0.7, ls=":")
ax[1].set_xlabel(r"vortex diffusion $\eta$ ($10^{-3}$)"); ax[1].set_ylabel(r"$\hat\alpha/\alpha_{\rm true}$ (synthetic gate G0)"); ax[1].set_ylim(0.7, 1.05); ax[1].legend(frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(FIG / "sw_fig2_verification.pdf"); plt.close(fig)
nums["CvodeOrder"] = f"{co['fitted_order']:.2f}"; nums["CvodeRhs"] = str(co["cvode_rhs_evals"]); nums["CvodeSteps"] = str(co["cvode_steps"])

# ---- Fig. 3: throughput scaling --------------------------------------------------------------------------------------------
sc = json.loads((B / "scaling.json").read_text())["results"]
fig, ax = plt.subplots(figsize=(3.6, 2.8))
for e, c in (("rust", COL["rust"]), ("numpy", COL["numpy"])):
    pts = sorted((r["procs"], r["steps_per_s"]) for r in sc if r["engine"] == e); ax.plot([p for p, _ in pts], [s for _, s in pts], "o-", color=c, ms=4, label=LAB[e].split(" (")[0])
    nums[f"Thr{e.capitalize()}One"] = f"{pts[0][1]:.0f}"; nums[f"Thr{e.capitalize()}Max"] = f"{max(s for _, s in pts):.0f}"
ax.set_xlabel("concurrent independent runs ($N=128$)"); ax.set_ylabel("aggregate steps per second"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "sw_fig3_throughput.pdf"); plt.close(fig)
thr = {(r["engine"], r["procs"]): r["steps_per_s"] for r in sc}
nums["ThroughputRatio"] = f"{max(v for (e, _), v in thr.items() if e == 'rust') / max(v for (e, _), v in thr.items() if e == 'numpy'):.1f}"
(ROOT / "paper/sw_numbers.tex").write_text("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in nums.items()))
print("figures and sw_numbers.tex written:", nums)
