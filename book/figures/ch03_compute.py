"""Chapter 3: every number of the chapter.  Reads the solver runs written by ch03_run.py (cache /mnt/data/xdev-cache/ch03),
analyses them and writes

    book/figures/ch03_numbers.json   all numbers, with their meaning
    book/figures/ch03_derived.npz    arrays behind the figures
    book/figures/ch03_numbers.tex    LaTeX macros \\cthree@<key> generated from the JSON (the chapter quotes them with \\cn{key})

    OMP_NUM_THREADS=1 PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch03_compute.py [const] [pair] [scan] [quad]     (default: all)

Units: hbar = m = g = n0 = 1 (healing length xi = 1, sound speed c = 1, kappa = 2 pi), box L = 64, N = 128, dx = 0.5.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_analysis import *            # noqa: F401,F403
import ch03_pv as PV
from scipy import constants as C

import os
FIGS = Path(os.environ.get("CH03_OUTDIR", Path(__file__).resolve().parent))
JSON_PATH = FIGS / "ch03_numbers.json"; NPZ_PATH = FIGS / "ch03_derived.npz"; TEX_PATH = FIGS / "ch03_numbers.tex"
OUT = json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() else {}
DER = dict(np.load(NPZ_PATH)) if NPZ_PATH.exists() else {}


def load(case):
    z = np.load(f"{CACHE}/{case}.npz"); meta = json.load(open(f"{CACHE}/{case}.json"))
    return z, meta


def f(x):                      # json-safe float
    return float(x)


# ------------------------------------------------------------------------------------------------------ constants
def part_fourier_check():
    """Zero-mean-flow torus point-vortex velocity: Fourier series (sigma = 0.7) against the Weiss-McWilliams closed form, test configuration of ch03_pv.py."""
    pos = np.array([[26.30, 30.70], [38.10, 31.20]]); q = np.array([1, -1])
    a = PV.vortex_velocity(pos, q, with_sector=False); b = PV.fourier_velocity(pos, pos, q, sigma=0.7)
    OUT["fourier_check"] = dict(config=dict(pos=pos.tolist(), q=q.tolist()), sigma=0.7, max_abs_diff=f(np.abs(a - b).max()), wm_velocity=a.tolist(), fourier_velocity=b.tolist(),
                                sector_flow=PV.sector_flow(pos, q).tolist())


def part_const():
    m_u = 4.00260325413                      # He-4 atomic mass in u: NIST Atomic Weights and Isotopic Compositions (fetched 2026-10-09)
    h = C.h; u = C.physical_constants["atomic mass constant"][0]
    kappa = h / (m_u * u)
    Omega = 1.0                              # rad/s
    nv = 2 * Omega / kappa
    OUT["constants"] = dict(
        h_Js=h, u_kg=u, m_He4_u=m_u, m_He4_kg=m_u * u, kappa_SI_m2_per_s=kappa,
        omega_example_rad_s=Omega, feynman_line_density_per_m2=nv, feynman_line_density_per_cm2=nv * 1e-4,
        source="h exact (SI); u = scipy.constants CODATA atomic mass constant; m(He-4) = 4.00260325413 u from NIST Atomic Weights and Isotopic Compositions")
    print("kappa =", kappa, " 2*Omega/kappa per cm^2 =", nv * 1e-4)


# ------------------------------------------------------------------------------------------------------ showcase pair
def part_pair(do_circ=False):
    old = OUT.get("pair", {})
    z, meta = load("pair_d12")
    snaps = z["snaps"]; snap_t = z["snap_t"]; pos = z["pos"]; q = z["q"]
    T_SNAP = 20
    assert snap_t[T_SNAP] == T_SNAP
    c = snaps[T_SNAP]; p20 = pos[T_SNAP]
    s = make()
    ip, im = int(np.nonzero(q == 1)[0][0]), int(np.nonzero(q == -1)[0][0])
    d = float(np.hypot(*(p20[ip] - p20[im])))
    R = {}
    R["snapshot_time"] = T_SNAP; R["vortex_plus"] = p20[ip].tolist(); R["vortex_minus"] = p20[im].tolist(); R["separation_d"] = d
    R["wall_s_run"] = meta["wall_s"]; R["load_at_start_of_run"] = meta["load_at_start"]
    # ---- grid-level detection: plaquette charges and the largest phase step
    R["grid_phase"] = grid_phase_steps(c)
    # ---- torus windings (sums of principal differences around the two cycles)
    wx, wy = torus_windings(c)
    R["torus"] = dict(row_winding_values=sorted(set(np.rint(wx).astype(int).tolist())), col_winding_values=sorted(set(np.rint(wy).astype(int).tolist())),
                      max_dev_from_integer=f(max(np.abs(wx - np.rint(wx)).max(), np.abs(wy - np.rint(wy)).max())),
                      n_rows_nonzero=int(np.count_nonzero(np.rint(wx))), n_cols_nonzero=int(np.count_nonzero(np.rint(wy))),
                      mean_uy_from_windings=f(2 * np.pi * np.rint(wy).sum() * s.dx / L ** 2), mean_ux_from_windings=f(2 * np.pi * np.rint(wx).sum() * s.dx / L ** 2))
    ub = PV.sector_flow(p20, q)
    R["torus"]["sector_flow_formula"] = ub.tolist(); R["torus"]["sector_flow_magnitude"] = f(np.hypot(*ub))
    R["torus"]["kappa_d_over_L2"] = f(2 * np.pi * d / L ** 2)
    # momentum of the field
    P = z["momentum"][T_SNAP]; Nn = z["norm"][T_SNAP]
    R["momentum"] = dict(Px=f(P[0]), Py=f(P[1]), P_over_N=f(np.hypot(*P) / Nn), impulse_2pi_d=f(2 * np.pi * d), ratio_P_to_impulse=f(np.hypot(*P) / (2 * np.pi * d)),
                         P_t0=z["momentum"][0].tolist(), P_t40=z["momentum"][40].tolist())
    if do_circ:
        # ---- circulation scan (line integral) and discrete detector, around the + vortex
        cen = p20[ip]
        r_in = np.geomspace(0.15, d - 3.0, 22)
        r_near = np.array([d - 1.5, d - 0.8, d - 0.4, d - 0.2, d - 0.1, d - 0.05, d + 0.05, d + 0.1, d + 0.2, d + 0.4, d + 0.8, d + 1.5])
        r_out = np.array([d + 3.0, d + 5.0, d + 8.0, d + 12.0, d + 16.0])
        radii = np.concatenate([r_in, r_near, r_out])
        t0 = time.time()
        gam, win, pmin, smax = circulation_scan(c, cen, radii, M=1600)
        R["circulation"] = dict(M=1600, n_loops=len(radii), seconds=f(time.time() - t0))
        inner = radii < d - 1.4; outer = radii > d + 1.4
        R["circulation"]["inner_max_dev_from_1"] = f(np.abs(gam[inner] - 1).max()); R["circulation"]["outer_max_dev_from_0"] = f(np.abs(gam[outer]).max())
        R["circulation"]["inner_winding_all_1"] = bool(np.all(win[inner] == 1)); R["circulation"]["outer_winding_all_0"] = bool(np.all(win[outer] == 0))
        R["circulation"]["R_range_inner"] = [f(radii[inner].min()), f(radii[inner].max())]
        DER["circ_R"] = radii; DER["circ_gamma"] = gam; DER["circ_winding"] = win; DER["circ_min_psi"] = pmin; DER["circ_max_step_over_pi"] = smax
        # detector with fewer samples (Lean's detector_correct holds for n >= n0)
        coarse = {}
        for M in (4, 8, 16, 64, 256):
            ev = Evaluator(s, c)
            wM = np.array([loop_winding(ev, cen[0], cen[1], r, M)[0] for r in radii])
            coarse[M] = wM; DER[f"circ_winding_M{M}"] = wM
            R["circulation"][f"n_wrong_M{M}"] = int(np.sum(np.abs(wM - np.where(radii < d, 1, 0)) > 1e-9))
    else:
        for k in ("circulation", "n0_scan"):
            if k in old: R[k] = old[k]
    if "circ_R" in DER:
        Rr_, gam_, win_ = DER["circ_R"], DER["circ_gamma"], DER["circ_winding"]
        inner_ = Rr_ < d - 1.4; outer_ = Rr_ > d + 1.4; near_in = (Rr_ >= d - 1.4) & (Rr_ < d); near_out = (Rr_ <= d + 1.4) & (Rr_ > d)
        cc_ = R.setdefault("circulation", {})
        cc_.update(dict(inner_max_dev_from_1=f(np.abs(gam_[inner_] - 1).max()), outer_max_dev_from_0=f(np.abs(gam_[outer_]).max()),
                        inner_winding_all_1=bool(np.all(np.rint(win_[inner_]) == 1)), outer_winding_all_0=bool(np.all(np.rint(win_[outer_]) == 0)),
                        all_windings_correct=bool(np.all(np.rint(win_[Rr_ < d]) == 1) and np.all(np.rint(win_[Rr_ > d]) == 0)),
                        max_dev_from_integer_all=f(np.abs(gam_ - np.rint(gam_)).max()),
                        dev_at_delta=[dict(delta=f(r_ - d), dev=f(abs(g_ - np.rint(g_)))) for r_, g_ in zip(Rr_, gam_) if abs(r_ - d) <= 0.21],
                        R_range_inner=[f(Rr_[inner_].min()), f(Rr_[inner_].max())], R_max=f(Rr_.max()), n_loops=int(len(Rr_)),
                        n_loops_dev_below_1e_9=int(np.sum(np.abs(gam_ - np.rint(gam_)) < 1e-9)),
                        min_delta_with_dev_below_1e_9=f(np.min(np.abs(Rr_ - d)[np.abs(gam_ - np.rint(gam_)) < 1e-9])),
                        max_step_over_pi_any_loop=f(DER["circ_max_step_over_pi"].max())))
    # ---- fields on the 4x refined grid: velocity against the periodic point-vortex field, and the energy split
    F = madelung_fields(c, 4)
    nf = F["n"].shape[0]; dxf = F["dx"]
    xs = np.arange(nf) * dxf
    sub = 2
    Xs, Ys = np.meshgrid(xs[::sub], xs[::sub], indexing="ij")
    pts = np.column_stack([Xs.ravel(), Ys.ravel()])
    r1 = np.hypot(*(((pts - p20[ip] + L / 2) % L - L / 2).T)); r2 = np.hypot(*(((pts - p20[im] + L / 2) % L - L / 2).T))
    rmin = np.minimum(r1, r2)
    v_wm = PV.wm_velocity(pts[rmin > 0.2], p20, q)
    ux = F["ux"][::sub, ::sub].ravel()[rmin > 0.2]; uy = F["uy"][::sub, ::sub].ravel()[rmin > 0.2]
    rr = rmin[rmin > 0.2]
    gp = np.column_stack([ux, uy])
    def rel(mask, shift):
        a = gp[mask] - (v_wm[mask] + shift); b = v_wm[mask] + shift
        return f(np.sqrt((a ** 2).sum() / (b ** 2).sum()))
    vel = {}
    for lo, hi, name in ((3, 1e9, "r_ge_3"), (1.5, 3, "r_1p5_to_3"), (3, 6, "r_3_to_6"), (6, 1e9, "r_ge_6"), (0.5, 1.5, "r_0p5_to_1p5")):
        m_ = (rr >= lo) & (rr < hi)
        a_ = gp[m_] - (v_wm[m_] + ub); b_ = v_wm[m_] + ub
        vel[name] = dict(rel_rms_with_sector_flow=rel(m_, ub), rel_rms_without_sector_flow=rel(m_, 0 * ub), abs_rms_diff_with_sector_flow=f(np.sqrt((a_ ** 2).sum() / m_.sum())),
                         rms_point_vortex_speed=f(np.sqrt((b_ ** 2).sum() / m_.sum())), n_points=int(m_.sum()))
    R["velocity_vs_point_vortex"] = vel
    # what the far-field difference is: its curl-free (sound) fraction and the density ripple
    v_all = PV.wm_velocity(pts, p20, q) + ub
    dux_ = F["ux"][::sub, ::sub] - v_all[:, 0].reshape(Xs.shape); duy_ = F["uy"][::sub, ::sub] - v_all[:, 1].reshape(Xs.shape)
    far = (np.minimum(r1, r2) > 6.0).reshape(Xs.shape); mid = (np.minimum(r1, r2) > 3.0).reshape(Xs.shape)
    R["velocity_difference_is_sound"] = dict(
        curl_free_fraction_r_gt_3=longitudinal_fraction(dux_, duy_, mid, dxf * sub), curl_free_fraction_r_gt_6=longitudinal_fraction(dux_, duy_, far, dxf * sub),
        rms_difference_r_gt_6=f(np.sqrt(((dux_ ** 2 + duy_ ** 2)[far]).mean())), rms_density_fluctuation_r_gt_6=f(np.sqrt((((F["n"][::sub, ::sub] - 1) ** 2)[far]).mean())))
    # velocity cut along the line through the two cores (nearest refined row)
    jrow = int(np.argmin(np.abs(xs - 0.5 * (p20[ip][1] + p20[im][1]))))
    xc = np.arange(nf) * dxf; yc = xs[jrow] * np.ones(nf)
    vcut = PV.wm_velocity(np.column_stack([xc, yc]), p20, q) + ub
    DER["cut_x"] = xc; DER["cut_y"] = xs[jrow]; DER["cut_uy_gp"] = F["uy"][:, jrow]; DER["cut_uy_pv"] = vcut[:, 1]
    DER["cut_ux_gp"] = F["ux"][:, jrow]; DER["cut_ux_pv"] = vcut[:, 0]
    # ---- energy
    E = energy_split(c, 4)
    R["energy"] = dict(coarse=E["x1"], refined=E["x4"], E_kin_parseval=E["E_kin_parseval"], E_gp_total=E["E_gp_total"], E_int=E["E_int"],
                       E_uniform=0.5 * L ** 2, E_excess=E["E_gp_total"] - 0.5 * L ** 2)
    k4 = E["x4"]
    R["energy"]["fraction_flow"] = k4["E_flow"] / k4["E_kin"]; R["energy"]["fraction_quantum_pressure"] = k4["E_q"] / k4["E_kin"]
    edges = np.linspace(0, d - 3.0, 85)
    cum_p = radial_cumulative(F, p20[ip], edges)
    cum_m = radial_cumulative(F, p20[im], edges)
    DER["en_R"] = edges[1:]; DER["en_flow_plus"] = cum_p["flow"]; DER["en_q_plus"] = cum_p["q"]; DER["en_kin_plus"] = cum_p["kin"]; DER["en_deficit_plus"] = cum_p["deficit"]
    DER["en_flow_minus"] = cum_m["flow"]; DER["en_q_minus"] = cum_m["q"]
    # local slope dE_flow / d ln R in the window [2.5, 5]
    mwin = (edges[1:] >= 2.5) & (edges[1:] <= 5.0)
    slope = np.polyfit(np.log(edges[1:][mwin]), cum_p["flow"][mwin], 1)[0]
    slope_m = np.polyfit(np.log(edges[1:][mwin]), cum_m["flow"][mwin], 1)[0]
    # mean density on the circle r = R (annulus average) for the predicted slope pi <n>
    X, Y = np.meshgrid(np.arange(nf) * dxf, np.arange(nf) * dxf, indexing="ij")
    dxv = X - p20[ip][0]; dyv = Y - p20[ip][1]; dxv -= L * np.round(dxv / L); dyv -= L * np.round(dyv / L); rg = np.hypot(dxv, dyv)
    ann = (rg > 3.5) & (rg < 4.0)
    nbar = float(F["n"][ann].mean())
    # decomposition of the flow density about the + vortex: own azimuthal flow 1/r, partner (and uniform) flow, cross term
    xx = X - p20[ip][0]; yy = Y - p20[ip][1]; xx -= L * np.round(xx / L); yy -= L * np.round(yy / L)
    r2_ = np.maximum(xx ** 2 + yy ** 2, 1e-12)
    usx, usy = -yy / r2_, xx / r2_
    unx, uny = F["ux"] - usx, F["uy"] - usy
    pieces = dict(self=0.5 * F["n"] * (usx ** 2 + usy ** 2), cross=F["n"] * (usx * unx + usy * uny), partner=0.5 * F["n"] * (unx ** 2 + uny ** 2))
    dec = {}
    for key_, dens_ in pieces.items():
        h_, _ = np.histogram(rg.ravel(), bins=edges, weights=(dens_ * dxf ** 2).ravel())
        cum_ = np.cumsum(h_)
        dec[key_] = dict(slope=f(np.polyfit(np.log(edges[1:][mwin]), cum_[mwin], 1)[0]), within_3=f(np.interp(3.0, edges[1:], cum_)), within_6=f(np.interp(6.0, edges[1:], cum_)))
    dec["sum_of_slopes"] = f(sum(v_["slope"] for v_ in dec.values() if isinstance(v_, dict)))
    R["energy"]["flow_decomposition_plus"] = dec
    R["energy"]["flow_slope_per_lnR_plus"] = f(slope); R["energy"]["flow_slope_per_lnR_minus"] = f(slope_m)
    R["energy"]["slope_window"] = [2.5, 5.0]; R["energy"]["pi_times_mean_density_at_R3p75"] = f(np.pi * nbar); R["energy"]["mean_density_R3p75"] = nbar
    R["energy"]["q_within_3"] = f(np.interp(3.0, edges[1:], cum_p["q"])); R["energy"]["q_within_6"] = f(np.interp(6.0, edges[1:], cum_p["q"]))
    R["energy"]["q_total_over_cum_6"] = f(cum_p["q"][-1])
    R["energy"]["flow_within_3"] = f(np.interp(3.0, edges[1:], cum_p["flow"])); R["energy"]["flow_within_6"] = f(np.interp(6.0, edges[1:], cum_p["flow"]))
    # ---- core profile against the exact radial solution, azimuthal mean about the + vortex
    from ch03_gpvortex import solve as solve_vortex
    X, Y = np.meshgrid(np.arange(nf) * dxf, np.arange(nf) * dxf, indexing="ij")
    dxv = X - p20[ip][0]; dyv = Y - p20[ip][1]; dxv -= L * np.round(dxv / L); dyv -= L * np.round(dyv / L); rg = np.hypot(dxv, dyv)
    edges_p = np.linspace(0, 8, 65)
    hn, _ = np.histogram(rg.ravel(), bins=edges_p, weights=F["n"].ravel()); hc, _ = np.histogram(rg.ravel(), bins=edges_p)
    rb = 0.5 * (edges_p[1:] + edges_p[:-1]); nb = hn / np.maximum(hc, 1)
    sol = solve_vortex(R=40.0); nex = sol.sol(rb)[0] ** 2
    DER["prof_r"] = rb; DER["prof_n"] = nb; DER["prof_exact"] = nex
    R["profile"] = dict(max_abs_diff_r_le_8=f(np.max(np.abs(nb - nex))), max_abs_diff_r_ge_2=f(np.max(np.abs(nb - nex)[rb >= 2])),
                        max_abs_diff_r_ge_1=f(np.max(np.abs(nb - nex)[rb >= 1])), n_at_r1_solver=f(np.interp(1.0, rb, nb)), n_at_r1_exact=f(sol.sol(1.0)[0] ** 2),
                        slope_at_origin_exact=f(sol.sol(1e-3)[1]), far_deficit_times_2r2_at_10_exact=f((1 - sol.sol(10.0)[0] ** 2) * 2 * 100.0))
    # ---- momentum decomposition: P_y = int n u_y = int u_y - int (1 - n) u_y
    d2f = dxf ** 2
    Iu = F["uy"].sum() * d2f; Iuw = (F["n"] * F["uy"]).sum() * d2f; Idef = ((1 - F["n"]) * F["uy"]).sum() * d2f
    R["momentum"]["decomposition"] = dict(box_integral_uy_over_L2=f(Iu / L ** 2), momentum_from_field_over_L2=f(Iuw / L ** 2), deficit_term_over_L2=f(Idef / L ** 2),
                                          P_over_N=f(np.hypot(*P) / Nn), sector_flow_formula_uy=f(ub[1]))
    # ---- the grid-level detector on the refined grid (convergence of the charge count)
    chf, wf, dxf_, dyf_ = plaquette_charges(F["psi"])
    R["grid_phase_refined"] = dict(n_plus=int((chf == 1).sum()), n_minus=int((chf == -1).sum()), n_other=int((np.abs(chf) > 1).sum()),
                                   max_step_over_pi=f(max(np.abs(dxf_).max(), np.abs(dyf_).max()) / np.pi))
    # ---- the detected cores against the exact zeros of the band-limited field
    from scipy.optimize import minimize
    ev_ = Evaluator(s, c); zer = []
    for i_ in range(2):
        fz = lambda xy: float(np.abs(ev_.psi(np.array([xy[0]]), np.array([xy[1]]))[0]) ** 2)
        rz = minimize(fz, p20[i_], method="Nelder-Mead", options=dict(xatol=1e-10, fatol=1e-30, maxiter=2000))
        zer.append(dict(detected=p20[i_].tolist(), exact_zero=rz.x.tolist(), psi2_at_zero=f(rz.fun), offset=f(np.hypot(*(rz.x - p20[i_])))))
    R["zeros_of_psi"] = zer
    # ---- Madelung's dynamical equations on this snapshot (engine right-hand side; no tracking)
    R["dynamics"] = madelung_dynamics(c, [p20[ip], p20[im]], 4)
    vt = (pos[T_SNAP + 5] - pos[T_SNAP - 5]).mean(0) / 10.0                       # tracked velocity, central difference over 10 time units
    R["dynamics"]["tracked_velocity_t20"] = vt.tolist(); R["dynamics"]["tracked_speed_t20"] = float(np.hypot(*vt))
    vpv = PV.vortex_velocity(p20, q).mean(0)
    R["dynamics"]["point_vortex_velocity_t20"] = vpv.tolist(); R["dynamics"]["point_vortex_speed_t20"] = float(np.hypot(*vpv))
    # ---- drift of invariants along the run
    R["invariants"] = dict(energy_t0=f(z["energy"][0]), energy_t40=f(z["energy"][40]), energy_rel_drift=f((z["energy"][40] - z["energy"][0]) / z["energy"][0]),
                           norm_t0=f(z["norm"][0]), norm_t40=f(z["norm"][40]), norm_rel_drift=f((z["norm"][40] - z["norm"][0]) / z["norm"][0]),
                           momentum_y_t0=f(z["momentum"][0][1]), momentum_y_t40=f(z["momentum"][40][1]))
    D_t = np.hypot(*(pos[:, ip] - pos[:, im]).T)
    R["separation_t0"] = f(D_t[0]); R["separation_t40"] = f(D_t[-1])
    R["dipole_moment_y_t0_t40"] = [f(2 * np.pi / L ** 2 * (q * pos[0][:, 0]).sum()), f(2 * np.pi / L ** 2 * (q * pos[-1][:, 0]).sum())]
    DER["pair_t"] = z["t"]; DER["pair_pos"] = pos
    OUT["pair"] = R
    print(json.dumps(R, indent=1)[:3000])



def part_n0():
    """How many samples does the detector need?  Loops of radius d -/+ delta about the + vortex (the other zero outside / inside the loop),
    several generic starting angles, the worst case over the angles."""
    z, meta = load("pair_d12")
    T_SNAP = OUT["pair"]["snapshot_time"]
    c = z["snaps"][T_SNAP]; p20 = z["pos"][T_SNAP]; q = z["q"]
    ip = int(np.nonzero(q == 1)[0][0]); cen = p20[ip]; d = OUT["pair"]["separation_d"]
    Mmax = 7200
    divs = [m for m in range(3, Mmax + 1) if Mmax % m == 0]
    phis = [0.37, 0.91, 1.58, 2.33, 3.77, 5.01]
    rows = []
    t0 = time.time()
    for delta in (8.0, 4.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05):
        for side, r, deg in (("zero_outside", d - delta, 1), ("zero_inside", d + delta, 0)):
            m0s = [n0_scan(c, cen, r, divs, Mmax=Mmax, phi0=ph, degree_expected=deg)[1] for ph in phis]
            rows.append(dict(delta=delta, side=side, radius=r, degree=deg, M0_worst=int(max(m0s)), M0_median=float(np.median(m0s)), M0_all=[int(m) for m in m0s]))
            print(rows[-1], flush=True)
    n0_postprocess(rows, phis, Mmax, f(time.time() - t0))


def n0_postprocess(rows, phis, Mmax, seconds, source="ch03_compute.py part n0"):
    """Store the sampling-threshold rows with their fits (exponent of the outside-zero series, ratio to pi sqrt(R/delta))."""
    OUT["pair"]["n0_scan"] = dict(Mmax=Mmax, start_angles=phis, rows=rows, seconds=seconds, source=source)
    out_ = [r for r in rows if r["side"] == "zero_outside"]; in_ = [r for r in rows if r["side"] == "zero_inside"]
    dl = np.array([r["delta"] for r in out_]); mw = np.array([r["M0_worst"] for r in out_], float); rr = np.array([r["radius"] for r in out_])
    ok = mw > 3
    OUT["pair"]["n0_scan"]["fit_exponent_zero_outside"] = f(np.polyfit(np.log(dl[ok]), np.log(mw[ok]), 1)[0]) if ok.sum() > 2 else None
    OUT["pair"]["n0_scan"]["ratio_to_pi_sqrt_R_over_delta_zero_outside"] = [f(m / (np.pi * np.sqrt(r_ / d_))) for m, r_, d_ in zip(mw, rr, dl)]
    OUT["pair"]["n0_scan"]["max_M0_zero_inside"] = int(max(r["M0_worst"] for r in in_))
    DER["n0_delta"] = dl; DER["n0_M0_outside"] = mw; DER["n0_radius_outside"] = rr
    DER["n0_M0_inside"] = np.array([r["M0_worst"] for r in in_], float)


# ------------------------------------------------------------------------------------------------------ separation scan
def part_scan():
    rows = []
    for d0 in (4, 6, 8, 12, 16, 20):
        z, meta = load(f"pair_d{d0}")
        t = z["t"]; pos = z["pos"]; q = z["q"]
        win = t >= 10
        cen = pos.mean(1)
        vx = np.polyfit(t[win], cen[win, 0], 1)[0]; vy = np.polyfit(t[win], cen[win, 1], 1)[0]
        vmeas = np.array([vx, vy])
        D = pos[:, 0] - pos[:, 1]; dd = np.hypot(D[:, 0], D[:, 1])
        vpv0 = np.zeros(2); vpv = np.zeros(2); vplane = []
        idx = np.nonzero(win)[0]
        for k in idx:
            a = PV.vortex_velocity(pos[k], q, with_sector=False); b = PV.vortex_velocity(pos[k], q, with_sector=True)
            vpv0 += a.mean(0); vpv += b.mean(0)
        vpv0 /= len(idx); vpv /= len(idx)
        ubar = PV.sector_flow(pos[0], q)
        proj = lambda v, w: f(np.dot(v, w) / np.dot(w, w))
        rows.append(dict(d_imprint=float(d0), d_t0=f(dd[0]), d_mean=f(dd[win].mean()), d_t40=f(dd[-1]),
                         v_meas=f(np.hypot(*vmeas)), v_meas_vec=vmeas.tolist(), v_plane_1_over_d=f((1 / dd[win]).mean()),
                         v_pv_zero_mean_flow=f(np.hypot(*vpv0)), v_pv_with_sector_flow=f(np.hypot(*vpv)), sector_flow_t0=f(np.hypot(*ubar)),
                         ratio_to_plane=f(np.hypot(*vmeas) / (1 / dd[win]).mean()),
                         ratio_to_pv_zero_mean=proj(vmeas, vpv0), ratio_to_pv_with_sector=proj(vmeas, vpv),
                         momentum_y_t0=f(z["momentum"][0][1]), momentum_y_t40=f(z["momentum"][-1][1]),
                         energy_rel_drift=f((z["energy"][-1] - z["energy"][0]) / z["energy"][0]), wall_s=meta["wall_s"], load_at_start=meta["load_at_start"]))
        print(rows[-1])
    OUT["scan"] = dict(window="t in [10, 40], linear fit of the pair centre; predictions from the instantaneous tracked positions, averaged over the window", rows=rows)
    for key in ("d_mean", "v_meas", "v_plane_1_over_d", "v_pv_zero_mean_flow", "v_pv_with_sector_flow", "ratio_to_pv_with_sector", "ratio_to_pv_zero_mean", "ratio_to_plane"):
        DER[f"scan_{key}"] = np.array([r[key] for r in rows])


# ------------------------------------------------------------------------------------------------------ leapfrog
def part_quad():
    z, meta = load("quad")
    t = z["t"]; pos = z["pos"]; q = z["q"]
    R = dict(T=f(t[-1]), wall_s_run=meta["wall_s"], load_at_start_of_run=meta["load_at_start"])
    t0 = time.time()
    traj, nfe = PV.integrate_cvode(pos[0], q, t, rtol=1e-10, atol=1e-10, method="adams")
    import rusty_sundials
    cv_commit = ""
    cpath = Path("/mnt/data/xdev-cache/rs_py_5db8041/commit.txt")
    if cpath.exists(): cv_commit = cpath.read_text().strip()
    R["cvode"] = dict(method="adams", rtol=1e-10, atol=1e-10, rhs_calls=int(nfe), seconds=f(time.time() - t0), segments=len(t) - 1,
                      rusty_sundials_file=str(rusty_sundials.__file__), rusty_sundials_build=cv_commit)
    t0 = time.time()
    ref = PV.integrate_dop853(pos[0], q, t)
    R["dop853_check"] = dict(max_abs_diff_cvode_vs_dop853=f(np.abs(traj - ref).max()), seconds=f(time.time() - t0))
    dip = np.array([(q[:, None] * tr).sum(0) for tr in traj])
    R["cvode_dipole_moment_drift"] = f(np.abs(dip - dip[0]).max())
    dip_gp = np.array([(q[:, None] * tr).sum(0) for tr in pos])
    R["gp_dipole_moment_t0_t120"] = [dip_gp[0].tolist(), dip_gp[-1].tolist()]
    R["gp_dipole_moment_rel_change"] = f(np.hypot(*(dip_gp[-1] - dip_gp[0])) / np.hypot(*dip_gp[0]))
    err = np.abs(pos - traj).max(axis=(1, 2)); errv = np.hypot(*(pos - traj).transpose(2, 0, 1))
    R["max_position_error_vs_t"] = {str(int(tt)): f(err[int(tt)]) for tt in (10, 20, 30, 40, 60, 80, 100, 120) if int(tt) < len(t)}
    R["max_position_error_overall"] = f(err.max())
    # pair labels: 0 = + (left), 1 = - (right) of the rear pair; 2 = + , 3 = - of the front pair
    yrear = lambda P: 0.5 * (P[:, 0, 1] + P[:, 1, 1]); yfront = lambda P: 0.5 * (P[:, 2, 1] + P[:, 3, 1])
    gap_gp = yrear(pos) - yfront(pos); gap_ode = yrear(traj) - yfront(traj)
    def crossing(gap):
        i = np.nonzero((gap[:-1] < 0) & (gap[1:] >= 0))[0]
        return [f(t[j] - gap[j] / (gap[j + 1] - gap[j]) * (t[j + 1] - t[j])) for j in i]
    R["pass_times"] = dict(gp=crossing(gap_gp), reduced_model=crossing(gap_ode))
    wid = lambda P, a, b: np.hypot(*(P[:, a] - P[:, b]).T)
    R["pair_widths"] = dict(rear_gp=[f(wid(pos, 0, 1)[0]), f(wid(pos, 0, 1).min())], front_gp=[f(wid(pos, 2, 3)[0]), f(wid(pos, 2, 3).max())],
                            rear_ode_min=f(wid(traj, 0, 1).min()), front_ode_max=f(wid(traj, 2, 3).max()))
    R["min_separation_gp"] = f(min(np.hypot(*(pos[:, a] - pos[:, b]).T).min() for a in range(4) for b in range(a + 1, 4)))
    R["min_separation_ode"] = f(min(np.hypot(*(traj[:, a] - traj[:, b]).T).min() for a in range(4) for b in range(a + 1, 4)))
    R["y_range_gp"] = [f(pos[:, :, 1].min()), f(pos[:, :, 1].max())]
    R["energy_rel_drift_gp"] = f((z["energy"][-1] - z["energy"][0]) / z["energy"][0]); R["norm_rel_drift_gp"] = f((z["norm"][-1] - z["norm"][0]) / z["norm"][0])
    DER["quad_t"] = t; DER["quad_pos_gp"] = pos; DER["quad_pos_ode"] = traj; DER["quad_err"] = err
    if "stale_first_run" in OUT.get("quad", {}): R["stale_first_run"] = OUT["quad"]["stale_first_run"]    # record of the first run with the stale module (kept for the honest box)
    OUT["quad"] = R
    print(json.dumps(R, indent=1))



def part_restart():
    """Where does the leapfrog discrepancy come from?  Restart the reduced model (DOP853, cheap) from the tracked positions at later times."""
    z, meta = load("quad")
    t = z["t"]; pos = z["pos"]; q = z["q"]
    yr = lambda P: 0.5 * (P[:, 0, 1] + P[:, 1, 1]); yf = lambda P: 0.5 * (P[:, 2, 1] + P[:, 3, 1])
    def crossing(tt, gap):
        i = np.nonzero((gap[:-1] < 0) & (gap[1:] >= 0))[0]
        return [f(tt[j] - gap[j] / (gap[j + 1] - gap[j]) * (tt[j + 1] - tt[j])) for j in i]
    rows = []
    for t0 in (0, 5, 10, 20, 30, 40):
        k0 = int(t0); tg = t[k0:]
        traj = PV.integrate_dop853(pos[k0], q, tg)
        err = np.abs(pos[k0:] - traj).max(axis=(1, 2))
        cr = crossing(tg, yr(traj) - yf(traj))
        rows.append(dict(t_start=t0, err_after_10=f(err[10]), err_after_20=f(err[20]), err_max=f(err.max()), err_mean=f(err.mean()), pass_time_model=cr))
    OUT.setdefault("quad", {})["restart"] = dict(integrator="scipy DOP853, rtol=atol=1e-12", rows=rows, pass_time_solver=crossing(t, yr(pos) - yf(pos)))
    print(json.dumps(OUT["quad"]["restart"], indent=1))

# ------------------------------------------------------------------------------------------------------ macros
def tex_sci(x, nd=0):
    """3.9e-10 -> '4\times10^{-10}' (to be used inside math mode)."""
    m, e = f"{x:.{nd}e}".split("e")
    return r"%s\times10^{%d}" % (m, int(e))


def write_macros():
    ex3 = FIGS / "ch03_exercise3.json"
    if ex3.exists():
        OUT["exercise3"] = json.loads(ex3.read_text())
    M = {}
    def put(key, val): M[key] = val
    if "fourier_check" in OUT:
        put("fourierDiff", tex_sci(OUT["fourier_check"]["max_abs_diff"]))
    c_ = OUT.get("constants")
    if c_:
        put("kappaHeFour", f"{c_['kappa_SI_m2_per_s'] * 1e8:.3f}")
        put("feynmanDens", r"%.1f\times10^{3}" % (c_["feynman_line_density_per_cm2"] / 1e3))
        put("mHeU", f"{c_['m_He4_u']:.9f}")
    sc = OUT.get("scan")
    if sc:
        rows = sc["rows"]
        nm = {4: "Four", 6: "Six", 8: "Eight", 12: "Twelve", 16: "Sixteen", 20: "Twenty"}
        for r in rows:
            k = nm[int(r["d_imprint"])]
            put(f"scan{k}RatioPvz", f"{r['ratio_to_pv_zero_mean']:.2f}"); put(f"scan{k}RatioPv", f"{r['ratio_to_pv_with_sector']:.3f}")
            put(f"scan{k}Meas", f"{r['v_meas']:.4f}")
            put(f"scan{k}D", f"{r['d_mean']:.1f}")
        pl = {int(r["d_imprint"]): 100 * (r["ratio_to_plane"] - 1) for r in rows}
        put("pctPlaneMin", f"{min(pl[4], pl[6], pl[8]):.1f}"); put("pctPlane8", f"{max(pl[4], pl[6], pl[8]):.1f}")
        put("pctPlane12", f"{pl[12]:.0f}"); put("pctPlane16", f"{pl[16]:.0f}"); put("pctPlane20", f"{pl[20]:.0f}")
        put("pctPvFour", f"{100 * (rows[0]['ratio_to_pv_with_sector'] - 1):.1f}")
        put("scanSixPctPv", f"{100 * (rows[1]['ratio_to_pv_with_sector'] - 1):.1f}")
        walls = [r["wall_s"] for r in rows]                                  # the six 40-time-unit runs
        loads = [r["load_at_start"] for r in rows] + ([OUT["quad"]["load_at_start_of_run"]] if "quad" in OUT else [])    # load average when each of the seven runs started
        put("runLoadLo", f"{min(loads):.0f}"); put("runLoadHi", f"{max(loads):.0f}"); put("runWallLo", f"{min(walls):.0f}"); put("runWallHi", f"{max(walls):.0f}")
        r20 = [r for r in rows if int(r["d_imprint"]) == 20][0]
        put("ubarOverV20", f"{100 * r20['sector_flow_t0'] * r20['d_t0']:.0f}")
        # the table
        lines = [r"\begin{tabular}{@{}rccccccc@{}}", r"\toprule",
                 r"$d/\xi$ & measured & plane & torus, & torus $+$ & \multicolumn{3}{c}{measured $/$}\\",
                 r" & & $1/d$ & zero flow & winding flow & plane & zero flow & $+$ flow\\", r"\midrule"]
        for r in rows:
            lines.append(f"{r['d_mean']:.1f} & {r['v_meas']:.4f} & {r['v_plane_1_over_d']:.4f} & {r['v_pv_zero_mean_flow']:.4f} & {r['v_pv_with_sector_flow']:.4f} & "
                         f"{r['ratio_to_plane']:.3f} & {r['ratio_to_pv_zero_mean']:.3f} & {r['ratio_to_pv_with_sector']:.3f}\\\\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        (FIGS / "ch03_table_scan.tex").write_text("\n".join(lines) + "\n")
    p = OUT.get("pair")
    if p:
        put("pairD", f"{p['separation_d']:.1f}")
        g = p["grid_phase"]
        put("maxStepOverPi", f"{g['max_step_over_pi']:.2f}"); put("nPlus", str(g["n_plus"])); put("nMinus", str(g["n_minus"])); put("nOther", str(g["n_other"]))
        put("plaqDev", tex_sci(g["max_dev_from_integer"]))
        gr = p["grid_phase_refined"]; put("maxStepRefined", f"{gr['max_step_over_pi']:.2f}")
        v = p["velocity_vs_point_vortex"]
        put("velRelInner", f"{100 * v['r_1p5_to_3']['rel_rms_with_sector_flow']:.1f}"); put("velRelThreeSix", f"{100 * v['r_3_to_6']['rel_rms_with_sector_flow']:.1f}")
        put("velRelThreeSixNoSector", f"{100 * v['r_3_to_6']['rel_rms_without_sector_flow']:.1f}")
        put("velFarRms", f"{v['r_ge_6']['abs_rms_diff_with_sector_flow']:.3f}"); put("velFarPV", f"{v['r_ge_6']['rms_point_vortex_speed']:.3f}")
        sd = p["velocity_difference_is_sound"]
        put("curlFree", f"{100 * sd['curl_free_fraction_r_gt_6']:.1f}"); put("rmsDn", f"{sd['rms_density_fluctuation_r_gt_6']:.3f}")
        d_ = p["dynamics"]
        put("contRel", f"{100 * d_['continuity_rel_rms_r_ge_3']:.1f}"); put("projIdentity", tex_sci(d_["projector_identity_max_abs_diff"])); put("projResidualMax", f"{d_['max_abs_residual']:.3f}")
        iv = p["invariants"]
        put("energyDrift", tex_sci(abs(iv["energy_rel_drift"]))); put("normDrift", tex_sci(abs(iv["norm_rel_drift"])))
        put("momDrift", tex_sci(abs(iv["momentum_y_t40"] - iv["momentum_y_t0"]) / iv["momentum_y_t0"]))
        put("sepTzero", f"{p['separation_t0']:.1f}"); put("sepTforty", f"{p['separation_t40']:.1f}")
        put("dipoleMomRelShrink", f"{100 * (1 - p['separation_t40'] / p['separation_t0']):.1f}")
        cc = p["circulation"]
        put("circRmax", f"{cc['R_max']:.1f}"); put("circLoops", str(cc["n_loops"])); put("circRlo", f"{cc['R_range_inner'][0]:.2f}"); put("circRhi", f"{cc['R_range_inner'][1]:.1f}")
        put("circInnerDev", tex_sci(cc["inner_max_dev_from_1"])); put("circOuterDev", tex_sci(cc["outer_max_dev_from_0"]))
        dev = {round(abs(x["delta"]), 2): [] for x in cc["dev_at_delta"]}
        for x in cc["dev_at_delta"]: dev[round(abs(x["delta"]), 2)].append(x["dev"])
        put("devDelta02", tex_sci(max(dev[0.2]))); put("devDelta01", tex_sci(max(dev[0.1]))); put("devDelta005", tex_sci(max(dev[0.05])))
        n0 = p.get("n0_scan")
        if isinstance(n0, dict):
            rowsn = n0["rows"]; d0 = p["separation_d"]
            out_ = [r for r in rowsn if r["side"] == "zero_outside"]; in_ = [r for r in rowsn if r["side"] == "zero_inside"]
            put("n0Mmax", str(n0["Mmax"]))
            put("n0OutFar", str(out_[0]["M0_worst"])); put("n0OutNear", str(out_[-1]["M0_worst"])); put("n0DeltaNear", f"{out_[-1]['delta']:g}"); put("n0DeltaFar", f"{out_[0]['delta']:g}")
            put("n0InMax", str(max(r["M0_worst"] for r in in_)))
            dl = np.array([r["delta"] for r in out_]); mw = np.array([r["M0_worst"] for r in out_], float); rr = np.array([r["radius"] for r in out_])
            okk = mw > 3
            put("n0OutExp", f"{np.polyfit(np.log(dl[okk]), np.log(mw[okk]), 1)[0]:.2f}")
            ratio = mw[okk] / (np.pi * np.sqrt(rr[okk] / dl[okk]))
            put("n0RatioLo", f"{ratio.min():.2f}"); put("n0RatioHi", f"{ratio.max():.2f}")
        t_ = p["torus"]
        put("torusDev", tex_sci(t_["max_dev_from_integer"])); put("nColsNonzero", str(t_["n_cols_nonzero"]))
        put("ubarWinding", f"{t_['mean_uy_from_windings']:.4f}"); put("ubarFormula", f"{t_['sector_flow_magnitude']:.4f}")
        put("ubarOverV", f"{100 * t_['sector_flow_magnitude'] * p['separation_d']:.0f}")
        m_ = p["momentum"]
        put("momPy", f"{m_['Py']:.2f}"); put("momImpulse", f"{m_['impulse_2pi_d']:.2f}"); put("momRatio", f"{100 * m_['ratio_P_to_impulse']:.1f}")
        md = m_["decomposition"]
        put("ubarBox", f"{md['box_integral_uy_over_L2']:.4f}"); put("momDeficitPct", f"{100 * md['deficit_term_over_L2'] / md['box_integral_uy_over_L2']:.1f}")
        e = p["energy"]
        put("pointwiseErr", tex_sci(e["refined"]["pointwise_max"])); put("pointwiseErrCoarse", tex_sci(e["coarse"]["pointwise_max"]))
        put("eKin", f"{e['refined']['E_kin']:.2f}"); put("eKinParseval", f"{e['E_kin_parseval']:.2f}"); put("eFlow", f"{e['refined']['E_flow']:.2f}"); put("eQ", f"{e['refined']['E_q']:.2f}")
        put("fracFlow", f"{100 * e['fraction_flow']:.1f}"); put("fracQ", f"{100 * e['fraction_quantum_pressure']:.1f}"); put("eExcess", f"{e['E_excess']:.2f}")
        put("qWithinThree", f"{e['q_within_3']:.2f}"); put("qWithinSix", f"{e['q_within_6']:.2f}"); put("flowWithinThree", f"{e['flow_within_3']:.2f}"); put("flowWithinSix", f"{e['flow_within_6']:.2f}")
        put("slopePlus", f"{e['flow_slope_per_lnR_plus']:.2f}"); put("slopeMinus", f"{e['flow_slope_per_lnR_minus']:.2f}")
        dec = e["flow_decomposition_plus"]
        put("slopeSelf", f"{dec['self']['slope']:.2f}"); put("slopePartner", f"{dec['partner']['slope']:.2f}"); put("slopeCross", f"{dec['cross']['slope']:.3f}")
        put("nbarR", f"{e['mean_density_R3p75']:.3f}"); put("slopePredicted", f"{e['pi_times_mean_density_at_R3p75']:.2f}")
        pr = p["profile"]
        put("profMaxDiff", f"{pr['max_abs_diff_r_le_8']:.3f}"); put("nAtR1Solver", f"{pr['n_at_r1_solver']:.3f}"); put("nAtR1Exact", f"{pr['n_at_r1_exact']:.3f}")
        put("fSlope", f"{pr['slope_at_origin_exact']:.3f}")
        zz = p["zeros_of_psi"]
        put("zeroPsiMax", tex_sci(max(z_["psi2_at_zero"] for z_ in zz))); put("zeroOffset", f"{max(z_['offset'] for z_ in zz):.3f}")
    qd = OUT.get("quad")
    if qd:
        put("quadT", f"{qd['T']:.0f}")
        put("cvodeCalls", f"{qd['cvode']['rhs_calls']:,}".replace(",", r"\,")); put("cvodeSeconds", f"{qd['cvode']['seconds']:.0f}")
        if "stale_first_run" in qd:
            put("staleCalls", f"{qd['stale_first_run']['rhs_calls']:,}".replace(",", r"\,")); put("staleVsDop", tex_sci(qd["stale_first_run"]["max_abs_diff_cvode_vs_dop853"]))
        put("cvodeVsDop", tex_sci(qd["dop853_check"]["max_abs_diff_cvode_vs_dop853"])); put("cvodeDipole", tex_sci(qd["cvode_dipole_moment_drift"]))
        for k_, v_ in qd["max_position_error_vs_t"].items():
            put(f"quadErr{k_}", f"{v_:.2f}")
        put("quadErrMax", f"{qd['max_position_error_overall']:.2f}")
        pg, po = qd["pass_times"]["gp"][0], qd["pass_times"]["reduced_model"][0]
        put("passGP", f"{pg:.1f}"); put("passODE", f"{po:.1f}"); put("passDiffPct", f"{100 * abs(pg - po) / pg:.0f}"); put("passDiff", f"{abs(pg - po):.1f}")
        pw = qd["pair_widths"]
        put("quadWidth0", f"{pw['rear_gp'][0]:.1f}"); put("quadRearMin", f"{pw['rear_gp'][1]:.2f}"); put("quadRearMinODE", f"{pw['rear_ode_min']:.2f}")
        put("quadFrontMax", f"{pw['front_gp'][1]:.1f}"); put("quadFrontMaxODE", f"{pw['front_ode_max']:.1f}")
        put("quadMinSepGP", f"{qd['min_separation_gp']:.2f}")
        put("quadDipoleChange", f"{100 * qd['gp_dipole_moment_rel_change']:.1f}"); put("quadEnergyDrift", tex_sci(abs(qd["energy_rel_drift_gp"])))
        zq = np.load(f"{CACHE}/quad.npz")
        put("quadMomDrift", tex_sci(abs(zq["momentum"][-1][1] - zq["momentum"][0][1]) / zq["momentum"][0][1]))
        pq = zq["pos"][-1]
        put("quadYLead", f"{0.5 * (pq[0][1] + pq[1][1]) - 0.5 * (pq[2][1] + pq[3][1]):.1f}")
        rs = qd.get("restart")
        if rs:
            for r_ in rs["rows"]:
                t0_ = r_["t_start"]
                put(f"restartPass{t0_}", f"{r_['pass_time_model'][0]:.1f}" if r_["pass_time_model"] else "none")
                put(f"restartErrTen{t0_}", f"{r_['err_after_10']:.2f}"); put(f"restartErrMax{t0_}", f"{r_['err_max']:.2f}")
    ex = OUT.get("exercise3")
    if ex:
        put("exLBox", f"{ex['L']:.0f}"); put("exVmeas", f"{ex['v_meas']:.4f}"); put("exVplane", f"{ex['v_plane']:.4f}"); put("exVpvz", f"{ex['v_pv_zero_mean_flow']:.4f}")
        put("exVpv", f"{ex['v_pv_with_sector_flow']:.4f}"); put("exRatio", f"{ex['ratio_to_pv_with_sector']:.3f}"); put("exRatioPvz", f"{ex['ratio_to_pv_zero_mean']:.3f}")
        put("exUbar", f"{ex['sector_flow']:.4f}"); put("exWall", f"{ex['wall_s']:.0f}"); put("exLoad", f"{ex['load_at_start']:.0f}")
    lines = ["% generated by ch03_compute.py from ch03_numbers.json -- do not edit"]
    for k, v in M.items():
        lines.append("\\expandafter\\def\\csname cthree@%s\\endcsname{%s}" % (k, v))
    TEX_PATH.write_text("\n".join(lines) + "\n")
    OUT["macros"] = M


if __name__ == "__main__":
    parts = sys.argv[1:] or ["const", "pair", "n0", "scan", "quad"]
    if "const" in parts: part_const(); part_fourier_check()
    if "pair" in parts or "circ" in parts: part_pair(do_circ="circ" in parts)
    if "n0" in parts: part_n0()
    if "scan" in parts: part_scan()
    if "quad" in parts: part_quad()
    if "restart" in parts: part_restart()
    write_macros()
    JSON_PATH.write_text(json.dumps(OUT, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    np.savez(NPZ_PATH, **DER)
    print("wrote", JSON_PATH, NPZ_PATH, TEX_PATH)
