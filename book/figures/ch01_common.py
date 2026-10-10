"""Shared helpers of the chapter-1 solver figures (triptych and speed budget).  Engine: qf_pgpe, the Rust projected Gross-Pitaevskii
engine of rusty-SUNDIALS (units hbar = m = g = 1, background density 1, so the sound speed is 1 and the healing length is 1).
Needs  PYTHONPATH=/mnt/data/xdev-cache/qf_ext  (the built Python extension)."""
import json, sys, subprocess
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "exploration" / "pgpe"))
import qf_pgpe

N, L = 128, 64.0
DX = L / N
IMPRINT = np.array([[26.0, 32.0], [38.0, 32.0]]); CHARGE = np.array([1, -1])      # vortex (+1) at x = 26, antivortex (-1) at x = 38, y = 32: separation 12


def engine():
    return qf_pgpe.Pgpe(N, L)


def fourier_data(c):
    """Active modes of a projected field c (numpy fft2 convention): wave vectors and amplitudes such that
    psi(x, y) = sum_k a_k exp(i (kx x + ky y))."""
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=DX)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    c = np.asarray(c); act = np.abs(c) > 0
    return KX[act], KY[act], c[act] / N ** 2


def velocity_grid(c):
    """psi, and the superfluid velocity v = Im(conj(psi) grad psi)/|psi|^2 on the grid (spectral derivatives); arrays [i, j] = [x, y]."""
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=DX)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    c = np.asarray(c)
    psi = np.fft.ifft2(c); px = np.fft.ifft2(1j * KX * c); py = np.fft.ifft2(1j * KY * c)
    n = np.abs(psi) ** 2
    return psi, (np.conj(psi) * px).imag / n, (np.conj(psi) * py).imag / n


_GL = np.polynomial.legendre.leggauss(12)


def line_integral(fd, a, b, pieces=4):
    """integral of v . dl along the straight segment a -> b (length units), Gauss-Legendre (12 nodes x `pieces`) on the exact
    band-limited field given by `fourier_data`."""
    kx, ky, ak = fd
    a = np.asarray(a, float); b = np.asarray(b, float)
    tot = 0.0
    for p in range(pieces):
        t0, t1 = p / pieces, (p + 1) / pieces
        t = t0 + 0.5 * (_GL[0] + 1) * (t1 - t0); w = 0.5 * _GL[1] * (t1 - t0)
        xs = a[0] + t * (b[0] - a[0]); ys = a[1] + t * (b[1] - a[1])
        ph = np.exp(1j * (np.outer(xs, kx) + np.outer(ys, ky)))
        psi = ph @ ak; px = ph @ (1j * kx * ak); py = ph @ (1j * ky * ak)
        n = np.abs(psi) ** 2
        vx = (np.conj(psi) * px).imag / n; vy = (np.conj(psi) * py).imag / n
        tot += np.sum(w * (vx * (b[0] - a[0]) + vy * (b[1] - a[1])))
    return float(tot)


def polygon_circulation(fd, corners):
    """circulation (in units of 2 pi hbar/m = kappa) along the closed polygon through `corners` (first corner repeated at the end)."""
    return sum(line_integral(fd, a, b) for a, b in zip(corners[:-1], corners[1:])) / (2 * np.pi)


def pdiff(a, b):
    """principal difference in (-pi, pi], exactly as QuantumFluids.VortexWinding.pdiff."""
    d = b - a
    return d - 2 * np.pi * np.ceil((d - np.pi) / (2 * np.pi))


def square_loop(i0, j0, i1, j1):
    """counter-clockwise lattice loop (x horizontal, y vertical), closed; grid indices."""
    pts = [(i, j0) for i in range(i0, i1)] + [(i1, j) for j in range(j0, j1)] + [(i, j1) for i in range(i1, i0, -1)] + [(i0, j) for j in range(j1, j0, -1)]
    return pts + [pts[0]]


def loop_corners(i0, j0, i1, j1):
    return [(i0 * DX, j0 * DX), (i1 * DX, j0 * DX), (i1 * DX, j1 * DX), (i0 * DX, j1 * DX), (i0 * DX, j0 * DX)]


def machine_note():
    up = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
    return up


def update_numbers(section, data):
    NJ = Path(__file__).with_name("ch01_numbers.json")
    allj = json.loads(NJ.read_text()) if NJ.exists() else {}
    allj[section] = data
    NJ.write_text(json.dumps(allj, indent=1))
