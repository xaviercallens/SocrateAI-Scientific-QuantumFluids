"""Solutions to the exercises of Chapter 3 (Appendix C): every computed number of chapters/sol03.tex except the two engine runs,
which sol03_run.py makes (figures/sol03_runs.json, read here).  Writes figures/sol03_numbers.json.
  .venv/bin/python book/figures/sol03_numbers.py        (about a minute: line integrals of the zero-mean-flow field)

Exercise 1  principal differences of n samples of the phase theta(phi) = phi, both senses, every starting angle on a grid,
            in EXACT arithmetic (angles as fractions of pi: a step of exactly pi is the point, and floating point cannot hold it).
Exercise 2  (a) ubar/(hbar/md) = 2 pi d^2/L^2; (b) the row and column circulations of the zero-mean-flow field of a pair,
            computed by quadrature of the chapter's Weiss-McWilliams field (ch03_pv.wm_velocity), against -kappa d/L and
            kappa (L - d)/L; (c) the pair with + below -: direction and speed from ch03_pv.vortex_velocity.
Exercise 3  predictions for L = 64 and 96 (zero-mean field, uniform flow), the leading-order law v_0 = 1/d - pi d/L^2 checked
            against the exact sum for growing L, and the measured speeds of sol03_runs.json.
"""
import json, math, sys
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch03_pv as PV                                             # noqa: E402

R = {"script": "book/figures/sol03_numbers.py"}
KAPPA = 2 * math.pi

# ------------------------------------------------------------------------------------------------ Exercise 1
def pdiff_pi(a: Fr, b: Fr) -> Fr:
    """VortexWinding.pdiff in units of pi, exactly: the representative of b - a in (-1, 1]."""
    d = b - a
    while d <= -1:
        d += 2
    while d > 1:
        d -= 2
    return d


def loop_sum(n: int, start: Fr, sense: int) -> Fr:
    """sum of principal differences (units of 2 pi) of n samples phi_i = start + sense*2i/n (units of pi) of theta = phi, closed."""
    th = [start + sense * Fr(2 * i, n) for i in range(n)] + [start + sense * 2]
    return sum(pdiff_pi(th[i], th[i + 1]) for i in range(n)) / 2


starts = [Fr(j, 48) for j in range(-48, 48)]                    # 96 starting angles, multiples of pi/48, on (-pi, pi]
ex1 = {"n2_start0": {"ccw_steps_over_pi": [str(pdiff_pi(Fr(0), Fr(1))), str(pdiff_pi(Fr(1), Fr(2)))],
                     "cw_steps_over_pi": [str(pdiff_pi(Fr(0), Fr(-1))), str(pdiff_pi(Fr(-1), Fr(-2)))],
                     "ccw_sum_over_2pi": str(loop_sum(2, Fr(0), +1)), "cw_sum_over_2pi": str(loop_sum(2, Fr(0), -1))}}
table = []
for n in range(1, 7):
    ccw = {str(loop_sum(n, a, +1)) for a in starts}
    cw = {str(loop_sum(n, a, -1)) for a in starts}
    table.append(dict(n=n, ccw_values=sorted(ccw), cw_values=sorted(cw), right_both_senses=(ccw == {"1"} and cw == {"-1"})))
ex1["n_scan_96_starting_angles"] = table
ex1["least_n_right_in_both_senses"] = min(r["n"] for r in table if r["right_both_senses"])
R["exercise1"] = ex1

# ------------------------------------------------------------------------------------------------ Exercise 2
L = 64.0
ex2 = {"a": [dict(d=d, ubar_over_plane=2 * math.pi * d * d / L ** 2) for d in (6.0, 12.0, 16.0)]}
ex2["a_at_measured_d_11.8"] = 2 * math.pi * 11.8 ** 2 / L ** 2       # the keybox's 21 % (scanTwelveD = 11.8)
# (b) circulations of the zero-mean-flow field (no uniform flow) of + at (x1, y), - at (x2, y)
x1, x2, y0 = 26.13, 38.13, 30.71                                # the chapter's showcase imprint, d = 12
pos = np.array([[x1, y0], [x2, y0]]); q = np.array([1.0, -1.0]); d = x2 - x1
ng = 4096
s = (np.arange(ng) + 0.5) * L / ng                             # midpoint rule on a periodic line: spectrally accurate for smooth integrands


def column_circ(xc):
    pts = np.column_stack([np.full(ng, xc), s])
    return float(PV.wm_velocity(pts, pos, q, L)[:, 1].sum() * L / ng)


def row_circ(yc):
    pts = np.column_stack([s, np.full(ng, yc)])
    return float(PV.wm_velocity(pts, pos, q, L)[:, 0].sum() * L / ng)


