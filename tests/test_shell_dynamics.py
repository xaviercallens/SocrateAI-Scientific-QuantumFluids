"""Tier B harness for w4_shell_model.shell_dynamics.

Promoted from exploration/verify_complexification.py (Tier C scratch) as
required by docs/designs/M2_W4_DISPERSIVE_SHELL.md §8: the promotion is the
FIRST implementation step after audit, not a retrofit afterwards.

NEGATIVE CONTROLS ARE THE POINT OF THIS FILE (LL-2, and OP2_LITE §1a-BIS's
recorded near-miss where a detector would have shipped inverted). The
energy-conservation diagnostic is only trustworthy if it is shown to
REJECT systems that genuinely fail to conserve. Every positive assertion
below is paired with a negative control exercising the same diagnostic.

MUTATION-TESTED 2026-08-14. Negative controls establish that the diagnostic
rejects broken *test-local* systems; a mutation test establishes that the
suite rejects broken *production* code, which is a different claim. Three
bugs were injected into shell_dynamics.py and all three were caught, each
by a different combination of tests:

  injected bug                              caught by
  ----------------------------------------  --------------------------------
  conjugate dropped from nonlinear_conj     loop-reference, energy conservation
  quantum_pressure made real (-D k^2 a)     energy-neutrality, reality-breaking
  off-by-one in the incoming k slice        loop-reference, energy conservation,
                                            exact-reduction-to-real

Re-run that check if this file is substantially restructured; a suite that
passes but cannot fail is worse than no suite.
"""

import numpy as np
import pytest

from quantumfluids.w4_shell_model.shell_dynamics import (
    energy,
    energy_rate,
    enstrophy_both,
    enstrophy_max,
    enstrophy_sum,
    k_shells,
    nonlinear_conj,
    nonlinear_real,
    quantum_pressure,
    rhs,
    viscous,
)

N = 10
N_TRIALS = 200
ROUNDOFF = 1e-8  # generous vs. the ~1e-12 actually observed at N=10


@pytest.fixture
def k():
    return k_shells(N)


def _rng():
    return np.random.default_rng(20260814)


def _random_complex(rng, n=N + 1):
    return rng.normal(size=n) + 1j * rng.normal(size=n)


def _random_real(rng, n=N + 1):
    return rng.normal(size=n)


# =====================================================================
# Reference implementation (deliberately written as an index loop, to
# cross-check the vectorised production code against a transcription of
# the model as stated in the memo).
# =====================================================================

def _nonlinear_conj_loop(a, k):
    M = len(a) - 1
    out = np.zeros_like(a)
    for n in range(M + 1):
        a_nm1 = a[n - 1] if n - 1 >= 0 else 0.0
        k_nm1 = k[n - 1] if n - 1 >= 0 else 0.0
        a_np1 = a[n + 1] if n + 1 <= M else 0.0
        out[n] = k_nm1 * a_nm1 * a_nm1 - k[n] * np.conj(a[n]) * a_np1
    return out


def test_vectorised_matches_loop_reference(k):
    """Guards against a vectorisation slip (off-by-one in the shifted slices)."""
    rng = _rng()
    worst = 0.0
    for _ in range(50):
        a = _random_complex(rng)
        worst = max(worst, float(np.max(np.abs(nonlinear_conj(a, k) - _nonlinear_conj_loop(a, k)))))
    assert worst < 1e-12, f"vectorised nonlinearity diverges from loop reference by {worst:.3e}"


# =====================================================================
# Energy conservation -- positive assertions
# =====================================================================

def test_real_nonlinearity_conserves_energy(k):
    rng = _rng()
    worst = max(abs(energy_rate(a := _random_real(rng), nonlinear_real(a, k))) for _ in range(N_TRIALS))
    assert worst < ROUNDOFF, f"real dyadic nonlinearity failed to conserve energy: {worst:.3e}"


def test_conjugated_nonlinearity_conserves_energy(k):
    """Memo §2b's central claim."""
    rng = _rng()
    worst = max(abs(energy_rate(a := _random_complex(rng), nonlinear_conj(a, k))) for _ in range(N_TRIALS))
    assert worst < ROUNDOFF, f"conjugated nonlinearity failed to conserve energy: {worst:.3e}"


def test_quantum_pressure_is_energy_neutral(k):
    """The defining property of a DISPERSIVE regulator (memo §3)."""
    rng = _rng()
    worst = max(abs(energy_rate(a := _random_complex(rng), quantum_pressure(a, k, D=0.03)))
                for _ in range(N_TRIALS))
    assert worst < ROUNDOFF, f"quantum-pressure term is not energy-neutral: {worst:.3e}"


# =====================================================================
# NEGATIVE CONTROLS -- the diagnostic must REJECT these.
# Without them, every assertion above could be passing vacuously.
# =====================================================================

