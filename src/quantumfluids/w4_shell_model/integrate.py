"""RK4 time integration for the complexified dyadic shell model.

Implements the runner for docs/designs/M2_W4_DISPERSIVE_SHELL.md (AUDITED
2026-08-14). Deliberately mirrors the step-size rule, horizon, divergence
guard and feasibility guard of MechanicaFluidorum's
exploration/dyadic_cascade.py, so that Positive Control #1 of the memo's
§6 is a like-for-like comparison rather than an approximate one:

    at D = 0 with real initial data, this integrator must reproduce that
    script's numbers, because §2b established the reduction is EXACT.

Per audit ruling O1 every run records BOTH enstrophy conventions
(sup over time of the sum form, and of the max form), so that whether the
choice affects a fitted exponent is settled empirically.

TIER B. No claims are made here about boundedness, blow-up or uniformity;
this module integrates and reports.
"""

from dataclasses import dataclass, field

import numpy as np

from quantumfluids.w4_shell_model.shell_dynamics import (
    energy,
    enstrophy_max,
    enstrophy_sum,
    k_shells,
    rhs,
)

__all__ = ["ShellRun", "integrate", "step_size", "make_profile", "PROFILES"]

# Matches exploration/dyadic_cascade.py so the positive control compares like
# with like. Changing these breaks that comparison -- do not tune them.
T_HORIZON = 10.0
DIVERGE_THRESHOLD = 1e12


def step_size(N: int, nu: float, D: float = 0.0) -> float:
    """dt = 0.1 / (nu*k_N^2 + k_N), extended to include D.

    MechanicaFluidorum's rule is dt = 0.1 / (nu*k_N^2 + k_N): the linear
    stiffness nu*k_N^2 plus a nonlinear-transfer estimate k_N. The
    dispersive term contributes stiffness D*k_N^2 of the same order (its
    coefficient is imaginary, but |−iDk^2| = Dk^2), so it enters the
    denominator the same way. At D = 0 this reduces EXACTLY to the
    MechanicaFluidorum rule, which is required for the positive control.
    """
    k_N = 2.0**N
    return 0.1 / ((nu + D) * k_N * k_N + k_N)


PROFILES = ("P1", "P2", "P3")


def make_profile(name: str, N: int) -> np.ndarray:
    """Initial states, matching MechanicaFluidorum's make_profile exactly.

    Returned real (float64), not complex: at D = 0 the reals are an
    invariant subspace (memo §2c(i)) and this is what exercises it.
    """
    a = np.zeros(N + 1, dtype=np.float64)
    if name == "P1":
        a[0] = 1.0
    elif name == "P2":
        a[:] = 2.0 ** (-np.arange(N + 1))
    elif name == "P3":
        a[0] = 1.0
        if N >= 1:
            a[1] = 0.5
    else:
        raise ValueError(f"unknown profile {name!r}; expected one of {PROFILES}")
    return a


@dataclass
class ShellRun:
    """Outcome of one integration. Both enstrophy conventions, per O1."""

    N: int
    nu: float
    D: float
    profile: str
    dt: float
    steps: int
    status: str  # "OK" | "DIVERGED"
    sup_enstrophy_sum: float
    sup_enstrophy_max: float
    energy_initial: float
    energy_final: float
    t_stop: float
    max_abs_imag: float = field(default=0.0)
    sup_abs_amplitude: float = field(default=0.0)
    """sup over t and n of |a_n|. Energy conservation bounds this by
    sqrt(2E) in the conservative case, which is why a TRUNCATED inviscid
    dyadic model cannot blow up -- see ERRATUM E1 in the design memo."""

    trace_t: np.ndarray | None = field(default=None)
    trace_omega_sum: np.ndarray | None = field(default=None)
    trace_omega_max: np.ndarray | None = field(default=None)
    """Optional (t, Omega_sum, Omega_max) time series, recorded when
    integrate(trace_every=k) is passed. Needed because OPEN ITEM O7
    established that sup_t Omega does not converge in T for a purely
    dispersive regulator, so candidate replacement observables have to be
    evaluated from the trajectory rather than from a running maximum."""

    def as_row(self) -> dict:
        return {
            "N": self.N,
            "nu": self.nu,
            "D": self.D,
            "profile": self.profile,
            "dt": self.dt,
            "steps": self.steps,
            "status": self.status,
            "sup_Omega_sum": self.sup_enstrophy_sum,
            "sup_Omega_max": self.sup_enstrophy_max,
            "E_initial": self.energy_initial,
            "E_final": self.energy_final,
            "t_stop": self.t_stop,
            "max_abs_imag": self.max_abs_imag,
            "sup_abs_amplitude": self.sup_abs_amplitude,
        }


