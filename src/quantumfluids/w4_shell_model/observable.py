"""First-peak enstrophy -- the replacement observable for W4.

BACKGROUND. The audited memo fits beta from sup_t Omega. OPEN ITEM O7
established that this does not converge in the horizon T for a purely
dispersive regulator: dispersion is energy-neutral, so at nu = 0 there is
no attractor and the enstrophy keeps finding new maxima up to the
truncation ceiling k_N^2 E. Owner ruling 2026-08-14: change the observable.

CHOICE, made on measured evidence rather than intuition (see
exploration/observable_convergence.py). Five candidates were evaluated for
convergence in T, separately for the viscous and dispersive regulators,
across horizons T = 2..64. Relative change between the last two horizons:

    observable                         viscous   dispersive
    sup_t Omega            (incumbent)   0.00%      10.35%   FAILS
    Omega at first peak                  0.00%       0.00%   converges
    Omega(T*) at fixed T*                0.00%       0.00%   converges
    time-averaged Omega                 49.99%       2.90%   FAILS (decays ~1/T)
    max_t dOmega/dt                      0.00%      19.31%   FAILS

Two survive. This module implements the FIRST-PEAK one, because it is a
DYNAMICALLY defined event -- the arrival of the initial cascade at the
smallest resolved scale -- so it compares the two regulators at the same
physical stage. Omega(T*) at a fixed clock time does not: at any given T*
the viscous run may have finished cascading while the dispersive one is
still going, so it would compare unlike states. First-peak also stays
closer to OP2_LITE section 3's "peak enstrophy" in spirit.

THE HAZARD THIS MODULE GUARDS AGAINST. First-peak detection is robust in
dt (values agree to 5-6 digits from dt = 2e-3 down to 5e-4) but SENSITIVE
to how finely the trajectory is sampled. Measured at N=4, D=0.02: sampling
every step gives 39.158, every 5th 39.109, every 20th 39.101 -- but every
50th gives 43.533, an 11% jump, because the detector steps over the true
first peak and latches onto a later, higher one. An undetected version of
that would be precisely the class of artifact that produced O7. So:

  - trace_every=1 is the default and is what production runs should use
    (memory is trivial at any N we can afford: ~24 MB per 1e6 steps);
  - sampling adequacy is CHECKED, not assumed, by re-detecting on a
    subsampled copy of the same trace and requiring agreement.

TIER B.
"""

from dataclasses import dataclass

import numpy as np

__all__ = [
    "PeakResult",
    "first_peak",
    "check_sampling_adequacy",
    "SAMPLING_TOL",
    "MIN_RISE",
]

# A peak is accepted only if re-detecting it on a 2x-subsampled copy of the
# same trace agrees to within this relative tolerance. Analogous in spirit to
# the pre-registered dt-refinement criterion of memo section 6, applied to the
# other discretisation parameter -- the one nothing previously checked.
SAMPLING_TOL = 0.01

# A first peak counts only if the cascade actually BUILT enstrophy: the peak
# must exceed Omega(0) by at least this relative margin. Pre-registered here,
# before any fit, and configurable so its influence can be checked.
#
# Why this exists. Under strong damping the cascade never gets going: at N=4,
# nu=0.3, profile P3 the enstrophy rises by 2.5e-5 relative (1.0000248 vs
# 1.000000) and then declines monotonically. That IS a local maximum, so a
# naive detector returns 1.0000 -- which is Omega(0), the initial condition,
# not a measurement of anything the regulator did. Worse, it corrupts a fit
# systematically rather than randomly: as the damping grows the observable
# tends to Omega(0), a CONSTANT independent of the swept parameter, flattening
# the log-log slope toward zero. Since beta = 0 is the pre-registered
# "cutoff mechanism is irrelevant" outcome, that would manufacture the very
# result the experiment is trying to test for.
MIN_RISE = 0.10


@dataclass(frozen=True)
class PeakResult:
    value: float
    t_peak: float
    index: int
    n_samples: int
    sampling_ok: bool
    sampling_rel_change: float
    reason: str = ""
    rise: float = 0.0
    """(peak - Omega(0)) / Omega(0): how much enstrophy the cascade built."""


def _detect(y: np.ndarray) -> int | None:
    """Index of the first strict interior local maximum, or None."""
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] > y[i + 1]:
            return i
    return None


