#!/usr/bin/env python3
"""Chapter 9: every number quoted in the text, recomputed from the raw files, written to figures/ch09_numbers.json.

Inputs (read-only):
  reference  : /mnt/data/xdev-cache/qf-external/20068724/extracted/{psi_time_{0,10,..,50}.npy, force_dt=0.02.txt, vortex.txt}   (Kwon & Shin, Zenodo 10.5281/zenodo.20068724)
  our run    : /mnt/data/xdev-cache/qf-external/ks_rust_t50/{snap/psi_time_{5,..,50}.npy, kwon_shin_force.csv}                     (Rust qf-pgpe::flow, 5000 steps)
  birth run  : /mnt/data/xdev-cache/qf-external/ch09/birth_t20_25.npz   (ch09_birth_run.py: numpy continuation of OUR t = 20 field, every 0.1 tau)
  conventions: /mnt/data/xdev-cache/qf-external/{ks_rust_dt005,ks_st_dt005,ks_st_dt01}/kwon_shin_force.csv   (t <= 5; step-end dt=0.005, stage-times dt=0.005, 0.01)
  fresh run  : $CH09_FRESH (default figures/ch09_fresh_run/run_t1.out)  -- output of the Rust example on t <= 1 made for this chapter (optional)
    nice .venv/bin/python -I book/figures/ch09_numbers.py
"""
import sys, json, os, re
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch09_common as C

XQ = Path("/mnt/data/xdev-cache/qf-external")
OUT = HERE / "ch09_numbers.json"
R = {}                                                   # the result tree
f = lambda a: float(a)

# ------------------------------------------------------------------------------------------------ 1. the dataset (constants of the deposited run)
R["dataset"] = dict(
    grid=[C.NX, C.NY], box_xi=[500, 250], dx=C.DX, dt=0.01, V0=C.V0, sigma=C.SIGMA, x_obstacle=C.XOBS, v_final=C.VFLOW, t_ramp=0.1,
    gamma0=0.1, layer_widths_xi=[50, 40], layer_tanh_scale_xi=15, force_every_tau=0.1, counts_every_tau=5.0, snapshots_every_tau=10.0,
    reference_t_end_force=100.0, noise_relative=1e-4, noise_seed=2026,
    source="Zenodo 10.5281/zenodo.20068724 v1.0.0 (README, input json, spec.txt, src/gpe_dynamics/*.py read); numbers of the paper quoted from arXiv:2602.03518v1",
)
R["paper_quoted_not_reproduced"] = dict(
    v_c_over_c=0.18, v_th_over_c=0.33, Re_s_threshold=2.0, D_eff_over_wv=1.31, St0_range=[0.20, 0.30], time_window_tau=[2000, 10000],
    fringe_region_in_paper=dict(gamma0=0.1, w_x_xi=25, w_y_xi=20, d_xi=3, paper_equation=2),
    paper_equation_numbers=dict(gpe=1, fringe_damping=2, local_landau_criterion=5, superfluid_reynolds_number=7),
    note=("quoted from Kwon & Shin, arXiv:2602.03518v1 (V0/mu = 0.9, sigma/xi = 20): critical velocity of the dipole emission, dipole-to-cluster transition velocity, threshold superfluid Reynolds number, "
          "the averaging window, the fringe-region numbers of the paper's Eq. (2) (the code's own are layer_widths_xi and layer_tanh_scale_xi of 'dataset'); read through alphaXiv on 2026-10-10"),
)

# the damping function of the code (qf-pgpe::flow header: Gamma = gamma0 max_{x,y}( (2 + tanh((x - W1)/s) - tanh((x - W2)/s))/2 ), W = +-(half-box - layer width), s = 15 xi),
# evaluated on the grid of the deposited run: how small it is where the obstacle sits
def _gamma(xx, yy, g0=0.1, w1x=250.0 - 50.0, w1y=125.0 - 40.0, sc=15.0):
    gx = g0 * (2 + np.tanh((xx - w1x) / sc) - np.tanh((xx + w1x) / sc)) / 2
    gy = g0 * (2 + np.tanh((yy - w1y) / sc) - np.tanh((yy + w1y) / sc)) / 2
    return np.maximum(gx, gy)
_XX, _YY = np.meshgrid(C.x, C.y); _G = _gamma(_XX, _YY); _disc = (_XX - C.XOBS) ** 2 + _YY ** 2 <= C.SIGMA ** 2
R["damping"] = dict(
    gamma_centre_of_obstacle=f(_gamma(C.XOBS, 0.0)), gamma_max_within_1_over_e2_radius=f(_G[_disc].max()), gamma_max_over_box=f(_G.max()), gamma_max_in_force_interior=f(_G[(np.abs(_XX) < 200) & (np.abs(_YY) < 85)].max()),
    note="formula of the Rust port (flow.rs header and constructor), layer starts at |x| = 200 and |y| = 85, scale 15 xi, gamma0 = 0.1; evaluated on the 1000 x 500 grid",
)
del _XX, _YY, _G, _disc