cols = {f"x={xc}": column_circ(xc) for xc in (5.0, 20.0, 30.0, 32.0, 36.0, 50.0, 60.0)}
rows = {f"y={yc}": row_circ(yc) for yc in (5.0, 20.0, 40.0, 60.0)}
ex2["b"] = dict(x1=x1, x2=x2, y=y0, d=d, column_circulation_over_kappa=cols and {k: v / KAPPA for k, v in cols.items()},
                row_circulation_over_kappa={k: v / KAPPA for k, v in rows.items()},
                predicted_outside=-d / L, predicted_inside=(L - d) / L,
                ubar_needed=[0.0, KAPPA * d / L ** 2], ubar_formula=PV.sector_flow(pos, q, L).tolist())
# (c) + below -, same x; and the original orientation, same d
for tag, P0 in (("plus_left", np.array([[26.0, 32.0], [38.0, 32.0]])), ("plus_below", np.array([[32.0, 26.0], [32.0, 38.0]]))):
    v0 = PV.vortex_velocity(P0, q, with_sector=False, L=L)
    v1 = PV.vortex_velocity(P0, q, with_sector=True, L=L)
    ex2.setdefault("c", {})[tag] = dict(pos=P0.tolist(), v_zero_mean=v0.tolist(), v_with_uniform_flow=v1.tolist(),
                                       uniform_flow=PV.sector_flow(P0, q, L).tolist(), speed=float(np.hypot(*v1[0])))
R["exercise2"] = ex2

# ------------------------------------------------------------------------------------------------ Exercise 3
def v_zero_mean(dd, LL):
    P0 = np.array([[LL / 2 - dd / 2, LL / 2], [LL / 2 + dd / 2, LL / 2]])
    return float(PV.vortex_velocity(P0, q, with_sector=False, L=LL)[0, 1])


lead = []
for LL in (48.0, 64.0, 96.0, 128.0, 256.0, 512.0):
    v0 = v_zero_mean(12.0, LL)
    lead.append(dict(L=LL, v_zero_mean=v0, image_correction=v0 - 1 / 12.0, leading_order=-math.pi * 12.0 / LL ** 2,
                     ratio_to_leading=(v0 - 1 / 12.0) / (-math.pi * 12.0 / LL ** 2), uniform_flow=KAPPA * 12.0 / LL ** 2,
                     box_speed=v0 + KAPPA * 12.0 / LL ** 2, box_excess_over_plane=v0 + KAPPA * 12.0 / LL ** 2 - 1 / 12.0))
ex3 = {"d12_by_L": lead}
runs = HERE / "sol03_runs.json"
if runs.exists():
    rr = json.loads(runs.read_text())["runs"]
    for tag, r in rr.items():
        vm = float(np.hypot(*r["v_meas"])); v1 = float(np.hypot(*r["v_pv_with_sector_flow"])); v0 = float(np.hypot(*r["v_pv_zero_mean_flow"]))
        ex3[tag] = dict(L=r["L"], N=r["N"], d_mean=r["d_mean"], v_meas=vm, v_halves=r["v_meas_y_halves"], v_plane=r["v_plane"],
                        v_zero_mean=v0, v_pred=v1, sector_flow=float(np.hypot(*r["sector_flow"])), ratio_meas_pred=vm / v1,
                        ratio_meas_zero_mean=vm / v0, excess_meas_over_plane=vm - r["v_plane"], excess_pred_over_plane=v1 - r["v_plane"],
                        leading_order_excess=math.pi * r["d_mean"] / r["L"] ** 2, wall_s=r["wall_s"], load=r["load_at_start"],
                        drifts=[r["energy_rel_drift"], r["norm_rel_drift"], r["momentum_y_rel_drift"]])
    if "L64" in ex3 and "L96" in ex3:
        a, b = ex3["L64"], ex3["L96"]
        ex3["change_64_to_96"] = dict(meas=a["v_meas"] - b["v_meas"], pred=a["v_pred"] - b["v_pred"],
                                      plane=a["v_plane"] - b["v_plane"], uniform_flow=a["sector_flow"] - b["sector_flow"],
                                      zero_mean=a["v_zero_mean"] - b["v_zero_mean"],
                                      excess_ratio_meas=b["excess_meas_over_plane"] / a["excess_meas_over_plane"],
                                      excess_ratio_pred=b["excess_pred_over_plane"] / a["excess_pred_over_plane"], four_ninths=4 / 9)
ch = json.loads((HERE / "ch03_numbers.json").read_text())
ex3["chapter_exercise3"] = ch.get("exercise3")
R["exercise3"] = ex3
(HERE / "sol03_numbers.json").write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1)[:7000])
