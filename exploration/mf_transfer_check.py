#!/usr/bin/env python3
"""Do the QuantumFluids lessons actually transfer to MechanicaFluidorum?

(numba is absent in this venv, so MF's njit decorator falls back to a no-op
and this runs as pure Python. Horizons are sized accordingly; the effect
under test saturates well before the longest one.)

LL-15 was learned the hard way next door: two conclusions from this stream were
exported to SOCRATES/Mensura without their hypotheses and were refuted in
Mensura's own code. The note drafted for MechanicaFluidorum carries the SAME
two conclusions (its Priority 3 = thermalization; Priority 4 = single-trajectory
noise), and MF's model is ALSO real-amplitude (dtype=np.float64). So the note
must not ship until the same two questions are tested HERE.

Hypotheses each conclusion needs, both proven discriminating by this stream:
  - thermalization to absolute equilibrium needs a LIOUVILLE (volume-preserving)
    flow. Real Katz-Pavlovic has div = -sum_n k_n a_{n+1} != 0 (CLAIM-011).
  - phase-randomisation scatter needs PHASES. A real amplitude has none.

Tests, in MF's own code, at nu = 0 (their O5 Euler regime):
  T1 HORIZON  -- does sup_t Omega climb toward the ceiling k_N^2 E as T grows,
                 as it does in our complexified model (beta -> -1)?
  T2 ENSEMBLE -- at fixed parameters and FIXED ENERGY, how much does sup_t
                 Omega scatter across perturbed initial amplitudes?

Pre-registered readings:
  T1 climbs   -> Priority 3 transfers. T1 flat -> Priority 3 must be retracted.
  T2 CV large -> Priority 4 transfers. T2 CV small -> Priority 4 must be
                 retracted for MF (the method-level lesson may still stand, but
                 stated as discipline, not as "your runs are noise-dominated").
"""
import sys
from pathlib import Path

import numpy as np

MF = Path("/home/xavkal/xdev/SocrateAI-Scientific-MechanicaFluidorum")
sys.path.insert(0, str(MF / "exploration"))

from dyadic_cascade import (  # noqa: E402
    _simulate,
    energy,
    make_k,
    make_profile,
)

N = 12
NU = 0.0
DIVERGE = 1e12


def run(a0, T):
    k = make_k(N)
    dt = 0.1 / (NU * k[N] * k[N] + k[N])
    steps = int(np.ceil(T / dt)) + 10
    a, sup_om, _, diverged, t_fin = _simulate(N, NU, k, dt, steps, T, a0, DIVERGE)
    return sup_om, diverged, t_fin, energy(a)


def main():
    k = make_k(N)
    a0 = make_profile("P3", N)
    E0 = energy(a0)
    ceiling = k[N] ** 2 * E0  # our stream's degeneracy ceiling for sup Omega
    print(f"MF model, N={N}, nu={NU}, profile P3.  E0 = {E0:.6g}")
    print(f"ceiling k_N^2 * E = {ceiling:.6g}   (our complexified model reaches this)\n")

    print("--- T1: horizon dependence of sup_t Omega (Priority 3) ---")
    print(f"{'T':>8} {'sup Omega':>14} {'/ceiling':>10} {'E drift':>10} {'diverged':>9}")
    sups = []
    for T in (2.0, 8.0, 32.0, 64.0):
        sup, div, t_fin, E_fin = run(a0, T)
        sups.append(sup)
        print(f"{T:>8.0f} {sup:>14.6g} {sup/ceiling:>9.4f} "
              f"{abs(E_fin-E0)/E0:>10.2e} {str(div):>9}")
    growth = (sups[-1] - sups[0]) / sups[0]
    print(f"\n  growth of sup Omega, T=2 -> T=64: {growth:+.3%}")
    print(f"  fraction of ceiling at T=64: {sups[-1]/ceiling:.4f}")
    if growth > 0.5 and sups[-1] / ceiling > 0.5:
        print("  => Priority 3 TRANSFERS: MF's model does climb toward the ceiling.")
    elif abs(growth) < 0.05:
        print("  => Priority 3 DOES NOT TRANSFER: sup Omega is horizon-flat. The")
        print("     thermalization claim must be retracted for MF, exactly as for Mensura.")
    else:
        print("  => PARTIAL. Report the numbers; do not round toward the hypothesis.")

    print("\n--- T2: ensemble scatter at FIXED energy (Priority 4) ---")
    rng = np.random.default_rng(20260815)
    T = 8.0
    vals = []
    for i in range(10):
        a = a0.copy()
        if i > 0:
            a = a + 0.10 * rng.standard_normal(N + 1) * np.abs(a).max()
            a *= np.sqrt(E0 / energy(a))  # renormalise to the SAME energy
        sup, div, _, _ = run(a, T)
        vals.append(sup)
    vals = np.array(vals)
    cv = vals.std(ddof=1) / vals.mean()
    print(f"  n = {len(vals)} realisations at fixed E = {E0:.6g}, T = {T}")
    print(f"  sup Omega: mean {vals.mean():.6g}  sd {vals.std(ddof=1):.4g}  "
          f"CV {cv:.2%}  spread {(vals.max()-vals.min())/vals.mean():.2%}")
    print(f"  (this stream's COMPLEX model, same kind of test: CV 23-49%)")
    if cv > 0.15:
        print("  => Priority 4 TRANSFERS: MF single-trajectory runs are noise-dominated.")
    elif cv < 0.05:
        print("  => Priority 4 DOES NOT TRANSFER at this amplitude: MF's real model is")
        print("     reproducible. The CV numbers are phase-driven and have no analogue.")
    else:
        print("  => PARTIAL. Report as measured.")

    print("\n--- Instrument note (contrast with Mensura's CLAIM-018) ---")
    print("  MF's _simulate tracks sup_om at EVERY STEP, not on a sampled grid,")
    print("  so MF does NOT have the sampled-max defect found in Mensura's shell.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