# ------------------------------------------------------------------------------------------------ 2. the initial field: one imaginary-time step
dtau, eps = 0.04, C.NX * C.NY * 10e-10
Vp = C.POT - 1.0
tf = np.where(Vp < 0, np.sqrt(np.maximum(-Vp, 0)), 0.0).astype(complex)
kx = 2 * np.pi * np.fft.fftfreq(C.NX, C.DX); ky = 2 * np.pi * np.fft.fftfreq(C.NY, C.DX)
K2 = kx[None, :] ** 2 + ky[:, None] ** 2
psi1 = np.fft.ifft2(np.fft.fft2(tf) * np.exp(-K2 / 2 * dtau))
with np.errstate(divide="ignore", invalid="ignore"):
    temp = np.where(np.abs(Vp) < 1e-14, 2 * dtau, (1 - np.exp(-2 * Vp * dtau)) / Vp)
psi2 = psi1 * np.exp(-Vp * dtau) / np.sqrt(1 + np.abs(psi1) ** 2 * temp)
gamma1 = float(np.trapezoid(np.trapezoid(np.abs(psi2 - tf) ** 2, C.x, axis=1), C.y))
rng = np.random.default_rng(seed=2026)
noise = 1e-4 * (rng.integers(-5, 5, size=(C.NY, C.NX)) + 1j * rng.integers(-5, 5, size=(C.NY, C.NX)))
mine_exact = psi2 + noise
mine = mine_exact.astype(np.complex64).astype(np.complex128)
p0 = C.load_ref(0.0)
rel_with = f(np.linalg.norm(mine - p0) / np.linalg.norm(p0)); rel_without = f(np.linalg.norm(psi2.astype(np.complex64).astype(np.complex128) - p0) / np.linalg.norm(p0))
rel_unrounded = f(np.linalg.norm(mine_exact - p0) / np.linalg.norm(p0)); n_diff = int(np.count_nonzero(mine != p0))
R["initial_field"] = dict(
    epsilon=f(eps), dtau=dtau, stop_threshold=f(eps * dtau), gamma_after_one_step=gamma1, stops_at_step_1=bool(gamma1 < eps * dtau),
    rel_L2_to_deposited_with_noise=rel_with, rel_L2_to_deposited_without_noise=rel_without, rel_L2_double_precision_to_deposited=rel_unrounded, n_elements_differing_after_rounding=n_diff, n_elements=int(mine.size), noise_rms_relative=f(np.linalg.norm(noise) / np.linalg.norm(p0)),
    note="Thomas-Fermi start sqrt(1-V), ONE step of the reference's first-order split imaginary-time operator, plus the seeded noise, cast to complex64; numpy re-derivation written for this chapter",
)
del psi1, psi2, tf, mine, mine_exact, noise

# ------------------------------------------------------------------------------------------------ 3. the force
t_o, F_o, F_r, dF = C.load_ours_force()
Fmax = f(np.abs(F_r).max())
wins = []
for lo, hi in ((0, 1), (1, 5), (5, 10), (10, 20), (20, 30), (30, 40), (40, 50)):
    m = (t_o >= lo - 1e-9) & (t_o < hi - 1e-9)
    wins.append(dict(lo=lo, hi=hi, max_dF=f(np.abs(dF[m]).max()), rms_dF=f(np.sqrt((dF[m] ** 2).mean())), rms_F_ref=f(np.sqrt((F_r[m] ** 2).mean()))))
