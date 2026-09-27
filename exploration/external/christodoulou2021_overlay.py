#!/usr/bin/env python3
"""P6 of paper/sector_temperature.tex: overlay the round-2 classical-field stiffness n_s lambda^2 (L=64 ladder, L=32 box)
against the measured superfluid phase-space density D_s of Christodoulou et al., Nature 594, 191 (2021) (Apollo
10.17863/CAM.66056, CC BY 4.0), using the scale-invariant identification D/D_c = T_BKT/T at fixed density.
No free parameter. Prediction fixed before reading: |D_s(last point at D/D_c ~ 1) - 4| <= 1.5, and overlay within 25 %."""
import json
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
exp = np.loadtxt(ROOT / "data/external/christodoulou2021_apollo_CAM66056/unpacked/Figure 3/Fig3b_superfluid_density.txt", skiprows=1)
x_e, dx_e, y_e, dy_e = exp.T
V = json.loads((ROOT / "data/generated/pgpe/r2_verdicts.json").read_text())
Tb64 = V["II"]["crossing"]["T_BKT"]; Tb32 = V["III"]["crossing_L32"]["T_BKT"]
ours = []
for part, Tb, lab in (("II", Tb64, "L=64 ladder"), ("III", Tb32, "L=32")):
    for r in V[part]["rows"]:
        ours.append((Tb / r["T"], r["K"], lab))
ours.sort()
xo = np.array([o[0] for o in ours]); yo = np.array([o[1] for o in ours])
# P6 part 1
near = [(x, y, dy) for x, y, dy in zip(x_e, y_e, dy_e) if 0.95 <= x <= 1.05 and y > 0]
p1 = all(abs(y - 4) <= 1.5 for _, y, _ in near)
# P6 part 2: our curve interpolated (log-linear in x) at each experimental superfluid point within our range
rows = []
for x, y, dy in zip(x_e, y_e, dy_e):
    if y <= 0 or not (xo.min() <= x <= xo.max()):
        continue
    yi = float(np.interp(x, xo, yo)); rows.append((x, y, dy, yi, abs(yi - y) / y))
p2 = all(r[4] <= 0.25 for r in rows)
print("T_BKT(64)=%.3f T_BKT(32)=%.3f" % (Tb64, Tb32))
print("P6 part 1 (|D_s - 4| <= 1.5 at D/D_c in [0.95,1.05]):", [(round(x, 3), round(y, 2)) for x, y, _ in near], "->", "PASS" if p1 else "FAIL")
print("P6 part 2 (overlay within 25 %):")
for x, y, dy, yi, rel in rows:
    print(f"   D/Dc={x:.3f}  exp D_s={y:.2f}±{dy:.2f}  ours={yi:.2f}  rel dev={rel*100:.1f} %")
print("->", "PASS" if p2 else "FAIL", " max dev %.1f %%" % (100 * max(r[4] for r in rows)))
json.dump({"T_BKT_64": Tb64, "T_BKT_32": Tb32, "P6_part1": p1, "near_Dc": near, "P6_part2": p2, "overlay": rows},
          open(ROOT / "data/generated/external_christodoulou2021_overlay.json", "w"), indent=1)
fig, ax = plt.subplots(figsize=(5.5, 4))
ax.errorbar(x_e, y_e, xerr=dx_e, yerr=dy_e, fmt="o", color="#4d4d4d", label="Christodoulou et al. 2021 ($\\tilde g=0.64$)")
for lab, mk, col in (("L=64 ladder", "o", "#b2182b"), ("L=32", "s", "#2166ac")):
    xs = [o[0] for o in ours if o[2] == lab]; ys = [o[1] for o in ours if o[2] == lab]
    ax.plot(xs, ys, "-" + mk, ms=4, color=col, label=f"this work, PGPE $g=1$, {lab}")
ax.axhline(4, ls="--", color="0.6", lw=0.8); ax.axvline(1, ls=":", color="0.6", lw=0.8)
ax.set_xlabel("$D/D_c$  (ours: $T_{BKT}/T$)"); ax.set_ylabel("$D_s = n_s\\lambda_T^2$"); ax.set_xlim(0.6, 2.05); ax.set_ylim(-0.5, 13)
ax.legend(frameon=False, fontsize=8); fig.tight_layout()
out = ROOT / "paper/figures/christodoulou_overlay.pdf"; fig.savefig(out); print("wrote", out)
