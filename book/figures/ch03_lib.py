"""Shared helpers for chapter 3 (units hbar = m = g = n0 = 1, healing length xi = hbar/sqrt(m g n0) = 1, kappa = 2 pi).
The solver is qf_pgpe (Rust, rusty-SUNDIALS workspace); its field is the array of projected Fourier amplitudes c_k
(numpy fft2 convention), so psi on the grid is ifft2(c) and psi at ANY point x is (1/N^2) sum_k c_k exp(i k.x)."""
import os, sys, json
sys.path.insert(0, "/mnt/data/xdev-cache/qf_ext")
import numpy as np
import qf_pgpe

CACHE = "/mnt/data/xdev-cache/ch03"
N, L = 128, 64.0
KAPPA = 2 * np.pi

def make(n=N, l=L):
    return qf_pgpe.Pgpe(n, l)

def kvec(s):
    k1 = 2 * np.pi * np.fft.fftfreq(s.n, d=s.dx)
    kx, ky = np.meshgrid(k1, k1, indexing="ij")
    return kx, ky

def psi_grid(s, c):
    return np.fft.ifft2(c)

def pdiff(a, b):
    """principal difference in (-pi, pi]: the numpy form of VortexWinding.pdiff."""
    d = np.mod(b - a + np.pi, 2 * np.pi) - np.pi      # in [-pi, pi)
    return np.where(d == -np.pi, np.pi, d)

class Evaluator:
    """Exact evaluation of the band-limited field (and its gradient) at arbitrary points from the nonzero modes."""
    def __init__(self, s, c):
        kx, ky = kvec(s)
        m = np.abs(c) > 0
        self.kx, self.ky, self.c = kx[m], ky[m], c[m] / s.n ** 2
    def psi(self, x, y):
        x = np.atleast_1d(x); y = np.atleast_1d(y)
        E = np.exp(1j * (np.outer(x, self.kx) + np.outer(y, self.ky)))
        return E @ self.c
    def psi_grad(self, x, y):
        x = np.atleast_1d(x); y = np.atleast_1d(y)
        E = np.exp(1j * (np.outer(x, self.kx) + np.outer(y, self.ky)))
        return E @ self.c, E @ (1j * self.kx * self.c), E @ (1j * self.ky * self.c)

def circle_points(cx, cy, r, M, phase0=0.0):
    t = phase0 + 2 * np.pi * np.arange(M) / M
    return cx + r * np.cos(t), cy + r * np.sin(t), t

def loop_winding(ev, cx, cy, r, M=720):
    """winding of arg(psi) on a circle of M samples: the sum of principal differences (the detector of ContinuumWinding)."""
    x, y, t = circle_points(cx, cy, r, M)
    p = ev.psi(x, y); th = np.angle(p)
    st = pdiff(th, np.roll(th, -1))
    return st.sum() / (2 * np.pi), np.abs(p).min(), np.abs(st).max()

def loop_circulation(ev, cx, cy, r, M=720):
    """Gamma = closed integral of u.dl, u = Im(conj(psi) grad psi)/|psi|^2 (Madelung velocity), trapezoid rule."""
    x, y, t = circle_points(cx, cy, r, M)
    p, px, py = ev.psi_grad(x, y)
    n = np.abs(p) ** 2
    ux = np.imag(np.conj(p) * px) / n; uy = np.imag(np.conj(p) * py) / n
    tx, ty = -np.sin(t), np.cos(t)
    return float(np.sum((ux * tx + uy * ty) * r * (2 * np.pi / M)))

def madelung_split(s, c):
    """Grid integrals (trapezoid = exact for the sampled integrand) of: kinetic 1/2 |grad psi|^2, quantum pressure
    1/2 |grad sqrt(n)|^2, flow 1/2 n |u|^2, interaction 1/2 n^2.  Returns dict + the density maps."""
    kx, ky = kvec(s)
    psi = np.fft.ifft2(c)
    px = np.fft.ifft2(1j * kx * c); py = np.fft.ifft2(1j * ky * c)
    n = np.maximum(np.abs(psi) ** 2, 1e-300)
    jx = np.imag(np.conj(psi) * px); jy = np.imag(np.conj(psi) * py)          # n u
    ax = np.real(np.conj(psi) * px); ay = np.real(np.conj(psi) * py)          # a grad a = grad n / 2
    kin = 0.5 * (np.abs(px) ** 2 + np.abs(py) ** 2)
    q = 0.5 * (ax ** 2 + ay ** 2) / n
    fl = 0.5 * (jx ** 2 + jy ** 2) / n
    d2 = s.dx ** 2
    out = dict(E_kin=float(kin.sum() * d2), E_q=float(q.sum() * d2), E_flow=float(fl.sum() * d2), E_int=float(0.5 * (n ** 2).sum() * d2),
               E_kin_parseval=float(np.sum(0.5 * (kx ** 2 + ky ** 2) * np.abs(c) ** 2) * d2 / s.n ** 2),
               max_pointwise=float(np.max(np.abs(kin - q - fl)) / np.max(kin)),
               E_pgpe=float(s.energy(c)))
    return out, dict(kin=kin, q=q, flow=fl, n=n, ux=jx / n, uy=jy / n)

def plaquette_charges(psi):
    th = np.angle(psi)
    dx_ = pdiff(th, np.roll(th, -1, 0)); dy_ = pdiff(th, np.roll(th, -1, 1))
    w = dx_ + np.roll(dy_, -1, 0) - np.roll(dx_, -1, 1) - dy_
    return np.rint(w / (2 * np.pi)).astype(int), w / (2 * np.pi), dx_, dy_

def per_dist(a, b, Lbox=L):
    d = a - b; d = d - Lbox * np.round(d / Lbox); return np.hypot(d[..., 0], d[..., 1])
