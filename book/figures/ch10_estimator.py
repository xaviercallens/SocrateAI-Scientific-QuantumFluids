"""Chapter 10, figure 'estimator': the registered synthetic gate G0 (known alpha = 0.02) run by the rusty-SUNDIALS example g0_scan (Rust Langevin generator
+ Rust estimators, seeds 0..7), and the numpy-versus-Rust comparison of the estimators on identical tracks.
Inputs (made by figures/ch10_run_estimator.sh under the shared heavy-job lock):
   figures/ch10_raw/g0_eta_scan.txt    g0_scan 8 --eta-scan   (detection noise 0, eta swept)
   figures/ch10_raw/g0_noise_scan.txt  g0_scan 8              (eta = 2e-3, detection noise swept)
   figures/ch10_raw/cross_impl.json    ch10_cross_impl.py     (same tracks, numpy and Rust)
Run:  .venv/bin/python book/figures/ch10_estimator.py"""
import sys, re, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
here = Path(__file__).resolve().parent; raw = here / "ch10_raw"
TRUE = 0.02

def parse(path):
    rows = []
    for ln in path.read_text().splitlines():
        m = re.match(r"noise\s+([\d.]+)\s+eta\s+(\S+)\s+([\d.]+)\s+\+-\s+([\d.]+|NaN)\s+([\d.]+)\s+\+-\s+([\d.]+|NaN)\s+([\d.]+)\s+(\S+)", ln)
        if m: rows.append(dict(noise=float(m[1]), eta=float(m[2]), e=float(m[3]), esd=float(m[4]), r=float(m[5]), rsd=float(m[6]), oma=float(m[7])))
    return rows
eta_rows, noise_rows = parse(raw / "g0_eta_scan.txt"), parse(raw / "g0_noise_scan.txt")
cross = json.load(open(raw / "cross_impl.json"))
assert len(eta_rows) == 4 and len(noise_rows) == 4, (len(eta_rows), len(noise_rows))

