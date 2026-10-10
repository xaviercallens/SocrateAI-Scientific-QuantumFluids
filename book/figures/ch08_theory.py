"""Chapter 8: closed forms of the 2D Landau (zero-sound) model with one Landau parameter F, units a = q v_F = 1.
Everything here is either a statement proved in Lean (ZeroSound.lean, Ch08_ZeroSound2D.lean) or a textbook formula that
is CHECKED numerically in ch08_zerosound.py / ch08_timedomain.py; the Lean/derived status of each is in the docstring.

Free response (Lean: omega2 for s>1):   Omega(s) = 1 - s/sqrt(s^2-1)  (s>1),   1 + i s/sqrt(1-s^2)  (0<s<1)
Dispersion relation                      1 + F Omega(s) = 0
Root (Lean, zero_sound_2d_iff/unique)    s0 = (1+F)/sqrt(1+2F),  F>0          s0^2 - 1 = F^2/(1+2F)
Structure factor (units N0, s = omega/(v_F q)),  S(s) = Im Omega /(pi |1+F Omega|^2):
    continuum (0<s<1)   S_c(s) = s sqrt(1-s^2) / (pi [(1+F)^2 - (1+2F) s^2])          (derived here, verified numerically)
    pole (F>0)          W delta(s - s0),   W = 1/(F^2 Omega'(s0)) = F/(1+2F)^(3/2)      (Lean: pole_weight)
First moment (f-sum rule, 2D, m* = m):  int s S ds = 1/4;  the pole carries 1 - 1/(1+2F)^2 of it (Lean: pole_fraction).
Time domain (the CVODE problem):  kick nu(theta,0)=cos(theta):   i m(t)/2 = int_0^1 S_c(s) sin(st) ds + W sin(s0 t)
                                  uniform nu(theta,0)=1 :          m(t) = 2F/(1+2F) cos(s0 t) + (2/pi) int_0^1 rho_U(y) cos(yt) dy,
                                                                   rho_U(y) = (1+F) sqrt(1-y^2) / ((1+F)^2 - (1+2F) y^2)
Special exact cases (uniform):  F = 0:  m = J0(t);   F = -1/2:  m = 2 J1(t)/t.
"""
import numpy as np
import mpmath as mp
from numpy.polynomial.legendre import leggauss

_X, _Wt = leggauss(900)
_PHI = 0.25 * np.pi * (_X + 1.0)          # nodes on [0, pi/2]
_WPHI = 0.25 * np.pi * _Wt


def s0(F): return (1.0 + F) / np.sqrt(1.0 + 2.0 * F)
def s1_first_sound(F): return np.sqrt((1.0 + F) / 2.0)          # 2D, F1 = 0:  c1^2 = (n/m) dmu/dn = v_F^2 (1+F)/2
def W_pole(F): return F / (1.0 + 2.0 * F) ** 1.5
def R_pole(F): return F / (1.0 + 2.0 * F)                        # residue of the uniform-IC Laplace transform
def pole_fraction(F): return 1.0 - 1.0 / (1.0 + 2.0 * F) ** 2    # share of the f-sum rule carried by the pole


def Omega2(s):
    s = np.asarray(s, float); out = np.empty(s.shape, complex); m = s > 1
    out[m] = 1 - s[m] / np.sqrt(s[m] ** 2 - 1)
    out[~m] = 1 + 1j * s[~m] / np.sqrt(1 - s[~m] ** 2)
    return out


def Omega3(s):
    s = np.asarray(s, float)
    return 1 - s / 2 * (np.log((s + 1) / np.abs(s - 1)) - 1j * np.pi * (s < 1))


def S_cont(s, F):
    s = np.asarray(s, float)
    return s * np.sqrt(1 - s ** 2) / (np.pi * ((1 + F) ** 2 - (1 + 2 * F) * s ** 2))


def S_cont_from_Omega(s, F):
    """Im Omega / (pi |1+F Omega|^2) evaluated from the definition (a check of S_cont)."""
    Om = Omega2(np.asarray(s, float))
    return Om.imag / (np.pi * np.abs(1 + F * Om) ** 2)


def first_moment_cont(F):
    """int_0^1 s S_cont ds, by Gauss-Legendre in s = sin(phi)."""
    s = np.sin(_PHI)
    return float(np.sum(_WPHI * np.cos(_PHI) * s * S_cont(s, F)))


def zeroth_moment_cont(F):
    s = np.sin(_PHI)
    return float(np.sum(_WPHI * np.cos(_PHI) * S_cont(s, F)))


def kick_ref(t, F):
    """k(t) = i m(t)/2 for the kick initial condition nu(theta,0) = cos(theta)  (m is purely imaginary)."""
    t = np.atleast_1d(np.asarray(t, float)); s = np.sin(_PHI)
    w = _WPHI * np.cos(_PHI) * S_cont(s, F)
    out = np.array([np.sum(w * np.sin(tt * s)) for tt in t])
    if F > 0: out = out + W_pole(F) * np.sin(s0(F) * t)
    return out


def rho_U(y, F): return (1 + F) * np.sqrt(1 - y ** 2) / ((1 + F) ** 2 - (1 + 2 * F) * y ** 2)


def uniform_cont(t, F):
    t = np.atleast_1d(np.asarray(t, float)); y = np.sin(_PHI)
    w = _WPHI * np.cos(_PHI) * rho_U(y, F) * (2 / np.pi)
    return np.array([np.sum(w * np.cos(tt * y)) for tt in t])


def uniform_ref(t, F):
    """m(t) for the uniform initial condition nu(theta,0) = 1 (real)."""
    t = np.atleast_1d(np.asarray(t, float)); out = uniform_cont(t, F)
    if F > 0: out = out + 2 * R_pole(F) * np.cos(s0(F) * t)
    return out


# ---- 3D (for contrast): g3(s) = (s/2) log((s+1)/(s-1)) - 1 = 1/F   (Lean: g3, zero_sound_iff)
def mp_g3(s): return s / 2 * mp.log((s + 1) / (s - 1)) - 1


def mp_s3(F, dps=40):
    mp.mp.dps = dps
    F = mp.mpf(F)
    f = lambda w: mp_g3(1 + mp.e ** w) - 1 / F
    w0 = mp.log(2) - 2 - 2 / F if F < 3 else mp.log(max(mp.sqrt(F / 3) - 1, mp.mpf('0.05')))
    w = mp.findroot(f, w0, tol=mp.mpf(10) ** -(dps - 10), maxsteps=300)
    return 1 + mp.e ** w
