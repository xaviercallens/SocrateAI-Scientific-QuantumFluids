"""Chapter 6 -- the universal number of the opening paragraph, computed from physical constants.

Kosterlitz-Thouless / Nelson-Kosterlitz: the superfluid areal mass density of a two-dimensional film just below the transition satisfies
    rho_s(T_c^-) = 8 pi k_B (m/h)^2 T_c = (2 m^2 k_B / (pi hbar^2)) T_c           (the form printed in the abstract of Bishop & Reppy 1978)
i.e. n_s lambda_T^2 = 4 with lambda_T^2 = 2 pi hbar^2 /(m k_B T) and rho_s = m n_s.
m = mass of a 4He atom = 4.002 603 254 13 u (NIST relative atomic mass, checked 2026-10-09 at physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=He);
k_B, h, u from scipy.constants (CODATA).  Writes figures/ch06_constants.json."""
import json, math
from pathlib import Path
import scipy
from scipy import constants as C

OUT = Path(__file__).resolve().parent
u_He4 = 4.00260325413
m = u_He4 * C.physical_constants["atomic mass constant"][0]            # kg
kB, h, hbar = C.k, C.h, C.hbar
jump_SI = 8 * math.pi * kB * (m / h) ** 2                            # kg m^-2 K^-1
jump_cgs = jump_SI * 1e3 / 1e4                                       # g cm^-2 K^-1   (1 kg = 1e3 g, 1 m^2 = 1e4 cm^2)
alt = 2 * m ** 2 * kB / (math.pi * hbar ** 2)
res = dict(
    scipy_version=scipy.__version__, codata_note="scipy.constants " + scipy.__version__ + " (CODATA values shipped with scipy)",
    m_He4_kg=m, m_He4_amu=u_He4, kB=kB, h=h, hbar=hbar,
    universal_jump_SI_kg_m2_K=jump_SI, universal_jump_cgs_g_cm2_K=jump_cgs, identity_check_relative_difference=abs(alt - jump_SI) / jump_SI,
    two_over_pi=2 / math.pi, pi_over_two=math.pi / 2, f_at_pi_over_2=math.pi - math.pi * math.log(math.pi / 2), four_pi_cubed=4 * math.pi ** 3, two_pi_cubed=2 * math.pi ** 3,
    ln380=math.log(380.0), two_pi_ln2=2 * math.pi * math.log(2.0), eta_at_jump=1 / (2 * math.pi * (2 / math.pi)),
)
json.dump(res, open(OUT / "ch06_constants.json", "w"), indent=1)
for k, v in res.items(): print(k, v)
