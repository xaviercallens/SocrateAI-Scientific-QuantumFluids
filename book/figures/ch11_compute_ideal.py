"""Chapter ch11, the ideal Bose gas: every number of the sections on the ideal gas, and the data of the figures
ch11_bimodal and ch11_saturation.  Run from book/ (about one minute):

    PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext ../.venv/bin/python figures/ch11_compute_ideal.py

Writes figures/ch11_ideal.npz and the section "ideal" of figures/ch11_numbers.json.

1. zeta values and the two Bose integrals of Ch11_BoseCondensation.lean, by scipy quadrature AND by CVODE (Adams).
2. London's estimate: the condensation temperature of an ideal gas of helium-4 atoms at the density of the liquid at T_lambda
   (NIST Chemistry WebBook, saturated liquid at 2.1768 K: 146.02 kg/m^3; 4He mass 4.002 603 254 13 u; CODATA via scipy).
3. Exact (grand-canonical) counting of N atoms in an isotropic harmonic trap: levels n hbar omega (n >= 0, measured from the
   ground state) with degeneracy (n+1)(n+2)/2.  T_c(N) is defined by saturation: the excited states, at the fugacity of
   the ground state (mu -> 0^-), hold exactly N atoms.  Condensate fraction N_0/N(T) by solving for mu at each T.
4. The momentum distribution of the ideal trapped gas (semiclassical thermal part, exact ground state for the condensate),
   column-integrated, at three temperatures: the bimodal signature.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import mpmath
import numpy as np
from scipy import constants as C
from scipy.integrate import quad
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch11_common import HERE, adams_probe, bose_g, cvode_info, update_numbers  # noqa: E402

t_start = time.time()
out: dict = {"script": "figures/ch11_compute_ideal.py"}

# ---------------------------------------------------------------- 1. zeta values and the Bose integrals of the Lean module
z32, z52, z3, z2, z4 = (float(mpmath.zeta(s)) for s in (1.5, 2.5, 3, 2, 4))
out.update(zeta32=z32, zeta52=z52, zeta3=z3, zeta2=z2, zeta4=z4)
# (2/sqrt(pi)) int_0^oo t^(1/2)/(e^t - 1) dt = zeta(3/2);  (1/2) int_0^oo t^2/(e^t - 1) dt = zeta(3)
I32_quad = quad(lambda t: math.sqrt(t) / math.expm1(t), 0, np.inf, limit=200)[0]
I3_quad = quad(lambda t: t * t / math.expm1(t), 0, np.inf, limit=200)[0]
out["crit_density_quad"] = 2 / math.sqrt(math.pi) * I32_quad
out["crit_density_quad_relerr"] = abs(out["crit_density_quad"] - z32) / z32
out["trap_count_quad"] = 0.5 * I3_quad
out["trap_count_quad_relerr"] = abs(out["trap_count_quad"] - z3) / z3

# CVODE: the same integrals as ODEs y' = integrand (substitution t = u^2 removes the t^(-1/2) of the first one)
from rusty_sundials import CvodeSolver  # noqa: E402

info = cvode_info()
probe = adams_probe()
out.update(cvode_module=info["module"], cvode_sha256=info["sha256"], cvode_commit=info["commit"],
           adams_probe_calls=probe["rhs_calls"], adams_probe_relerr=probe["rel_err"])


def f32(u):                       # 2 u^2/(e^{u^2} - 1) -> 2 at u = 0
    x = u * u
    return 2.0 if x == 0.0 else 2.0 * x / math.expm1(x)


def f3(t):                        # t^2/(e^t - 1) -> 0 at t = 0
    return 0.0 if t == 0.0 else t * t / math.expm1(t)


cv = {}
for label, func, upper, exact in (("crit", f32, 8.0, math.sqrt(math.pi) / 2 * z32), ("trap", f3, 80.0, 2 * z3)):
    n = {"c": 0}

    def rhs(t, y, func=func):
        n["c"] += 1
        return [func(t)]

    _, y = CvodeSolver("adams", 1e-11, 1e-14, 1_000_000).solve(rhs, 0.0, [0.0], upper)
    cv[label] = dict(value=y[0], exact=exact, relerr=abs(y[0] - exact) / exact, rhs_calls=n["c"], upper=upper)
out["cvode_crit_integral"] = cv["crit"]["value"]            # = Gamma(3/2) zeta(3/2) = (sqrt(pi)/2) zeta(3/2)
out["cvode_crit_exact"] = cv["crit"]["exact"]
out["cvode_crit_relerr"] = cv["crit"]["relerr"]
out["cvode_crit_calls"] = cv["crit"]["rhs_calls"]
out["cvode_crit_density"] = 2 / math.sqrt(math.pi) * cv["crit"]["value"]
out["cvode_trap_integral"] = cv["trap"]["value"]            # = Gamma(3) zeta(3) = 2 zeta(3)
out["cvode_trap_relerr"] = cv["trap"]["relerr"]
out["cvode_trap_calls"] = cv["trap"]["rhs_calls"]

# ---------------------------------------------------------------- 2. London's estimate for helium-4
m4 = 4.00260325413 * C.atomic_mass                 # kg (NIST atomic mass of 4He, as in chapter ch06)
rho_lambda = 146.02                                # kg/m^3, NIST WebBook saturated liquid at 2.1768 K
T_lambda = 2.1768                                  # K, lower end of the NIST saturation table (the lambda point at SVP)
n_he = rho_lambda / m4
T_BE = 2 * math.pi * C.hbar ** 2 / (m4 * C.k) * (n_he / z32) ** (2 / 3)
lam = math.sqrt(2 * math.pi * C.hbar ** 2 / (m4 * C.k * T_lambda))
out.update(he_density_kgm3=rho_lambda, he_T_lambda=T_lambda, he_number_density=n_he, he_T_BE=T_BE,
           he_nlambda3_at_Tlambda=n_he * lam ** 3, he_lambda_at_Tlambda_A=lam * 1e10,
           he_interatomic_A=n_he ** (-1 / 3) * 1e10)
# uniform ideal gas: C_V / (N k_B) at T_c (the cusp) = (15/4) zeta(5/2)/zeta(3/2)
out["uniform_cv_at_Tc"] = 15 / 4 * z52 / z32
# isotropic trap, thermodynamic limit: C/(N k_B) just below and above T_c, and the jump 9 zeta(3)/zeta(2)
out["trap_c_below"] = 12 * z4 / z3
out["trap_c_jump"] = 9 * z3 / z2
out["trap_c_above"] = out["trap_c_below"] - out["trap_c_jump"]
out["tc_shift_coeff"] = z2 / (2 * z3 ** (2 / 3))           # T_c(N)/T_0 = 1 - coeff N^(-1/3) + ...

# ---------------------------------------------------------------- 3. exact counting in the isotropic harmonic trap
NMAX_LEVEL = 200000
nlev = np.arange(0, NMAX_LEVEL + 1, dtype=float)
deg = (nlev + 1) * (nlev + 2) / 2


def n_excited(t: float, x: float) -> float:
    """Atoms in the excited levels n >= 1 at temperature t = k_B T/(hbar omega) and fugacity exp(-x), x >= 0."""
    kmax = int(min(NMAX_LEVEL, 60 * t + 50))
    e = nlev[1:kmax + 1] / t + x
    return float(np.sum(deg[1:kmax + 1] / np.expm1(e)))


def t_c_saturation(N: float) -> float:
    """The temperature at which the excited states, filled to saturation (x -> 0), hold all N atoms."""
    t0 = (N / z3) ** (1 / 3)
    return brentq(lambda t: n_excited(t, 0.0) - N, 0.5 * t0, 1.5 * t0, xtol=1e-13, rtol=1e-14)


def condensed(N: float, t: float) -> float:
    """N_0 at temperature t: solve N = 1/(e^x - 1) + n_excited(t, x) for x = -beta mu > 0."""
    g = lambda lx: 1.0 / math.expm1(math.exp(lx)) + n_excited(t, math.exp(lx)) - N
    lx = brentq(g, -60.0, 8.0, xtol=1e-14)
    return 1.0 / math.expm1(math.exp(lx))


Ns = [1e2, 1e3, 1e4, 1e5, 1e6]
tc_rows = []
for N in Ns:
    t0 = (N / z3) ** (1 / 3)
    tc = t_c_saturation(N)
    two_term = brentq(lambda t: z3 * t ** 3 + 1.5 * z2 * t ** 2 - N, 0.5 * t0, 1.5 * t0)
    tc_rows.append(dict(N=N, t0=t0, tc=tc, ratio=tc / t0, shift_times_N13=(1 - tc / t0) * N ** (1 / 3),
                        ratio_two_term=two_term / t0, ratio_one_term=1 - out["tc_shift_coeff"] * N ** (-1 / 3)))
out["tc_table"] = tc_rows
out["tc_ratio_N1e3"] = tc_rows[1]["ratio"]
out["tc_ratio_N1e4"] = tc_rows[2]["ratio"]
out["tc_ratio_N1e5"] = tc_rows[3]["ratio"]
out["tc_ratio_N1e6"] = tc_rows[4]["ratio"]
out["tc_shift_N13_N1e2"] = tc_rows[0]["shift_times_N13"]
out["tc_shift_N13_N1e6"] = tc_rows[4]["shift_times_N13"]

tgrid = np.linspace(0.02, 1.25, 124)
frac = {}
for N in Ns:
    t0 = (N / z3) ** (1 / 3)
    frac[N] = np.array([condensed(N, s * t0) / N for s in tgrid])
# deviation from the thermodynamic limit, scaled: (N_0/N - (1 - s^3)) N^(1/3) against s = T/T_0  (-> -(3/2) zeta(2)/zeta(3)^(2/3) s^2)
dev_coeff = 1.5 * z2 / z3 ** (2 / 3)
out["frac_dev_coeff"] = dev_coeff
i07 = int(np.argmin(abs(tgrid - 0.7)))
out["frac_t07"] = float(tgrid[i07])
for N in Ns:
    out[f"frac_dev_scaled_t07_N{int(N)}"] = float((frac[N][i07] - (1 - tgrid[i07] ** 3)) * N ** (1 / 3))
out["frac_dev_pred_t07"] = -dev_coeff * float(tgrid[i07]) ** 2

# ---------------------------------------------------------------- 4. the bimodal momentum distribution (N = 1e5)
Nb = 1e5
t0b = (Nb / z3) ** (1 / 3)
out["bimodal_N"] = Nb
out["bimodal_t0"] = t0b
pmax = 3.2 * math.sqrt(t0b)
px = np.linspace(-pmax, pmax, 361)
PX, PY = np.meshgrid(px, px, indexing="xy")
P2 = PX ** 2 + PY ** 2
temps = [1.10, 0.90, 0.70]
images, cuts, N0s, zs = [], [], [], []


def g2_array(zarr: np.ndarray) -> np.ndarray:
    """g_2 on an array (series for z < 0.5, mpmath otherwise; a single evaluation per distinct value is cached)."""
    flat = zarr.ravel()
    uniq, inv = np.unique(np.round(flat, 15), return_inverse=True)
    vals = np.array([float(mpmath.polylog(2, v)) for v in uniq])
    return vals[inv].reshape(zarr.shape)


for s in temps:
    t = s * t0b
    if s >= 1.0:
        z = brentq(lambda zz: t ** 3 * bose_g(3, zz) - Nb, 1e-6, 1.0 - 1e-15)
        N0 = 0.0
    else:
        z, N0 = 1.0, Nb * (1 - s ** 3)
    # column-integrated momentum distribution (units p_ho = sqrt(m hbar omega)):
    # thermal  (t^2 / 2 pi) g_2(z exp(-p^2/2t)),  condensate  N_0 exp(-p^2)/pi
    r_p = np.sqrt(P2).ravel()
    rr = np.linspace(0, math.sqrt(2) * pmax + 1e-9, 1201)
    g2r = np.array([float(mpmath.polylog(2, z * math.exp(-q * q / (2 * t)))) for q in rr])
    thermal = (t ** 2 / (2 * math.pi)) * np.interp(np.sqrt(P2), rr, g2r)
    cond = N0 * np.exp(-P2) / math.pi
    images.append(thermal + cond)
    cut_th = (t ** 2 / (2 * math.pi)) * np.interp(np.abs(px), rr, g2r)
    cut_c = N0 * np.exp(-px ** 2) / math.pi
    cuts.append(np.vstack([cut_th, cut_c]))
    N0s.append(N0)
    zs.append(z)
out["bimodal_temps"] = temps
out["bimodal_N0"] = N0s
out["bimodal_z"] = zs
out["bimodal_peak_ratio_07"] = float(images[2].max() / images[1].max())
out["bimodal_width_ratio_Tc"] = math.sqrt(2 * t0b)   # thermal rms momentum sqrt(t) per axis vs condensate 1/sqrt(2)

np.savez_compressed(HERE / "ch11_ideal.npz", tgrid=tgrid, Ns=np.array(Ns), frac=np.array([frac[N] for N in Ns]),
                    px=px, images=np.array(images), cuts=np.array(cuts), temps=np.array(temps),
                    tc_N=np.array([r["N"] for r in tc_rows]), tc_ratio=np.array([r["ratio"] for r in tc_rows]),
                    zline=np.linspace(0, 1, 401),
                    g32=np.array([bose_g(1.5, z) for z in np.linspace(0, 1, 401)]),
                    g1=np.array([-math.log1p(-z) if z < 1 else np.inf for z in np.linspace(0, 1, 401)]))
out["seconds"] = round(time.time() - t_start, 1)
update_numbers("ideal", out)
for k in ("zeta32", "crit_density_quad_relerr", "cvode_crit_relerr", "cvode_crit_calls", "cvode_trap_relerr", "adams_probe_calls",
          "he_T_BE", "he_nlambda3_at_Tlambda", "tc_ratio_N1e3", "tc_ratio_N1e6", "tc_shift_N13_N1e6", "tc_shift_coeff", "seconds"):
    print(k, out[k])
for r in tc_rows:
    print(r)