m3 = t_o <= 0.3 + 1e-9; m10 = t_o <= 10 + 1e-9
t_ref, fx_ref, fy_ref, de_ref = C.load_ref_force()
R["force"] = dict(
    max_abs_F_ref_0_50=Fmax, t_of_max=f(t_o[np.abs(F_r).argmax()]), max_abs_F_ref_0_100=f(np.abs(fx_ref).max()),
    windows=wins, max_dF_t_le_0p3=f(np.abs(dF[m3]).max()), max_dF_t_le_10=f(np.abs(dF[m10]).max()), rel_t_le_10=f(np.abs(dF[m10]).max() / Fmax),
    max_dF_overall=f(np.abs(dF).max()), rel_overall=f(np.abs(dF).max() / Fmax),
    max_abs_F_ref_t_le_10=f(np.abs(F_r[m10]).max()), rel_t_le_10_window_max=f(np.abs(dF[m10]).max() / np.abs(F_r[m10]).max()), rel_t_le_0p3_window_max=f(np.abs(dF[m3]).max() / np.abs(F_r[m3]).max()),
    D_at_24=f(-fx_ref[240]),
    drag_ref=dict(t=[0.1, 1, 5, 10, 20, 25, 30, 40, 50, 100], D=[f(-fx_ref[int(round(a / 0.1))]) for a in (0.1, 1, 5, 10, 20, 25, 30, 40, 50, 100)]),
    dF_plateau_mean_t26_50=f(dF[(t_o >= 26) & (t_o <= 50)].mean()), dF_plateau_min=f(dF[(t_o >= 26) & (t_o <= 50)].min()), dF_plateau_max=f(dF[(t_o >= 26) & (t_o <= 50)].max()),
    dF_at=dict(t=[10, 14, 18, 20, 24, 28, 30, 40, 50], dF=[f(dF[int(round(a / 0.1))]) for a in (10, 14, 18, 20, 24, 28, 30, 40, 50)]),
    growth_factor_window5_10_to_10_20=f(wins[3]["max_dF"] / wins[2]["max_dF"]),
    note="F_x = int dV/dx |psi|^2 over |x|<200, |y|<85 (the reference's Eren_force); negative = pushed along the flow; drag D = -F_x",
)
# lift
tt = np.array([5., 10., 15., 20., 25., 30., 35., 40., 45., 50.])
Fy_o = np.array([C.forces(C.load_ours(a))[1] for a in tt]); Fy_r = np.array([fy_ref[int(round(a / 0.1))] for a in tt])
Fx_o = np.array([C.forces(C.load_ours(a))[0] for a in tt])
R["lift"] = dict(t=tt.tolist(), Fy_ours=Fy_o.tolist(), Fy_ref_file=Fy_r.tolist(), rel_diff=(np.abs(Fy_o - Fy_r) / np.maximum(np.abs(Fy_r), 1e-30)).tolist(),
                 max_abs_Fy_ref_to_t100=f(np.abs(fy_ref).max()), ratio_to_max_drag=f(np.abs(fy_ref).max() / np.abs(fx_ref).max()), Fy_ref_t0=f(fy_ref[0]),
                 Fx_ours_from_snapshots=Fx_o.tolist(),
                 note="F_y from OUR snapshots at the snapshot times against the reference file at the same times")

# a constant time shift?  dF ~ s F'_ref(t)  (least squares in each window)
dFr = np.gradient(F_r, t_o)
fits = []
for lo, hi in ((10, 20), (20, 30), (30, 40), (40, 50)):
    mm = (t_o >= lo - 1e-9) & (t_o < hi - 1e-9)
    sfit = float((dF[mm] * dFr[mm]).sum() / (dFr[mm] ** 2).sum()); res = dF[mm] - sfit * dFr[mm]
    fits.append(dict(lo=lo, hi=hi, shift=sfit, rms_residual_over_rms_dF=float(np.sqrt((res ** 2).mean()) / np.sqrt((dF[mm] ** 2).mean()))))
R["force"]["time_shift_fit"] = fits
R["force"]["t_zero_crossing_of_dF"] = f(t_o[np.where((dF[:-1] < 0) & (dF[1:] >= 0))[0][-1]])
R["force"]["dF_fraction_of_plateau_at_t24"] = f(dF[240] / R["force"]["dF_plateau_mean_t26_50"])

# ------------------------------------------------------------------------------------------------ 4. conventions of the velocity ramp (t <= 5)
def csv(path):
    d = np.loadtxt(path, delimiter=",", skiprows=1); return d[:, 0], d[:, 1], d[:, 3]
ts, f_st01, d_st01 = csv(XQ / "ks_st_dt01" / "kwon_shin_force.csv"); _, f_st005, d_st005 = csv(XQ / "ks_st_dt005" / "kwon_shin_force.csv"); _, f_se005, d_se005 = csv(XQ / "ks_rust_dt005" / "kwon_shin_force.csv")
a_ramp, h, n_ramp = C.VFLOW / 0.1, 0.01, 10
over01 = a_ramp * h * h * n_ramp / 2; over005 = a_ramp * 0.005 ** 2 * 20 / 2
R["ramp"] = dict(
    overshoot_dt0p01=f(over01), overshoot_dt0p005=f(over005), sum_v_dt_step_end=f(sum(a_ramp * (i + 1) * h * h for i in range(n_ramp))), integral_v_dt=f(a_ramp * (n_ramp * h) ** 2 / 2),
    step_end_dt0p01_max_dF_t_le_0p3=R["force"]["max_dF_t_le_0p3"],
    stage_times_dt0p01_dF_t0p1=f(d_st01[1]), stage_times_dt0p005_dF_t0p1=f(d_st005[1]), step_end_dt0p005_dF_t0p1=f(d_se005[1]),
    sensitivity_dF_per_displacement_stage=f(d_st01[1] / over01), sensitivity_dF_per_displacement_dt0p005=f(d_se005[1] / (over01 - over005)),
    stage_times_max_dF_t_le_5=f(np.abs(d_st01).max()), stage_times_dF_t5=f(d_st01[-1]), stage_times_dF_min_t1_5=f(d_st01[10:].min()), stage_times_dF_max_t1_5=f(d_st01[10:].max()),
    own_temporal_error_stage_dt0p01_vs_0p005_max_t_le_5=f(np.abs(f_st01 - f_st005).max()),
)