def _nonlinear_naive(a, k):
    """The obvious complexification: same formula, no conjugate. Memo §2a."""
    out = np.zeros_like(a)
    out[1:] = k[:-1] * a[:-1] ** 2
    out[:-1] -= k[:-1] * a[:-1] * a[1:]
    return out


def _nonlinear_signflip(a, k):
    """Conjugated form with the outgoing term's sign flipped."""
    out = np.zeros_like(a)
    out[1:] = k[:-1] * a[:-1] ** 2
    out[:-1] += k[:-1] * np.conj(a[:-1]) * a[1:]
    return out


def _nonlinear_conj_misplaced(a, k):
    """Conjugate on the WRONG factor (incoming rather than outgoing)."""
    out = np.zeros_like(a)
    out[1:] = k[:-1] * np.conj(a[:-1]) ** 2
    out[:-1] -= k[:-1] * a[:-1] * a[1:]
    return out


@pytest.mark.parametrize(
    "broken,label",
    [
        (_nonlinear_naive, "naive complexification (no conjugate)"),
        (_nonlinear_signflip, "sign-flipped outgoing term"),
        (_nonlinear_conj_misplaced, "conjugate on the wrong factor"),
    ],
)
def test_negative_control_broken_nonlinearity_is_detected(k, broken, label):
    """Each variant MUST be caught. If any passes, the checker is inert."""
    rng = _rng()
    worst = max(abs(energy_rate(a := _random_complex(rng), broken(a, k))) for _ in range(N_TRIALS))
    assert worst > 1.0, (
        f"NEGATIVE CONTROL FAILED: the energy diagnostic did not detect "
        f"non-conservation in the {label} (max |dE/dt| = {worst:.3e}). "
        f"The conservation tests above cannot be trusted."
    )


def test_negative_control_viscous_term_is_detected_as_dissipative(k):
    """A real k^2 coefficient must show up as strictly removing energy."""
    rng = _rng()
    rates = [energy_rate(a := _random_complex(rng), viscous(a, k, nu=0.03)) for _ in range(N_TRIALS)]
    assert max(rates) < 0.0, (
        f"NEGATIVE CONTROL FAILED: viscous term did not register as dissipative "
        f"(least-negative dE/dt = {max(rates):.3e})"
    )


def test_negative_control_forcing_term_is_detected_as_amplifying(k):
    """Sign-inverted viscosity must register as ADDING energy.

    Catches an inverted-sign diagnostic, which would otherwise report
    dissipation and forcing identically -- the OP2_LITE §1a-BIS trap.
    """
    rng = _rng()
    rates = [energy_rate(a := _random_complex(rng), -viscous(a, k, nu=0.03)) for _ in range(N_TRIALS)]
    assert min(rates) > 0.0, (
        f"NEGATIVE CONTROL FAILED: forcing term did not register as amplifying "
        f"(least-positive dE/dt = {min(rates):.3e})"
    )


# =====================================================================
# Reduction to the real model, and the invariant subspace (memo §2c(i))
# =====================================================================

def test_conjugated_reduces_exactly_to_real_model(k):
    """Must be EXACT, not approximate -- this is what gives the free
    bit-for-bit positive control against MechanicaFluidorum at D=0."""
    rng = _rng()
    for _ in range(N_TRIALS):
        a = _random_real(rng)
        assert np.array_equal(nonlinear_conj(a, k), nonlinear_real(a, k)), (
            "conjugated nonlinearity does not reduce exactly to the real model"
        )


def test_reals_are_an_invariant_subspace_at_D_zero(k):
    """At D=0 real data must stay exactly real, so Katz-Pavlovic blow-up
    solutions remain solutions and the O5 trap survives (memo §2c(i), §6)."""
    rng = _rng()
    for _ in range(50):
        a = _random_real(rng)
        out = rhs(a, k, nu=0.01, D=0.0)
        assert np.max(np.abs(np.imag(out))) == 0.0, "reality-invariance broken at D=0"


def test_dispersive_term_breaks_reality_invariance(k):
    """The converse, and NOT a defect: this is why the O5 trap's scope is
    limited to D=0 (memo §6). Asserting it pins down that limitation."""
    rng = _rng()
    a = _random_real(rng)
    out = rhs(a, k, nu=0.0, D=0.03)
    assert np.max(np.abs(np.imag(out))) > 0.0, (
        "dispersive term left the data real -- it is not acting as a phase rotation"
    )


# =====================================================================
# Observables, including audit ruling O1 (record BOTH enstrophies)
# =====================================================================

def test_enstrophy_both_returns_both_conventions(k):
    rng = _rng()
    a = _random_complex(rng)
    both = enstrophy_both(a, k)
    assert set(both) == {"sum", "max"}
    assert both["sum"] == pytest.approx(enstrophy_sum(a, k))
    assert both["max"] == pytest.approx(enstrophy_max(a, k))


