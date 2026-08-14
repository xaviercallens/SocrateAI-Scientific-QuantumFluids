"""Complexified dyadic shell dynamics for the W4 dispersive regulator.

Implements the model designed in docs/designs/M2_W4_DISPERSIVE_SHELL.md
(AUDITED 2026-08-14). Read that memo before changing anything here; in
particular §2c records why this specific complexification was chosen and
what it costs.

MODEL
  Shells n = 0..N, wavenumbers k_n = 2^n, complex amplitudes a_n.
  Boundary convention a_{-1} = a_{N+1} = 0.

    da_n/dt = B_n(a)  -  nu k_n^2 a_n  -  i D k_n^2 a_n

  where the nonlinearity is the CONJUGATED complexification

    B_n(a) = k_{n-1} a_{n-1}^2  -  k_n conj(a_n) a_{n+1}

  which (memo §2b, and tests/test_shell_dynamics.py):
    - conserves E = 1/2 sum |a_n|^2 exactly (to round-off),
    - reduces EXACTLY to the real Katz-Pavlovic dyadic nonlinearity on
      real data, so the reals are an invariant subspace and
      MechanicaFluidorum's exploration/dyadic_cascade.py is recovered
      bit-for-bit at D = 0.

  The two linear terms are the same k^2 structure with the coefficient
  rotated 90 degrees in the complex plane:
    -nu k^2 a   (nu real)  -> DISSIPATIVE, removes energy
    -i D k^2 a  (D real)   -> DISPERSIVE, energy-neutral phase rotation

  Note that the dispersive term BREAKS the reality-invariance: applied to
  real data it produces a purely imaginary contribution. That is not a
  defect -- it is the whole point, and it is why the Katz-Pavlovic
  falsification trap applies only at D = 0 (memo §6).

TIER
  Tier B (unit-testable). This module carries NO Tier A backing:
  MechanicaFluidorum's Lean theorems (shellB_energy_conservation,
  DyadicShellHypothesisU) are about the REAL model and do not transfer to
  the complexification -- memo §2c(ii), audit ruling O2.

SCOPE
  Per audit ruling O4 this is a BEC/GPE-regime construction. The quantum
  pressure term yields Bogoliubov dispersion, which is monotonic and has
  NO roton minimum. It does not model superfluid He-4's excitation
  spectrum, and M1's fitted Delta / Q_m have no counterpart here.
"""

import numpy as np

__all__ = [
    "k_shells",
    "nonlinear_real",
    "nonlinear_conj",
    "viscous",
    "quantum_pressure",
    "rhs",
    "energy",
    "enstrophy_sum",
    "enstrophy_max",
    "enstrophy_both",
    "energy_rate",
]


def k_shells(N: int) -> np.ndarray:
    """Wavenumbers k_n = 2^n for n = 0..N."""
    if N < 0:
        raise ValueError(f"N must be >= 0, got {N}")
    return 2.0 ** np.arange(N + 1)