def integrate(
    N: int,
    nu: float,
    D: float = 0.0,
    profile: str = "P1",
    t_horizon: float = T_HORIZON,
    dt: float | None = None,
    max_steps: int | None = None,
    trace_every: int | None = None,
) -> ShellRun:
    """Integrate the shell model with classical RK4 and a divergence guard.

    max_steps, if given, caps the run: it raises rather than silently
    truncating, because a sup_Omega measured over a dynamically
    meaningless sliver of the horizon is worse than no number at all
    (the failure mode MechanicaFluidorum's own feasibility guard exists
    to avoid).

    trace_every: if set, record (t, Omega_sum, Omega_max) every k-th step.
    Needed to evaluate candidate observables other than sup_t Omega, which
    OPEN ITEM O7 established does not converge in T for a purely
    dispersive regulator.
    """
    k = k_shells(N)
    a = make_profile(profile, N)
    if D:
        a = a.astype(np.complex128)

    if dt is None:
        dt = step_size(N, nu, D)
    steps_required = int(np.ceil(t_horizon / dt))
    if max_steps is not None and steps_required > max_steps:
        raise ValueError(
            f"N={N}, nu={nu}, D={D} needs {steps_required} RK4 steps to reach "
            f"t={t_horizon}, exceeding max_steps={max_steps}. Refusing to run "
            f"rather than report a sup_Omega measured over a fraction of the "
            f"horizon. Raise max_steps deliberately, or reduce N."
        )

    e_initial = energy(a)
    sup_sum = enstrophy_sum(a, k)
    sup_max = enstrophy_max(a, k)
    max_abs_imag = float(np.max(np.abs(np.imag(a)))) if np.iscomplexobj(a) else 0.0
    sup_abs = float(np.max(np.abs(a)))

    t = 0.0
    steps_done = 0
    status = "OK"
    tr_t: list[float] = []
    tr_s: list[float] = []
    tr_m: list[float] = []
    if trace_every:
        tr_t.append(0.0); tr_s.append(sup_sum); tr_m.append(sup_max)

    for _ in range(steps_required):
        remaining = t_horizon - t
        h = dt if remaining >= dt else remaining
        if h <= 0.0:
            break

        k1 = rhs(a, k, nu, D)
        k2 = rhs(a + 0.5 * h * k1, k, nu, D)
        k3 = rhs(a + 0.5 * h * k2, k, nu, D)
        k4 = rhs(a + h * k3, k, nu, D)
        a = a + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        steps_done += 1
        t += h

        if not np.all(np.isfinite(a)) or np.max(np.abs(a)) > DIVERGE_THRESHOLD:
            status = "DIVERGED"
            break

        sup_sum = max(sup_sum, enstrophy_sum(a, k))
        sup_max = max(sup_max, enstrophy_max(a, k))
        sup_abs = max(sup_abs, float(np.max(np.abs(a))))
        if trace_every and steps_done % trace_every == 0:
            tr_t.append(t)
            tr_s.append(enstrophy_sum(a, k))
            tr_m.append(enstrophy_max(a, k))
        if np.iscomplexobj(a):
            max_abs_imag = max(max_abs_imag, float(np.max(np.abs(np.imag(a)))))

    # A diverged state's energy is meaningless and its square overflows, so
    # report nan rather than computing a number nobody should use.
    e_final = float("nan") if status == "DIVERGED" else energy(a)

    return ShellRun(
        N=N,
        nu=nu,
        D=D,
        profile=profile,
        dt=dt,
        steps=steps_done,
        status=status,
        sup_enstrophy_sum=sup_sum,
        sup_enstrophy_max=sup_max,
        energy_initial=e_initial,
        energy_final=e_final,
        t_stop=t,
        max_abs_imag=max_abs_imag,
        sup_abs_amplitude=sup_abs,
        trace_t=np.array(tr_t) if trace_every else None,
        trace_omega_sum=np.array(tr_s) if trace_every else None,
        trace_omega_max=np.array(tr_m) if trace_every else None,
    )
