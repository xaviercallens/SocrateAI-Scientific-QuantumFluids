"""Tier B tests for the invariant search (design memo DUAL_SCALE_SECOND_INVARIANT + addendum A1)."""
import numpy as np
import pytest

from quantumfluids.w4_shell_model import invariant_search as S

N = 4
K = 2.0 ** np.arange(N + 1)


def _null(seam, mu=0.0, D=0.0, cubic=True, seed=0):
    rng = np.random.default_rng(seed)
    basis = S.quadratic_basis(N + 1) + S.quartic_basis(N + 1) + (S.cubic_basis(N + 1) if cubic else [])
    V = S.sample_states(3 * len(basis), N + 1, rng)
    null, _ = S.nullspace(S.lie_matrix(basis, V, S.shell_rhs(V, K, seam, mu, D)))
    return basis, null


def _mass(basis):
    return np.array([1.0 if b.label.startswith("|v") else 0.0 for b in basis])


def test_positive_control_gp_energy_found():
    modes = [-1, 0, 1]; omega = np.array([1.0, 0.0, 1.0]); g = 0.7
    basis = S.quadratic_basis(3) + S.quartic_basis(3)
    P = S.sample_states(4 * len(basis), 3, np.random.default_rng(1))
    null, _ = S.nullspace(S.lie_matrix(basis, P, S.gp_rhs(P, modes, omega, g)))
    assert S.in_span(S.gp_energy_coeffs(basis, modes, omega, g), null) < 1e-8


def test_negative_control_leaking_seam_loses_mass():
    basis, null = _null("leak")
    assert S.in_span(_mass(basis), null) > 1e-3


@pytest.mark.parametrize("seam,mu,D", [("trunc", 0.0, 0.0), ("gpe", 1.0, 0.0), ("trunc", 0.0, 0.3), ("gpe", 0.5, 0.3)])
def test_predicted_hamiltonian_is_conserved(seam, mu, D):
    basis, null = _null(seam, mu, D)
    assert S.in_span(_mass(basis), null) < 1e-8
    assert S.in_span(S.predicted_H(basis, K, mu, D), null) < 1e-8


def test_wrong_weights_are_rejected():
    basis, null = _null("trunc")
    c = S.predicted_H(basis, K)
    j = [i for i, b in enumerate(basis) if b.label == "Im c2^2 v3"][0]
    c[j] *= 1.5
    assert S.in_span(c, null) > 1e-3


def _mass_sq(basis):
    idx = {b.label: j for j, b in enumerate(basis)}
    c = np.zeros(len(basis))
    for a in range(N + 1):
        for b in range(N + 1):
            lo, hi = min(a, b), max(a, b)
            c[idx[f"Re c{lo}c{hi}v{lo}v{hi}"]] += 1.0
    return c


def test_nullspace_is_exactly_mass_masssq_and_H():
    """Addendum A1 predicted dim 1 / 2 and forgot the trivial quartic mass^2; the measured answer is dim 2 / 3."""
    basis, null = _null("trunc", cubic=False)
    assert null.shape[1] == 2
    known = np.stack([_mass(basis), _mass_sq(basis)], axis=1)
    assert max(S.in_span(null[:, i], known) for i in range(2)) < 1e-8
    basis, null = _null("trunc", cubic=True)
    assert null.shape[1] == 3
    known = np.stack([_mass(basis), _mass_sq(basis), S.predicted_H(basis, K)], axis=1)
    assert max(S.in_span(null[:, i], known) for i in range(3)) < 1e-8
