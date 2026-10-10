"""Chapter 7, Figure 5: measuring the friction in the field.
 (a) the energy identity of DissipativeVortexDynamics.energy_dissipation on the tracks of the fresh Rust run (ch07_pairrun.py): the change of the
     point-vortex energy H(t) - H(0) against I(t) = int 2 sum_i |v_s,i|^2 dt is a straight line of slope -alpha (hbar = m = 1);
 (b) single-run estimates of alpha at T = 0.115 (energy estimator): the 8 archived runs of the campaign and the fresh run;
 (c) the friction against the temperature for the six arms (three cutoffs) of the friction-law campaign, with the line alpha = a T;
 (d) the same data against the normal fraction of the base state, with the three lines through the origin of a fixed coefficient at each cutoff.
The estimators are the programme's registered ones (exploration/pgpe/transport_estimators.py), evaluated here through the Rust extension
qf_pgpe.analyse_tracks, which agrees with the Python code to 6e-16 on the 8 archived tracks (see 'estimator_crosscheck' in ch07_numbers.json).
    PYTHONPATH=/mnt/data/xdev-cache/qf_ext python ch07_friction.py [tag]"""
import sys, json, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch07_common import addnum
ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"
sys.path.insert(0, str(ROOT / "exploration/pgpe"))
import qf_pgpe
from transport_estimators import pv_energy, pv_velocity, min_opposite_distance
tag = sys.argv[1] if len(sys.argv) > 1 else "e060_d10_s7"
L = 64.0; res = {}
import hashlib, os, time as _time
_qf = Path(qf_pgpe.__file__).resolve(); res["qf_pgpe_module"] = dict(path=str(_qf), sha256=hashlib.sha256(_qf.read_bytes()).hexdigest(), mtime=_time.strftime("%Y-%m-%d %H:%M", _time.localtime(os.path.getmtime(_qf))))


# BOOK-BEGIN rust_estimators
def load_tracks(files):
    out = []
    for f in files:
        z = np.load(f, allow_pickle=True); out.append((z["t"].astype(float), z["R"].astype(float), z["q"].astype(np.int64)))
    return out


def est(tracks):
    return qf_pgpe.analyse_tracks([(t, R, q) for t, R, q in tracks], L)
# BOOK-END rust_estimators


def identity_series(tt, RR, qq, settle=100.0, d_valid=4.0):
    """H(t) and I(t) = int 2 sum_i |v_s,i|^2 dt of a track, with the registered settling time and validity cut (stop where a vortex and an antivortex are closer than 4)"""
    close = np.array([min_opposite_distance(np.mod(RR[k], L), qq, L) < d_valid for k in range(len(tt))]); n_ok = int(np.argmax(close)) if close.any() else len(tt)
    m = tt[:n_ok] >= settle; t_ = tt[:n_ok][m]; R_ = RR[:n_ok][m]
    H_ = np.array([pv_energy(np.mod(R_[k], L), qq, L) for k in range(len(t_))])
    S_ = np.array([float((pv_velocity(np.mod(R_[k], L), qq, L) ** 2).sum()) for k in range(len(t_))])
    I_ = np.concatenate([[0.0], np.cumsum(0.5 * (S_[1:] + S_[:-1]) * np.diff(t_))]) * 2.0
    return t_, H_, I_


# ------------------------------------------------------------------ the fresh run
zf = np.load(tag if tag.endswith(".npz") else f"/mnt/data/xdev-cache/book_ch07/ch07_pairrun_{tag}.npz", allow_pickle=True); mf = json.loads(str(zf["meta"]))
tf, Rf, qf = zf["t"].astype(float), zf["R"].astype(float), zf["q"].astype(np.int64)
res["fresh_run"] = dict(tag=tag, ended=mf["ended"], t_end=mf["t_end"], d0=mf["d0"], seed=mf["seed"], drift_E=mf.get("drift_E"), seconds=mf.get("seconds"))
# registered validity: settling time 100, and stop where any vortex-antivortex distance drops below 4
t, H, I = identity_series(tf, Rf, qf)
slope = np.sum((I - I.mean()) * (H - H.mean())) / np.sum((I - I.mean()) ** 2); alpha_E_fit = -slope
resid = (H - H.mean()) - slope * (I - I.mean())
res["energy_identity"] = dict(n_samples=int(len(t)), t_range=[float(t[0]), float(t[-1])], I_range=float(I[-1] - I[0]), H_change=float(H[-1] - H[0]), alpha_E_direct=float(alpha_E_fit),
                              rms_residual=float(np.sqrt(np.mean(resid ** 2))), r2=float(1 - np.sum(resid ** 2) / np.sum((H - H.mean()) ** 2)))
