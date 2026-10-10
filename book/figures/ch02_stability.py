"""Figure ch02_stability: regions of absolute stability of the two multistep families of CVODE, computed (not drawn) from the
characteristic polynomials of the fixed-step formulas by a root test on a grid of z = h*lambda.
  Adams-Moulton, k steps, order k+1:   y_{n+1} - y_n = h sum_{j=0}^k beta_j f_{n+1-j}
  BDF of order k:                      sum_{j=1}^k (1/j) nabla^j y_{n+1} = h f_{n+1}
Every coefficient set is first checked against its order conditions (exact on polynomials up to the order).
CVODE itself changes step and order at run time, so these regions are a guide to the two families, not a law for a run.
Writes the real-axis and imaginary-axis facts used in the text to figures/ch02_numbers.json (key F_stability)."""
import sys, json
from pathlib import Path
from fractions import Fraction as Fr
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.patches import Patch

AM = {1: [Fr(1)], 2: [Fr(1, 2), Fr(1, 2)], 3: [Fr(5, 12), Fr(8, 12), Fr(-1, 12)], 4: [Fr(9, 24), Fr(19, 24), Fr(-5, 24), Fr(1, 24)],
      5: [Fr(251, 720), Fr(646, 720), Fr(-264, 720), Fr(106, 720), Fr(-19, 720)],
      6: [Fr(475, 1440), Fr(1427, 1440), Fr(-798, 1440), Fr(482, 1440), Fr(-173, 1440), Fr(27, 1440)]}   # key = order p, k = p - 1 steps

def check_am(p):
    """y = t^m, h = 1, t_{n+1-j} = -j:  y(0) - y(-1) = sum_j beta_j m (-j)^{m-1}  for m = 1..p (exact rational arithmetic)"""
    b = AM[p]
    for m in range(1, p + 1):
        lhs = Fr(0) ** m - Fr(-1) ** m
        rhs = sum(bj * m * Fr(-j) ** (m - 1) for j, bj in enumerate(b))
        assert lhs == rhs, (p, m, lhs, rhs)
    return True

def check_bdf(k):
    """sum_{j=1}^k (1/j) nabla^j y_{n+1} = h y'_{n+1} exactly for y = t^m, m <= k, h = 1, t_{n+1} = 0"""
    from math import comb
    for m in range(1, k + 1):
        y = lambda s: Fr(s) ** m                       # y(t_{n+1-i}) = (-i)^m
        total = Fr(0)
        for j in range(1, k + 1):
            nab = sum((-1) ** i * comb(j, i) * y(-i) for i in range(j + 1))
            total += Fr(1, j) * nab
        yprime = Fr(m) * Fr(0) ** (m - 1) if m > 1 else Fr(1)
        assert total == yprime, (k, m, total, yprime)
    return True

for p in AM: check_am(p)
for k in range(1, 6): check_bdf(k)

def poly_am(p):
    """z-dependent polynomial  zeta^{k+1} - zeta^k - z sum_j beta_j zeta^{k+1-j}  (k = p-1), coefficients as functions of z (descending powers)"""
    k = p - 1; b = [float(x) for x in AM[p]]
    def coeffs(z):
        c = np.zeros((len(z), k + 2), dtype=complex)
        c[:, 0] = 1.0; c[:, 1] += -1.0
        for j, bj in enumerate(b): c[:, j] += -z * bj          # power zeta^{k+1-j} sits at index j
        return c
    return coeffs

def poly_bdf(k):
    """rho(zeta) - z zeta^k,  rho(zeta) = sum_{j=1}^k (1/j) zeta^{k-j} (zeta-1)^j"""
    rho = np.zeros(k + 1)
    for j in range(1, k + 1):
        term = np.poly1d([1.0, -1.0]) ** j * np.poly1d([1.0] + [0.0] * (k - j)); cc = term.coeffs
        rho[k + 1 - len(cc):] += cc / j
    def coeffs(z):
        c = np.zeros((len(z), k + 1), dtype=complex); c[:] = rho; c[:, 0] += -z               # -z zeta^k
        return c
    return coeffs