# ------------------------------------------------------------------------------------------------ 5. wave function distances
rows = []
for t in (10.0, 20.0, 30.0, 40.0, 50.0):
    pr, po = C.load_ref(t), C.load_ours(t)
    phi = np.angle(np.vdot(pr, po))
    nr, no = np.abs(pr) ** 2, np.abs(po) ** 2
    rows.append(dict(t=t, psi_rel_L2=f(np.linalg.norm(po - pr) / np.linalg.norm(pr)), psi_rel_L2_global_phase_removed=f(np.linalg.norm(po * np.exp(-1j * phi) - pr) / np.linalg.norm(pr)),
                     global_phase=f(phi), density_rel_L2=f(np.linalg.norm(no - nr) / np.linalg.norm(nr)), max_abs_dpsi=f(np.abs(po - pr).max()),
                     density_diff_rms=f(np.sqrt(((no - nr) ** 2).mean())), density_diff_max=f(np.abs(no - nr).max()),
                     density_diff_share_within_40xi_of_obstacle=f((((no - nr) ** 2)[((C.XX - 100) ** 2 + C.YY ** 2) < 40 ** 2]).sum() / ((no - nr) ** 2).sum())))
R["psi"] = rows
R["psi_density_diff_rms_range"] = [min(r["density_diff_rms"] for r in rows), max(r["density_diff_rms"] for r in rows)]

# ------------------------------------------------------------------------------------------------ 6. the vortex census
cnt_t, cnt_ref, cnt_ref2 = C.load_ref_counts()
times = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0]
ours_rule, ours_census, ref_census, match = {}, {}, {}, {}
for t in times:
    po = C.load_ours(t)
    ours_rule[t] = len(C.ref_rule(po)); co = C.charged(po); ours_census[t] = len(co)
    q, qi = C.plaquette_charge(po)
    if abs(t - round(t / 10) * 10) < 1e-9 and t >= 10:
        pr = C.load_ref(t); cr = C.charged(pr); ref_census[t] = len(cr); match[t] = dict(zip(("identical", "within_one_cell", "only_ref", "only_ours"), C.census_match(cr, co)))
R["census"] = dict(
    times=times, reference_rule_in_file=[int(cnt_ref[int(round(t / 5))]) for t in times], ours_with_reference_rule=[ours_rule[t] for t in times], ours_exact_census=[ours_census[t] for t in times],
    reference_exact_census={str(t): v for t, v in ref_census.items()}, match_ours_vs_reference={str(t): v for t, v in match.items()},
    reference_counts_to_t100=dict(t=cnt_t.tolist(), n=cnt_ref.tolist()), equal_counts_of_10=int(sum(int(cnt_ref[int(round(t / 5))]) == ours_rule[t] for t in times)),
)
R["census"]["port_validation"] = {str(t): dict(port_on_deposited_field=int(len(C.ref_rule(C.load_ref(t)))), deposited_file=int(cnt_ref[int(round(t / 5))])) for t in (10.0, 20.0, 30.0, 40.0, 50.0)}
# integrality and total charge on every snapshot
maxdev, sums, edge_steps = 0.0, [], 0.0
for loader, tl in ((C.load_ref, (0., 10., 20., 30., 40., 50.)), (C.load_ours, tuple(times))):
    for t in tl:
        p = loader(t); q, qi = C.plaquette_charge(p); maxdev = max(maxdev, f(np.abs(q - qi).max())); sums.append(int(qi.sum()))
        sx, sy = C.edge_steps(p); edge_steps = max(edge_steps, f(max(np.abs(sx).max(), np.abs(sy).max())) / np.pi)
R["winding_checks"] = dict(snapshots_checked=len(sums), max_abs_q_minus_round=maxdev, all_total_charges_zero=bool(all(s == 0 for s in sums)), max_edge_step_over_pi=edge_steps,
                           note="q = (1/2pi) x sum of principal differences around each plaquette of the periodic grid (counter-clockwise); Lean: VortexWinding.loop_sum_eq_mul")

# mirror structure of the census: for each charged plaquette (i, j, q) the mirror partner is (i, 499 - j, -q)
def mirror_stats(census):
    ss = {(int(round((xx - C.DX / 2 + 250) / C.DX)), int(round((yy - C.DX / 2 + 125) / C.DX)), q) for xx, yy, q in census}
    unpaired = [(i, j, q) for (i, j, q) in ss if (i, 499 - j, -q) not in ss]
    return len(ss), len(unpaired)
R["census"]["mirror_pairs"] = {f"ours_{t:g}": mirror_stats(C.charged(C.load_ours(t))) for t in times}
R["census"]["mirror_pairs"].update({f"ref_{t:g}": mirror_stats(C.charged(C.load_ref(t))) for t in (10.0, 20.0, 30.0, 40.0, 50.0)})

