"""Peak-enstrophy exponent harness: fit beta from sup_t Omega ~ p^beta.

Implements the pre-registered protocol of
docs/designs/M2_W4_DISPERSIVE_SHELL.md §6 (AUDITED 2026-08-14), which is
written to be comparable with MechanicaFluidorum's
docs/designs/OP2_LITE_CANDIDATES.md §3.

WHAT IS FITTED, AND AGAINST WHAT (see OPEN ITEM O6, below)
  beta is the log-log slope of sup_t Omega against the regulator's OWN
  parameter p:  d log(sup_t Omega) / d log(p).

  The memo's §6 phrases the exponent as sup_t Omega ~ alpha'^beta. For the
  TRUNCATION regulator that is exact and unambiguous (alpha' = 4^-N). For
  the viscous and dispersive regulators it is NOT, and the reason is
  dimensional:

    alpha'      has dimensions of LENGTH^2
    nu and D    have dimensions of LENGTH^2 / TIME

  Converting a diffusivity to a length^2 needs a second quantity, and the
  natural choice differs by regulator -- the Kolmogorov length gives
  eta^2 ~ nu^(3/2) (needing the dissipation rate eps), while the healing
  length gives xi^2 = D^2/c^2 (needing the sound speed c). Different
  powers (1.5 vs 2.0), and neither eps nor c is yet defined for this model
  (audit ruling O3 deferred exactly this).

  CONSEQUENCE, and why the experiment is still sound: nu and D have the
  SAME dimensions as each other. So beta_nu and beta_D are directly
  comparable with no conversion at all, and that comparison is precisely
  the memo §3 design -- identical k^2 structure, coefficient rotated 90
  degrees, so it isolates dispersive-vs-dissipative without confounding it
  with a different spectral slope. That is the PRIMARY experiment.
  Comparison against the truncation control on a shared alpha' axis is
  SECONDARY and blocked on O6.

Per audit ruling O1 every fit is performed TWICE, once per enstrophy
convention, and both are reported.

TIER B. This module fits and reports; it makes no claim about what a
particular beta means.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy import stats

from quantumfluids.w4_shell_model.integrate import integrate

__all__ = [
    "SweepPoint",
    "ExponentFit",
    "SweepResult",
    "fit_loglog",
    "refine_and_check",
    "run_sweep",
]

# Pre-registered inclusion tolerance (memo §6 / OP2_LITE §3): a configuration
# enters the fit only if sup Omega agrees to within this relative tolerance
# at two successive dt refinements. Fixed before any run -- do not tune.
DT_REFINEMENT_TOL = 0.01


@dataclass(frozen=True)
class SweepPoint:
    """One parameter value, run at dt and dt/2, with its inclusion verdict."""

    param: float
    sup_sum: float
    sup_max: float
    sup_sum_fine: float
    sup_max_fine: float
    included: bool
    reason: str
    alpha_prime: float | None = None  # only when exactly derivable (truncation)

    @property
    def rel_change_sum(self) -> float:
        return abs(self.sup_sum_fine - self.sup_sum) / abs(self.sup_sum)

    @property
    def rel_change_max(self) -> float:
        return abs(self.sup_max_fine - self.sup_max) / abs(self.sup_max)


@dataclass(frozen=True)
class ExponentFit:
    """Log-log slope with a 95% confidence interval from the t-distribution."""

    convention: str  # "sum" | "max"
    beta: float
    stderr: float
    ci95_low: float
    ci95_high: float
    r_squared: float
    n_points: int

    def __str__(self) -> str:
        return (
            f"beta[{self.convention}] = {self.beta:+.4f} "
            f"(95% CI {self.ci95_low:+.4f} .. {self.ci95_high:+.4f}, "
            f"r^2 = {self.r_squared:.4f}, n = {self.n_points})"
        )


@dataclass(frozen=True)
class SweepResult:
    regulator: str
    param_name: str
    points: list = field(default_factory=list)
    fit_sum: ExponentFit | None = None
    fit_max: ExponentFit | None = None

    @property
    def n_excluded(self) -> int:
        return sum(1 for p in self.points if not p.included)

    def exclusion_report(self) -> str:
        """Exclusions are ALWAYS reported with their count, never silently
        dropped (memo §6)."""
        excluded = [p for p in self.points if not p.included]
        if not excluded:
            return f"{len(self.points)} points, 0 excluded"
        lines = [f"{len(self.points)} points, {len(excluded)} EXCLUDED:"]
        lines += [f"  {self.param_name}={p.param:g}: {p.reason}" for p in excluded]
        return "\n".join(lines)


def fit_loglog(params: np.ndarray, values: np.ndarray, convention: str) -> ExponentFit:
    """Least-squares slope of log(values) against log(params), with a 95% CI.

    Requires >= 3 points: two points give a slope with zero residual degrees
    of freedom, hence no confidence interval, and a beta without an interval
    cannot be compared against another beta -- which is the entire purpose of
    the experiment.
    """
    params = np.asarray(params, dtype=float)
    values = np.asarray(values, dtype=float)
    if params.shape != values.shape:
        raise ValueError(f"shape mismatch: params {params.shape} vs values {values.shape}")
    if len(params) < 3:
        raise ValueError(
            f"need at least 3 points to fit an exponent with a confidence "
            f"interval, got {len(params)}"
        )
    if np.any(params <= 0) or np.any(values <= 0):
        raise ValueError("log-log fit requires strictly positive params and values")

    log_p, log_v = np.log(params), np.log(values)

    if np.ptp(log_p) == 0.0:
        raise ValueError(
            "cannot fit a slope against a constant parameter: all swept values "
            "are identical"
        )

    if np.ptp(log_v) == 0.0:
        # Exactly flat response. scipy's rvalue is 0/0 -> nan here, but beta = 0
        # is a LEGITIMATE and pre-registered experimental outcome (memo §6: three
        # equal exponents means the cutoff mechanism is irrelevant at this
        # observable, "a real and useful negative"). Returning nan for the single
        # most consequential possible result would be a defect, so it is handled
        # explicitly: a constant is perfectly described by a slope-zero power law.
        return ExponentFit(
            convention=convention, beta=0.0, stderr=0.0,
            ci95_low=0.0, ci95_high=0.0, r_squared=1.0, n_points=len(params),
        )

    res = stats.linregress(log_p, log_v)
    dof = len(params) - 2
    t_crit = stats.t.ppf(0.975, dof)
    half = t_crit * res.stderr

    return ExponentFit(
        convention=convention,
        beta=float(res.slope),
        stderr=float(res.stderr),
        ci95_low=float(res.slope - half),
        ci95_high=float(res.slope + half),
        r_squared=float(res.rvalue**2),
        n_points=len(params),
    )


def refine_and_check(
    N: int,
    nu: float,
    D: float,
    profile: str,
    t_horizon: float,
    tol: float = DT_REFINEMENT_TOL,
    max_steps: int | None = None,
) -> tuple[float, float, float, float, bool, str]:
    """Run at dt and dt/2; report both, and whether they agree within tol.

    This is the pre-registered inclusion criterion. It is applied to BOTH
    enstrophy conventions: a point is included only if both agree, since a
    point whose fitted value depends on the timestep in either convention
    is not a measurement of the model.
    """
    # integrate() REFUSES (raises) rather than silently truncating a run it
    # cannot complete. In a sweep that refusal is not a fatal error -- it is
    # exactly what the inclusion criterion exists to record. Convert it to a
    # stated exclusion so the point is reported and counted, never dropped.
    try:
        coarse = integrate(N=N, nu=nu, D=D, profile=profile, t_horizon=t_horizon,
                           max_steps=max_steps)
    except ValueError as exc:
        return (np.nan, np.nan, np.nan, np.nan, False, f"run refused: {exc}")

    if coarse.status != "OK":
        return (coarse.sup_enstrophy_sum, coarse.sup_enstrophy_max, np.nan, np.nan,
                False, f"coarse run status={coarse.status}")

    try:
        fine = integrate(N=N, nu=nu, D=D, profile=profile, t_horizon=t_horizon,
                         dt=coarse.dt / 2.0,
                         max_steps=None if max_steps is None else 2 * max_steps)
    except ValueError as exc:
        return (coarse.sup_enstrophy_sum, coarse.sup_enstrophy_max, np.nan, np.nan,
                False, f"refined run refused: {exc}")

    if fine.status != "OK":
        return (coarse.sup_enstrophy_sum, coarse.sup_enstrophy_max,
                fine.sup_enstrophy_sum, fine.sup_enstrophy_max,
                False, f"refined run status={fine.status}")

    d_sum = abs(fine.sup_enstrophy_sum - coarse.sup_enstrophy_sum) / abs(coarse.sup_enstrophy_sum)
    d_max = abs(fine.sup_enstrophy_max - coarse.sup_enstrophy_max) / abs(coarse.sup_enstrophy_max)
    ok = d_sum <= tol and d_max <= tol
    reason = "" if ok else (
        f"dt refinement changed sup_Omega by {d_sum:.2%} (sum) / {d_max:.2%} (max), "
        f"exceeding the pre-registered {tol:.0%} tolerance"
    )
    return (coarse.sup_enstrophy_sum, coarse.sup_enstrophy_max,
            fine.sup_enstrophy_sum, fine.sup_enstrophy_max, ok, reason)


def run_sweep(
    regulator: str,
    values,
    N: int,
    profile: str = "P3",
    t_horizon: float = 1.0,
    tol: float = DT_REFINEMENT_TOL,
    max_steps: int | None = None,
) -> SweepResult:
    """Sweep one regulator's parameter and fit beta under both conventions.

    regulator: "viscous" (sweeps nu) or "dispersive" (sweeps D). These two
    are the PRIMARY comparison -- same dimensions, no conversion needed.
    "truncation" (sweeps N) is accepted too, and is the only one for which
    alpha' = 4^-N is exact, but see O6 in the module docstring before
    comparing its beta against the other two.
    """
    values = [float(v) for v in values]
    points: list[SweepPoint] = []

    for v in values:
        if regulator == "viscous":
            cs, cm, fs, fm, ok, why = refine_and_check(N, v, 0.0, profile, t_horizon, tol, max_steps)
            alpha = None
        elif regulator == "dispersive":
            cs, cm, fs, fm, ok, why = refine_and_check(N, 0.0, v, profile, t_horizon, tol, max_steps)
            alpha = None
        elif regulator == "truncation":
            n = int(v)
            cs, cm, fs, fm, ok, why = refine_and_check(n, 0.0, 0.0, profile, t_horizon, tol, max_steps)
            alpha = 4.0 ** (-n)
        else:
            raise ValueError(
                f"unknown regulator {regulator!r}; expected 'viscous', "
                f"'dispersive' or 'truncation'"
            )
        points.append(SweepPoint(param=v, sup_sum=cs, sup_max=cm, sup_sum_fine=fs,
                                 sup_max_fine=fm, included=ok, reason=why,
                                 alpha_prime=alpha))

    param_name = {"viscous": "nu", "dispersive": "D", "truncation": "N"}[regulator]
    kept = [p for p in points if p.included]

    fit_sum = fit_max = None
    if len(kept) >= 3:
        ps = np.array([p.param for p in kept])
        fit_sum = fit_loglog(ps, np.array([p.sup_sum for p in kept]), "sum")
        fit_max = fit_loglog(ps, np.array([p.sup_max for p in kept]), "max")

    return SweepResult(regulator=regulator, param_name=param_name, points=points,
                       fit_sum=fit_sum, fit_max=fit_max)