def test_enstrophy_sum_and_max_differ_and_reproduce_the_MF_discrepancy():
    """Pins the numbers in docs/DEFECT_REPORT_MF_ENSTROPHY.md.

    On MechanicaFluidorum's profile P2 (a_n = 2^-n) every shell contributes
    equally, so sum = (N+1) * max exactly. At N=8 that is 4.5 vs 0.5.
    """
    M = 8
    kk = k_shells(M)
    a = 2.0 ** (-np.arange(M + 1))
    assert enstrophy_sum(a, kk) == pytest.approx(4.5)
    assert enstrophy_max(a, kk) == pytest.approx(0.5)
    assert enstrophy_sum(a, kk) / enstrophy_max(a, kk) == pytest.approx(M + 1)


def test_enstrophy_sum_dominates_max(k):
    """Sanity: a sum of non-negative terms is never below its own maximum."""
    rng = _rng()
    for _ in range(50):
        a = _random_complex(rng)
        assert enstrophy_sum(a, k) >= enstrophy_max(a, k) - 1e-12


def test_energy_is_nonnegative_and_zero_only_at_rest(k):
    rng = _rng()
    assert energy(np.zeros(N + 1)) == 0.0
    for _ in range(50):
        assert energy(_random_complex(rng)) > 0.0


# =====================================================================
# Input validation
# =====================================================================

def test_k_shells_values():
    assert np.array_equal(k_shells(4), np.array([1.0, 2.0, 4.0, 8.0, 16.0]))


def test_k_shells_rejects_negative_N():
    with pytest.raises(ValueError, match="N must be >= 0"):
        k_shells(-1)


@pytest.mark.parametrize("fn", [nonlinear_real, nonlinear_conj, enstrophy_sum, enstrophy_max])
def test_rejects_mismatched_array_lengths(fn):
    with pytest.raises(ValueError, match="does not match"):
        fn(np.zeros(5), k_shells(7))


def test_energy_rate_rejects_mismatched_shapes():
    with pytest.raises(ValueError, match="shape mismatch"):
        energy_rate(np.zeros(5), np.zeros(6))


# =====================================================================
# Boundary-condition / seam analysis (W2 bounce regulator)
#
# The Lean telescoping theorem (lean_src/QuantumFluidsShell.lean,
# sum_re_conj_mul_shellBc) gives the energy pairing as -k_N * Re(conj(v_N)^2
# * v_{N+1}). So ANY boundary condition conserves energy IFF that real part
# vanishes. These tests pin what that means for a reflective seam.
# =====================================================================

def _pairing(vN, vNp1, kN=1.0):
    """The quantity the Lean theorem says the energy pairing equals (up to sign)."""
    return kN * float(np.real(np.conj(vN) ** 2 * vNp1))


def test_truncation_seam_conserves():
    """v_{N+1} = 0 -- the only conserving choice for REAL data."""
    rng = _rng()
    for _ in range(50):
        assert _pairing(rng.normal(), 0.0) == 0.0


def test_real_reflective_seam_leaks_energy():
    """NEGATIVE CONTROL and a real finding: on real data a reflective seam
    v_{N+1} = v_{N-1} does NOT conserve. The pairing reduces to
    v_N^2 * v_{N-1}, which vanishes only if the reflected value is zero.
    A W2 bounce built this way would measure broken conservation rather than
    the bounce -- the failure OP2_LITE flags for its Candidate A."""
    rng = _rng()
    leaks = 0
    for _ in range(50):
        vN, vNm1 = rng.normal(), rng.normal()
        if abs(_pairing(vN, vNm1)) > 1e-12:
            leaks += 1
    assert leaks >= 45, "a real reflective seam should generically leak energy"


def test_complex_seam_can_conserve_exactly():
    """The complexification BUYS something beyond the dispersive regulator:
    the seam v_{N+1} = i*mu*v_N^2 conserves exactly, because
    conj(v_N)^2 * (i mu v_N^2) = i mu |v_N|^4 is purely imaginary.
    No real analogue exists -- see test_real_reflective_seam_leaks_energy."""
    rng = _rng()
    for mu in (0.5, 1.0, 2.0, -1.5):
        for _ in range(20):
            vN = rng.normal() + 1j * rng.normal()
            assert abs(_pairing(vN, 1j * mu * vN**2)) < 1e-9


def test_conserving_seam_condition_is_exactly_orthogonality():
    """Restates the condition: v_{N+1} must be orthogonal to v_N^2 under the
    real inner product Re(conj(x) y). Anything satisfying that conserves."""
    rng = _rng()
    for _ in range(50):
        vN = rng.normal() + 1j * rng.normal()
        target = vN**2
        perp = 1j * target                      # rotate 90 degrees
        assert abs(float(np.real(np.conj(target) * perp))) < 1e-9
        assert abs(_pairing(vN, perp)) < 1e-9
