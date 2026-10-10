"""Shared helpers of the chapter-9 figure scripts: loaders for the reference (Kwon & Shin, Zenodo 20068724) and our Rust snapshots,
the discrete winding (plaquette charges), the local Mach number, and the reference's own vortex counter."""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration" / "external"))
import ks_vortex_count as KC                      # the reference's own counting rule (ported)
REFDIR = Path("/mnt/data/xdev-cache/qf-external/20068724/extracted")
OURDIR = Path("/mnt/data/xdev-cache/qf-external/ks_rust_t50/snap")
CSV_OURS = Path("/mnt/data/xdev-cache/qf-external/ks_rust_t50/kwon_shin_force.csv")
DX = 0.5; NX, NY = 1000, 500
x = np.arange(-250, 250, DX); y = np.arange(-125, 125, DX)
V0, SIGMA, XOBS, VFLOW = 0.9, 20.0, 100.0, 0.55
XX, YY = np.meshgrid(x, y)
POT = V0 * np.exp(-2 * ((XX - XOBS) ** 2 + YY ** 2) / SIGMA ** 2)

def load_ref(t): return np.load(REFDIR / f"psi_time_{t:.1f}.npy").astype(np.complex128)
def load_ours(t): return np.load(OURDIR / f"psi_time_{t:.1f}.npy")

def pdiff(a, b):
    """principal difference of two angles, in (-pi, pi]  (VortexWinding.pdiff)"""
    d = (b - a + np.pi) % (2 * np.pi) - np.pi
    return np.where(d == -np.pi, np.pi, d)

def edge_steps(psi):
    th = np.angle(psi)
    return pdiff(th, np.roll(th, -1, 1)), pdiff(th, np.roll(th, -1, 0))      # step along +x, step along +y (periodic)

def plaquette_charge(psi):
    """integer charge of every elementary plaquette (counter-clockwise loop, corners (j,i),(j,i+1),(j+1,i+1),(j+1,i)), periodic grid.
    Returns (q_float, q_int): q_float = loop sum of principal differences / 2 pi  (an integer up to rounding: VortexWinding.loop_sum_eq_mul)."""
    sx, sy = edge_steps(psi)
    s = sx + np.roll(sy, -1, 1) - np.roll(sx, -1, 0) - sy
    q = s / (2 * np.pi)
    return q, np.rint(q).astype(int)

def mach(psi, vflow=VFLOW):
    """local Mach number in the frame of the obstacle: u = grad(theta) - v e_x (the fluid streams towards -x), c = sqrt(n)  (g = m = hbar = 1)"""
    kx = 2 * np.pi * np.fft.fftfreq(NX, DX); ky = 2 * np.pi * np.fft.fftfreq(NY, DX)
    ph = np.fft.fft2(psi); px = np.fft.ifft2(1j * kx[None, :] * ph); py = np.fft.ifft2(1j * ky[:, None] * ph)
    n = np.abs(psi) ** 2; nn = n + 1e-30
    ux = (psi.conj() * px).imag / nn - vflow; uy = (psi.conj() * py).imag / nn
    return np.sqrt(ux ** 2 + uy ** 2) / np.sqrt(nn), ux, uy, n

def vorticity(psi):
    """curl of the superfluid velocity u = Im(psi* grad psi)/|psi|^2, central differences (zero except at cores in the continuum)"""
    kx = 2 * np.pi * np.fft.fftfreq(NX, DX); ky = 2 * np.pi * np.fft.fftfreq(NY, DX)
    ph = np.fft.fft2(psi); px = np.fft.ifft2(1j * kx[None, :] * ph); py = np.fft.ifft2(1j * ky[:, None] * ph)
    nn = np.abs(psi) ** 2 + 1e-30
    ux = (psi.conj() * px).imag / nn; uy = (psi.conj() * py).imag / nn
    return np.gradient(uy, DX, axis=1) - np.gradient(ux, DX, axis=0)

def charged(psi):
    """list of (x, y, q) of the nonzero plaquettes (centre of the plaquette)"""
    _, qi = plaquette_charge(psi)
    nz = np.argwhere(qi != 0)
    return [(x[i] + DX / 2, y[j] + DX / 2, int(qi[j, i])) for j, i in nz]

def ref_rule(psi):
    """vortices found by the reference's own rule: list of (X_index, Y_index, sign) -> (x, y, sign)"""
    return [(x[a], y[b], s) for a, b, s in KC.count(psi)]

def scale_bar(ax, x0, y0, length=10, label=None, color="white", fs=7.5):
    ax.plot([x0, x0 + length], [y0, y0], color=color, lw=2.0, solid_capstyle="butt")
    ax.text(x0 + length / 2, y0 + 0.02 * (ax.get_ylim()[1] - ax.get_ylim()[0]) + 0.6, label or rf"{length}$\,\xi$", color=color, ha="center", va="bottom", fontsize=fs)


