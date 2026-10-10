"""Chapter 1, 'speed budget': where does the translation speed of a vortex-antivortex pair in a periodic box come from?
The pair of ch01_triptych.py (separation about 12 xi, box 64 xi) is tracked for 60 time units with qf_pgpe (rusty-SUNDIALS, Rust PGPE engine).
Prediction: planar point vortices move at 1/d (hbar = m = 1, circulation 2 pi); on a torus the Weiss-McWilliams sum of the periodic images (the
programme's transport_estimators.pv_velocity) lowers it; and the fluid as a whole moves with the mean velocity u = P/(n L^2) set by the
pair's momentum, which the point-vortex formula does not contain.  The integer windings of the phase around the two non-contractible cycles
of the torus (QuantumFluids.VortexWinding.loop_sum_eq_mul) show that such a mean flow cannot be zero: this is checked on the field itself.
Run:  PYTHONPATH=/mnt/data/xdev-cache/qf_ext  flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice .venv/bin/python book/figures/ch01_budget.py
Writes ch01_budget.{pdf,png} and the section "budget" of ch01_numbers.json."""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch01_common import *
from transport_estimators import pv_velocity, unwrap
from scipy import stats

plt.rcParams["axes.unicode_minus"] = False
T_TRACK, T_FIT0 = 60, 20
REDRAW = "--redraw" in sys.argv          # redraw the figure from ch01_numbers.json without running the solver
t_start = time.time()
if not REDRAW:
    s = engine()
    c = s.imprint_v2(s.uniform(), IMPRINT, CHARGE)
    P0 = s.momentum(c); Nrm = s.norm(c); E0 = s.energy(c)
    u_vec = np.array(P0) / Nrm                                      # mean (mass-weighted) velocity of the whole fluid
    pdet, qdet = s.detect(c)
    last = pdet[[int(np.nonzero(qdet == qq)[0][0]) for qq in CHARGE]]
    R = [last.copy()]; T = [0.0]
    snap10 = None
    for k in range(T_TRACK):
        c = s.run(c, 1.0); dp, dq = s.detect(c)
        cur = []
        for i, qq in enumerate(CHARGE):
            cand = np.nonzero(dq == qq)[0]
            dd = dp[cand] - last[i]; dd -= L * np.round(dd / L)
            cur.append(dp[cand[int(np.argmin(np.hypot(dd[:, 0], dd[:, 1])))]])
        last = np.array(cur); R.append(last.copy()); T.append(k + 1.0)
        if k + 1 == 10: snap10 = (np.array(c), last.copy())
    seconds = time.time() - t_start
    P1 = s.momentum(c); E1 = s.energy(c); N1 = s.norm(c)
    R = np.array(R); T = np.array(T); U = unwrap(R, L)
    cen = 0.5 * (U[:, 0] + U[:, 1]); sep_vec = U[:, 0] - U[:, 1]; sep = np.hypot(sep_vec[:, 0], sep_vec[:, 1])
    vpv_all = np.array([0.5 * (pv_velocity(np.mod(U[k], L), CHARGE, L)[0] + pv_velocity(np.mod(U[k], L), CHARGE, L)[1]) for k in range(len(T))])

    def fit(t0):
        m = T >= t0
        ry = stats.linregress(T[m], cen[m, 1]); rx = stats.linregress(T[m], cen[m, 0])
        vpv = vpv_all[m].mean(0); d = sep[m].mean()
        return dict(t0=t0, v_meas_y=ry.slope, v_meas_y_stderr=ry.stderr, v_meas_x=rx.slope, d_mean=float(d), d_std=float(sep[m].std()), v_planar=1.0 / d,
                    v_pv_torus_y=float(vpv[1]), v_pv_torus_x=float(vpv[0]))
    fits = {str(t0): fit(t0) for t0 in (10, 20, 30)}
    F = fits[str(T_FIT0)]
    u_y = float(u_vec[1])
    pred = F["v_pv_torus_y"] + u_y
    # ---- the integer windings of the two non-contractible cycles, on the field at t = 10, exact line integrals of the band-limited field
    c10, last10 = snap10
    fd10 = fourier_data(c10)
    xs_v = sorted(float(x) for x in last10[:, 0])
    cycles = {}
    for x0 in (10.0, 32.0, 54.0):
        cycles[f"vertical x={x0:g}"] = line_integral(fd10, (x0, 0.0), (x0, L), pieces=24) / (2 * np.pi)
    for y0 in (10.0, 54.0):
        cycles[f"horizontal y={y0:g}"] = line_integral(fd10, (0.0, y0), (L, y0), pieces=24) / (2 * np.pi)
    dx_sep = float(abs(last10[0, 0] - last10[1, 0]))
    n_in = cycles["vertical x=32"]; n_out = 0.5 * (cycles["vertical x=10"] + cycles["vertical x=54"])
    u_wind = 2 * np.pi / L ** 2 * (n_in * dx_sep + n_out * (L - dx_sep))
    out = dict(N=N, L=L, t_track=T_TRACK, fit_from=T_FIT0, fits=fits,
               u_mean_flow_P_over_N=u_y, u_vec=u_vec.tolist(), P_t0=list(P0), P_t60=list(P1), momentum_y_rel_drift=float(abs(P1[1] - P0[1]) / abs(P0[1])),
               u_incompressible_2pi_d_over_L2=float(2 * np.pi * F["d_mean"] / L ** 2),
               v_pred_torus_plus_u=float(pred), v_pred_minus_planar=float(pred - F["v_planar"]), images_correction=float(F["v_pv_torus_y"] - F["v_planar"]),
               rel_dev_meas_vs_pred=float(F["v_meas_y"] / pred - 1), rel_dev_meas_vs_pred_t10=float(fits["10"]["v_meas_y"] / (fits["10"]["v_pv_torus_y"] + u_y) - 1),
               rel_dev_meas_vs_pred_t30=float(fits["30"]["v_meas_y"] / (fits["30"]["v_pv_torus_y"] + u_y) - 1),
               ratio_box_frame_meas_over_torus_pv=float(F["v_meas_y"] / F["v_pv_torus_y"]), ratio_fluid_frame=float((F["v_meas_y"] - u_y) / F["v_pv_torus_y"]),
               cycle_windings_t10=cycles, x_separation_t10=dx_sep, u_from_windings=float(u_wind), u_P_over_u_windings=float(u_y / u_wind),
               separation_vs_t={str(int(t)): float(d) for t, d in zip(T, sep) if int(t) % 5 == 0},
               energy_rel_drift_60=float(abs(E1 - E0) / E0), norm_rel_drift_60=float(abs(N1 - Nrm) / Nrm), detected_pos_t10=last10.tolist(),
               track_t=T.tolist(), track_center_x=cen[:, 0].tolist(), track_center_y=cen[:, 1].tolist(),
           seconds=seconds, machine=machine_note())
    update_numbers("budget", out)
    print(json.dumps(out, indent=1))

