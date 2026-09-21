"""Pins for src/quantumfluids/tda/cubical.py: the duality control (pre-registration D0)."""
import numpy as np

from quantumfluids.tda.cubical import duality_defect, minima_with_depth


def _field(n=64, seed=3, kc=8):
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(n, 1 / n); K = np.hypot(k[:, None], k[None, :])
    return np.real(np.fft.ifft2(np.fft.fft2(rng.normal(size=(n, n))) * (K < kc)))


def test_dual_constructions_agree_exactly():
    n0, n1, d = duality_defect(_field(), "V")
    assert n0 == n1 and n0 > 5 and d == 0.0


def test_same_construction_does_not():
    """The control's control: if this ever starts agreeing, the constructions are not what we think."""
    n0, n1, d = duality_defect(_field(), "T")
    assert n0 != n1 or d > 0


def test_reported_birth_pixels_are_local_minima():
    """Guards GUDHI's Fortran-order cell indexing (a tautological version of this check was written first)."""
    f = _field(48, 5)
    b, dep, ij = minima_with_depth(f)
    nb = np.stack([np.roll(np.roll(f, di, 0), dj, 1) for di in (-1, 0, 1) for dj in (-1, 0, 1) if (di, dj) != (0, 0)])
    assert np.all((f <= nb.min(axis=0))[ij[:, 0], ij[:, 1]])
    assert np.allclose(b, f[ij[:, 0], ij[:, 1]]) and np.all(dep > 0)
