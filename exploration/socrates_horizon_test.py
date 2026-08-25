#!/usr/bin/env python3
"""Test the R1 prediction IN SOCRATES/MENSURA'S OWN CODE.

Prediction (docs/NOTE_TO_SOCRATES_MENSURA.md section 1, retrofit item R1):
their FINDINGS section 4 headline exponent -0.672, measured at nu=0 and
t_max=12, is a FIXED-HORIZON TRANSIENT, not an asymptotic exponent. At nu=0
the truncated model conserves energy, has no attractor, and relaxes toward
absolute equilibrium, so the fit should drift monotonically toward the
trivial ceiling exponent -1 as the horizon grows.

Falsifiable both ways, pre-registered before running:
  CONFIRMS   -- beta moves monotonically toward -1 with t_max, and the
                drift is much larger than the run-to-run spread.
  REFUTES    -- beta stays near -0.672 across horizons (then QuantumFluids
                is wrong about their model, and the note must be retracted).

This script imports their package READ-ONLY. It writes nothing into their
repository and calls neither their figure code nor their reporting code.
It re-runs THEIR hypothesis_u_scaling internals at several horizons.

Second control included: SEED SCATTER at fixed parameters (retrofit item R2).
Their -0.672 is a single-seed measurement. If the seed scatter in beta is
comparable to the horizon drift, then the horizon claim is not separable
from noise and BOTH results are underdetermined -- that outcome is reported
honestly rather than suppressed.
"""
import sys
from pathlib import Path

import numpy as np

SOC = Path("/home/xavkal/socrates-project")
sys.path.insert(0, str(SOC / "src"))

from socrates.dualscale.geometry import effective_wavenumber  # noqa: E402
from socrates.dualscale.shell import (  # noqa: E402
    dyadic_wavenumbers,
    simulate_shell_model,
)

# Their section-4 protocol, verbatim from scripts/experiment_stage1.py.
N_SHELLS = 30
CFL = 0.05
ALPHAS = np.logspace(-2, -10, 9)
HORIZONS = (6.0, 12.0, 24.0, 48.0)


def beta_at(t_max, initial=None, max_steps=2_000_000):
    """Their fit: log-log slope of peak enstrophy vs alpha', t_max runs only."""
    k_raw = dyadic_wavenumbers(N_SHELLS)
    peaks, converged = [], []
    for alpha in ALPHAS:
        k = effective_wavenumber(alpha, k_raw)
        r = simulate_shell_model(k, t_max=t_max, cfl=CFL, max_steps=max_steps,
                                 initial=None if initial is None else initial.copy())
        peaks.append(r.max_enstrophy)
        converged.append(r.terminated == "t_max")
    peaks, mask = np.array(peaks), np.array(converged)
    if mask.sum() < 3:
        return None, mask.sum(), peaks, mask
    slope = float(np.polyfit(np.log10(ALPHAS[mask]), np.log10(peaks[mask]), 1)[0])
    return slope, mask.sum(), peaks, mask


def main():
    print("=" * 72)
    print("R1 TEST: is SOCRATES' -0.672 a horizon-dependent transient?")
    print(f"Their protocol: N={N_SHELLS}, nu=0, cfl={CFL}, {len(ALPHAS)} alphas")
    print("=" * 72)

    print("\n--- Horizon sweep (default seed, their default initial condition) ---")
    print(f"{'t_max':>8} {'beta':>10} {'n_conv':>8}   peak enstrophy at alpha=1e-2, 1e-6, 1e-10")
    results = {}
    for T in HORIZONS:
        beta, nconv, peaks, mask = beta_at(T)
        results[T] = beta
        shown = " ".join(f"{peaks[i]:.4g}" for i in (0, 4, 8))
        print(f"{T:>8.0f} {('--' if beta is None else f'{beta:+.4f}'):>10} "
              f"{nconv:>8}   {shown}")

    print("\n--- Verdict on the horizon prediction ---")
    betas = [results[T] for T in HORIZONS if results[T] is not None]
    if len(betas) < 2:
        print("  INDETERMINATE: too few horizons produced a fit.")
        return 0
    drift = betas[-1] - betas[0]
    monotone = all(betas[i + 1] <= betas[i] + 1e-9 for i in range(len(betas) - 1))
    print(f"  beta({HORIZONS[0]:.0f}) = {betas[0]:+.4f} -> "
          f"beta({HORIZONS[len(betas)-1]:.0f}) = {betas[-1]:+.4f}   drift = {drift:+.4f}")
    print(f"  monotonically decreasing toward -1: {monotone}")
    print(f"  distance from -1 at longest horizon: {abs(betas[-1] + 1.0):.4f}")
    if monotone and drift < -0.05:
        print("  => CONSISTENT with the transient prediction (R1).")
    elif abs(drift) < 0.05:
        print("  => PREDICTION NOT SUPPORTED: beta is horizon-stable. R1 must be retracted.")
    else:
        print("  => MIXED. Report as-is; do not round toward the prediction.")

    print("\n--- Control (R2): seed scatter in beta at FIXED t_max=12 ---")
    print("  If this scatter rivals the horizon drift above, both are underdetermined.")
    rng = np.random.default_rng(20260815)
    k_raw = dyadic_wavenumbers(N_SHELLS)
    seed_betas = []
    for s in range(4):
        u0 = np.zeros(N_SHELLS)
        u0[0] = 1.0
        if s > 0:  # perturb the seed at fixed leading amplitude
            u0[:3] = np.array([1.0, 0.0, 0.0]) + 0.05 * rng.standard_normal(3)
        b, nconv, _, _ = beta_at(12.0, initial=u0)
        seed_betas.append(b)
        print(f"  seed {s}: beta = {('--' if b is None else f'{b:+.4f}')}  (n_conv={nconv})")
    valid = [b for b in seed_betas if b is not None]
    if len(valid) >= 2:
        spread = max(valid) - min(valid)
        print(f"  seed spread = {spread:.4f}   horizon drift = {abs(drift):.4f}   "
              f"ratio drift/spread = {abs(drift)/spread if spread > 0 else float('inf'):.1f}")
        if spread > abs(drift):
            print("  => WARNING: seed scatter EXCEEDS horizon drift. R1 is not separable "
                  "from seed noise on this evidence.")
        else:
            print("  => horizon drift dominates seed scatter; R1 signal survives the control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