# ----------------------------------------------------------------------------------------------------------------------------
# additions of the chapter-9 session (2026-10-09): forces, census matching, symmetry, supersonic statistics, spectral zoom
# ----------------------------------------------------------------------------------------------------------------------------
# interior of the absorbing layers used by the reference for the force (Eren_force: x in [-200,200), y in [-85,85), np.gradient + trapezoid)
_XMIN = int(np.where(x == -200.0)[0][0]); _XMAX = int(np.where(x == 200.0)[0][0])
_YMIN = int(np.where(y == -85.0)[0][0]); _YMAX = int(np.where(y == 85.0)[0][0])
_DVX = np.gradient(POT[_YMIN:_YMAX, _XMIN:_XMAX], DX, axis=1)
_DVY = np.gradient(POT[_YMIN:_YMAX, _XMIN:_XMAX], DX, axis=0)

def forces(psi):
    """(F_x, F_y) = (int dV/dx |psi|^2, int dV/dy |psi|^2) over the interior, exactly as the reference's Eren_force.
    F_x < 0 here: the obstacle is pushed along the flow (towards -x); the drag is D = -F_x."""
    n = np.abs(psi[_YMIN:_YMAX, _XMIN:_XMAX]) ** 2
    xc, yc = x[_XMIN:_XMAX], y[_YMIN:_YMAX]
    return (float(np.trapezoid(np.trapezoid(_DVX * n, xc, axis=1), yc)), float(np.trapezoid(np.trapezoid(_DVY * n, xc, axis=1), yc)))

def load_ref_force():
    """columns of the reference's Force/force_dt=0.02.txt (written every 0.1 tau): t, F_x, F_y, dE/dt"""
    return np.loadtxt(REFDIR / "force_dt=0.02.txt").T

def load_ref_counts():
    """columns of the reference's Vortex/vortex.txt (every 5 tau, to t = 100): t, count, count + unwound (the two columns are equal here)"""
    return np.loadtxt(REFDIR / "vortex.txt").T

def load_ours_force():
    """t, F_x(ours), F_x(reference), difference, every 0.1 tau to t = 50 (written by the Rust example kwon_shin)"""
    return np.loadtxt(CSV_OURS, delimiter=",", skiprows=1).T

def census_match(A, B, tol=1):
    """compare two censuses [(x, y, q), ...] of plaquettes: returns (identical, within_tol, only_A, only_B), counting a pair when the
    charges are equal and the plaquette indices differ by at most `tol` cells in each direction (greedy nearest matching)"""
    ia = [(int(round((xx - DX / 2 + 250) / DX)), int(round((yy - DX / 2 + 125) / DX)), q) for xx, yy, q in A]
    ib = [(int(round((xx - DX / 2 + 250) / DX)), int(round((yy - DX / 2 + 125) / DX)), q) for xx, yy, q in B]
    sa, sb = set(ia), set(ib)
    ident = sa & sb
    ra, rb = sorted(sa - ident), sorted(sb - ident)
    close = 0
    for (i, j, q) in ra:
        best = None
        for (k, (i2, j2, q2)) in enumerate(rb):
            if q2 == q and abs(i - i2) <= tol and abs(j - j2) <= tol:
                best = k; break
        if best is not None:
            rb.pop(best); close += 1
    ra_left = len(ra) - close
    return len(ident), close, ra_left, len(rb)

def mirror(psi):
    """psi(x, -y) on the grid (row j -> row (Ny - j) mod Ny)"""
    return np.roll(psi[::-1, :], 1, axis=0)

def asymmetry(psi):
    """relative L2 distance of psi from its mirror image: 0 for a y-symmetric field"""
    return float(np.linalg.norm(psi - mirror(psi)) / np.linalg.norm(psi))

def supersonic_stats(psi):
    """local Mach number M = |grad theta - v e_x| / sqrt(n); returns dict with max M and its position, area of {M > 1}, extents, number of blobs"""
    from scipy import ndimage
    M, ux, uy, n = mach(psi)
    sup = M > 1.0
    lab, nb = ndimage.label(sup)
    jmax = np.unravel_index(M.argmax(), M.shape)
    out = dict(Mmax=float(M.max()), x_Mmax=float(x[jmax[1]]), y_Mmax=float(y[jmax[0]]), area=float(sup.sum() * DX ** 2), blobs=int(nb))
    if sup.any():
        ys_, xs_ = y[np.any(sup, axis=1)], x[np.any(sup, axis=0)]
        out.update(y_min=float(ys_.min()), y_max=float(ys_.max()), x_min=float(xs_.min()), x_max=float(xs_.max()), width_y=float(ys_.max() - ys_.min() + DX))
    return out

