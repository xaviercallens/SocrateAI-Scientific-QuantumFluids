"""Solutions to the exercises of Chapter 1 (Appendix C): every number of chapters/sol01.tex.

Writes figures/sol01_numbers.json.  Run:  .venv/bin/python book/figures/sol01_numbers.py   (a few seconds; no solver run).

Exercise 1  neutron kinematics, inequality (ch01:eq-vmin): k_i >= Q/2 + m eps/(hbar^2 Q), with the exercise's rounded inputs,
            with exact constants, and lambda_max(Q) on the authors' table as Q -> 0 (the limit h/(m_n c)).
Exercise 2  principal differences of the loop (0, pi, 0, pi): the numpy form of VortexWinding.pdiff (same as the
            chapter's snippet), the reversed loop, and four smooth loops through the same samples with windings 2, -2, 0, 1.
Exercise 3  mean superflow of a neutral pair on the torus, 2 pi (n_in d + n_out (L - d)) / L^2, its least magnitude, and an
            independent evaluation of the torus point-vortex speed (closed-form periodic rows of vortices, summed over the
            x-images) that also shows v_box = v_torus + 2 pi d / L^2 in the sector (n_out, n_in) = (0, 1).
            Chapter numbers used (measured speed, P/N, ...) are read from figures/ch01_numbers.json, not recomputed.
"""
import json, math, sys
from pathlib import Path
import numpy as np
import scipy.constants as C

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
OUT = HERE / "sol01_numbers.json"
CH = json.loads((HERE / "ch01_numbers.json").read_text())
R = {"script": "book/figures/sol01_numbers.py", "chapter_numbers_file": "book/figures/ch01_numbers.json"}

# ------------------------------------------------------------------------------------------------ Exercise 1
meV = 1e-3 * C.e
H2M_EXACT = C.hbar ** 2 / (2 * C.m_n) / meV * 1e20          # meV A^2
HBAR_OVER_M = C.hbar / C.m_n * 1e10                          # m/s per A^-1 (v = (hbar/m) k)


def window(Q, eps, h2m):
    """Least incident wave number (A^-1), longest wavelength (A), least energy (meV), least speed (m/s), and the two
    terms of (ch01:eq-vmin) in m/s, for a transfer Q (A^-1) and an energy eps (meV); h2m = hbar^2/2m_n in meV A^2."""
    recoil = Q / 2                                   # A^-1
    price = eps / (2 * h2m * Q)                      # m eps / (hbar^2 Q) = eps / (2 (hbar^2/2m) Q)
    k = recoil + price
    hbar_over_m = 2 * h2m / (C.hbar / meV) * 1e-20   # m^2/s from hbar/m = 2 (hbar^2/2m)/hbar   -> times 1e10 for m/s per A^-1
    v_per_k = hbar_over_m * 1e10
    return dict(Q=Q, eps_meV=eps, hbar2_over_2m=h2m, k_min=k, recoil_term_invA=recoil, price_term_invA=price,
                lam_max_A=2 * math.pi / k, E_i_min_meV=h2m * k ** 2, v_min_ms=v_per_k * k,
                v_recoil_ms=v_per_k * recoil, v_phase_ms=v_per_k * price)


ex1 = {"constants": {"hbar2_over_2m_n_exact_meV_A2": H2M_EXACT, "hbar2_over_2m_n_exercise": 2.072,
                     "hbar_over_m_n_ms_per_invA": HBAR_OVER_M, "h_over_m_n_ms_A": 2 * math.pi * HBAR_OVER_M}}
ex1["roton_rounded"] = window(1.92, 0.741, 2.072)
ex1["roton_exact_constants_table_values"] = window(CH["bench"]["roton"]["Q0"], CH["bench"]["roton"]["eps_meV"], H2M_EXACT)
ex1["Q3_rounded"] = window(3.0, 1.478, 2.072)
ex1["Q3_exact_constants_table_values"] = window(3.0, CH["bench"]["at_Q3"]["eps_meV"], H2M_EXACT)
c_fit = CH["bench"]["sound"]["c_fit_ms"]                      # 238.70 m/s, the chapter's extrapolation of the table
for tag, c in (("c_fit_ch01", c_fit), ("c_ultrasound_paper", 238.3)):
    lam = 2 * math.pi * HBAR_OVER_M / c
    ex1[f"Q_to_0_{tag}"] = dict(c_ms=c, lam_max_A=lam, E_i_min_meV=H2M_EXACT * (2 * math.pi / lam) ** 2)