def first_peak(t: np.ndarray, y: np.ndarray, tol: float = SAMPLING_TOL,
               min_rise: float = MIN_RISE) -> PeakResult:
    """Enstrophy at the first local maximum of the trace, with an adequacy check.

    Raises ValueError if no interior local maximum exists -- which means the
    horizon did not contain the initial cascade peak, and the caller must
    extend T rather than receive a number that is really just Omega at the
    end of the run.

    Also raises if the peak fails to exceed Omega(0) by min_rise, i.e. the
    cascade never built appreciable enstrophy (see MIN_RISE). Both are
    refusals rather than flags, because in each case the returned number
    would not be a measurement of the regulator.
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    if t.shape != y.shape:
        raise ValueError(f"shape mismatch: t {t.shape} vs y {y.shape}")
    if len(y) < 3:
        raise ValueError(f"need at least 3 trace samples to detect a peak, got {len(y)}")

    i = _detect(y)
    if i is None:
        raise ValueError(
            "no interior local maximum in the trace: the horizon does not "
            "contain the first cascade peak (the series is still monotonic). "
            "Extend t_horizon rather than treating the endpoint as a peak."
        )

    rise = (float(y[i]) - float(y[0])) / abs(float(y[0])) if y[0] != 0 else float("inf")
    if rise < min_rise:
        raise ValueError(
            f"first peak rises only {rise:.3%} above Omega(0), below the "
            f"pre-registered {min_rise:.0%} minimum: the cascade did not build "
            f"appreciable enstrophy, so this value is the initial condition "
            f"rather than a measurement of the regulator (see MIN_RISE)"
        )

    ok, rel, why = check_sampling_adequacy(y, i, tol)
    return PeakResult(
        value=float(y[i]), t_peak=float(t[i]), index=i, n_samples=len(y),
        sampling_ok=ok, sampling_rel_change=rel, reason=why, rise=rise,
    )


def check_sampling_adequacy(y: np.ndarray, i: int, tol: float = SAMPLING_TOL):
    """Re-detect the first peak on 2x-subsampled copies; require agreement.

    If halving the sampling rate moves the detected peak value, the detector
    is resolution-limited and the finer sampling may itself be inadequate.

    BOTH subsampling phases are checked -- y[::2] and y[1::2]. Checking only
    the even phase leaves a parity blind spot: a peak sitting at an even index
    survives y[::2] untouched, so the guard would pass on a trace that is in
    fact marginally resolved. (Found by a negative-control test that failed
    for exactly this reason, having placed its spike at an even index.) The
    worse of the two phases decides.
    """
    worst_rel = 0.0
    worst_why = ""
    for phase, coarse in ((0, y[::2]), (1, y[1::2])):
        j = _detect(coarse)
        if j is None:
            return (False, float("nan"),
                    f"subsampled trace (phase {phase}) has no detectable peak, so "
                    f"sampling adequacy cannot be established; record more finely")
        rel = abs(float(coarse[j]) - float(y[i])) / abs(float(y[i]))
        if rel > worst_rel:
            worst_rel = rel
            worst_why = (
                f"first-peak value moved by {rel:.2%} under 2x subsampling "
                f"(phase {phase}), exceeding the {tol:.0%} sampling tolerance -- "
                f"the trace is too coarse to resolve the peak (this is the failure "
                f"mode that gave a spurious +11% at trace_every=50; see module "
                f"docstring)")
    if worst_rel > tol:
        return (False, worst_rel, worst_why)
    return (True, worst_rel, "")


# =====================================================================
# Crossing time -- the round-3 observable (battery pre-registration,
# docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md "Round 3")
# =====================================================================

@dataclass(frozen=True)
class CrossingResult:
    time: float
    index: int          # first sample index at or above the level
    n_samples: int
    sampling_ok: bool
    sampling_rel_change: float
    reason: str = ""


def crossing_time(t, y, level, tol: float = SAMPLING_TOL) -> CrossingResult:
    """First time y(t) reaches `level`, linearly interpolated between the
    bracketing samples.

    Adopted for round 3 because, unlike every amplitude observable and unlike
    first_peak, a threshold crossing (a) is defined for EVERY conservative arm
    -- all of them climb toward the ceiling (M2_REPORT section 6a) -- and
    (b) does not depend on peak STRUCTURE, so the extra local maxima that
    broke first_peak's parameter-monotonicity cannot move it.

    Guards, all refusals rather than flags (a number that is not a
    measurement must not be returned):
      - y[0] >= level: the threshold is at or below the initial condition,
        so the "crossing" would be the initial condition in disguise (the
        MIN_RISE failure mode, transposed).
      - no sample reaches level: the horizon does not contain the crossing;
        extend t_horizon rather than treating the endpoint as an answer.
    Sampling adequacy is checked as for first_peak: the interpolated
    crossing time re-computed on each 2x-subsampled phase must agree within
    tol (relative in time).
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    if t.shape != y.shape:
        raise ValueError(f"shape mismatch: t {t.shape} vs y {y.shape}")
    if len(y) < 2:
        raise ValueError(f"need at least 2 trace samples, got {len(y)}")
    if y[0] >= level:
        raise ValueError(
            f"threshold {level:g} is at or below the initial value {y[0]:g}: "
            f"the crossing would be the initial condition in disguise"
        )

    tc = _interp_crossing(t, y, level)
    if tc is None:
        raise ValueError(
            f"trace never reaches level {level:g} within the horizon "
            f"(max reached: {float(np.max(y)):g}); extend t_horizon rather "
            f"than treating the endpoint as a crossing"
        )
    tc_time, idx = tc

    worst_rel = 0.0
    worst_why = ""
    for phase in (0, 1):
        sub = _interp_crossing(t[phase::2], y[phase::2], level)
        if sub is None:
            return CrossingResult(tc_time, idx, len(y), False, float("nan"),
                                  f"2x-subsampled trace (phase {phase}) never crosses; "
                                  f"sampling adequacy cannot be established")
        rel = abs(sub[0] - tc_time) / tc_time if tc_time > 0 else float("inf")
        if rel > worst_rel:
            worst_rel = rel
            worst_why = (f"crossing time moved by {rel:.2%} under 2x subsampling "
                         f"(phase {phase}), exceeding the {tol:.0%} tolerance")
    if worst_rel > tol:
        return CrossingResult(tc_time, idx, len(y), False, worst_rel, worst_why)
    return CrossingResult(tc_time, idx, len(y), True, worst_rel, "")


def _interp_crossing(t, y, level):
    """(interpolated time, first index at/above level), or None if no crossing."""
    above = np.flatnonzero(y >= level)
    if len(above) == 0:
        return None
    i = int(above[0])
    if i == 0:
        return float(t[0]), 0
    t0, t1, y0, y1 = t[i - 1], t[i], y[i - 1], y[i]
    if y1 == y0:
        return float(t1), i
    return float(t0 + (level - y0) / (y1 - y0) * (t1 - t0)), i