def fourier_zoom(psi, xlim, ylim, up=4):
    """spectral interpolation of the periodic field psi on the window xlim x ylim, `up` times finer than the grid.
    Returns (xf, yf, field); the field is band-limited exactly as psi, so densities and phases are not smoothed by the interpolation."""
    Ny_, Nx_ = psi.shape
    ph = np.fft.fft2(psi) / (Nx_ * Ny_)
    kx = 2 * np.pi * np.fft.fftfreq(Nx_, DX); ky = 2 * np.pi * np.fft.fftfreq(Ny_, DX)
    xf = np.arange(xlim[0], xlim[1], DX / up); yf = np.arange(ylim[0], ylim[1], DX / up)
    Ex = np.exp(1j * np.outer(xf + 250.0, kx)); Ey = np.exp(1j * np.outer(yf + 125.0, ky))
    return xf, yf, Ey @ ph @ Ex.T


def rule_candidates(psi):
    """The reference's counting rule (exploration/external/ks_vortex_count.py, a line-by-line port of vortex_GPU.py::vortex_detect), opened up:
    returns every candidate that survives the density test (local minimum along axis 0 with n < 0.2, outside the disc of radius 5 cells around the
    obstacle) and the merging test (closer than 3 xi to an earlier one is dropped), with the loop integral of the rule (principal differences on the
    square loop of half-width 4 cells, steps of 0.3 pi or more are DROPPED from the sum) in units of pi, and whether |integral| > 0.9 pi (counted).
    The accepted entries are asserted to be exactly KC.count(psi)."""
    from scipy import spatial
    from scipy.signal import argrelmin
    density = np.abs(psi) ** 2; phase = np.arctan2(psi.imag, psi.real)
    ox = int(KC.OBST * NX / 2 / KC.RX + NX // 2); oy = NY // 2
    r_th = 5 // DX
    Y, X = argrelmin(density)
    temp = np.array([[yy, xx] for yy, xx in zip(Y, X) if density[yy, xx] < 0.2 and (xx - ox) ** 2 + (yy - oy) ** 2 > r_th ** 2])
    out = []
    if len(temp) == 0:
        return out
    count = 0
    while count < len(temp):
        dist, idx = spatial.KDTree(temp).query(temp[count], k=min(10, len(temp)))
        dist, idx = np.atleast_1d(dist)[1:], np.atleast_1d(idx)[1:]
        temp = np.delete(temp, idx[dist <= int(3 // DX)], axis=0); count += 1
    l = int(2 // DX)
    for Yc, Xc in temp:
        if Xc + l >= NX - l or Yc + l >= NY - l:
            continue
        xs = list(range(Xc - l, Xc + l + 1)) + [Xc + l] * (2 * l - 1) + list(range(Xc - l, Xc + l + 1))[::-1] + [Xc - l] * (2 * l - 1)
        ys = [Yc + l] * (2 * l + 1) + list(range(Yc - l + 1, Yc + l))[::-1] + [Yc - l] * (2 * l + 1) + list(range(Yc - l + 1, Yc + l))
        integral, dropped = 0.0, 0
        for k in range(len(xs) - 1):
            dd = np.angle(np.exp(1j * (phase[ys[k + 1], xs[k + 1]] - phase[ys[k], xs[k]])))
            if abs(dd) < 0.3 * np.pi: integral += dd
            else: dropped += 1
        integral += np.angle(np.exp(1j * (phase[ys[0], xs[0]] - phase[ys[-1], xs[-1]])))
        out.append(dict(X=int(Xc), Y=int(Yc), x=float(x[Xc]), y=float(y[Yc]), n_min=float(density[Yc, Xc]), integral_over_pi=float(integral / np.pi), dropped=int(dropped), counted=bool(abs(integral) > 0.9 * np.pi),
                        sign_ref_convention=(1 if integral > 0 else -1)))
    acc = sorted((o["X"], o["Y"]) for o in out if o["counted"])
    assert acc == sorted((int(a), int(b)) for a, b, s in KC.count(psi)), "port mismatch"
    return out

def enclosed_charge(cands, psi):
    """for each ACCEPTED candidate of rule_candidates: the plaquettes of non-zero exact charge inside its loop (indices of the plaquette centres within the loop square)"""
    q, qi = plaquette_charge(psi)
    res = []
    l = int(2 // DX)
    for c in cands:
        if not c["counted"]: continue
        sub = qi[c["Y"] - l: c["Y"] + l, c["X"] - l: c["X"] + l]          # plaquettes (j, i) with corners inside the loop square
        res.append(dict(x=c["x"], y=c["y"], net=int(sub.sum()), n_plaq=int(np.count_nonzero(sub)), plaq=[(int(i + c["X"] - l), int(j + c["Y"] - l), int(sub[j, i])) for j, i in np.argwhere(sub != 0)]))
    return res
