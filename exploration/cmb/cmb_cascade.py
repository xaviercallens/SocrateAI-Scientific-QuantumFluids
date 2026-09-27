import numpy as np
from scipy import integrate, special

from pdt_exact import P_exact_k_elor

# ---- Planck 2018 best-fit background (as adopted by Koren-Tsai-Wang, their Sec. III) ----
H0 = 68.0          # km/s/Mpc
Om = 0.31
OL = 0.69
c_light = 299792.458  # km/s
T_CMB_uK = 2.7255e6    # muK

H0_invMpc = H0 / c_light  # 1/Mpc


def H_over_H0(z):
    return np.sqrt(OL + Om * (1 + z) ** 3)


def Hstar_invMpc(zpt):
    return H0_invMpc * H_over_H0(zpt)


def chi0(zi, zf):
    """Comoving distance (no-PT LCDM), Mpc, from zf to zi (zi > zf)."""
    integrand = lambda z: 1.0 / ((1 + z) * H0_invMpc * H_over_H0(z))
    val, _ = integrate.quad(integrand, zf, zi, limit=200)
    return val


# ---- Bubble-time power spectrum ----
# Elor, Jinno, Kumar, McGehee, Tsai (arXiv:2311.16222) give this spectrum only as two asymptotic
# power laws (their Fig. S4: P_{beta dtc}(x) ~ 100 x^3 for x<<1, ~ x^-3 for x>>1, x = k/beta at
# their reference beta=1, vw=1) plus a numerically-computed full curve shown only as a plot -- no
# single closed form for the whole curve is published in either paper. Converting their asymptotic
# coefficient into Koren-Tsai-Wang's own rescaled variable xi (via their Eq. 3-4 and the definition
# of xi in their Fig. 4) gives (beta/Hstar)^2 * Pdt(xi) ~ 3 xi^3 for xi<<1 (matching their Fig. 4
# curve, which also falls off as xi^-3 for xi>>1). We therefore use a smooth double-power-law
# interpolation matching BOTH asymptotic coefficients exactly (peaking at xi=3^(-1/6)=0.833 with
# value ~0.867, close to the ~1 the published Fig. 4 plot shows near the peak). This is an
# approximation to their published curve, not a re-derivation or digitisation of it -- see
# docs/designs/CMB_CASCADE_REPRODUCTION.md for the full derivation and its honest limitations.
def P_interp_xi(xi):
    xi = np.asarray(xi, dtype=float)
    return 1.0 / (1.0 / (3.0 * xi ** 3) + xi ** 3)


XI_PEAK = 3.0 ** (-1.0 / 6.0)  # peak of the interpolation, ~0.833


def xi_of_hatk(hat_k, zpt, beta_over_H, vw=1.0):
    return (8 * np.pi) ** (1.0 / 3.0) * vw * (1 + zpt) * hat_k / beta_over_H


def hatk_of_xi(xi, zpt, beta_over_H, vw=1.0):
    return xi * beta_over_H / ((8 * np.pi) ** (1.0 / 3.0) * vw * (1 + zpt))


def Pdt_hatk(hat_k, zpt, beta_over_H, vw=1.0):
    xi = xi_of_hatk(hat_k, zpt, beta_over_H, vw)
    return P_interp_xi(xi) / beta_over_H ** 2


def Pdt_hatk_exact(hat_k, zpt, beta_over_H, vw=1.0):
    """The exact replacement for `Pdt_hatk`, using `pdt_exact.P_exact_k_elor` (Elor et al.'s own
    correlator, Eqs. S9-S16, Fourier-transformed exactly rather than interpolated between the two
    published asymptotes). k_elor = (1+zpt)*hat_k/beta_over_H = xi/(8pi)^(1/3) -- see
    `pdt_exact.py`'s module docstring for the derivation of this correspondence."""
    k_elor = (1 + zpt) * hat_k / beta_over_H / vw
    return P_exact_k_elor(k_elor) / beta_over_H ** 2


_MU, _MU_W = np.polynomial.legendre.leggauss(16)

