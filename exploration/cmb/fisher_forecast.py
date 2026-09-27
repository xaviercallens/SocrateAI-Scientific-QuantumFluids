"""Fisher-forecast-style analysis: how much could a next-generation CMB temperature dataset
improve on Koren-Tsai-Wang's (arXiv:2509.07076) own bound on the dark-energy-conversion fraction r?

Signal-to-noise scaling. D_ell,pt(r) is proportional to r^2 (Eq. 11: Pdz0 proportional to r^2), so
the chi^2 in Eq. (14) scales as chi2(r) proportional to r^4/sigma_ell^2, and the 2-sigma bound
scales as r_bound proportional to sigma_ell^(1/2) -- an experiment N times more sensitive
(sigma_ell -> sigma_ell/N) tightens the bound by a factor of sqrt(N), exactly, no linearization
needed (this is the same exact r^4 scaling `cmb_bound.r_bound_2sigma` already uses, just applied to
a different sigma_ell). This holds for ANY consistent rescaling of the noise; the real question is
what rescaling is physically achievable.

The key check, done here with real data before assuming any number: is Planck's own TT measurement
at the l<50 multipoles where this PT signal peaks already close to the COSMIC VARIANCE floor
(sigma_CV(l) = D_l * sqrt(2/((2l+1) f_sky)), the noise floor from having only 2l+1 independent modes
per multipole on a finite sky -- no experiment, however large, can beat this with temperature alone)?
If so, "run this on a bigger telescope" cannot deliver the naive sqrt(N) improvement a raw noise
number might suggest, because Planck already IS close to the best any TT-only experiment can do.
"""
import numpy as np

from cmb_cascade import Pdt_hatk_exact, XI_PEAK_EXACT
from cmb_bound import _ELL_P, _DL_P, sigma_ell, dl_ell, r_bound_2sigma

F_SKY = 0.7  # order-of-magnitude Planck TT analysis sky fraction after masking; not fine-tuned,
             # since the comparison below is a ratio and only mildly sensitive to this choice.


def sigma_cv(ell):
    """The cosmic-variance-only floor at this ell, from Planck's own measured D_ell."""
    dl = dl_ell(ell)
    return dl * np.sqrt(2.0 / ((2 * ell + 1) * F_SKY))


def check_cosmic_variance_limited():
    print("Is Planck's own TT already cosmic-variance-limited at l<50 (where the PT signal peaks)?")
    print(f"{'ell':>4} {'D_l (muK^2)':>12} {'sigma_Planck':>13} {'sigma_CV':>10} {'ratio (Planck/CV)':>18}")
    ratios = []
    for l in (2, 3, 5, 10, 15, 20, 30, 40, 50):
        sp, scv = sigma_ell(l), sigma_cv(l)
        ratios.append(sp / scv)
        print(f"{l:4d} {dl_ell(l):12.2f} {sp:13.2f} {scv:10.2f} {sp / scv:18.2f}")
    return ratios


def bound_with_sigma(zpt, beta_over_H, sigma_func, r_probe=0.1):
    return r_bound_2sigma(zpt, beta_over_H, r_probe=r_probe, pdt_func=Pdt_hatk_exact,
                           xi_peak=XI_PEAK_EXACT, sigma_func=sigma_func)


if __name__ == "__main__":
    ratios = check_cosmic_variance_limited()
    print(f"\nFor l=5-50 (excluding the l=2,3 quadrupole/octopole, where masking residuals still "
          f"matter): Planck/CV ratio ranges {min(ratios[2:]):.2f}-{max(ratios[2:]):.2f} -- i.e. "
          f"Planck's TT error bars are ALREADY within {abs(1 - min(ratios[2:])) * 100:.0f}-"
          f"{abs(1 - max(ratios[2:])) * 100:.0f}% of the cosmic-variance floor over exactly the "
          f"multipole range this PT signal occupies.")

    print("\nConcrete bound comparison, exact spectrum, Planck's real bars vs. the pure "
          "cosmic-variance floor (the best ANY future TT-only experiment could do on this sky):")
    print(f"{'beta/H*':>8} {'zpt':>5} {'r_2sigma (Planck)':>18} {'r_2sigma (CV floor)':>20} "
          f"{'tightening':>11}")
    for zpt in (0.1, 0.2):
        for beta_h in (10, 50, 100, 200, 500):
            r_planck, _ = bound_with_sigma(zpt, beta_h, sigma_ell)
            r_cv, _ = bound_with_sigma(zpt, beta_h, sigma_cv)
            print(f"{beta_h:8d} {zpt:5.2f} {r_planck:18.4g} {r_cv:20.4g} "
                  f"{r_planck / r_cv:10.2f}x")