fig, ax = plt.subplots(1, 3, figsize=(TEXTW * 1.12, 2.8), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.25], wspace=0.62))
def panel_ratio(a, rows, xlabels, xlabel, below=False):
    x = np.arange(len(rows)); d = 0.10
    a.axhspan(0.85, 1.15, color=BLUE, alpha=0.08, lw=0); a.axhline(1, color=BLUE, lw=0.9)
    a.errorbar(x - d, [r["e"] / TRUE for r in rows], [r["esd"] / TRUE for r in rows], fmt="o", color=RED, ms=4.5, capsize=2, lw=1.0, label="energy estimator")
    a.errorbar(x + d, [r["r"] / TRUE for r in rows], [r["rsd"] / TRUE for r in rows], fmt="s", color=TEAL, ms=4, capsize=2, lw=1.0, label="regression estimator")
    for xi, r in zip(x, rows):
        pct = 100 * (r["e"] / TRUE - 1)
        if below: continue
        a.annotate((f"{pct:+.1f}%" if abs(pct) > 0.05 else "0").replace("+", "+").replace("-", "\u2212"), (xi - d, r["e"] / TRUE), textcoords="offset points", xytext=((0, -14) if below else (-6, -3)), ha=("center" if below else "right"), va="center", fontsize=6.2, color=RED, family="DejaVu Sans", bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
    a.set_xticks(x); a.set_xticklabels(xlabels); a.set_xlabel(xlabel); a.set_ylim(0.55, 1.3); a.set_xlim(-0.75, len(rows) - 0.35)
    a.set_ylabel(r"estimate / true $\alpha$")
panel_ratio(ax[0], eta_rows, ["0", "5e-4", "1e-3", "2e-3"], r"vortex diffusion $\eta$")
ax[0].legend(fontsize=6.3, loc="lower left", handletextpad=0.3, borderpad=0.2, bbox_to_anchor=(0.0, -0.02), frameon=False)
ax[0].text(0.98, 0.955, "registered 15% band", transform=ax[0].transAxes, ha="right", va="top", fontsize=6.2, color=BLUE)
panel(ax[0], "a")
panel_ratio(ax[1], noise_rows, ["0", "0.05", "0.1", "0.2"], "detection noise on the positions", below=True)
ax[1].set_ylabel(""); ax[1].set_yticklabels([]); panel(ax[1], "b")
ax[1].text(0.98, 0.955, r"fixed $\eta=2\times10^{-3}$", transform=ax[1].transAxes, ha="right", va="top", fontsize=6.2, color=GREY)
_b = sorted(abs(100 * (r["e"] / TRUE - 1)) for r in noise_rows)
ax[1].text(0.03, 0.885, "energy estimator:\n\u2212%.0f to \u2212%.0f%%" % (_b[0], _b[-1]), transform=ax[1].transAxes, ha="left", va="top", fontsize=6.2, color=RED, family="DejaVu Sans", linespacing=1.15)

# (c) numpy against Rust on identical tracks: lollipops on a log axis; exact agreement is drawn as an open diamond at the left edge
c = ax[2]
names = {"one_minus_alpha_prime": r"$1-\alpha'$", "alpha_regression": r"$\alpha$ (regression)", "alpha_energy": r"$\alpha$ (energy)", "eta": r"$\eta$", "msd_exponent": "MSD exponent", "msd_offset": "MSD offset"}
rows = {r["name"]: r["rel_diff"] for r in cross["rows"]}
y = np.arange(len(names))[::-1]; LEFT, ZERO = 2e-17, 4e-17
for yy, (k, lab) in zip(y, names.items()):
    for val, col, off, lbl in ((rows[k], BLUE, 0.17, "estimate"), (rows[k + "_se"], "#6F9CC4", -0.17, "its jackknife error")):
        if val == 0:
            c.plot([ZERO], [yy + off], marker="D", mfc="white", mec=col, ms=4, ls="none")
        else:
            c.hlines(yy + off, LEFT, val, color=col, lw=1.0); c.plot([val], [yy + off], "o", color=col, ms=4.3)
c.plot([], [], "o", color=BLUE, ms=4, label="estimate"); c.plot([], [], "o", color="#6F9CC4", ms=4, label="jackknife error"); c.plot([], [], marker="D", mfc="white", mec=GREY, ms=4, ls="none", label="identical (0)")
c.set_xscale("log"); c.set_xlim(LEFT, 3e-14); c.set_yticks(y); c.set_yticklabels(list(names.values()), fontsize=7.2); c.set_ylim(-0.7, len(names) - 0.3)
c.axvline(2.2e-16, color=GREY, lw=0.7, ls=":"); c.text(2.5e-16, -0.62, "machine epsilon", fontsize=5.8, color=GREY, va="bottom", family="DejaVu Sans")
c.set_xlabel("|Rust $-$ numpy| / |numpy|"); c.legend(fontsize=6.0, loc="upper right", bbox_to_anchor=(1.0, 0.97), handletextpad=0.2, borderpad=0.2, frameon=False)
c.set_xticks([1e-16, 1e-15, 1e-14]); c.set_xticklabels([r"$10^{-16}$", r"$10^{-15}$", r"$10^{-14}$"]); c.minorticks_off(); c.tick_params(axis="x", labelsize=7.2)
panel(c, "c")
rev = (raw / 'rusty_sundials_rev.txt').read_text().split()[0][:7]
fig.text(0.5, -0.045, f"Panels a, b: Rust example g0_scan, 8 seeds of 8 tracks (nominally 2000 time units), mean ± standard deviation over seeds; rusty-SUNDIALS commit {rev}. "
         f"Panel c: the registered tracks (numpy seed {cross['seed']}), analysed by both implementations.", ha="center", va="top", fontsize=6.2, color=GREY)
save(fig, "ch10_estimator")