# The exact spectrum (pdt_exact.P_exact_k_elor) peaks at k_elor=0.493 (see pdt_exact.py's __main__
# check), i.e. at xi = 0.493*(8pi)^(1/3) = 1.468 -- NOT at the interpolation's XI_PEAK=0.833. Using
# the right peak for each spectrum keeps the kmin/kmax integration window centered correctly.
XI_PEAK_EXACT = 0.493 * (8 * np.pi) ** (1.0 / 3.0)


def Idt(hat_k, zpt, beta_over_H, vw=1.0, n_r=40, pdt_func=Pdt_hatk, xi_peak=XI_PEAK):
    """Eq. (12), worked entirely in hat_k = k/Hstar units (dimensionless). `pdt_func` selects the
    bubble-time spectrum (`Pdt_hatk`, the interpolation, or `Pdt_hatk_exact`, Elor et al.'s exact
    correlator); `xi_peak` must match the peak of whichever spectrum is passed."""
    hatk_peak = hatk_of_xi(xi_peak, zpt, beta_over_H, vw)
    kmin, kmax = hatk_peak / 10.0, hatk_peak * 10.0
    log_r = np.linspace(np.log(kmin), np.log(kmax), n_r)
    r_grid = np.exp(log_r)
    vals = np.empty(n_r)
    for i, r in enumerate(r_grid):
        s = np.sqrt(hat_k ** 2 + r ** 2 - 2 * hat_k * r * _MU)
        s = np.clip(s, 1e-12, None)
        integrand_mu = np.array([pdt_func(x, zpt, beta_over_H, vw) for x in s]) / s ** 3
        inner = np.sum(_MU_W * integrand_mu)
        vals[i] = pdt_func(r, zpt, beta_over_H, vw) * inner
    outer = np.trapezoid(vals, log_r)
    return hat_k ** 3 * outer


def Pdz0_hatk(hat_k, zpt, r_pt, beta_over_H, vw=1.0, pdt_func=Pdt_hatk, xi_peak=XI_PEAK):
    pref = r_pt ** 2 * OL ** 2 * (OL + Om * (1 + zpt) ** 3) ** (-3)
    return pref * Idt(hat_k, zpt, beta_over_H, vw, pdt_func=pdt_func, xi_peak=xi_peak)


def D_ell_pt(ell, zpt, r_pt, beta_over_H, vw=1.0, n_k=60, pdt_func=Pdt_hatk, xi_peak=XI_PEAK):
    """Eq. (13), restoring T_CMB^2 to express the result in muK^2 (see design doc: this factor
    is not spelled out explicitly in Eq. 13 but is required to match the paper's muK^2 axis)."""
    Hstar = Hstar_invMpc(zpt)
    Deltatau = chi0(zpt, 0.0)
    hatk_peak = hatk_of_xi(xi_peak, zpt, beta_over_H, vw)
    hatk_min, hatk_max = hatk_peak / 10.0, hatk_peak * 10.0
    log_k = np.linspace(np.log(hatk_min), np.log(hatk_max), n_k)
    hk = np.exp(log_k)
    k_phys = hk * Hstar
    jl = special.spherical_jn(ell, k_phys * Deltatau)
    Pz0 = np.array([Pdz0_hatk(x, zpt, r_pt, beta_over_H, vw, pdt_func=pdt_func, xi_peak=xi_peak)
                    for x in hk])
    integrand = Pz0 * jl ** 2
    val = np.trapezoid(integrand, log_k)
    return 2 * ell * (ell + 1) * val * T_CMB_uK ** 2


if __name__ == "__main__":
    print("Sanity: Hstar(z=0.1) =", Hstar_invMpc(0.1), "1/Mpc")
    print("Sanity: chi0(0.1,0) =", chi0(0.1, 0.0), "Mpc")
    for beta_h in [40, 80, 100, 200]:
        ells = [5, 10, 15, 20, 25, 30]
        vals = [D_ell_pt(l, 0.1, 0.1, beta_h) for l in ells]
        print(f"beta/H={beta_h}: D_ell,pt =", ["%.2f" % v for v in vals])
