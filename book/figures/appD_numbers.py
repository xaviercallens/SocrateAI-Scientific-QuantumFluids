"""Appendix D (Constants, Units and Notation): every constant and conversion factor the appendix prints.

Run from anywhere with the book's environment:

    /home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/.venv/bin/python book/figures/appD_numbers.py [--check]

writes book/figures/appD_numbers.json.  With --check it also verifies that every printed string ("tex" field) of the
JSON occurs in book/chapters/appD.tex, and that no number of the appendix's tables is absent from the JSON.

Sources (details and the access dates in facts/appD_report.md):
  * CODATA 2022 recommended values through scipy.constants (scipy 1.18.1, whose module scipy.constants._codata sets
    _current_codata = "CODATA 2022"; two values checked by hand against the NIST CODATA pages on 2026-10-10:
    atomic mass constant 1.660 539 068 92(52)e-27 kg and neutron mass 1.674 927 500 56(85)e-27 kg, both labelled
    "Source: 2022 CODATA recommended values").  Reference: P. J. Mohr, D. B. Newell, B. N. Taylor, E. Tiesinga,
    Rev. Mod. Phys. 97, 025002 (2025), doi:10.1103/RevModPhys.97.025002 (checked on Crossref).
  * Relative atomic masses of 3He and 4He: NIST, "Atomic Weights and Isotopic Compositions for Helium",
    https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=He (consulted 2026-10-10):
    A_r(3He) = 3.016 029 3201(25), A_r(4He) = 4.002 603 254 13(6).
  * Helium-4 properties: read from the chapters' own number files (figures/ch04_numbers.json, figures/ch05_numbers.json)
    and from the module constants of figures/ch04_common.py / figures/ch05_helium.py, which give the source of each value
    (Godfrin et al., Phys. Rev. B 103, 104516 (2021), arXiv:2012.09067, and the papers it cites).
Nothing here is new physics; the point of the file is that every number of Appendix D is computed, not typed.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import scipy
import scipy.constants as C
import scipy.constants._codata as _codata

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
OUT = HERE / "appD_numbers.json"

# ----------------------------------------------------------------------------------------------------------- helpers

def sig(x: float, n: int) -> str:
    """x with n significant digits, plain decimal (no exponent) when 1e-4 <= |x| < 1e6, digits grouped by siunitx later."""
    if x == 0:
        return "0"
    e = math.floor(math.log10(abs(x)))
    d = max(n - 1 - e, 0)
    s = f"{x:.{d}f}"
    return s


def sci(x: float, n: int) -> tuple[str, int]:
    """(mantissa with n significant digits, exponent) of x."""
    e = math.floor(math.log10(abs(x)))
    m = x / 10 ** e
    ms = f"{m:.{n - 1}f}"
    if float(ms) >= 10:                     # rounding overflow, e.g. 9.9996 -> 10.000
        e += 1
        ms = f"{x / 10 ** e:.{n - 1}f}"
    return ms, e


def num_tex(x: float, n: int, unc_digits: str | None = None) -> str:
    """siunitx \\num{...} argument: '1.66053906892(52)e-27' style (the appendix prints it with \\num)."""
    e = math.floor(math.log10(abs(x)))
    if -4 <= e < 6:
        body = sig(x, n)
        return body + (f"({unc_digits})" if unc_digits else "")
    ms, e = sci(x, n)
    return ms + (f"({unc_digits})" if unc_digits else "") + f"e{e}"


def codata(key: str) -> dict:
    v, unit, unc = C.physical_constants[key]
    return dict(scipy_key=key, value=v, unit=unit, uncertainty=unc, exact=(unc == 0.0))


def unc_digits(value: float, unc: float, n_sig: int) -> str | None:
    """the two (or fewer) digits in parentheses for a value printed with n_sig significant digits"""
    if unc == 0:
        return None
    e = math.floor(math.log10(abs(value)))
    last = e - (n_sig - 1)                  # decimal position of the last printed digit
    return str(int(round(unc / 10 ** last)))


R: dict = {}

# --------------------------------------------------------------------------------- 1. CODATA 2022 through scipy
assert _codata._current_codata == "CODATA 2022", _codata._current_codata
R["meta"] = dict(
    python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
    scipy_current_codata=_codata._current_codata,
    codata_reference="P. J. Mohr, D. B. Newell, B. N. Taylor, E. Tiesinga, CODATA recommended values of the fundamental "
                     "physical constants: 2022, Rev. Mod. Phys. 97, 025002 (2025), doi:10.1103/RevModPhys.97.025002 "
                     "(Crossref record checked 2026-10-10)",
    nist_codata_pages_checked_2026_10_10={
        "atomic mass constant (https://physics.nist.gov/cgi-bin/cuu/Value?ukg)": "1.660 539 068 92(52) x 10^-27 kg, Source: 2022 CODATA",
        "neutron mass (https://physics.nist.gov/cgi-bin/cuu/Value?mn)": "1.674 927 500 56(85) x 10^-27 kg, Source: 2022 CODATA",
    },
    nist_helium_page="https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=He (consulted 2026-10-10)",
)
# the two hand-checked values must be the ones scipy returns
assert C.physical_constants["atomic mass constant"][0] == 1.66053906892e-27
assert C.physical_constants["atomic mass constant"][2] == 0.00000000052e-27 or abs(C.physical_constants["atomic mass constant"][2] - 5.2e-37) < 1e-45
assert C.physical_constants["neutron mass"][0] == 1.67492750056e-27

CODATA_ROWS = [
    # symbol, name, scipy key, significant digits printed, uncertainty digits printed?
    ("h", "Planck constant", "Planck constant", 9),
    ("hbar", "reduced Planck constant", "reduced Planck constant", 10),
    ("kB", "Boltzmann constant", "Boltzmann constant", 7),
    ("e", "elementary charge", "elementary charge", 10),
    ("NA", "Avogadro constant", "Avogadro constant", 9),
    ("c0", "speed of light in vacuum", "speed of light in vacuum", 9),
    ("mu", "atomic mass constant", "atomic mass constant", 12),
    ("mn", "neutron mass", "neutron mass", 12),
]
R["codata"] = {}
for sym, name, key, nsig in CODATA_ROWS:
    d = codata(key)
    d["name"] = name
    ud = unc_digits(d["value"], d["uncertainty"], nsig)
    d["tex"] = num_tex(d["value"], nsig, ud)
    d["tex_unit"] = d["unit"]
    R["codata"][sym] = d
# hbar is exact but irrational: printed truncated with an ellipsis, as CODATA does
R["codata"]["hbar"]["tex"] = "1.054571817e-34"
R["codata"]["hbar"]["note"] = "exact (h/2pi); CODATA prints 1.054 571 817... x 10^-34 J s"
assert abs(C.hbar - 1.054571817e-34) < 1e-43

hbar, h, kB, e, NA, c0 = C.hbar, C.h, C.k, C.e, C.N_A, C.c
m_u = C.physical_constants["atomic mass constant"][0]
m_n = C.physical_constants["neutron mass"][0]

# --------------------------------------------------------------------------------- 2. helium atomic masses (NIST)
A3, A3_unc, A3_str = 3.0160293201, 0.0000000025, "3.0160293201(25)"
A4, A4_unc, A4_str = 4.00260325413, 0.00000000006, "4.00260325413(6)"
m3, m4 = A3 * m_u, A4 * m_u
R["helium_masses"] = dict(
    source="NIST Atomic Weights and Isotopic Compositions for Helium, physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=He, consulted 2026-10-10",
    A_r_He3=dict(value=A3, uncertainty=A3_unc, tex=A3_str),
    A_r_He4=dict(value=A4, uncertainty=A4_unc, tex=A4_str),
    standard_atomic_weight_He="4.002602(2) (same page)",
    isotopic_composition="3He 0.000 001 34(3), 4He 0.999 998 66(3) (same page)",
    m3_kg=dict(value=m3, tex=num_tex(m3, 9)),
    m4_kg=dict(value=m4, tex=num_tex(m4, 9)),
)
# consistency of the NIST atomic masses with the CODATA nuclear masses: A_r(atom) = A_r(nucleus) + 2 A_r(e) - B/(m_u c^2),
# B = total electronic binding energy of He (24.587 + 54.418 eV ~ 79.0 eV; textbook ionisation energies, used only for this check)
Ae = C.physical_constants["electron relative atomic mass"][0]
Aalpha = C.physical_constants["alpha particle relative atomic mass"][0]
Ahelion = C.physical_constants["helion relative atomic mass"][0]
muc2_eV = C.physical_constants["atomic mass constant energy equivalent in MeV"][0] * 1e6
B4 = (Aalpha + 2 * Ae - A4) * muc2_eV
B3 = (Ahelion + 2 * Ae - A3) * muc2_eV
# the two ionisation energies of He from the NIST Atomic Spectra Database (consulted 2026-10-10): He I 24.587389011(25) eV,
# He II 54.4177655282(10) eV; their sum is the binding energy of the two electrons
IE_He = 24.587389011 + 54.4177655282
R["helium_masses"]["crosscheck_binding_energy_eV"] = dict(
    He4=B4, He3=B3, He3_uncertainty_eV=A3_unc * muc2_eV, He_ionisation_sum_eV=IE_He,
    tex=[f"{B4:.1f}", f"{B3:.1f}", f"{IE_He:.1f}", f"{A3_unc * muc2_eV:.1f}"],   # He-4, He-3, sum of ionisation energies, He-3 uncertainty
    note="(A_r(nucleus, CODATA 2022) + 2 A_r(e) - A_r(atom, NIST)) m_u c^2 against the sum of the two ionisation energies "
         "of helium (NIST ASD: 24.587389011 + 54.4177655282 eV); He-3 agrees within the 2.3 eV that the NIST uncertainty "
         "(25 in the last digits) allows")
assert abs(B4 - IE_He) < 0.1, (B4, IE_He)
assert abs(B3 - IE_He) < A3_unc * muc2_eV, (B3, A3_unc * muc2_eV)

# earlier chapters used the same NIST value (or the rounded molar mass of Godfrin et al. 2021) -- check, do not assume
ch03 = json.loads((HERE / "ch03_numbers.json").read_text())
ch06 = json.loads((HERE / "ch06_constants.json").read_text())
assert ch03["constants"]["m_He4_u"] == A4 and ch06["m_He4_amu"] == A4
assert abs(ch03["constants"]["m_He4_kg"] / m4 - 1) < 1e-15 and abs(ch06["m_He4_kg"] / m4 - 1) < 1e-15
M4_ch05 = 4.0026032             # figures/ch05_helium.py: "atom mass 4.0026032 u (as quoted in that paper)"
R["helium_masses"]["ch05_rounded_value"] = dict(
    value=M4_ch05, relative_difference_to_NIST=(M4_ch05 - A4) / A4,
    note="Chapter ch05 uses 4.0026032 (the molar mass quoted by Godfrin et al. 2021); ch03 and ch06 use the NIST value")

# --------------------------------------------------------------------------------- 3. conversion factors
meV = 1e-3 * e                  # J
A = 1e-10                       # m
conv = {}


def put(key, value, n, unit, used_in, how, tex=None):
    conv[key] = dict(value=value, tex=tex or num_tex(value, n), unit=unit, used_in=used_in, how=how)


put("meV_in_K", meV / kB, 7, "K", ["ch01", "ch04", "ch05"], "1e-3 e / k_B")
put("K_in_meV", kB / meV, 7, "meV", [], "k_B / (1e-3 e)")
put("meV_in_THz", meV / h / 1e12, 7, "THz", [], "1e-3 e / h  (frequency nu = E/h)")
put("hbar2_2mn_meV_A2", hbar ** 2 / (2 * m_n) / meV / A ** 2, 6, "meV A^2", ["ch01"], "hbar^2/(2 m_n): neutron E = 2.0721 meV A^2 k^2")
put("h2_2mn_meV_A2", h ** 2 / (2 * m_n) / meV / A ** 2, 6, "meV A^2", ["ch01"], "h^2/(2 m_n): neutron E lambda^2")
put("h_over_mn_ms_A", h / m_n / A, 6, "m s^-1 A", ["ch01"], "h/m_n: neutron v lambda")
put("hbar2_2m4_meV_A2", hbar ** 2 / (2 * m4) / meV / A ** 2, 5, "meV A^2", ["ch05"], "hbar^2/(2 m_4), free 4He atom")
put("hbar2_2m4_K_A2", hbar ** 2 / (2 * m4) / kB / A ** 2, 5, "K A^2", [], "hbar^2/(2 m_4 k_B)")
put("hbar2_2m3_meV_A2", hbar ** 2 / (2 * m3) / meV / A ** 2, 5, "meV A^2", [], "hbar^2/(2 m_3), free 3He atom")
put("hbar2_2m3_K_A2", hbar ** 2 / (2 * m3) / kB / A ** 2, 5, "K A^2", [], "hbar^2/(2 m_3 k_B)")
put("meVA_over_hbar_ms", meV * A / hbar, 6, "m s^-1", ["ch05"], "a slope d eps/dk of 1 meV A is a group velocity of 151.93 m/s")
put("kappa4_m2_s", h / m4, 5, "m^2 s^-1", ["ch03"], "h/m_4, quantum of circulation in 4He")
put("kappa3pair_m2_s", h / (2 * m3), 5, "m^2 s^-1", [], "h/(2 m_3), circulation quantum of a Cooper-paired 3He superfluid (pair mass 2 m_3)")
put("universal_jump_SI", 8 * math.pi * kB * (m4 / h) ** 2, 5, "kg m^-2 K^-1", ["ch06"], "rho_s(T_c^-)/T_c = 8 pi k_B (m_4/h)^2")
put("universal_jump_cgs", 8 * math.pi * kB * (m4 / h) ** 2 * 1e3 / 1e4, 5, "g cm^-2 K^-1", ["ch06"], "same in g cm^-2 K^-1")
R["conversions"] = conv

ch01 = json.loads((HERE / "ch01_numbers.json").read_text())["bench"]["constants"]
ch04 = json.loads((HERE / "ch04_numbers.json").read_text())
ch05 = json.loads((HERE / "ch05_numbers.json").read_text())

# --------------------------------------------------------------------------------- 4. helium-4 values of ch04/ch05
# (read from the chapters' number files; the source of each is the one the chapter gives, recorded in "source")
c4 = ch04["constants"]["c_m_per_s"]
assert c4 == ch05["c"]["value"] == 238.3
Vm = ch04["constants"]["V_cm3_per_mol"]                      # cm^3/mol
al = ch04["constants"]["alpha_A_powers"]
assert (al["a2"], al["a3"], al["a4"], al["a5"], al["a6"]) == (1.55, -4.04, 2.3, 0.0, 0.0)
quotes = ch05["paper_quotes_used_literally"]
he4 = {}


def he(key, value, tex, unit, chapters, source, numbers_key):
    he4[key] = dict(value=value, tex=tex, unit=unit, chapters=chapters, source=source, numbers_file_key=numbers_key)


SRC21 = "Godfrin et al., Phys. Rev. B 103, 104516 (2021), arXiv:2012.09067 (the chapters read the arXiv v1 source)"
he("c", c4, "238.3", "m s^-1", ["ch04", "ch05"], SRC21 + "; ultrasound value 238.3 +- 0.1 m/s quoted there",
   "ch04_numbers.json constants.c_m_per_s; ch05_numbers.json c; ch05 paper_quotes_used_literally.c_ultrasound_ms = " + quotes["c_ultrasound_ms"])
he("Vm", Vm, "27.5793", "cm^3 mol^-1", ["ch04"], SRC21 + " (molar volume at saturated vapour pressure quoted there)", "ch04_numbers.json constants.V_cm3_per_mol")
he("alpha2", al["a2"], "1.55", "A^2", ["ch04", "ch05"], SRC21 + "; alpha2 = 1.55(1) A^2 from Rugar & Foster (1984), alpha1 = 0",
   "ch04 constants.alpha_A_powers.a2; ch05 paper_quotes_used_literally.alpha2_Rugar_Foster_A2 = " + quotes["alpha2_Rugar_Foster_A2"])
he("alpha3", al["a3"], "-4.04", "A^3", ["ch04", "ch05"], SRC21 + " (series set for saturated vapour pressure, 'valid k < 0.5 A^-1')", "ch04 constants.alpha_A_powers.a3")
he("alpha4", al["a4"], "2.30", "A^4", ["ch04", "ch05"], SRC21, "ch04 constants.alpha_A_powers.a4")
# table extrema (the authors' ancillary dispersion table, read by ch05's scripts) -- printed in ch05 and ch01
he("roton_E_table", ch05["rotonE"]["value"], ch05["rotonE"]["tex"], "meV", ["ch05"], "minimum of the authors' ancillary table DispersionP0allRange.txt", "ch05 rotonE")
he("roton_E_table_K", ch05["rotonGapK"]["value"], ch05["rotonGapK"]["tex"], "K", ["ch05"], "same, times 11.6045 K/meV", "ch05 rotonGapK")
he("roton_k_table", ch05["rotonKshort"]["value"], ch05["rotonKshort"]["tex"], "A^-1", ["ch05"], "same table", "ch05 rotonKshort")
he("maxon_E_table", ch05["maxonE"]["value"], ch05["maxonE"]["tex"], "meV", ["ch05"], "maximum of the same table", "ch05 maxonE")
he("maxon_k_table", ch05["maxonKshort"]["value"], ch05["maxonKshort"]["tex"], "A^-1", ["ch05"], "same table", "ch05 maxonKshort")
he("landau_v", ch05["landauV"]["value"], ch05["landauV"]["tex"], "m s^-1", ["ch05"], "min of eps/(hbar k) over the same table", "ch05 landauV")
he("landau_k", ch05["landauK"]["value"], ch05["landauK"]["tex"], "A^-1", ["ch05"], "same", "ch05 landauK")
he("landau_over_c", ch05["landauOverC"]["value"], ch05["landauOverC"]["tex"], "", ["ch05"], "v_L / c with c = 238.3 m/s", "ch05 landauOverC")
# the paper's own roton parameters (its Table III, arXiv v1), quoted in ch05's Exercise 1
assert quotes["exercise1_roton"].startswith("Delta = 0.7418 meV, k_R = 1.918 A^-1, mu_R = 0.141")
he("Delta_R_paper", 0.7418, "0.7418", "meV", ["ch05"], SRC21 + ", Table III (energy scale calibrated on Delta_R = 0.7418(10) meV measured by Stirling, triple axis)",
   "ch05 paper_quotes_used_literally.exercise1_roton / Delta_R_calibration_meV = " + quotes["Delta_R_calibration_meV"])
he("k_R_paper", 1.918, "1.918", "A^-1", ["ch05"], SRC21 + ", Table III", "ch05 paper_quotes_used_literally.exercise1_roton")
he("mu_R_paper", 0.141, "0.141", "m_4", ["ch05"], SRC21 + ", Table III", "ch05 paper_quotes_used_literally.exercise1_roton")
R["he4"] = he4
# derived numbers of the conversion table that use c = 238.3 m/s (ch04, ch05)
put("hbar_c_meV_A", hbar * c4 / meV / A, 5, "meV A", ["ch05"], "hbar c with c = 238.3 m/s: the slope of the phonon branch")
put("theta_K_A", hbar * c4 / kB / A, 5, "K A", ["ch04"], "hbar c / k_B with c = 238.3 m/s")
put("kT_per_K", kB / (hbar * c4) * A, 4, "A^-1 K^-1", ["ch04"], "k_B T/(hbar c) per kelvin: the thermal phonon wave number")
put("kstar_A", 2 * m4 * c4 / hbar * A, 3, "A^-1", ["ch05"], "2 m_4 c / hbar: the one Bogoliubov wave number of 4He parameters")
put("n_from_Vm_A3", NA / (Vm * 1e24), 5, "A^-3", [], "N_A / V_m: number density at the molar volume of ch04")
put("rho_from_Vm_g_cm3", A4 / Vm, 5, "g cm^-3", [], "A_r(4He) g/mol / V_m: mass density at the molar volume of ch04")

# --------------------------------------------------------------------------------- 5. Gross-Pitaevskii units
# i hbar psi_t = -(hbar^2/2m) Lap psi + g |psi|^2 psi on a background of density n: the units are built from hbar, m and g n.
# Check the dictionary symbolically (sympy) and record the numbers the appendix prints.
import sympy as sp
hb, mm, gg, nn, kk, TT = sp.symbols("hbar m g n k T", positive=True)
mu_s = gg * nn
xi_s = hb / sp.sqrt(mm * gg * nn)
tau_s = hb / (gg * nn)
c_s = sp.sqrt(gg * nn / mm)
eps0 = hb ** 2 * kk ** 2 / (2 * mm)
bog = sp.sqrt(eps0 * (eps0 + 2 * gg * nn))
units = {hb: 1, mm: 1, gg: 1, nn: 1}
gp = {}
assert sp.simplify(xi_s / tau_s - c_s) == 0                      # the unit of speed xi/tau is the Bogoliubov sound speed
assert sp.simplify(bog.subs(units) - kk * sp.sqrt(1 + kk ** 2 / 4)) == 0
assert sp.limit(bog.subs(units) / kk, kk, 0) == 1                 # phonon slope c = 1
kstar_s = 2 * mm * c_s / hb
assert kstar_s.subs(units) == 2 and sp.simplify(kstar_s * xi_s) == 2
kappa_s = 2 * sp.pi * hb / mm
lamT2 = 2 * sp.pi * hb ** 2 / (mm * TT)                            # k_B = 1
xi_alt = hb / sp.sqrt(2 * mm * gg * nn)                          # the other convention (e.g. Pitaevskii-Stringari; crate qf-gpe2d)
for key, expr, n_sig in [("mu", mu_s, 4), ("xi", xi_s, 4), ("tau", tau_s, 4), ("c", c_s, 4), ("kstar", kstar_s, 4),
                         ("kappa", kappa_s, 5), ("xi_alt", xi_alt, 5), ("xi_over_xi_alt", xi_s / xi_alt, 5)]:
    v = float(expr.subs(units))
    gp[key] = dict(expression=str(expr), value_in_gp_units=v, tex=num_tex(v, n_sig) if v not in (1.0, 2.0) else str(int(v)))
gp["lambdaT2"] = dict(expression=str(lamT2), value_in_gp_units="2*pi/T")
gp["bogoliubov"] = dict(expression=str(bog), value_in_gp_units="k*sqrt(1+k^2/4)")
R["gp_units"] = gp

# cross-checks against the chapters' own computations (they must agree to round-off, otherwise the appendix is wrong)
checks = {
    "ch01 meV_in_K": (ch01["meV_in_K"], conv["meV_in_K"]["value"]),
    "ch01 hbar2/2m_n": (ch01["hbar2_over_2m_neutron_meV_A2"], conv["hbar2_2mn_meV_A2"]["value"]),
    "ch01 E lambda^2": (ch01["E_over_lambda2_meV_A2"], conv["h2_2mn_meV_A2"]["value"]),
    "ch01 v lambda": (ch01["neutron_v_times_lambda_ms_A"], conv["h_over_mn_ms_A"]["value"]),
    "ch03 kappa_He4": (ch03["constants"]["kappa_SI_m2_per_s"], conv["kappa4_m2_s"]["value"]),
    "ch06 universal jump SI": (ch06["universal_jump_SI_kg_m2_K"], conv["universal_jump_SI"]["value"]),
    "ch04 theta = hbar c/k_B": (ch04["constants"]["theta_K_A"], conv["theta_K_A"]["value"]),
    "ch04 k_T per kelvin": (ch04["constants"]["k_T_per_K_inv_A"], conv["kT_per_K"]["value"]),
}
R["crosschecks_with_chapters"] = {k: dict(chapter=a, appendix=b, rel_diff=abs(a - b) / abs(b)) for k, (a, b) in checks.items()}
for k, (a, b) in checks.items():
    assert abs(a - b) <= 1e-12 * abs(b), (k, a, b)
# ch05 prints hbar^2/2m_4 = 0.522 meV A^2 with its rounded mass 4.0026032 u
assert ch05["h2m4"]["tex"] == "0.522" and abs(hbar ** 2 / (2 * M4_ch05 * m_u) / meV / A ** 2 - 0.522) < 5e-4

def all_tex_strings(x, acc=None):
    acc = set() if acc is None else acc
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ("tex", "tex_also") and isinstance(v, str):
                acc.add(v)
            elif k in ("tex", "tex_also") and isinstance(v, list):
                acc.update(v)
            else:
                all_tex_strings(v, acc)
    elif isinstance(x, list):
        for v in x:
            all_tex_strings(v, acc)
    return acc


def check_appendix(path=BOOK / "chapters" / "appD.tex") -> int:
    """Every \\num{...} of the appendix must be a 'tex' string of the JSON (so every printed number was computed or read
    from a chapter's number file by this script). Returns the number of problems and prints them."""
    src = path.read_text()
    src = re.sub(r"(?m)(?<!\\)%.*$", "", src)              # drop comments
    printed = re.findall(r"\\num\{([^}]*)\}", src)
    known = all_tex_strings(R)
    bad = sorted({p for p in printed if p not in known})
    for p in bad:
        print("appD.tex prints \\num{" + p + "} which is not a 'tex' value of appD_numbers.json")
    unused = sorted(known - set(printed))
    print(f"check: {len(printed)} \\num occurrences, {len(set(printed))} distinct, {len(bad)} unknown; "
          f"{len(unused)} JSON values not printed: {unused}")
    return len(bad)


if __name__ == "__main__":
    OUT.write_text(json.dumps(R, indent=1, ensure_ascii=False))
    if "--check" in sys.argv:
        sys.exit(1 if check_appendix() else 0)
    for sec in ("codata", "conversions"):
        for k, v in R[sec].items():
            print(f"{sec:12s} {k:22s} {v['value']!r:28} tex={v['tex']}")
    print(json.dumps(R["helium_masses"], indent=1))
    print(json.dumps(R["crosschecks_with_chapters"], indent=1))
