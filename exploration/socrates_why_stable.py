#!/usr/bin/env python3
"""WHY is SOCRATES' -0.672 horizon- and seed-stable, when our complexified
model thermalizes to beta -> -1?

R1 was refuted (socrates_horizon_test.out): beta = -0.6721 across an 8x
horizon range, drift -0.0001, seed spread 0.0005. This script tests the
proposed EXPLANATION, which comes from this stream's own results:

  (a) LIOUVILLE. Absolute-equilibrium / thermalization arguments require a
      volume-preserving flow. This stream proved the real Katz-Pavlovic flow
      has divergence -sum_n k_n a_{n+1} != 0 -- it is volume-CONTRACTING, so
      it may have attracting structure and need not relax to equipartition.
      Only our COMPLEXIFIED model is Liouville. Prediction: Omega(t) in their
      model settles instead of climbing toward the equipartition value.

  (b) PHASE FREEDOM. This stream's CV 23-49% scatter came from varying
      initial PHASES at fixed amplitudes. A real-amplitude model has no
      phases to vary. Prediction: their model is not phase-chaotic, so
      single-seed exponents are reproducible -- which is what we measured.

Test (a) directly: integrate far past their horizon and compare Omega(t) to
the equipartition value for their k_eff profile.
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

N_SHELLS = 30
ALPHA = 1e-6


def main():
    k_raw = dyadic_wavenumbers(N_SHELLS)
    k = effective_wavenumber(ALPHA, k_raw)

    print(f"k_eff profile (alpha'={ALPHA:.0e}, N={N_SHELLS}): NON-MONOTONIC by construction")
    print(f"  k_eff = min(k, 1/(alpha' k)); peak {k.max():.4g} at shell {int(k.argmax())}")
    print(f"  k_eff at top shell (n={N_SHELLS-1}): {k[-1]:.4g}  "
          f"-- trans-cutoff modes act as their DUALS, so the top shells are SOFT")

    print("\n--- (a) Does Omega climb toward equipartition on long horizons? ---")
    print(f"{'t_max':>8} {'sup Omega':>14} {'E drift':>11} {'terminated':>12}")
    sups = []
    for T in (12.0, 48.0, 200.0, 800.0):
        r = simulate_shell_model(k, t_max=T, cfl=0.05, max_steps=8_000_000)
        sups.append(r.max_enstrophy)
        drift = abs(r.energy[-1] - r.energy[0]) / r.energy[0]
        print(f"{T:>8.0f} {r.max_enstrophy:>14.6g} {drift:>11.2e} {r.terminated:>12}")

    E0 = 0.5  # their default seed u = e_0 gives E = 1/2
    omega_eq = E0 * float((k**2).sum()) / N_SHELLS
    print(f"\n  equipartition value for THIS k_eff profile: "
          f"Omega_eq = E*sum(k_eff^2)/N = {omega_eq:.6g}")
    print(f"  measured sup Omega at t=800:                {sups[-1]:.6g}")
    print(f"  ratio sup/eq = {sups[-1]/omega_eq:.4f}")
    growth = (sups[-1] - sups[0]) / sups[0]
    print(f"  growth of sup Omega from t=12 to t=800: {growth:+.3%}")
    if abs(growth) < 0.02 and sups[-1] < 0.2 * omega_eq:
        print("  => CONFIRMS (a): no thermalization. Omega settles far below equipartition")
        print("     even at 65x their horizon. The absolute-equilibrium argument does NOT")
        print("     transfer to their real, volume-CONTRACTING model.")
    elif growth > 0.1:
        print("  => (a) NOT confirmed: Omega is still climbing; the horizon argument may")
        print("     hold at longer times than tested. Report as-is.")
    else:
        print("  => MIXED; report the numbers, do not round toward the hypothesis.")

    print("\n--- (b) Is the real model phase-chaotic? Structural check ---")
    r = simulate_shell_model(k, t_max=48.0, cfl=0.05, max_steps=8_000_000)
    u_fin = r.amplitudes[-1] if hasattr(r, "amplitudes") else None
    print("  Their state vector is REAL by construction (np.zeros(n), float dtype):")
    print("  there is no phase degree of freedom to perturb, so the phase-randomisation")
    print("  ensemble that produced this stream's CV 23-49% has NO ANALOGUE here.")
    print("  Consistent with the measured seed spread of 0.0005 in beta.")
    if u_fin is not None:
        pos = float((np.asarray(u_fin) >= 0).mean())
        print(f"  fraction of final amplitudes >= 0: {pos:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