else:
    out = json.load(open(Path(__file__).with_name("ch01_numbers.json")))["budget"]
    T = np.array(out["track_t"]); cen = np.column_stack([out["track_center_x"], out["track_center_y"]])
    fits = out["fits"]; F = fits[str(T_FIT0)]; u_y = out["u_mean_flow_P_over_N"]; pred = out["v_pred_torus_plus_u"]

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(TEXTW, 2.95))
gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.62)
ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])
m = T >= T_FIT0
t = T[m]; yc = cen[m, 1] - cen[m, 1][0]
ax.plot(t, F["v_planar"] * (t - t[0]), color=GREY, lw=1.1, ls=(0, (4, 2)), label=r"planar point vortices, $1/d$")
ax.plot(t, F["v_pv_torus_y"] * (t - t[0]), color=ORANGE, lw=1.3, label="periodic images (torus)")
ax.plot(t, pred * (t - t[0]), color=TEAL, lw=1.5, label=r"images $+$ mean flow $u$")
ax.plot(t, yc, "o", color=BLUE, ms=2.6, label="solver (tracked cores)")
ax.set_xlabel(r"time $t$ ($\xi/c$)"); ax.set_ylabel(r"displacement along $y$ ($\xi$)")
ax.set_xlim(T_FIT0 - 1, T_TRACK + 1)
ax.legend(loc="upper left", fontsize=7.6, handlelength=1.8, borderaxespad=0.2)
panel(ax, "a")
# waterfall of the speed
vals = [F["v_planar"], F["v_pv_torus_y"] - F["v_planar"], u_y, pred, F["v_meas_y"]]
labs = [r"planar pair, $1/d$", "periodic images", r"mean flow $u=P/N$", "prediction", "solver"]
left = [0, F["v_planar"], F["v_pv_torus_y"], 0, 0]
wid = [F["v_planar"], F["v_pv_torus_y"] - F["v_planar"], u_y, pred, F["v_meas_y"]]
cl = [GREY, ORANGE, TEAL, TEAL, BLUE]
yy = np.arange(len(vals))[::-1]
for yv, l0, w, cc in zip(yy, left, wid, cl):
    bx.barh(yv, w, left=l0, color=cc, height=0.62, alpha=0.9 if cc != TEAL or yv == yy[3] else 0.9, lw=0)
txt = [f"{F['v_planar']:.4f}", f"{F['v_pv_torus_y'] - F['v_planar']:+.4f}", f"{u_y:+.4f}", f"{pred:.4f}", f"{F['v_meas_y']:.4f}"]
spread = [fits[k]["v_meas_y"] for k in fits]                       # fits starting at t = 10, 20, 30
bx.errorbar(F["v_meas_y"], yy[4], xerr=[[F["v_meas_y"] - min(spread)], [max(spread) - F["v_meas_y"]]], color="#111111", lw=1.0, capsize=2.5, zorder=5)
for j, (yv, l0, w, tx) in enumerate(zip(yy, left, wid, txt)):
    x_end = max(l0, l0 + w) if j < 4 else max(spread)
    bx.text(x_end + 0.002, yv, tx, va="center", ha="left", fontsize=7.8, color="#222222")
bx.set_yticks(yy); bx.set_yticklabels(labs, fontsize=8)
bx.set_xlim(0, 0.125); bx.set_xlabel(r"speed of the pair ($c$)")
bx.spines["left"].set_visible(False); bx.tick_params(axis="y", length=0)
bx.text(0.004, yy[4], rf"{100 * out['rel_dev_meas_vs_pred']:+.1f} % from the prediction", fontsize=7.4, color="white", ha="left", va="center")
panel(bx, "b"); bx.texts[-1].set_position((-0.55, 1.04))
save(fig, "ch01_budget")