def stable(coeffs, Z):
    z = Z.ravel(); c = coeffs(z); deg = c.shape[1] - 1
    comp = np.zeros((len(z), deg, deg), dtype=complex)
    comp[:, 0, :] = -c[:, 1:] / c[:, [0]]
    for i in range(1, deg): comp[:, i, i - 1] = 1.0
    ev = np.linalg.eigvals(comp)
    return (np.max(np.abs(ev), axis=1) <= 1 + 1e-9).reshape(Z.shape)

def real_axis_interval(coeffs, lo=-40.0, hi=0.0, n=2001):
    x = np.linspace(lo, hi, n); ok = stable(coeffs, x.astype(complex)[None, :])[0]
    if ok[-1]:
        # leftmost x such that [x, 0] is all stable; the grid only brackets it (step (hi-lo)/(n-1) = 0.02, which printed
        # -1.82 for Adams-Moulton order 5 instead of -1.8367), so refine by bisection between the last unstable and the
        # first stable grid point (editor's fix, 2026-10-10)
        bad = np.where(~ok)[0]
        if len(bad) == 0:
            return None
        a, b = float(x[bad.max()]), float(x[bad.max() + 1])        # a unstable, b stable
        for _ in range(60):
            m = 0.5 * (a + b)
            if stable(coeffs, np.array([[m + 0j]]))[0, 0]:
                b = m
            else:
                a = m
        return b
    return 0.0

def imag_axis_largest(coeffs, hi=8.0, n=1001):
    y = np.linspace(0, hi, n); ok = stable(coeffs, (1j * y).astype(complex)[None, :])[0]
    bad = np.where(~ok)[0]
    return float(y[-1]) if len(bad) == 0 else float(y[bad.min() - 1]) if bad.min() > 0 else 0.0

# ------------------------------------------------------------ data
xs = np.linspace(-10.5, 18.5, 300); ys = np.linspace(-14.0, 14.0, 280); XX, YY = np.meshgrid(xs, ys); Z = XX + 1j * YY
am_orders = [3, 4, 5, 6]; bdf_orders = [1, 2, 3, 4, 5]
am_mask = {p: stable(poly_am(p), Z) for p in am_orders}
bdf_mask = {k: stable(poly_bdf(k), Z) for k in bdf_orders}
facts = {"am_real_axis_left_end": {p: real_axis_interval(poly_am(p)) for p in [1, 2, 3, 4, 5, 6]},
         "am_largest_stable_imag_from_origin": {p: imag_axis_largest(poly_am(p)) for p in [2, 3, 4, 5, 6]},
         "bdf_real_axis_left_end": {k: real_axis_interval(poly_bdf(k)) for k in bdf_orders},
         "bdf_unstable_right_extent": {k: float(xs[np.where((~bdf_mask[k]).any(axis=0))[0].max()]) for k in bdf_orders},
         "bdf_imag_axis_origin_neighbourhood_stable": {k: bool(stable(poly_bdf(k), np.array([[0.05j, 0.5j, 1.0j]]))[0].all()) for k in bdf_orders},
         "grid": {"x": [float(xs[0]), float(xs[-1]), len(xs)], "y": [float(ys[0]), float(ys[-1]), len(ys)]},
         "order_conditions_checked": "AM orders 1..6 (exactness on t^m, m <= order); BDF orders 1..5"}
# BDF angle of the wedge: the unstable lobe of BDF-k touches the imaginary axis; A(alpha) angles from the left half plane known values are NOT used -- measured below
def wedge_angle(k):
    """A(alpha)-stability angle: largest alpha such that the whole ray at angle alpha from the negative real axis (out to |z| = 40)
    is stable; bisection on the angle (stable rays form an interval [0, alpha])"""
    r = np.linspace(0.01, 40, 300)
    ray_ok = lambda t: bool(stable(poly_bdf(k), ((-np.cos(t) + 1j * np.sin(t)) * r)[None, :]).all())
    if ray_ok(np.pi / 2 - 1e-6): return 90.0
    lo, hi = 0.0, np.pi / 2
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        if ray_ok(mid): lo = mid
        else: hi = mid
    return float(np.degrees(lo))