def nonlinear_real(a: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Real dyadic (Katz-Pavlovic / Desnyansky-Novikov) nonlinearity.

        B_n = k_{n-1} a_{n-1}^2 - k_n a_n a_{n+1}

    Provided for cross-checking against MechanicaFluidorum's reference
    implementation and as the D=0 positive control (memo §6). Conserves
    1/2 sum a_n^2 for real a.
    """
    _check_shapes(a, k)
    out = np.zeros_like(a)
    out[1:] = k[:-1] * a[:-1] ** 2
    out[:-1] -= k[:-1] * a[:-1] * a[1:]
    return out


def nonlinear_conj(a: np.ndarray, k: np.ndarray) -> np.ndarray:
    """Conjugated complexification of the dyadic nonlinearity.

        B_n = k_{n-1} a_{n-1}^2 - k_n conj(a_n) a_{n+1}

    Conserves E = 1/2 sum |a_n|^2 for complex a, and coincides with
    nonlinear_real on real input (np.conj is a no-op there), so real
    dtype in gives real dtype out.

    The single conjugation placement is what makes the energy cancellation
    work; moving or removing it breaks conservation (memo §2a shows the
    unconjugated version failing by ~1e+3). It is NOT unique -- other
    placements also conserve -- and this one is chosen for the
    invariant-subspace property, as a labelled deformation (memo §2c(iii)).
    """
    _check_shapes(a, k)
    out = np.zeros_like(a)
    out[1:] = k[:-1] * a[:-1] ** 2
    out[:-1] -= k[:-1] * np.conj(a[:-1]) * a[1:]
    return out


def viscous(a: np.ndarray, k: np.ndarray, nu: float) -> np.ndarray:
    """Dissipative regulator: -nu k^2 a. Real coefficient, removes energy."""
    _check_shapes(a, k)
    return -nu * k**2 * a


def quantum_pressure(a: np.ndarray, k: np.ndarray, D: float) -> np.ndarray:
    """Dispersive regulator (W4): -i D k^2 a.

    Imaginary coefficient, energy-neutral. D = hbar/2m in the GPE reading
    (memo §3). Always returns a complex array, even for real input --
    dispersion takes you out of the real subspace.
    """
    _check_shapes(a, k)
    return -1j * D * k**2 * a


def rhs(a: np.ndarray, k: np.ndarray, nu: float = 0.0, D: float = 0.0) -> np.ndarray:
    """Full right-hand side: conjugated nonlinearity + both regulator terms.

    nu = D = 0 gives the inviscid, undispersed model, whose real subspace
    is where Katz-Pavlovic (2005) proves finite-time blow-up -- the O5
    falsification trap of memo §6.
    """
    out = nonlinear_conj(a, k)
    if nu:
        out = out + viscous(a, k, nu)
    if D:
        out = out + quantum_pressure(a, k, D)
    return out


def energy(a: np.ndarray) -> float:
    """E = 1/2 sum |a_n|^2. Conserved by the nonlinearity alone."""
    return 0.5 * float(np.sum(np.abs(a) ** 2))


def enstrophy_sum(a: np.ndarray, k: np.ndarray) -> float:
    """Omega_sum = 1/2 sum_n k_n^2 |a_n|^2 -- enstrophy as conventionally defined."""
    _check_shapes(a, k)
    return 0.5 * float(np.sum((k**2) * np.abs(a) ** 2))


def enstrophy_max(a: np.ndarray, k: np.ndarray) -> float:
    """Omega_max = max_n 1/2 k_n^2 |a_n|^2 -- the largest single-shell contribution.

    NOT enstrophy. Provided because MechanicaFluidorum's
    exploration/dyadic_cascade.py writes this quantity to CSV under the
    name sup_Omega while its docstring defines the sum form -- see
    docs/DEFECT_REPORT_MF_ENSTROPHY.md. Audit ruling O1 requires this
    stream to record BOTH so that whether beta differs between the two
    definitions is settled empirically rather than assumed.
    """
    _check_shapes(a, k)
    return float(np.max(0.5 * (k**2) * np.abs(a) ** 2))


def enstrophy_both(a: np.ndarray, k: np.ndarray) -> dict:
    """Both enstrophy conventions in one call, per audit ruling O1."""
    return {"sum": enstrophy_sum(a, k), "max": enstrophy_max(a, k)}


def energy_rate(a: np.ndarray, da: np.ndarray) -> float:
    """dE/dt = sum_n Re(conj(a_n) * da_n).

    The diagnostic the conservation tests are built on. Its detection
    power is established by negative controls in
    tests/test_shell_dynamics.py -- per OP2_LITE §1a-BIS, a conservation
    checker never shown to REJECT a non-conserving system cannot be
    believed when it accepts a conserving one.
    """
    if a.shape != da.shape:
        raise ValueError(f"shape mismatch: a {a.shape} vs da {da.shape}")
    return float(np.sum(np.real(np.conj(a) * da)))


def _check_shapes(a: np.ndarray, k: np.ndarray) -> None:
    if a.shape != k.shape:
        raise ValueError(
            f"amplitude array shape {a.shape} does not match wavenumber "
            f"array shape {k.shape} -- these must be the same length (N+1)"
        )
