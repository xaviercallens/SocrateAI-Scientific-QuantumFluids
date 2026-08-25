#!/usr/bin/env python3
"""Is SOCRATES' sup-enstrophy instrument sampling-limited, and does it affect
their published section-4 exponent?

FOUND (socrates_why_stable.out): their `max_enstrophy` fell 11425.5 -> 9885.8
(-13.5%) as t_max went 12 -> 800 at fixed alpha'. A supremum over a NESTED,
GROWING window cannot decrease. So it is not a supremum.

CAUSE (src/socrates/dualscale/shell.py): `max_enstrophy` is the max over
RECORDED SAMPLES, and `sample_times = np.linspace(0, t_max, n_samples)` with
n_samples fixed at 2000. The sampling interval is t_max/2000, so it COARSENS
in proportion to the horizon and the sampled max misses a sharper peak. The
per-step `current_enstrophy` needed for a true running max is already
computed for the enstrophy_ceiling test and simply not retained.

THIS SCRIPT decides the question that matters for their record: is the
PUBLISHED -0.672 (t_max=12) biased by this? Their n_samples is a public
parameter, so the test needs no patching of their code: re-run their exact
section-4 protocol at n_samples = 2_000 (their default) vs 200_000 and
compare peaks and the fitted exponent.

Pre-registered reading:
  peaks agree to <1% and beta to <0.005  -> published number is SOUND; the
      defect is a latent fragility that bites at longer horizons only.
  peaks differ materially                -> the published number is BIASED
      and section 4 needs re-measurement.
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
CFL = 0.05
T_MAX = 12.0
ALPHAS = np.logspace(-2, -10, 9)


def sweep(n_samples):
    k_raw = dyadic_wavenumbers(N_SHELLS)
    peaks, conv = [], []
    for alpha in ALPHAS:
        k = effective_wavenumber(alpha, k_raw)
        r = simulate_shell_model(k, t_max=T_MAX, cfl=CFL, max_steps=2_000_000,
                                 n_samples=n_samples)
        peaks.append(r.max_enstrophy)
        conv.append(r.terminated == "t_max")
    peaks, mask = np.array(peaks), np.array(conv)
    beta = float(np.polyfit(np.log10(ALPHAS[mask]), np.log10(peaks[mask]), 1)[0])
    return peaks, beta


def main():
    print("Their section-4 protocol, varying ONLY n_samples (a public parameter).")
    print(f"N={N_SHELLS}, nu=0, cfl={CFL}, t_max={T_MAX}\n")

    p_default, b_default = sweep(2_000)
    p_fine, b_fine = sweep(200_000)

    print(f"{'alpha':>10} {'peak @2k':>14} {'peak @200k':>14} {'rel. miss':>11}")
    worst = 0.0
    for a, pd, pf in zip(ALPHAS, p_default, p_fine):
        miss = (pf - pd) / pf
        worst = max(worst, abs(miss))
        print(f"{a:>10.0e} {pd:>14.6g} {pf:>14.6g} {miss:>10.3%}")

    print(f"\n  beta @ n_samples=2000   (their default): {b_default:+.4f}")
    print(f"  beta @ n_samples=200000 (100x finer):    {b_fine:+.4f}")
    print(f"  |delta beta| = {abs(b_fine - b_default):.4f}   worst peak miss = {worst:.3%}")

    if worst < 0.01 and abs(b_fine - b_default) < 0.005:
        print("\n  => PUBLISHED -0.672 IS SOUND. At t_max=12 the sampling is adequate:")
        print("     the enstrophy peak is broad on that horizon. The defect is a LATENT")
        print("     FRAGILITY -- it bites whenever t_max grows (or the peak sharpens),")
        print("     because the sampling interval t_max/n_samples is not tied to the")
        print("     feature being measured. Fix: track a running max of the per-step")
        print("     `current_enstrophy` already computed for the ceiling test.")
    else:
        print("\n  => PUBLISHED NUMBER IS AFFECTED. Section 4 needs re-measurement with")
        print("     a step-resolved maximum.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