# the same quantity through the Rust extension, whole track and four consecutive sub-tracks (for a jackknife error)
full = est([(tf, Rf, qf)]); res["fresh_run"]["rust_full"] = {k: full[k] for k in ("alpha_energy", "alpha_regression", "one_minus_alpha_prime", "eta", "msd_exponent")}
m1000 = tf <= 1000.0; early = est([(tf[m1000], Rf[m1000], qf)])                          # the interim look at the checkpoint t = 1000 (made to test the pipeline; nothing was decided on it)
res["fresh_run"]["first_1000"] = {k: early[k] for k in ("alpha_energy", "alpha_regression", "one_minus_alpha_prime")}
cuts = np.linspace(0, len(tf), 5).astype(int); subs = [(tf[a:b], Rf[a:b], qf) for a, b in zip(cuts[:-1], cuts[1:])]
sub = est(subs); res["fresh_run"]["rust_four_subtracks"] = {k: sub[k] for k in ("alpha_energy", "alpha_energy_se", "alpha_regression", "alpha_regression_se", "one_minus_alpha_prime", "one_minus_alpha_prime_se", "n_blocks")}
# separations: d^2 slope
def pair_d(R_, i, j):
    d = R_[:, i] - R_[:, j]; d -= L * np.round(d / L); return np.hypot(d[:, 0], d[:, 1])
sl = []
for (i, j) in ((0, 1), (2, 3)):
    d = pair_d(Rf, i, j); a_, b_ = np.polyfit(tf, d ** 2, 1); sl.append(a_)
res["fresh_run"]["alpha_from_d2_slope_mean"] = float(-np.mean(sl) / 4); res["fresh_run"]["alpha_from_d2_slope_each"] = [float(-s_ / 4) for s_ in sl]

# ------------------------------------------------------------------ archived single-run estimates at T = 0.115
arch = sorted(glob.glob(str(TR / "prod_e0.60_d*_s*.npz"))) + sorted(glob.glob(str(TR / "G2_e0.60_antiparallel_d10_s*.npz")))
single = []; T_END = float(tf[-1])                                  # single-run estimates over the SAME duration as the fresh run, and over the full archived track
for f in arch:
    z_ = np.load(f, allow_pickle=True); t_, R_, q_ = z_["t"].astype(float), z_["R"].astype(float), z_["q"].astype(np.int64); w_ = t_ <= T_END
    r = est([(t_[w_], R_[w_], q_)]); rf_ = est([(t_, R_, q_)])
    single.append(dict(file=Path(f).name, alpha_energy=r["alpha_energy"], alpha_regression=r["alpha_regression"], alpha_energy_full_track=rf_["alpha_energy"], alpha_regression_full_track=rf_["alpha_regression"], t_end_full=float(t_[-1])))
ens = est(load_tracks(arch))
res["archived_T0115"] = dict(runs=single, ensemble={k: ens[k] for k in ("alpha_energy", "alpha_energy_se", "alpha_regression", "alpha_regression_se", "one_minus_alpha_prime", "one_minus_alpha_prime_se", "eta", "eta_se", "msd_exponent", "n_blocks")})
aE = np.array([s_["alpha_energy"] for s_ in single]); res["archived_T0115"]["single_run_alpha_energy_mean_sd"] = [float(aE.mean()), float(aE.std(ddof=1))]; res["archived_T0115"]["window_t_end"] = T_END
res["fresh_run"]["z_vs_archived_same_duration"] = float((full["alpha_energy"] - aE.mean()) / aE.std(ddof=1))
res["fresh_run"]["rank_lowest_first_of_nine"] = int(1 + (aE < full["alpha_energy"]).sum())
aEf = np.array([s_["alpha_energy_full_track"] for s_ in single]); res["archived_T0115"]["single_run_alpha_energy_full_track_mean_sd"] = [float(aEf.mean()), float(aEf.std(ddof=1))]

# ------------------------------------------------------------------ the six arms
fl = json.loads((TR / "fl/friction_law_results.json").read_text()); arms = fl["arms"]
def wmean(v, s):
    v, s = np.array(v), np.array(s); w = 1 / s ** 2; mu = (w * v).sum() / w.sum(); return float(mu), float(1 / np.sqrt(w.sum())), float(((v - mu) ** 2 * w).sum())
