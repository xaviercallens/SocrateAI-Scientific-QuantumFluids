"""Figure ch03_pairspeed: the speed of a vortex pair in the periodic box against its separation d (six solver runs, 40 time units each).
(a) v d / (hbar/m): plane-wave law (=1), point vortices on the torus with zero mean flow, the same plus the uniform flow fixed by the winding
integers of the torus, and the measurements; (b) ratio of the measured speed to each of the three predictions.
Data: ch03_numbers.json (ch03_compute.py, part `scan`); the curves are computed here with ch03_pv.py."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
import ch03_pv as PV
HERE = Path(__file__).resolve().parent
J = json.loads((HERE / "ch03_numbers.json").read_text())["scan"]["rows"]
d = np.array([r["d_mean"] for r in J]); vm = np.array([r["v_meas"] for r in J])
fig, (axa, axb) = plt.subplots(1, 2, figsize=(TEXTW, 2.4), gridspec_kw=dict(wspace=0.32, left=0.085, right=0.985, top=0.955, bottom=0.185))
dd = np.linspace(3.0, 23.0, 81); q = np.array([1, -1])
xc, yc = 32.13, 30.71
v0 = np.zeros_like(dd); v1 = np.zeros_like(dd)
for i, di in enumerate(dd):
    pos = np.array([[xc - di / 2, yc], [xc + di / 2, yc]])
    v0[i] = np.hypot(*PV.vortex_velocity(pos, q, with_sector=False).mean(0)); v1[i] = np.hypot(*PV.vortex_velocity(pos, q, with_sector=True).mean(0))
axa.axhline(1.0, color=GREY, lw=0.9, ls=":", label=r"plane: $v=\hbar/(md)$")
axa.plot(dd, v0 * dd, "-", color=ORANGE, lw=1.3, label="torus, zero mean flow")
axa.plot(dd, v1 * dd, "-", color=BLUE, lw=1.3, label="torus + flow fixed by the windings")
axa.plot(d, vm * d, "o", ms=4.6, color="#111111", label="solver (qf-pgpe)")
axa.set_xlabel(r"separation $d/\xi$"); axa.set_ylabel(r"$v\,d\;/\;(\hbar/m)$")
axa.set_xlim(2.5, 23); axa.set_ylim(0.55, 1.9)
axa.legend(loc="upper left", fontsize=6.8, handlelength=1.4, borderaxespad=0.2)
panel(axa, "a")
r_pl = np.array([r["ratio_to_plane"] for r in J]); r_p0 = np.array([r["ratio_to_pv_zero_mean"] for r in J]); r_p1 = np.array([r["ratio_to_pv_with_sector"] for r in J])
axb.axhspan(0.99, 1.01, color=BLUE, alpha=0.12, lw=0)
axb.axhline(1.0, color=GREY, lw=0.7)
axb.plot(d, r_pl, "s", ms=3.8, mfc="none", mec=GREY, label="measured / plane law")
axb.plot(d, r_p0, "^", ms=4.2, mfc="none", mec=ORANGE, label="measured / torus, zero mean flow")
axb.plot(d, r_p1, "o", ms=4.6, color=BLUE, label="measured / torus + winding flow")
axb.set_xlabel(r"separation $d/\xi$"); axb.set_ylabel("speed ratio")
axb.set_xlim(2.5, 23); axb.set_ylim(0.95, 2.05)
axb.legend(loc="upper left", fontsize=6.8, handlelength=1.2, borderaxespad=0.2)
panel(axb, "b")
save(fig, "ch03_pairspeed")