# the reference's rule opened up: loop integrals of the same vortex in the two fields, double counting, the marginal candidate at t = 45
rd = {}
for label, loader, tl in (("ours", C.load_ours, (30.0, 35.0, 40.0, 45.0, 50.0)), ("ref", C.load_ref, (30.0, 40.0, 50.0))):
    for t in tl:
        p = loader(t); cs = C.rule_candidates(p); en = C.enclosed_charge(cs, p)
        rd[f"{label}_{t:g}"] = dict(accepted=[dict(x=c["x"], y=c["y"], integral_over_pi=c["integral_over_pi"], dropped=c["dropped"]) for c in cs if c["counted"]],
                                    n_candidates=len(cs), enclosed=[dict(x=e["x"], y=e["y"], net=e["net"], plaq=e["plaq"]) for e in en])
def pair_diff(t):
    a, b = rd[f"ours_{t:g}"]["accepted"], rd[f"ref_{t:g}"]["accepted"]
    diffs = []
    for ca in a:
        for cb in b:
            if abs(ca["x"] - cb["x"]) < 1e-9 and abs(ca["y"] - cb["y"]) < 1e-9:
                diffs.append(abs(ca["integral_over_pi"] - cb["integral_over_pi"]))
    return diffs
rule_diff = {str(t): pair_diff(t) for t in (30.0, 40.0, 50.0)}
marg = sorted(rd["ours_45"]["accepted"], key=lambda c: abs(c["integral_over_pi"]))[0]
R["rule"] = dict(
    loop_integral_difference_same_vortex_ours_vs_ref=rule_diff, max_loop_integral_difference_over_pi=f(max(max(v) for v in rule_diff.values() if v)),
    marginal_candidate_t45_ours=marg, threshold_over_pi=0.9,
    accepted_t45_ours=rd["ours_45"]["accepted"],
    double_counted_t30=[e for e in rd["ours_30"]["enclosed"]], n_accepted_t30=len(rd["ours_30"]["accepted"]),
    n_accepted={k: len(v["accepted"]) for k, v in rd.items()},
    detail=rd,
    note="candidates = local minima along axis 0 with n<0.2 outside 5 cells of the obstacle, merged within 3 xi; loop = square of half-width 4 cells; steps >= 0.3 pi are dropped from the sum; counted if |sum| > 0.9 pi (the reference's sign convention is clockwise-positive)",
)

R["symmetry"] = dict(t=[0.0, 10.0, 20.0, 30.0, 40.0, 50.0], asym_ref=[f(C.asymmetry(C.load_ref(t))) for t in (0., 10., 20., 30., 40., 50.)],
                     t_ours=times, asym_ours=[f(C.asymmetry(C.load_ours(t))) for t in times])

# ------------------------------------------------------------------------------------------------ 7. the supersonic region before the first pair
sup = {}
for label, loader, tl in (("ref", C.load_ref, (10.0, 20.0)), ("ours", C.load_ours, (5.0, 10.0, 15.0, 20.0))):
    for t in tl:
        sup[f"{label}_{t:g}"] = C.supersonic_stats(loader(t))
R["supersonic"] = sup
# Lean: sonic_speed_threshold -- with Bernoulli's relation at a point, M > 1 iff |u|^2 > (2/3)(B - V), B = 1 + v^2/2
Bc = 1 + 0.5 * C.VFLOW ** 2
sb2 = {}
for label, loader, tl in (("ref", C.load_ref, (10.0, 20.0)), ("ours", C.load_ours, (5.0, 10.0, 15.0, 20.0))):
    for t in tl:
        Mq, uxq, uyq, nq = C.mach(loader(t)); u2q = uxq ** 2 + uyq ** 2
        regB = u2q > (2.0 / 3.0) * (Bc - C.POT); regM = Mq > 1.0; near = ((C.XX - 100) ** 2 + C.YY ** 2) < 60 ** 2
        jq, iq = int(np.argmin(np.abs(C.y))), int(round((100 + 250) / C.DX))
        sb2[f"{label}_{t:g}"] = dict(area_threshold_region=f((regB & near).sum() * C.DX ** 2), area_mach_region=f((regM & near).sum() * C.DX ** 2), area_intersection=f((regB & regM & near).sum() * C.DX ** 2),
                                     fraction_of_mach_region_inside=f((regB & regM & near).sum() / (regM & near).sum()), n_centre=f(nq[jq, iq]), n_bernoulli_centre=f(Bc - C.POT[jq, iq] - 0.5 * u2q[jq, iq]), speed_centre=f(np.sqrt(u2q[jq, iq])))
R["sonic_threshold"] = dict(B=f(Bc), u_c_far_field=f(np.sqrt(2.0 / 3.0 * Bc)), u_c_centre=f(np.sqrt(2.0 / 3.0 * (Bc - C.V0))), sqrt_1_minus_V0=f(np.sqrt(1 - C.V0)), by_snapshot=sb2,
                            note="regions restricted to r < 60 xi from the obstacle centre; the threshold region needs only |u| and V, the Mach region needs n as well")