aT_E = wmean([a["alpha_energy"] / a["T"] for a in arms], [a["alpha_energy_se"] / a["T"] for a in arms])
aT_R = wmean([a["alpha_regression"] / a["T"] for a in arms], [a["alpha_regression_se"] / a["T"] for a in arms])
cE = {}; cR = {}
for kc in sorted({round(a["kcut"], 2) for a in arms}):
    sel = [a for a in arms if round(a["kcut"], 2) == kc]
    cE[kc] = wmean([a["alpha_energy"] / a["rho_n"] for a in sel], [a["alpha_energy_se"] / a["rho_n"] for a in sel])
    cR[kc] = wmean([a["alpha_regression"] / a["rho_n"] for a in sel], [a["alpha_regression_se"] / a["rho_n"] for a in sel])
oneE = wmean([a["alpha_energy"] / a["rho_n"] for a in arms], [a["alpha_energy_se"] / a["rho_n"] for a in arms])
oneR = wmean([a["alpha_regression"] / a["rho_n"] for a in arms], [a["alpha_regression_se"] / a["rho_n"] for a in arms])
res["six_arms"] = dict(alpha_over_T_energy=dict(a=aT_E[0], se=aT_E[1], chi2=aT_E[2], dof=len(arms) - 1), alpha_over_T_regression=dict(a=aT_R[0], se=aT_R[1], chi2=aT_R[2], dof=len(arms) - 1),
                       c_energy_by_cutoff={str(k): dict(c=v[0], se=v[1], chi2=v[2]) for k, v in cE.items()}, c_regression_by_cutoff={str(k): dict(c=v[0], se=v[1]) for k, v in cR.items()},
                       one_common_c_energy=dict(c=oneE[0], se=oneE[1], chi2=oneE[2], dof=len(arms) - 1), one_common_c_regression=dict(c=oneR[0], se=oneR[1], chi2=oneR[2], dof=len(arms) - 1),
                       spread_c_energy=float((max(v[0] for v in cE.values()) - min(v[0] for v in cE.values())) / np.mean([v[0] for v in cE.values()])),
                       arms=[{k: a.get(k) for k in ("label", "kcut", "T", "rho_n", "n_runs", "alpha_energy", "alpha_energy_se", "alpha_regression", "alpha_regression_se", "alpha_prime")} for a in arms],
                       FL2=fl["FL2"], Born_rival=fl["Born_rival"], H_T_stored=fl["H_T"], one_c_stored=fl["one_c"])
for a in arms:
    print(f"{a['label']:16s} alpha_E={a['alpha_energy']:.5f}  alpha_R={a['alpha_regression']:.5f}  alpha_E/T={a['alpha_energy'] / a['T']:.4f}")
print("alpha/T energy", aT_E, "regression", aT_R); print("c_E", cE); print("one c", oneE, oneR)

# separations of the pairs of the two archived zero-impulse G2 runs (d_0 = 10): mean of the first 20 and of the last 20 samples before t = 1500, for the text of the chapter
g2 = []
for fn in arch:
    if "G2_" not in Path(fn).name:
        continue
    z_ = np.load(fn, allow_pickle=True); t_, R_ = z_["t"].astype(float), z_["R"].astype(float)
    for k, (i, j) in enumerate(((0, 1), (2, 3))):
        d_ = pair_d(R_, i, j); g2.append(dict(file=Path(fn).name, pair=k + 1, d_start=float(d_[t_ < 20].mean()), d_end_t1500=float(d_[(t_ > 1480) & (t_ <= 1500)].mean())))
res["archived_G2_pairs"] = g2
# ------------------------------------------------------------------ the figure
colk = {2.09: TEAL, 3.14: BLUE, 6.28: ORANGE}; labk = {2.09: r"$k_c\xi=2\pi/3$", 3.14: r"$k_c\xi=\pi$", 6.28: r"$k_c\xi=2\pi$"}
fig = plt.figure(figsize=(TEXTW, 3.8)); gs = fig.add_gridspec(2, 2, wspace=0.34, hspace=0.46, left=0.085, right=0.99, top=0.955, bottom=0.095)
ax = fig.add_subplot(gs[0, 0])
sm = lambda y, n=25: np.convolve(y, np.ones(n) / n, mode="valid")
for fn in arch:
    z_ = np.load(fn, allow_pickle=True); w_ = z_["t"].astype(float) <= T_END                                            # the same duration as the fresh run
    t_, H_, I_ = identity_series(z_["t"].astype(float)[w_], z_["R"].astype(float)[w_], z_["q"].astype(np.int64))
    ax.plot(sm(I_ - I_[0]), sm(H_ - H_[0]), "-", color="#9EC1DD", lw=0.7, zorder=1)
