import os
"""Chapter 7, Figure 2: the dissipative point-vortex model integrated with CVODE (rusty_sundials.CvodeSolver) against the statements of the
Lean modules DissipativeVortexDynamics (dipole_sq_law, centre_velocity_identity) and of the book's new module
Ch07_DissipativePairs.lean (co-rotating pair law |d|^2 = |d_0|^2 + 4 alpha t).  Model (hbar = m = 1, circulation 2 pi):
    dr_i/dt = (1 - alpha') v_s,i - alpha q_i z x v_s,i .
The closed forms compared with are
    dipole        |d|^2 = d_0^2 - 4 alpha t,            centre displacement s = (1 - alpha')(d_0 - d)/(2 alpha)   (integral of centre_velocity_identity)
    co-rotating   |d|^2 = d_0^2 + 4 alpha t,            rotation angle  Theta = (1 - alpha')/(2 alpha) ln(1 + 4 alpha t/d_0^2)
(the displacement and angle integrals are elementary and done by hand here; only the |d|^2 laws are Lean theorems).
Every number printed in the book from this script is written to ch07_numbers.json (key 'fig_dipole')."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
from ch07_common import addnum, logfmt, cvode_env
from rusty_sundials import CvodeSolver


# BOOK-BEGIN cvode_rhs
def rhs_dipole(a, ap):
    def rhs(t, y):
        px, py, mx, my = y; dx = px - mx; dy = py - my; r2 = dx * dx + dy * dy
        return [((1 - ap) * dy - a * dx) / r2, (-(1 - ap) * dx - a * dy) / r2,
                ((1 - ap) * dy + a * dx) / r2, (-(1 - ap) * dx + a * dy) / r2]
    return rhs
# BOOK-END cvode_rhs


def rhs_corot(a, ap):
    """two vortices of the SAME sign: v_s,1 = z x d / r2, v_s,2 = -z x d / r2 (d = p1 - p2)."""
    def rhs(t, y):
        x1, y1, x2, y2 = y; dx = x1 - x2; dy = y1 - y2; r2 = dx * dx + dy * dy
        return [(-(1 - ap) * dy + a * dx) / r2, ((1 - ap) * dx + a * dy) / r2,
                ((1 - ap) * dy - a * dx) / r2, (-(1 - ap) * dx - a * dy) / r2]
    return rhs


# BOOK-BEGIN cvode_int
def integrate(rhs, y0, tgrid, rtol, atol=1e-10, method="bdf"):
    s = CvodeSolver(method=method, rtol=rtol, atol=atol, max_steps=200000)
    t = float(tgrid[0]); y = list(y0); out = [list(y)]
    for tn in tgrid[1:]:
        t, y = s.solve(rhs, t, y, float(tn)); out.append(list(y))
    return np.array(out)
# BOOK-END cvode_int


ENV = cvode_env()                                             # refuses the stale rusty_sundials of the shared venv
d0 = 8.0; frac = np.linspace(0, 0.95, 60); res = {"cvode_env": ENV}; t_start = time.time(); load_start = os.getloadavg()[0]
cols = {0.005: BLUE, 0.01: TEAL, 0.02: ORANGE}
fig = plt.figure(figsize=(TEXTW, 3.8))
gs = fig.add_gridspec(2, 6, wspace=2.2, hspace=0.62, left=0.075, right=0.995, top=0.94, bottom=0.115)
axA = fig.add_subplot(gs[0, 0:2]); axB = fig.add_subplot(gs[0, 2:4]); axC = fig.add_subplot(gs[0, 4:6])
axD = fig.add_subplot(gs[1, 0:3]); axE = fig.add_subplot(gs[1, 3:6])

# ---- A: the dipole in the plane (exaggerated alpha = 0.2 so that the funnel is visible) -----------------------------------
aP = 0.2; tauP = d0 ** 2 / (4 * aP); tgP = np.linspace(0, 0.9 * tauP, 80)
for ap, ls, lw in ((0.0, "-", 1.3), (0.3, "--", 1.1)):
    Y = integrate(rhs_dipole(aP, ap), [d0 / 2, 0, -d0 / 2, 0], tgP, 1e-8)
    s_ex = (1 - ap) * (d0 - np.sqrt(d0 ** 2 - 4 * aP * tgP)) / (2 * aP); half = (d0 / 2) * np.sqrt(1 - 4 * aP * tgP / d0 ** 2)
    axA.plot(-Y[:, 1], Y[:, 0], ls, color=BLUE, lw=lw); axA.plot(-Y[:, 3], Y[:, 2], ls, color=ORANGE, lw=lw)
    axA.plot(s_ex, half, ":", color="#222222", lw=0.7); axA.plot(s_ex, -half, ":", color="#222222", lw=0.7)
    res[f"portrait_alpha{aP}_alphap{ap}_max_abs_err_vs_exact"] = float(max(np.abs(-Y[:, 1] - s_ex).max(), np.abs(Y[:, 0] - half).max()))
for k in (0, 20, 40, 60, 79):                        # the pair axis at selected times (alpha' = 0)
    Yk = integrate(rhs_dipole(aP, 0.0), [d0 / 2, 0, -d0 / 2, 0], tgP[:k + 1], 1e-8)[-1] if k else np.array([d0 / 2, 0, -d0 / 2, 0])
    axA.plot([-Yk[1], -Yk[3]], [Yk[0], Yk[2]], "-", color="#AAAAAA", lw=0.7, zorder=0)
axA.set_xlabel(r"distance travelled $s$"); axA.set_ylabel(r"position across the track")
axA.text(-0.9, d0 / 2, r"$+$", color=BLUE, fontsize=9, fontweight="bold", va="center", ha="center"); axA.text(-0.9, -d0 / 2, r"$-$", color=ORANGE, fontsize=9, fontweight="bold", va="center", ha="center")
axA.set_ylim(-4.9, 4.9); axA.set_xlim(-1.6, 14.5); panel(axA, "a")

# ---- B: the co-rotating pair spirals out ----------------------------------------------------------------------------------
aS, apS, dS = 0.05, 0.0, 4.0; tgS = np.linspace(0, 600, 240)
Ys = integrate(rhs_corot(aS, apS), [dS / 2, 0, -dS / 2, 0], tgS, 1e-8, atol=1e-6)
dS_ex = np.sqrt(dS ** 2 + 4 * aS * tgS); th_ex = (1 - apS) / (2 * aS) * np.log(1 + 4 * aS * tgS / dS ** 2)
p1_ex = np.column_stack([dS_ex / 2 * np.cos(th_ex), dS_ex / 2 * np.sin(th_ex)])
tt = tgS / tgS[-1]
for i, col in ((0, BLUE), (2, TEAL)):
    axB.plot(Ys[:, i], Ys[:, i + 1], "-", color=col, lw=1.0)
axB.plot(p1_ex[::12, 0], p1_ex[::12, 1], "o", ms=2.2, color=GREY, mfc="none", mew=0.6); axB.plot(-p1_ex[::12, 0], -p1_ex[::12, 1], "o", ms=2.2, color=GREY, mfc="none", mew=0.6)
axB.plot([Ys[0, 0], Ys[0, 2]], [Ys[0, 1], Ys[0, 3]], "-", color="#999999", lw=0.8); axB.plot([Ys[-1, 0], Ys[-1, 2]], [Ys[-1, 1], Ys[-1, 3]], "-", color="#999999", lw=0.8)
axB.set_aspect("equal"); axB.set_xlabel(r"$x$"); axB.set_ylabel(r"$y$"); axB.set_xlim(-7.5, 7.5); axB.set_ylim(-7.5, 7.5)
axB.text(0.02, 0.02, "two $+$ vortices\n" + rf"$\alpha={aS}$, $d_0={dS:.0f}$", transform=axB.transAxes, fontsize=5.8, va="bottom", ha="left", color="#333333"); panel(axB, "b")
d2S = (Ys[:, 0] - Ys[:, 2]) ** 2 + (Ys[:, 1] - Ys[:, 3]) ** 2
ang = np.unwrap(np.arctan2(Ys[:, 1] - Ys[:, 3], Ys[:, 0] - Ys[:, 2]))
res["spiral"] = dict(alpha=aS, alphap=apS, d0=dS, t_end=float(tgS[-1]), d_end_exact=float(dS_ex[-1]), d_end_cvode=float(np.sqrt(d2S[-1])),
                     max_rel_err_d2=float(np.abs(d2S - dS_ex ** 2).max() / dS_ex[-1] ** 2), max_abs_err_angle_rad=float(np.abs(ang - ang[0] - th_ex).max()),
                     turns=float(th_ex[-1] / (2 * np.pi)))

# ---- C: |d|^2 against t: dipole falls with slope -4 alpha, co-rotating pair rises with +4 alpha ---------------------------------
maxerr = {}
for a, col in cols.items():
    tau = d0 ** 2 / (4 * a); tg = frac * tau
    axC.plot(tg, d0 ** 2 - 4 * a * tg, "-", color=col, lw=0.9); axC.plot(tg, d0 ** 2 + 4 * a * tg, "--", color=col, lw=0.9)
    for ap, mk in ((0.0, "o"), (0.3, "s")):
        Y = integrate(rhs_dipole(a, ap), [d0 / 2, 0, -d0 / 2, 0], tg, 1e-8); d2 = (Y[:, 0] - Y[:, 2]) ** 2 + (Y[:, 1] - Y[:, 3]) ** 2
        err = np.abs(d2 - (d0 ** 2 - 4 * a * tg)).max() / d0 ** 2; maxerr[f"dipole_alpha{a}_alphap{ap}"] = float(err)
        axC.plot(tg[::6], d2[::6], mk, ms=2.4, color=col, mfc=col if ap == 0 else "none", mew=0.7, lw=0)
        Yc = integrate(rhs_corot(a, ap), [d0 / 2, 0, -d0 / 2, 0], tg, 1e-8, atol=1e-6); d2c = (Yc[:, 0] - Yc[:, 2]) ** 2 + (Yc[:, 1] - Yc[:, 3]) ** 2
        errc = np.abs(d2c - (d0 ** 2 + 4 * a * tg)).max() / (d0 ** 2 + 4 * a * tg[-1]); maxerr[f"corotating_alpha{a}_alphap{ap}"] = float(errc)
        axC.plot(tg[::6], d2c[::6], mk, ms=2.4, color=col, mfc=col if ap == 0 else "none", mew=0.7, lw=0)
res["max_rel_err_d2_rtol1e-8"] = maxerr
axC.axhline(d0 ** 2, color="#999999", lw=0.5, ls=":")
axC.set_xlabel(r"time $t$"); axC.set_ylabel(r"$|d|^2$"); panel(axC, "c")

# ---- D: centre displacement of the dipole along its straight track ---------------------------------------------------------------
a = 0.01; tau = d0 ** 2 / (4 * a); tg = frac * tau
for ap, col in ((0.0, BLUE), (0.3, RED)):
    Y = integrate(rhs_dipole(a, ap), [d0 / 2, 0, -d0 / 2, 0], tg, 1e-8); c = (Y[:, :2] + Y[:, 2:]) / 2
    d = np.sqrt((Y[:, 0] - Y[:, 2]) ** 2 + (Y[:, 1] - Y[:, 3]) ** 2)
    s_num = np.hypot(c[:, 0] - c[0, 0], c[:, 1] - c[0, 1]); s_ex = (1 - ap) * (d0 - np.sqrt(d0 ** 2 - 4 * a * tg)) / (2 * a)
    axD.plot(frac, s_ex, "-", color=col, lw=1.0); axD.plot(frac[::4], s_num[::4], "o", ms=2.6, color=col, label=rf"$\alpha'={ap}$")
    # the Lean identity c' . (dy, -dx) = 1 - alpha' evaluated on the CVODE track (finite differences of the output grid are too coarse:
    # evaluate the right-hand side of the model at the CVODE states instead)
    vel = np.array([np.array(rhs_dipole(a, ap)(0, list(y))) for y in Y]); cp = (vel[:, :2] + vel[:, 2:]) / 2
    dxv = Y[:, 0] - Y[:, 2]; dyv = Y[:, 1] - Y[:, 3]
    ident = cp[:, 0] * dyv - cp[:, 1] * dxv
    res[f"centre_identity_alphap{ap}"] = dict(target=1 - ap, max_abs_dev=float(np.abs(ident - (1 - ap)).max()))
    res[f"centre_displacement_max_abs_err_alphap{ap}"] = float(np.abs(s_num - s_ex).max())
    res[f"centre_displacement_end_alphap{ap}"] = float(s_num[-1]); res[f"centre_displacement_end_exact_alphap{ap}"] = float(s_ex[-1])
    res[f"centre_x_drift_alphap{ap}"] = float(np.abs(c[:, 0]).max())
axD.set_xlabel(r"$t/\tau,\ \ \tau=d_0^2/4\alpha$"); axD.set_ylabel(r"centre displacement $s(t)$"); axD.legend(loc="upper left", handlelength=1.2)
axD.text(0.97, 0.06, r"$\alpha=0.01$, $d_0=8$", transform=axD.transAxes, ha="right", fontsize=6.8); panel(axD, "d")

# ---- E: work-precision diagram: right-hand-side evaluations against the error of |d|^2 at 0.95 of the lifetime -------------------
class Counter:
    """wraps a right-hand side and counts its calls (the machine-independent cost of a CVODE run)"""
    def __init__(self, f): self.f, self.n = f, 0
    def __call__(self, t, y): self.n += 1; return self.f(t, y)


a, ap = 0.01, 0.1; tend = frac[-1] * d0 ** 2 / (4 * a); exact_end = d0 ** 2 - 4 * a * tend; wp = []; y00 = [d0 / 2, 0, -d0 / 2, 0]
d2f = lambda y: (y[0] - y[2]) ** 2 + (y[1] - y[3]) ** 2
for meth in ("bdf", "adams"):
    for rtol in (1e-4, 1e-6, 1e-8, 1e-10):
        c = Counter(rhs_dipole(a, ap)); sv = CvodeSolver(method=meth, rtol=rtol, atol=1e-10, max_steps=5_000_000); _, y = sv.solve(c, 0.0, list(y00), tend)
        wp.append(dict(method=meth, mode="one call", rtol=rtol, rhs_calls=c.n, err=abs(d2f(y) - exact_end) / d0 ** 2))
        c = Counter(rhs_dipole(a, ap)); sv = CvodeSolver(method=meth, rtol=rtol, atol=1e-10, max_steps=5_000_000); t_ = 0.0; y = list(y00)
        for tn in np.linspace(0, tend, 60)[1:]:
            t_, y = sv.solve(c, t_, y, float(tn))
        wp.append(dict(method=meth, mode="60 outputs", rtol=rtol, rhs_calls=c.n, err=abs(d2f(y) - exact_end) / d0 ** 2))
res["work_precision"] = wp; res["work_precision_setup"] = dict(alpha=a, alphap=ap, d0=d0, t_end=float(tend), atol=1e-10)
for meth, mode, col, mk, ls in (("bdf", "one call", BLUE, "o", "-"), ("adams", "one call", ORANGE, "s", "-"), ("bdf", "60 outputs", BLUE, "o", "--"), ("adams", "60 outputs", ORANGE, "s", "--")):
    r_ = [w for w in wp if w["method"] == meth and w["mode"] == mode]
    axE.loglog([w["rhs_calls"] for w in r_], [max(w["err"], 1e-13) for w in r_], marker=mk, ls=ls, color=col, ms=3.5, lw=1.0, mfc=col if mode == "one call" else "white",
               label=f"{'BDF' if meth == 'bdf' else 'Adams'}, {'1 call' if mode == 'one call' else '60 calls'}")
axE.set_xlabel("right-hand-side evaluations"); axE.set_ylabel(r"error of $|d|^2$ at $0.95\,\tau$"); axE.yaxis.set_major_formatter(logfmt()); axE.xaxis.set_major_formatter(logfmt())
axE.set_ylim(2e-11, 1.5e-1); axE.legend(loc="upper center", ncol=2, fontsize=6.2, handlelength=1.8, columnspacing=1.0, borderaxespad=0.2); panel(axE, "e")
axE.text(0.03, 0.04, r"markers: rtol $=10^{-4},\,10^{-6},\,10^{-8},\,10^{-10}$", transform=axE.transAxes, fontsize=5.8, color="#333333")
probes = {}                                                   # aborts seen with the STALE rusty_sundials of the shared venv: do they reproduce with the fixed build?
for name, rh, kw in (("dipole_bdf_rtol1e-10_atol1e-12_60outputs", rhs_dipole(0.01, 0.1), dict(rtol=1e-10, atol=1e-12)), ("dipole_bdf_rtol1e-9_atol1e-11_60outputs", rhs_dipole(0.01, 0.1), dict(rtol=1e-9, atol=1e-11)),
                     ("corotating_bdf_rtol1e-8_atol1e-10_60outputs", rhs_corot(0.01, 0.0), dict(rtol=1e-8, atol=1e-10))):
    try:
        integrate(rh, [d0 / 2, 0, -d0 / 2, 0], frac * d0 ** 2 / 0.04, **kw); probes[name] = "ok"
    except RuntimeError as ex:
        probes[name] = str(ex)
res["stale_build_aborts_reproduce_with_fixed_build"] = probes
res["seconds"] = round(time.time() - t_start, 1); res["load_average_start_end"] = [round(load_start, 1), round(os.getloadavg()[0], 1)]; res["d0"] = d0; res["alpha_list"] = list(cols)
addnum("fig_dipole", res)
save(fig, "ch07_dipole")
