"""Shared definitions for the chapter-4 computations.

* physical constants (SI 2019 exact values through scipy.constants);
* the coefficient set quoted for superfluid 4He at saturated vapour pressure in the arXiv source of
  Godfrin et al., PRB 103, 104516 (2021) (c = 238.3 m/s, alpha_2 = 1.55 A^2, alpha_3 = -4.04 A^3, alpha_4 = 2.30 A^4,
  alpha_5 = alpha_6 = 0) and the molar volume 27.5793 cm^3/mol quoted there;
* the closed forms A..L of Eq. (22) -- exactly the right-hand sides of `PhononSpecificHeat.phonon_specific_heat`;
* loaders for the two open ancillary files of that paper (CC BY 4.0): the measured dispersion DispersionP0allRange.txt and
  the specific-heat table Cv-and-Entropy.txt.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import scipy.constants as C
from scipy.special import zeta

kB, hbar, NA = C.k, C.hbar, C.N_A
c = 238.3                      # m/s
Vm = 27.5793e-6                # m^3 / mol
ALPHA = dict(a2=1.55, a3=-4.04, a4=2.30, a5=0.0, a6=0.0)   # Angstrom^2, ^3, ^4, ^5, ^6
Aa = 1e-10                     # metre per Angstrom
THETA = hbar * c / (kB * Aa)   # hbar*c/k_B in kelvin * Angstrom  (eps_K = THETA * k[1/A] * (1+...))
MEV_K = 1e-3 * C.e / C.k       # 1 meV in kelvin
PREF = Vm * 1e30 * kB / (2 * np.pi**2)    # V k_B / (2 pi^2), J/(mol K) per (1/Angstrom)^3 -- multiplies  int k^2 f(x) dk  (k in 1/A)
KMAX_MODEL = 2.5               # upper limit of the k-integral for the polynomial model (1/A)

REPO = Path(__file__).resolve().parents[2]
ANC = REPO / "data/external/godfrin_papers/2021_godfrin_landau-dispersion-thermo-he4_anc"


def coeffs_SI(a2=1.55, a3=-4.04, a4=2.30, a5=0.0, a6=0.0):
    """Closed forms of Eq. (22) in J/(mol K^p) -- the right-hand sides of PhononSpecificHeat.phonon_specific_heat."""
    A2, A3, A4, A5, A6 = a2*Aa**2, a3*Aa**3, a4*Aa**4, a5*Aa**5, a6*Aa**6
    V = Vm; pi = np.pi
    A = 2*pi**2*kB**4*V/(15*c**3*hbar**3)
    Cc = -40*pi**4*A2*kB**6*V/(21*c**5*hbar**5)
    D = -15120*A3*kB**7*V*zeta(7)/(pi**2*c**6*hbar**6)
    E = 224*pi**6*kB**8*V*(4*A2**2-A4)/(15*c**7*hbar**7)
    K = 1451520*kB**9*V*zeta(9)*(9*A2*A3-A5)/(pi**2*c**8*hbar**8)
    L = -640*pi**8*kB**10*V*(55*A2**3-30*A2*A4-15*A3**2+3*A6)/(11*c**9*hbar**9)
    return dict(A=A, C=Cc, D=D, E=E, K=K, L=L)

POWERS = dict(A=3, C=5, D=6, E=7, K=8, L=9)
PRINTED = dict(A=0.0831, C=-0.0548, D=0.0653, E=0.0603, K=-0.262, L=0.141)   # arXiv v1 source, J/(mol K^p), T in kelvin


def u_poly(k, a2=1.55, a3=-4.04, a4=2.30, a5=0.0, a6=0.0):
    """u = eps/(hbar c) in 1/Angstrom as a function of k in 1/Angstrom."""
    return k*(1 + a2*k**2 + a3*k**3 + a4*k**4 + a5*k**5 + a6*k**6)


def du_dk(k, a2=1.55, a3=-4.04, a4=2.30, a5=0.0, a6=0.0):
    return 1 + 3*a2*k**2 + 4*a3*k**3 + 5*a4*k**4 + 6*a5*k**5 + 7*a6*k**6


def bose_weight(x):
    """x^2 e^x/(e^x-1)^2 for x > 0 (vectorised, overflow-safe; equals 1 at x -> 0)."""
    x = np.asarray(x, dtype=float)
    em = -np.expm1(-x)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(x > 0, x*x*np.exp(-x)/(em*em), 1.0)
    return out


def load_dispersion(return_err=False):
    """(k [1/A], eps [meV]) of the measured dispersion at P = 0, T < 0.1 K (1727 numeric rows; one placeholder row '-- -- --' is skipped).
    With return_err=True a third array is returned: the uncertainty column in meV (nan where the table has '--'; 34 rows carry one)."""
    k, e, er = [], [], []
    for line in (ANC/"DispersionP0allRange.txt").read_bytes().decode("latin-1").splitlines()[2:]:
        p = line.split("\t")
        try:
            kk, ee = float(p[0]), float(p[1])
        except (ValueError, IndexError):
            continue
        try:
            e3 = float(p[2])
        except (ValueError, IndexError):
            e3 = float("nan")
        k.append(kk); e.append(ee); er.append(e3)
    if return_err:
        return np.array(k), np.array(e), np.array(er)
    return np.array(k), np.array(e)


def load_paper_cv():
    """Table Cv-and-Entropy.txt: columns T, CvTotal, err, CvPhonons, CvRotons, S (J/(K mol)); '--' -> nan."""
    rows = []
    for line in (ANC/"Cv-and-Entropy.txt").read_bytes().decode("latin-1").splitlines()[2:]:
        p = line.split("\t")
        if len(p) < 7:
            continue
        def f(s):
            try: return float(s)
            except ValueError: return np.nan
        rows.append([f(x) for x in p[:7]])
    a = np.array(rows)
    return dict(T=a[:, 0], tot=a[:, 1], err=a[:, 2], ph=a[:, 3], rot=a[:, 4], S=a[:, 6])