facts["bdf_A_alpha_angle_deg_measured"] = {k: wedge_angle(k) for k in bdf_orders}
print(json.dumps(facts, indent=1, default=str))

# ------------------------------------------------------------ figure
fig = plt.figure(figsize=(TEXTW, 2.95))
ax = fig.add_axes([0.075, 0.14, 0.40, 0.76]); bx = fig.add_axes([0.575, 0.14, 0.40, 0.76])
colA = {3: "#9EC1DD", 4: "#6FA3CC", 5: "#3F7DB4", 6: BLUE}
for p in am_orders:                                      # bigger orders on top, smaller region
    ax.contourf(XX, YY, am_mask[p].astype(float), levels=[0.5, 1.5], colors=[colA[p]], alpha=0.85 if p > 3 else 0.7)
    ax.contour(XX, YY, am_mask[p].astype(float), levels=[0.5], colors=[BLUE], linewidths=0.5)
ax.axhline(0, color=GREY, lw=0.5); ax.axvline(0, color=GREY, lw=0.5)
# Adams-Moulton order 2 (trapezoidal rule) = the whole left half plane
ax.axvspan(-10.5, 0, color=TEAL, alpha=0.07, lw=0)
ax.text(-10.0, -6.5, "orders 1 and 2\n(implicit Euler,\ntrapezoidal rule)\ncontain the whole\nleft half-plane", fontsize=6.4, color=TEAL, va="top", linespacing=1.15)
ax.set_xlim(-10.5, 18.5); ax.set_ylim(-14.0, 14.0); ax.set_aspect("equal")
ax.set_xlabel(r"Re$\,h\lambda$"); ax.set_ylabel(r"Im$\,h\lambda$"); panel(ax, "a")
ax.set_title("Adams–Moulton, orders 3–6: stable inside", fontsize=8.8, pad=3)
ax.legend(handles=[Patch(color=colA[p], label=f"order {p}") for p in am_orders], loc="upper right", fontsize=7.2, ncol=1, handlelength=1.0, borderpad=0.2)
colB = {1: "#F0D5CF", 2: "#E7B8AE", 3: "#D98F82", 4: "#C26352", 5: RED}
bx.set_facecolor("#EAF2F8")
for k in bdf_orders[::-1]:
    bx.contourf(XX, YY, (~bdf_mask[k]).astype(float), levels=[0.5, 1.5], colors=[colB[k]], alpha=0.95)
    bx.contour(XX, YY, bdf_mask[k].astype(float), levels=[0.5], colors=[RED], linewidths=0.5)
bx.axhline(0, color=GREY, lw=0.5); bx.axvline(0, color=GREY, lw=0.5)
bx.set_xlim(-10.5, 18.5); bx.set_ylim(-14.0, 14.0); bx.set_aspect("equal")
bx.set_xlabel(r"Re$\,h\lambda$"); bx.set_ylabel(r"Im$\,h\lambda$"); panel(bx, "b")
bx.set_title("BDF, orders 1–5: stable outside", fontsize=8.8, pad=3)
bx.legend(handles=[Patch(color=colB[k], label=f"order {k}") for k in bdf_orders], loc="upper left", fontsize=7.2, ncol=1, handlelength=1.0, borderpad=0.2)
save(fig, "ch02_stability")
d = json.loads((Path(__file__).with_name("ch02_numbers.json")).read_text()) if Path(__file__).with_name("ch02_numbers.json").exists() else {}
d["F_stability"] = facts; Path(__file__).with_name("ch02_numbers.json").write_text(json.dumps(d, indent=1, default=str))