# lambda_max(Q) on the authors' table for small Q: how the limit is approached
sys.path.insert(0, str(HERE))
from ch05_helium import load_table                            # noqa: E402  (the chapter-5 reader of the same ancillary file)
k_t, e_t, _ = load_table()
rows = []
for Q in (0.02, 0.05, 0.1, 0.2, 0.4):
    j = int(np.argmin(np.abs(k_t - Q)))
    w = window(float(k_t[j]), float(e_t[j]), H2M_EXACT)
    rows.append(dict(Q=w["Q"], eps_meV=w["eps_meV"], v_phase_ms=w["v_phase_ms"], v_recoil_ms=w["v_recoil_ms"],
                     v_min_ms=w["v_min_ms"], lam_max_A=w["lam_max_A"]))
ex1["lam_max_small_Q_from_table"] = rows
# consistency with the chapter (5.97 A, 2.30 meV, 663 m/s; 3.88 A; 16.6 A)
assert abs(ex1["roton_rounded"]["lam_max_A"] - 5.97) < 0.005 and abs(ex1["roton_rounded"]["E_i_min_meV"] - 2.30) < 0.005
assert abs(ex1["Q3_rounded"]["lam_max_A"] - 3.88) < 0.005 and abs(ex1["Q_to_0_c_fit_ch01"]["lam_max_A"] - 16.6) < 0.05
R["exercise1"] = ex1

# ------------------------------------------------------------------------------------------------ Exercise 2
def pdiff(a, b):
    """numpy form of QuantumFluids.VortexWinding.pdiff = toIocMod two_pi_pos (-pi) (b - a): the representative in (-pi, pi]."""
    d = np.asarray(b, float) - np.asarray(a, float)
    return d - 2 * np.pi * np.ceil((d - np.pi) / (2 * np.pi))


th = np.array([0.0, np.pi, 0.0, np.pi, 0.0])                   # theta_0..theta_4, closed
steps = pdiff(th[:-1], th[1:])
rev = th[::-1]
steps_rev = pdiff(rev[:-1], rev[1:])
ex2 = {"theta": th.tolist(), "steps_over_pi": (steps / np.pi).tolist(), "sum_over_2pi": float(steps.sum() / (2 * np.pi)),
       "reversed_steps_over_pi": (steps_rev / np.pi).tolist(), "reversed_sum_over_2pi": float(steps_rev.sum() / (2 * np.pi)),
       "round_trip_per_edge_over_pi": float((pdiff(0.0, np.pi) + pdiff(np.pi, 0.0)) / np.pi)}
# smooth loops phi in [0, 2 pi] whose samples at phi = 0, pi/2, pi, 3pi/2 are (0, pi, 0, pi) modulo 2 pi
loops = {"theta = 2 phi": lambda p: 2 * p,
         "theta = -2 phi": lambda p: -2 * p,
         "theta = pi sin^2 phi": lambda p: np.pi * np.sin(p) ** 2,
         "theta = phi + 3pi/4 - (pi/2)(cos phi + sin phi) - (pi/4) cos 2phi": lambda p: p + 3 * np.pi / 4 - np.pi / 2 * (np.cos(p) + np.sin(p)) - np.pi / 4 * np.cos(2 * p)}
lr = []
for name, f in loops.items():
    s4 = f(np.arange(4) * np.pi / 2)
    s4_mod = np.mod(s4 + 1e-12, 2 * np.pi) - 1e-12
    fine = f(np.linspace(0, 2 * np.pi, 20001))
    w_true = float(np.sum(pdiff(fine[:-1], fine[1:])) / (2 * np.pi))     # fine sampling: every true step << pi
    assert np.allclose(np.cos(s4), np.cos(th[:4])) and np.allclose(np.sin(s4), np.sin(th[:4]), atol=1e-12)
    lr.append(dict(loop=name, samples_mod_2pi_over_pi=(s4_mod / np.pi).round(12).tolist(), winding_fine=round(w_true, 12),
                   detector_on_4_samples=float(np.sum(pdiff(np.r_[s4, f(2 * np.pi)][:-1], np.r_[s4, f(2 * np.pi)][1:])) / (2 * np.pi))))
ex2["smooth_loops_through_the_samples"] = lr
R["exercise2"] = ex2