# axis profile at t = 20 (ours): density, speed, local flux, sonic density
pa = C.load_ours(20.0); Ma, uxa, uya, na = C.mach(pa); jy0 = int(np.argmin(np.abs(C.y)))
ja = na * np.hypot(uxa, uya)
R["axis_t20_ours"] = dict(
    x_center=100.0, n_center=f(na[jy0, int(round((100 + 250) / C.DX))]), u_center=f(uxa[jy0, int(round((100 + 250) / C.DX))]), M_center=f(Ma[jy0, int(round((100 + 250) / C.DX))]),
    j_center=f(ja[jy0, int(round((100 + 250) / C.DX))]), j_upstream=C.VFLOW, j_center_over_upstream=f(ja[jy0, int(round((100 + 250) / C.DX))] / C.VFLOW),
    axis_supersonic_x_range=[f(C.x[np.where(Ma[jy0] > 1)[0].min()]), f(C.x[np.where(Ma[jy0] > 1)[0].max()])], axis_min_density=f(na[jy0].min()), x_axis_min_density=f(C.x[na[jy0].argmin()]),
    axis_max_M=f(Ma[jy0].max()), x_axis_max_M=f(C.x[Ma[jy0].argmax()]),
    speed_max=f(np.hypot(uxa, uya).max()), speed_max_at=[f(C.x[np.unravel_index(np.hypot(uxa, uya).argmax(), uxa.shape)[1]]), f(C.y[np.unravel_index(np.hypot(uxa, uya).argmax(), uxa.shape)[0]])],
    speed_max_axis=f(np.abs(uxa[jy0]).max()), x_speed_max_axis=f(C.x[np.abs(uxa[jy0]).argmax()]), n_at_speed_max_axis=f(na[jy0, np.abs(uxa[jy0]).argmax()]),
)

# ------------------------------------------------------------------------------------------------ 8. the birth of the first pair (sub-box continuation, every 0.1 tau)
d = np.load(XQ / "ch09" / "birth_t20_25.npz"); tb = d["t"]; box = d["box"]; bx0 = int(d["x0"]); by0 = int(d["y0"])
xs = C.x[bx0:bx0 + box.shape[2]]; ys = C.y[by0:by0 + box.shape[1]]
def pdm(a, b):
    dd = (b - a + np.pi) % (2 * np.pi) - np.pi
    return np.where(dd == -np.pi, np.pi, dd)
def box_charges(psi):
    th = np.angle(psi); sx = pdm(th[:, :-1], th[:, 1:]); sy = pdm(th[:-1, :], th[1:, :])
    s = sx[:-1, :] + sy[:, 1:] - sx[1:, :] - sy[:, :-1]
    return np.rint(s / (2 * np.pi)).astype(int), s / (2 * np.pi), sx, sy
series = []
first = None
for k in range(len(tb)):
    psi = box[k]; q, qf, sx, sy = box_charges(psi); n = np.abs(psi) ** 2; nz = np.argwhere(q != 0)
    jmn, imn = np.unravel_index(n.argmin(), n.shape)
    series.append(dict(t=f(tb[k]), n_min=f(n.min()), x_nmin=f(xs[imn]), y_nmin=f(ys[jmn]), charged=int(len(nz)), max_edge_step_over_pi=f(max(np.abs(sx).max(), np.abs(sy).max()) / np.pi),
                       n_axis_min=f(n[np.argmin(np.abs(ys)), :].min())))
    if first is None and len(nz):
        first = dict(t=f(tb[k]), plaquettes=[dict(q=int(q[j, i]), x=f(xs[i] + C.DX / 2), y=f(ys[j] + C.DX / 2)) for j, i in nz], n_min=f(n.min()))
kb = [s["charged"] > 0 for s in series].index(True)
R["birth"] = dict(
    t_last_without=series[kb - 1]["t"], t_first_with=series[kb]["t"], first_charges=first, n_min_before=series[kb - 1]["n_min"], n_min_at=series[kb]["n_min"],
    n_min_series=[(s["t"], s["n_min"]) for s in series], charged_series=[(s["t"], s["charged"]) for s in series], max_edge_step_series=[(s["t"], s["max_edge_step_over_pi"]) for s in series],
    max_edge_step_over_pi_after_birth=f(max(s["max_edge_step_over_pi"] for s in series[kb:])), max_edge_step_over_pi_at_birth=series[kb]["max_edge_step_over_pi"],
    numpy_continuation_vs_rust_t25_rel_L2=f(np.linalg.norm(d["final"] - C.load_ours(25.0)) / np.linalg.norm(C.load_ours(25.0))),
    n_min_at_t20=series[0]["n_min"], x_nmin_at_t20=series[0]["x_nmin"],
)
# supersonic region at the moment of birth, and the position of the pair relative to it
def mach_box(psi):
    n = np.abs(psi) ** 2; h = C.DX
    gx = np.gradient(psi, h, axis=1); gy = np.gradient(psi, h, axis=0)
    ux = (psi.conj() * gx).imag / n - C.VFLOW; uy = (psi.conj() * gy).imag / n
    return np.hypot(ux, uy) / np.sqrt(n)