ax.scatter(I - I[0], H - H[0], s=1.6, color="#E8B0A6", linewidths=0, zorder=2)
ax.plot(sm(I - I[0]), sm(H - H[0]), "-", color=RED, lw=1.3, zorder=4, label=rf"fresh run: line fit $\alpha={alpha_E_fit:.4f}$")
xs = np.array([0, 180]); ax.plot(xs, -0.0062 * xs, "--", color="#222222", lw=0.9, label=r"slope $-0.0062$ (ensemble)", zorder=3)
ax.plot([], [], "-", color="#9EC1DD", lw=1.0, label="eight archived runs")
ax.set_xlabel(r"$I(t)=\int 2\sum_i|v_{s,i}|^2\,dt$"); ax.set_ylabel(r"$H(t)-H(0)$"); ax.set_xlim(0, 180); ax.set_ylim(-1.7, 0.45); ax.legend(loc="lower left", fontsize=6.2, handlelength=1.4); panel(ax, "a")
ax = fig.add_subplot(gs[0, 1]); ys = [s_["alpha_energy"] for s_ in single]
ax.axhspan(ens["alpha_energy"] - ens["alpha_energy_se"], ens["alpha_energy"] + ens["alpha_energy_se"], color=BLUE, alpha=0.15, lw=0); ax.axhline(ens["alpha_energy"], color=BLUE, lw=0.8)
ax.plot(np.arange(len(ys)), ys, "o", color=BLUE, ms=4, label="archived runs"); ax.plot([len(ys)], [full["alpha_energy"]], "D", color=RED, ms=5, label="fresh Rust run")
ax.set_xticks(range(len(ys) + 1)); ax.set_xticklabels([f"{i + 1}" for i in range(len(ys))] + ["new"], fontsize=7); ax.set_xlabel("run"); ax.set_ylabel(r"$\alpha_E$ of one run"); ax.legend(loc="lower right", fontsize=6.6, handlelength=1.2); panel(ax, "b")
ax = fig.add_subplot(gs[1, 0]); Ts = np.linspace(0, 0.25, 50)
ax.fill_between(Ts, (aT_E[0] - aT_E[1]) * Ts, (aT_E[0] + aT_E[1]) * Ts, color="#999999", alpha=0.25, lw=0); ax.plot(Ts, aT_E[0] * Ts, "-", color="#555555", lw=0.9)
for a in arms:
    kc = round(a["kcut"], 2); ax.errorbar(a["T"], a["alpha_energy"], a["alpha_energy_se"], fmt="o", color=colk[kc], ms=4.2, capsize=2, lw=0.9)
    ax.errorbar(a["T"] + 0.003, a["alpha_regression"], a["alpha_regression_se"], fmt="o", mfc="white", color=colk[kc], ms=3.8, capsize=2, lw=0.7)
ax.set_xlabel(r"temperature $T$ of the base state"); ax.set_ylabel(r"friction $\alpha$"); ax.set_xlim(0.08, 0.24); ax.set_ylim(0, 0.0215); panel(ax, "c")
for kc in (2.09, 3.14, 6.28): ax.plot([], [], "o", color=colk[kc], label=labk[kc])
ax.legend(loc="upper left", fontsize=6.3, handlelength=0.8); ax.text(0.97, 0.05, rf"line: $\alpha={aT_E[0]:.3f}\,T$" + "\nfilled: energy; open: regression", transform=ax.transAxes, ha="right", fontsize=6.3, color="#333333")
ax = fig.add_subplot(gs[1, 1]); xr = np.linspace(0, 0.09, 20)
for kc, (cm, cs, _) in cE.items():
    ax.plot(xr, cm * xr, "-", color=colk[kc], lw=1.0, alpha=0.9, label=rf"$c={cm:.2f}$")
for a in arms:
    kc = round(a["kcut"], 2); ax.errorbar(a["rho_n"], a["alpha_energy"], a["alpha_energy_se"], fmt="o", color=colk[kc], ms=4.2, capsize=2, lw=0.9)
ax.set_xlabel(r"normal fraction $\rho_n/\rho$ of the base state"); ax.set_ylabel(r"friction $\alpha$"); ax.set_xlim(0, 0.09); ax.set_ylim(0, 0.0215); panel(ax, "d")
ax.legend(loc="upper left", fontsize=6.6, handlelength=1.3, title=r"$\alpha=c\,\rho_n/\rho$ at each cutoff", title_fontsize=6.4)
res["figure_note"] = "panels c,d: energy-estimator values with jackknife errors from data/generated/pgpe/transport/fl/friction_law_results.json (written by analyze_friction_law.py)"
addnum("fig_friction", res)
save(fig, "ch07_friction")