# ------------------------------------------------------------------------------------------------ Exercise 3
L, d = 64.0, 11.75
ex3 = {"L": L, "d": d, "u_min": 2 * math.pi * d / L ** 2,
       "u_next_sector_magnitude": 2 * math.pi * (L - d) / L ** 2,       # (n_out, n_in) = (-1, 0): |n_out L + d| = L - d
       "table_of_sectors": [dict(n_out=n, n_in=n + 1, mean_vy=2 * math.pi * (n * L + d) / L ** 2) for n in (-2, -1, 0, 1)]}


def row_velocity(z, za, gamma, L):
    """(u, v) at z of the vertical row of point vortices of circulation gamma at za + i j L (j in Z):
    u - i v = gamma/(2 i L) coth(pi (z - za)/L)."""
    w = gamma / (2j * L) / np.tanh(np.pi * (z - za) / L)
    return np.array([w.real, -w.imag])


def self_row_velocity(L, gamma):
    """the vortex's own vertical row without the vortex itself, at the vortex: gamma/(2iL) (coth w - 1/w) -> 0 as w -> 0."""
    return np.array([0.0, 0.0])


def pair_speed_rows(d, L, x1=26.0, y=32.0, imax=60):
    """Velocity of the - vortex (at x1 + d) of a +/- pair (circulations +/- 2 pi) from the + rows at x1 + iL (all i) and the
    - rows at x1 + d + iL (i != 0), summed over -imax..imax (paired rows: the sum converges exponentially)."""
    z2 = complex(x1 + d, y)
    v = self_row_velocity(L, -2 * math.pi).copy()
    for i in range(-imax, imax + 1):
        v += row_velocity(z2, complex(x1 + i * L, y), 2 * math.pi, L)
        if i != 0:
            v += row_velocity(z2, complex(x1 + d + i * L, y), -2 * math.pi, L)
    return v


v_rows = pair_speed_rows(d, L)
from transport_estimators import pv_velocity                     # noqa: E402  the programme's zero-mean-flow (Weiss-McWilliams) field
pos = np.array([[26.0, 32.0], [26.0 + d, 32.0]]); qq = np.array([1, -1])
v_wm = pv_velocity(pos, qq, L)
ex3.update(v_rows_box_sector00=v_rows.tolist(), v_torus_zero_mean_WM=v_wm[1].tolist(),
           v_rows_minus_WM_over_u=float((v_rows[1] - v_wm[1, 1]) / ex3["u_min"]),
           v_plane=1 / d, images_correction=float(v_wm[1, 1] - 1 / d))
# the same at the chapter's mean separation of the fit window t >= 20 (11.7616): the chapter's 0.0757
d20 = CH["budget"]["fits"]["20"]["d_mean"]
pos20 = np.array([[26.0, 32.0], [26.0 + d20, 32.0]])
ex3["at_d_fit20"] = dict(d=d20, v_torus_WM=float(pv_velocity(pos20, qq, L)[1, 1]), v_rows=float(pair_speed_rows(d20, L)[1]),
                         chapter_v_pv_torus=CH["budget"]["fits"]["20"]["v_pv_torus_y"])
# leading-order expansion of the zero-mean torus speed (square box):  v_torus ~ 1/d - pi d / L^2   (derived in sol03)
ex3["leading_order_torus"] = 1 / d - math.pi * d / L ** 2
# chapter's measured and derived numbers, quoted (not recomputed)
b = CH["budget"]
ex3["chapter"] = dict(v_meas=b["fits"]["20"]["v_meas_y"], v_meas_half_range=0.5 * (b["fits"]["10"]["v_meas_y"] - b["fits"]["30"]["v_meas_y"]),
                      v_torus=b["fits"]["20"]["v_pv_torus_y"], u_P_over_N=b["u_mean_flow_P_over_N"], u_from_windings=b["u_from_windings"],
                      x_separation_t10=b["x_separation_t10"], cycle_windings_t10=b["cycle_windings_t10"])
ch = ex3["chapter"]
ex3["meas_minus_torus"] = ch["v_meas"] - ch["v_torus"]
ex3["meas_minus_torus_over_u_min"] = ex3["meas_minus_torus"] / ex3["u_min"]
ex3["pred_torus_plus_u_windings"] = ch["v_torus"] + ch["u_from_windings"]
ex3["rel_dev_meas_vs_torus_plus_u_windings"] = ch["v_meas"] / ex3["pred_torus_plus_u_windings"] - 1
ex3["u_windings_t10_check"] = 2 * math.pi * ch["x_separation_t10"] / L ** 2
R["exercise3"] = ex3

OUT.write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1)[:6000])
