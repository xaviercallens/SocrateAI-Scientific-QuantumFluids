"""Chapter 7: the bath that rubs against the vortex, computed (no solver run; numpy only).
(i)  Landau normal density of a free-quasiparticle bath with the Bogoliubov dispersion  eps_k^2 = k^2 + k^4/4  (hbar = m = g n = 1)
         rho_n = (1/2) (1/L^2) sum_k k^2 (-dn/d eps)
     on the ACTUAL mode set of each PGPE arm (grid N, box L = 64, disk |k| <= k_cut, k = 2 pi m / L, k != 0), for
     - the classical-field (Rayleigh-Jeans) occupation  n = T/eps     (-dn/deps = T/eps^2),  the bath of the projected GPE, and
     - the Bose occupation  n = 1/(exp(eps/T) - 1)                  (-dn/deps = exp(eps/T)/(T (exp(eps/T) - 1)^2)),  a quantum gas at the same T.
    compared with the measured normal fraction 1 - n_s/n of each base state (docs/designs/FRICTION_LAW_THEORY_NOTE.md did this for three bases).
(ii) occupations n_RJ and n_Bose at a few wavenumbers, and the fraction of the RJ Landau sum carried by modes with eps < T.
Arms and measured (T, rho_n/rho) are read from data/generated/pgpe/transport/fl/friction_law_results.json (written by analyze_friction_law.py).
Nothing here is a statement about helium: it is textbook kinetic theory evaluated on this model's modes."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from ch07_common import addnum
ROOT = Path(__file__).resolve().parents[2]
fl = json.loads((ROOT / "data/generated/pgpe/transport/fl/friction_law_results.json").read_text())
L = 64.0
GRID = {2.0944: (128, 1 / 3), 3.1416: (128, 1 / 2), 6.2832: (256, 1 / 2)}      # k_cut -> (N, kcut_frac) as in the campaign


def modes(kc, N, frac):
    dx = L / N; k1 = 2 * np.pi * np.fft.fftfreq(N, d=dx); kx, ky = np.meshgrid(k1, k1, indexing="ij"); k = np.sqrt(kx ** 2 + ky ** 2)
    kcut = frac * np.pi / dx; m = (k <= kcut) & (k > 0); return k[m], kcut


def eps(k):
    return np.sqrt(k ** 2 + k ** 4 / 4)


def rho_n_rj(k, T):
    return 0.5 / L ** 2 * np.sum(T * k ** 2 / eps(k) ** 2)


def rho_n_bose(k, T):
    x = eps(k) / T; mdn = np.exp(-x) / (T * (1 - np.exp(-x)) ** 2)          # -dn/d eps = e^{x}/(T (e^{x}-1)^2), rewritten for large x
    return 0.5 / L ** 2 * np.sum(k ** 2 * mdn)


rows = []
for a in fl["arms"]:
    N, frac = GRID[round(a["kcut"], 4)]; k, kcut = modes(a["kcut"], N, frac); T = a["T"]
    r_rj = rho_n_rj(k, T); r_b = rho_n_bose(k, T)
    rows.append(dict(label=a["label"], kcut=float(kcut), N=N, n_modes=int(len(k)), T=T, rho_n_measured=a["rho_n"], rho_n_landau_RJ=float(r_rj), ratio_landau_RJ_over_measured=float(r_rj / a["rho_n"]),
                     rho_n_landau_Bose=float(r_b), ratio_RJ_over_Bose=float(r_rj / r_b)))
    print(f"{a['label']:16s} modes={len(k):6d} T={T:.3f}  measured={a['rho_n']:.4f}  Landau-RJ={r_rj:.4f} ({r_rj / a['rho_n']:.2f})  Landau-Bose={r_b:.2e}  RJ/Bose={r_rj / r_b:.0f}")

# (ii) occupations at T = 0.115 (the T/T_BKT = 0.14 base)
T = 0.115; occ = []
for kk in (0.1, 0.2, 0.5, 1.0, 2.0, np.pi, 2 * np.pi):
    e = float(eps(kk)); n_rj = T / e; n_b = 1.0 / np.expm1(e / T); occ.append(dict(k=float(kk), eps=e, eps_over_T=e / T, n_RJ=n_rj, n_Bose=n_b, ratio=n_rj / n_b))
    print(f"k={kk:6.3f} eps={e:7.3f} eps/T={e / T:7.2f}  n_RJ={n_rj:.3e}  n_Bose={n_b:.3e}  ratio={n_rj / n_b:.3e}")
k, kcut = modes(np.pi, 128, 0.5)
w = 0.5 / L ** 2 * T * k ** 2 / eps(k) ** 2; frac_below = float(w[eps(k) < T].sum() / w.sum())
frac_below_3T = float(w[eps(k) < 3 * T].sum() / w.sum())
print("fraction of the RJ Landau sum (k_c = pi, T = 0.115) carried by modes with eps < T:", frac_below, " eps < 3T:", frac_below_3T)
# the phonon limit of the Bose bath in two dimensions: rho_n = 3 zeta(3) T^3 / (2 pi c^4), c = 1
from scipy.special import zeta
phonon_bose = 3 * zeta(3) / (2 * np.pi) * T ** 3
print("2D phonon-gas Landau density 3 zeta(3) T^3/(2 pi):", phonon_bose)
addnum("bath", dict(arms=rows, occupations_T0p115=occ, fraction_RJ_landau_sum_eps_lt_T=frac_below, fraction_RJ_landau_sum_eps_lt_3T=frac_below_3T,
                    phonon_bose_landau_T0p115=float(phonon_bose), note="free Bogoliubov quasiparticles, hbar = m = g n = 1; Landau rho_n = (1/2)(1/L^2) sum_k k^2 (-dn/d eps)"))
