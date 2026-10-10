"""Chapter 7, Figure 7: two theorems that were true and did not describe what they were applied to.
 (a) the phonon-wind stall (hypothesis W): archived single-pair runs at L = 64 (W1) and in the L = 96 control (W2); the wind equation
     d' = -2 alpha (1/d - w (d_0 - d)) integrated with CVODE (rusty_sundials) with the independently measured alpha = 0.0062 and no free
     parameter; free shrinking d^2 = d_0^2 - 4 alpha t; and the stall point b of the Lean theorem Ch07_DissipativePairs.wind_stall_at_b;
 (b) the wind seen directly: momentum of the phonon band |k| > 1 projected on the initial impulse against the impulse shed by the pair (W1 runs);
 (c) the energy estimator of alpha against the diffusion eta of synthetic tracks (Rust example g0_scan --eta-scan of qf-pgpe, run for this chapter).
Archived data: data/generated/pgpe/transport/{W1_*, W2_L96_*, W2_result.json, base_L96_e0.60.json}, sweep/e0.60_s11_t4000.json."""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch07_common import addnum, cvode_env
from rusty_sundials import CvodeSolver
ROOT = Path(__file__).resolve().parents[2]; TR = ROOT / "data/generated/pgpe/transport"
SCRATCH = Path("/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-SocrateAI-Scientific-QuantumFluids/74574ea7-7320-4d9f-8911-de38b1699e5e/scratchpad/ch07")
ENV = cvode_env()                                             # refuses the stale rusty_sundials of the shared venv
res = {"cvode_env": ENV}


def pair_sep(z, L):
    R = z["R"]; d = R[:, 0] - R[:, 1]; d -= L * np.round(d / L); return z["t"], np.hypot(d[:, 0], d[:, 1])


def runmean(x, n=25):
    k = np.ones(n) / n; return np.convolve(x, k, mode="valid"), n // 2


def solve_chain(rhs, y0, tgrid, rtol=1e-9, atol=1e-11):
    s = CvodeSolver(method="bdf", rtol=rtol, atol=atol, max_steps=200000); t = float(tgrid[0]); y = [y0]; out = [y0]
    for tn in tgrid[1:]:
        t, y = s.solve(rhs, t, y, float(tn)); out.append(y[0])
    return np.array(out)