sb = {}
for tq in (20.0, 22.0, 24.0, 24.2, 24.3):
    k = int(np.argmin(np.abs(tb - tq))); Mb = mach_box(box[k]); mk = Mb > 1.0
    mk[:2], mk[-2:], mk[:, :2], mk[:, -2:] = False, False, False, False        # margins of the non-periodic sub-box
    j0 = int(np.argmin(np.abs(ys)))
    xa = xs[np.where(mk[j0])[0]]
    sb[f"{tb[k]:.1f}"] = dict(axis_supersonic_x=[f(xa.min()), f(xa.max())] if len(xa) else None, area=f(mk.sum() * C.DX ** 2))
R["birth"]["supersonic_axis_range_by_time"] = sb
sep = {}
for tq in (24.3, 24.5, 24.9):
    k = int(np.argmin(np.abs(tb - tq))); qk = box_charges(box[k])[0]; nzk = np.argwhere(qk != 0)
    pts = [(xs[i] + C.DX / 2, ys[j] + C.DX / 2, int(qk[j, i])) for j, i in nzk]
    sep[f"{tb[k]:.1f}"] = dict(n_charged=len(pts), plaquettes=[dict(x=f(a), y=f(b), q=c) for a, b, c in pts],
                              separation=(f(np.hypot(pts[0][0] - pts[1][0], pts[0][1] - pts[1][1])) if len(pts) == 2 else None))
R["birth"]["pair_by_time"] = sep
# Madelung-Bernoulli identity on the sub-box at t = 20.1: R = 1/2 |u|^2 + n + V + Q - 1 - v^2/2 should equal -d theta/dt
h = C.DX
def d1(fld, axis):
    out = np.full_like(fld, np.nan); n = fld.shape[axis]
    sl = lambda a, b: tuple(slice(a, b) if ax == axis else slice(None) for ax in range(fld.ndim))
    out[sl(2, n - 2)] = (-np.take(fld, range(4, n), axis) + 8 * np.take(fld, range(3, n - 1), axis) - 8 * np.take(fld, range(1, n - 3), axis) + np.take(fld, range(0, n - 4), axis)) / (12 * h)
    return out
def d2(fld, axis):
    out = np.full_like(fld, np.nan); n = fld.shape[axis]
    sl = lambda a, b: tuple(slice(a, b) if ax == axis else slice(None) for ax in range(fld.ndim))
    out[sl(2, n - 2)] = (-np.take(fld, range(4, n), axis) + 16 * np.take(fld, range(3, n - 1), axis) - 30 * np.take(fld, range(2, n - 2), axis) + 16 * np.take(fld, range(1, n - 3), axis) - np.take(fld, range(0, n - 4), axis)) / (12 * h * h)
    return out
XXb, YYb = np.meshgrid(xs, ys); Vb = C.V0 * np.exp(-2 * ((XXb - C.XOBS) ** 2 + YYb ** 2) / C.SIGMA ** 2)
kk = int(np.argmin(np.abs(tb - 20.1))); psi0 = box[kk]; n0 = np.abs(psi0) ** 2
ux = (psi0.conj() * d1(psi0, 1)).imag / n0 - C.VFLOW; uy = (psi0.conj() * d1(psi0, 0)).imag / n0
a0 = np.sqrt(n0); Q = -0.5 * (d2(a0, 1) + d2(a0, 0)) / a0
Rb = 0.5 * (ux ** 2 + uy ** 2) + n0 + Vb + Q - 1 - 0.5 * C.VFLOW ** 2
dth = np.angle(box[kk + 1] * np.conj(box[kk - 1])) / (tb[kk + 1] - tb[kk - 1])
ok = np.isfinite(Rb) & np.isfinite(dth)
jax = int(np.argmin(np.abs(ys)))
R["bernoulli"] = dict(
    t=f(tb[kk]), corr_R_vs_minus_dtheta_dt=f(np.corrcoef(Rb[ok], -dth[ok])[0, 1]), max_abs_difference=f(np.abs(Rb + dth)[ok].max()), rms_R=f(np.sqrt((Rb[ok] ** 2).mean())),
    axis_R_range=[f(np.nanmin(Rb[jax])), f(np.nanmax(Rb[jax]))], axis_R_span=f(np.nanmax(Rb[jax]) - np.nanmin(Rb[jax])), axis_Q_abs_max_away_from_core=f(np.nanmax(np.abs(Q[jax, (xs < 84) | (xs > 92)]))),
    axis_Q_min=f(np.nanmin(Q[jax])), x_axis_Q_min=f(xs[np.nanargmin(Q[jax])]),
    note="R is computed from one snapshot (4th-order stencils), d theta/dt from the snapshots 0.1 tau before and after; the Madelung transform of the model gives R = - d theta / dt",
)