# ---------------------------------------------------------------- wind parameters, from the base states
base64 = json.loads((ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000.json").read_text()); base96 = json.loads((TR / "base_L96_e0.60.json").read_text())
ns64, ns96 = base64["ns_over_n"], base96["ns_over_n"]; alpha = 0.0062; d0 = 12.0
def wind_w(ns, L): return 2 * np.pi * ns / ((1 - ns) * L ** 2)
w64, w96 = wind_w(ns64, 64.0), wind_w(ns96, 96.0)
def roots(w, d0_):
    disc = d0_ ** 2 - 4 / w
    return (None, None) if disc < 0 else ((d0_ - np.sqrt(disc)) / 2, (d0_ + np.sqrt(disc)) / 2)
a64, b64 = roots(w64, d0); a96, b96 = roots(w96, d0)
lam64 = 2 * alpha * w64 * (b64 - a64) / b64                       # linearised relaxation rate onto b: d' ~ -2 alpha w (b-a)/b (d-b)
tg = np.linspace(0, 4000, 81)
rhs64 = lambda t, y: [-2 * alpha * (1 / y[0] - w64 * (d0 - y[0]))]; rhs96 = lambda t, y: [-2 * alpha * (1 / y[0] - w96 * (d0 - y[0]))]
d_w64 = solve_chain(rhs64, d0, tg); d_w96 = solve_chain(rhs96, d0, tg); d_free = np.sqrt(d0 ** 2 - 4 * alpha * tg)
# the approach to b: fit an exponential to the CVODE curve, d - b ~ A exp(-lambda t) for t in [2000, 4000]
m = tg >= 2000; lam_fit = -np.polyfit(tg[m], np.log(d_w64[m] - b64), 1)[0]
res["wind"] = dict(alpha=alpha, d0=d0, ns64=ns64, ns96=ns96, rho_n64=1 - ns64, rho_n96=1 - ns96, w64=float(w64), w96=float(w96), w64_d0sq=float(w64 * d0 ** 2), w96_d0sq=float(w96 * d0 ** 2), w8_d0sq=float(w64 * 8.0 ** 2),
                   a64=float(a64), b64=float(b64), stall_exists_L96=bool(b96 is not None), C96=float(1 / w96), C64=float(1 / w64), d0sq_over_4=float(d0 ** 2 / 4),
                   relaxation_rate_L64_linearised=float(lam64), relaxation_time_L64_linearised=float(1 / lam64), relaxation_rate_L64_cvode_fit=float(lam_fit),
                   free_lifetime_d0sq_over_4alpha=float(d0 ** 2 / (4 * alpha)), cvode_d_at_4000_L64=float(d_w64[-1]), cvode_d_at_4000_L96=float(d_w96[-1]), free_d_at_4000=float(d_free[-1]),
                   cvode_min_minus_b_L64=float(d_w64.min() - b64), cvode_wind_time_to_within_5pct_of_b=float(tg[np.argmax(d_w64 - b64 < 0.05 * (d0 - b64))]))
fig = plt.figure(figsize=(TEXTW, 4.1)); gs = fig.add_gridspec(2, 2, height_ratios=[1.12, 1], wspace=0.34, hspace=0.50, left=0.085, right=0.99, top=0.955, bottom=0.095)
ax = fig.add_subplot(gs[0, :]); runs = {}; Wruns = {}
for f, col, L, lab in ((sorted(TR.glob("W1_e0.60_dipole_d12_s*.npz")), BLUE, 64.0, "single pairs, $L=64$"), (sorted(TR.glob("W2_L96_e0.60_dipole_d12_s*.npz")), ORANGE, 96.0, "control, $L=96$")):
    for i, fn in enumerate(f):
        z = np.load(fn, allow_pickle=True); t, d = pair_sep(z, L); y, off = runmean(d); ax.plot(t[off:off + len(y)], y, "-", color=col, lw=0.8, alpha=0.8, label=lab if i == 0 else None)
        runs[fn.name] = dict(L=L, d_first20=float(d[:20].mean()), d_at_1800=float(d[1790:1810].mean()), d_end_last100=float(d[-100:].mean()), d_min_smoothed=float(y.min()), d_max_smoothed=float(y.max()),
                             d_range_after_2000_smoothed=[float(y[1975:].min()), float(y[1975:].max())], t_end=float(t[-1]))
        cur_end = float(d_w64[-1] if L == 64.0 else d_w96[-1]); runs[fn.name].update(wind_curve_end=cur_end, free_curve_end=float(d_free[-1]), end_minus_wind=float(runs[fn.name]["d_end_last100"] - cur_end),
                                                                                       end_minus_free=float(runs[fn.name]["d_end_last100"] - d_free[-1]))
        if L == 64.0:
            Wruns[fn.name] = (z, d)
ax.plot(tg, d_free, linestyle=":", color=GREY, lw=1.1, label="free shrinking, $d^2=d_0^2-4\\alpha t$"); ax.plot(tg, d_w64, color=BLUE, lw=1.6, ls=(0, (3, 1.2)), label="wind equation, $L=64$ (CVODE)")
ax.plot(tg, d_w96, color=ORANGE, lw=1.6, ls=(0, (3, 1.2)), label="wind equation, $L=96$ (CVODE)")
ax.axhline(b64, color=RED, lw=0.9, label=rf"stall point $b={b64:.1f}$ of the Lean theorem, $L=64$")
ax.set_xlabel(r"time $t$"); ax.set_ylabel(r"pair separation $d$"); ax.set_ylim(5.0, 12.5); ax.set_xlim(0, 4000); ax.legend(loc="lower left", fontsize=6.4, handlelength=1.8, ncol=2, columnspacing=1.2); panel(ax, "a")
res["wind_runs"] = runs
em = [abs(v["end_minus_wind"]) for v in runs.values()]; ef = [v["end_minus_free"] for v in runs.values()]
res["wind_vs_data_summary"] = dict(n_pairs=len(runs), abs_end_minus_wind_min=min(em), abs_end_minus_wind_max=max(em), end_minus_free_min=min(ef), end_minus_free_max=max(ef))
# ---------------------------------------------------------------- (b) the wind seen directly
ax = fig.add_subplot(gs[1, 0]); xs_all = []; slopes = {}
for (name, (z, d)), col in zip(Wruns.items(), (BLUE, TEAL)):
    meta = json.loads(str(z["meta"])); P = z["P"]; Ph = z["P_hi"]; t = z["t"]
    e = (P[0] - np.array(meta["P_base"])); e = e / np.hypot(*e)
    yv = (Ph - Ph[0]) @ e; dsm, off = runmean(d, 25); ysm = np.convolve(yv, np.ones(25) / 25, mode="valid")
    d_init = d[:20].mean(); shed = 2 * np.pi * ns64 * (d_init - dsm)
    ax.scatter(shed[::8], ysm[::8], color=col, s=4.5, alpha=0.55, linewidths=0, label=f"run {name[-5]}")
    sl = np.polyfit(shed, ysm, 1)[0]; slopes[name] = dict(slope=float(sl), slope_unsmoothed=float(np.polyfit(2 * np.pi * ns64 * (d_init - d), yv, 1)[0]), d_init=float(d_init), P_hi_change_along_impulse=float(yv[-1]), shed_end=float(shed[-1]), max_shed=float(shed.max()))
xx = np.array([0, 20]); ax.plot(xx, xx, "--", color="#333333", lw=0.8)
ax.set_xlabel(r"impulse shed by the pair, $2\pi\rho_s(d_0-d)$"); ax.set_ylabel(r"$\Delta P_{|k|>1}$ along the impulse"); panel(ax, "b")
ax.legend(loc="upper left", fontsize=6.4, handlelength=0.8, markerscale=2); ax.text(0.97, 0.05, "dashed: conservation", transform=ax.transAxes, fontsize=6.3, ha="right", color="#333333")
res["W3"] = slopes
# ---------------------------------------------------------------- (c) estimator bias
src = SCRATCH / "g0_scan_eta_8seeds.txt"; rows = []
if src.exists():
    for line in src.read_text().splitlines():
        mm = re.match(r"noise\s+([\d.]+) eta\s+(\S+)\s+([\d.]+) \+- ([\d.]+)\s+([\d.]+) \+- ([\d.]+)\s+([\d.]+)\s+(\S+)", line)
        if mm:
            rows.append(dict(eta=float(mm.group(2)), aE=float(mm.group(3)), aE_sd=float(mm.group(4)), aR=float(mm.group(5)), aR_sd=float(mm.group(6)), omap=float(mm.group(7)), eta_est=float(mm.group(8))))
    res["bias_source"] = f"g0_scan 8 --eta-scan, run for this chapter ({src.name})"
if not rows:                                                         # fall back to the table of docs/designs/PGPE_ENERGY_ESTIMATOR_BIAS.md
    rows = [dict(eta=0.0, aE=0.0200, aE_sd=0.0, aR=0.0200, aR_sd=0.0), dict(eta=5e-4, aE=0.0183, aE_sd=0.0017, aR=0.0198, aR_sd=0.0), dict(eta=1e-3, aE=0.0163, aE_sd=0.0012, aR=0.0194, aR_sd=0.0),
            dict(eta=2e-3, aE=0.0156, aE_sd=0.0032, aR=0.0194, aR_sd=0.0024)]
    res["bias_source"] = "docs/designs/PGPE_ENERGY_ESTIMATOR_BIAS.md table (8-10 seeds); the g0_scan output for this chapter was not available at figure time"
res["bias_rows"] = rows
ax = fig.add_subplot(gs[1, 1]); x = np.array([r["eta"] for r in rows]) * 1e3; at = 0.02
ax.axhline(1.0, color="#999999", lw=0.8); ax.errorbar(x - 0.03, [r["aE"] / at for r in rows], [r["aE_sd"] / at for r in rows], fmt="o-", color=RED, ms=3.5, lw=1.0, capsize=2, label="energy estimator")
ax.errorbar(x + 0.03, [r["aR"] / at for r in rows], [r["aR_sd"] / at for r in rows], fmt="s-", color=BLUE, ms=3.2, lw=1.0, capsize=2, label="regression")
ax.set_xlabel(r"diffusion $\eta$ of the synthetic track  ($10^{-3}$)"); ax.set_ylabel(r"$\hat\alpha/\alpha_{\rm true}$"); ax.set_ylim(0.6, 1.1); ax.legend(loc="lower left", fontsize=6.6, handlelength=1.4)
ax.text(0.97, 0.06, r"$\alpha_{\rm true}=0.02$", transform=ax.transAxes, ha="right", fontsize=7, color="#333333"); panel(ax, "c")
addnum("fig_failures", res)
save(fig, "ch07_failures")