# ------------------------------------------------------------------------------------------------ 9. numbers of the Lean statements (new module Ch09_FlowPast, library statements)
j = C.VFLOW; s = j ** (2 / 3); Vc = (1 - s) ** 2 * (s + 2) / 2
sol = None
from scipy.optimize import brentq
s_for_V0 = brentq(lambda s_: (1 - s_) ** 2 * (s_ + 2) / 2 - C.V0, 1e-6, 1.0)
R["lean_numbers"] = dict(
    sonic_density_s=f(s), V_c_at_v0p55=f(Vc), V0_over_Vc=f(C.V0 / Vc), s_where_Vc_equals_V0=f(s_for_V0), j_where_Vc_equals_V0=f(s_for_V0 ** 1.5),
    sound_speed_in_obstacle_core_TF=f(np.sqrt(1 - C.V0)), TF_depleted_density_core=f(1 - C.V0),
    landau_velocity_GP=1.0, bog_eps_over_k_at=dict(k=[0.1, 0.5, 1.0, 2.0, 4.0], value=[f(np.sqrt(1 + k_ ** 2 / 4)) for k_ in (0.1, 0.5, 1.0, 2.0, 4.0)]),
    Vc_small_barrier_approx_2over3_1minusj_sq=f(2 / 3 * (1 - j) ** 2),
)

# ------------------------------------------------------------------------------------------------ 10. the fresh run of the Rust example (t <= 1)
fresh = Path(os.environ.get("CH09_FRESH", str(HERE / "ch09_fresh_run" / "run_t1.out")))
if fresh.exists() and "force_x: max" in fresh.read_text():
    txt = fresh.read_text(); err = (fresh.parent / "run_t1.err").read_text()
    m = re.search(r"max \|ours - reference\| = ([0-9.eE+-]+), relative to max \|F\| = ([0-9.eE+-]+); wall (\d+) s \((\d+) steps\)", txt)
    cd = np.loadtxt(fresh.parent / "kwon_shin_force.csv", delimiter=",", skiprows=1)
    la = [float(a) for a in re.findall(r"load average: ([0-9.]+),", txt)]
    ut = float(re.search(r"User time \(seconds\): ([0-9.]+)", err).group(1)); et = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([0-9:.]+)", err).group(1)
    R["fresh_run"] = dict(command="kwon_shin --ref-dir <Zenodo extract> --t-end 1.0 --dt 0.01 --ramp step-end", max_abs_dF_t_le_1=f(m.group(1)), rel_to_max_F_in_window=f(m.group(2)), program_wall_s=int(m.group(3)), steps=int(m.group(4)),
                          max_abs_dF_t_le_0p3=f(np.abs(cd[:4, 3]).max()), max_abs_dF_t_lt_1=f(np.abs(cd[:10, 3]).max()), rows=int(len(cd)), user_cpu_s=ut, elapsed_incl_lock_wait=et, load_average_start_end=la,
                          identical_to_5000_step_run_to_printed_digits=bool(np.allclose(cd[:, 3], C.load_ours_force()[3][:len(cd)], atol=1e-9, rtol=0)))
else:
    R["fresh_run"] = None

# the production run to t = 50: its own output file
_po = (XQ / "ks_rust_t50" / "ks_rust_t50.out").read_text()
_m = re.search(r"wall (\d+) s \((\d+) steps\)", _po)
R["production_run"] = dict(wall_s=int(_m.group(1)), steps=int(_m.group(2)), wall_minutes=f(int(_m.group(1)) / 60), source="/mnt/data/xdev-cache/qf-external/ks_rust_t50/ks_rust_t50.out (printed by the kwon_shin example at the end of the run)",
                           note="wall-clock on the shared eight-core machine (the load was not recorded for this run)")

import platform, scipy
R["provenance"] = dict(
    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
    cvode_solver_used=False,
    note=("no CvodeSolver and no qf_pgpe Python call is made by any chapter-9 script; the solver is the Rust example program kwon_shin of qf-pgpe::flow "
          "(worktree /home/xavkal/xdev/rusty-SUNDIALS-c3 at commit 5db8041, branch feat/qf-pgpe-reproduction, `git describe` v11.5.0-6-g5db8041; binary built 2026-10-09 21:23:35, after the last modification of flow.rs at 21:22:29; "
          "the programme's ledger (CLAIM-106) records this work as released in v11.6.0, PR #71, 6545abf -- that the released tree equals this worktree was not re-checked); the 5000-step run "
          "(2741 s, snapshots every 5 tau) and the convention runs (ks_st_dt01, ks_st_dt005, ks_rust_dt005) were made in the programme's session of 2026-10-09 and are read from /mnt/data/xdev-cache/qf-external; "
          "the t <= 1 run of this chapter is stored in figures/ch09_fresh_run/"),
    inputs=["/mnt/data/xdev-cache/qf-external/20068724/extracted", "/mnt/data/xdev-cache/qf-external/ks_rust_t50", "/mnt/data/xdev-cache/qf-external/ch09/birth_t20_25.npz",
            "/mnt/data/xdev-cache/qf-external/{ks_st_dt01,ks_st_dt005,ks_rust_dt005}/kwon_shin_force.csv", "figures/ch09_fresh_run/"],
    paper=dict(arxiv="2602.03518v1", doi="10.1103/wlft-tc8w", dataset_doi="10.5281/zenodo.20068724"),
)
OUT.write_text(json.dumps(R, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
print("wrote", OUT)
