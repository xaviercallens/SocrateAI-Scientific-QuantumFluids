"""Shared code of the chapter "Giant Vortex Clusters and Onsager's Negative Temperatures" (file ch13).

Contents
  * the numbers file  figures/ch13_numbers.json  (addnum) and the CVODE environment check (cvode_env, as in ch07_common.py);
  * the experimental vortex positions of Gauthier et al., Science 364, 1264 (2019), Zenodo record 2548958 (CC BY 4.0),
    read from data/external/gauthier2019_zenodo_2548958 and turned into coordinates in the frame of the elliptical trap;
  * point vortices in an ellipse: the exact conformal map of the ellipse onto the unit disc,
        w(z) = theta_1(zeta, q) / theta_4(zeta, q),   zeta = arcsin(z / c),   c^2 = a^2 - b^2,   q = ((a - b)/(a + b))^2
    (Szego's map; zeta sends the ellipse to a rectangle, and sqrt(k) sn sends the rectangle onto the disc), the Dirichlet
    Green function G = -(1/2pi) ln|(w - w')/(1 - conj(w') w)|, the Robin function R = (1/2pi) ln((1 - |w|^2)/|w'|), the
    Kirchhoff-Routh energy and its gradient (the velocities); the same for a disc (images) and for the plane.

Units.  Energies are reported as E/E0 with E0 = rho0 Gamma^2/(4 pi) (Gauthier et al.'s unit); for N vortices of signs s_i
    E/E0 = -2 sum_{i<j} s_i s_j ln|f(z_i, z_j)| + sum_i ln((1 - |w_i|^2)/|w'_i|),    f(z, z') = (w - w')/(1 - conj(w') w),
up to an additive constant that depends on N only (the core cut-off).  Lengths in micrometres, times in seconds.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
ROOT = BOOK.parent
NUM = HERE / "ch13_numbers.json"
DATA = ROOT / "data/external/gauthier2019_zenodo_2548958"
VORTEX_DIR = DATA / "exp/Exp_Vortex_Location_Data"

# --------------------------------------------------------------------------------------------- numbers file
def addnum(key, d):
    """read-modify-write of ch13_numbers.json under an advisory lock"""
    import fcntl
    lock = Path("/mnt/data/xdev-cache/tmp/ch13_numbers.lock"); lock.parent.mkdir(parents=True, exist_ok=True)
    with open(lock, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = json.loads(NUM.read_text()) if NUM.exists() else {}
        cur[key] = d
        NUM.write_text(json.dumps(cur, indent=1, default=_jsonable))


def _jsonable(x):
    if isinstance(x, (np.floating,)): return float(x)
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, complex): return [x.real, x.imag]
    raise TypeError(type(x))


def cvode_env(require_fixed=True):
    """Identify the rusty_sundials module and refuse the stale build of the shared .venv (pre-fix Adams method).
    Probe (as in ch02/ch06/ch07): Adams on y' = -y, t in [0, 10], rtol 1e-8, atol 1e-14 must need < 5000 right-hand sides."""
    import hashlib, time
    import rusty_sundials
    from rusty_sundials import CvodeSolver
    n = [0]

    def f(t, y):
        n[0] += 1; return [-y[0]]
    s = CvodeSolver("adams", 1e-8, 1e-14, 5_000_000); _, y = s.solve(f, 0.0, [1.0], 10.0)
    err = abs(y[0] - math.exp(-10.0)) / math.exp(-10.0)
    path = Path(rusty_sundials.__file__).resolve()
    if require_fixed and (".venv" in str(path) or n[0] >= 5000):
        raise SystemExit(f"rusty_sundials at {path} is the stale build (Adams probe: {n[0]} right-hand sides); run with "
                         "PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext")
    commit_f = path.parent / "commit.txt"; sha = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return dict(module=str(path), module_sha256=sha, commit=commit_f.read_text().strip() if commit_f.exists() else None,
                adams_probe_rhs_calls=n[0], adams_probe_relerr=err, date=time.strftime("%Y-%m-%d %H:%M"))


# --------------------------------------------------------------------------------------------- physical constants
def gamma_rb87_um2_per_s():
    """quantum of circulation h/m for 87Rb in um^2/s (CODATA h and u from scipy; 87Rb mass 86.909180531 u, NIST AME)."""
    from scipy.constants import h, atomic_mass
    return h / (86.909180531 * atomic_mass) * 1e12


# --------------------------------------------------------------------------------------------- the experiment's geometry
UM_PER_PX = 0.49372025          # spacing of the 'xaxis' vector stored in every vortexData.mat (252.8 um over 512 px)
CENTRE_PX = (257.15, 256.00)    # 1-based (column, row) centre of the 120 x 85 um elliptical mask stored with the data
A_UM, B_UM = 60.0, 42.4         # semi-axes of that mask (fit of its second moments: 60.01, 42.42 um)
DETECT_RHO = math.sqrt(0.89)    # detection restricted to the inner 89 % of the ellipse area (Gauthier et al., Methods)

SETS = {   # folder -> (label, condensate fraction in %, as in Gauthier et al. Fig. 4 / Database S1; matched by l/l0(0))
    "FiniteTemp/0.9VEvap": ("0.9 V", 75.3), "FiniteTemp/1.1VEvap": ("1.1 V", 66.795), "FiniteTemp/1.5VEvap": ("1.5 V", 44.0),
    "FiniteTemp/2.0VEvap": ("2.0 V", 33.1), "FiniteTemp/2.5VEvap": ("2.5 V", 26.1125), "FiniteTemp/3.0VEvap": ("3.0 V", 17.63),
}
GRID_SET = "SlowComb"           # the grid ("comb") stir of Gauthier et al. Fig. 3 (l/l0 reproduced to a constant factor 0.994)


def load_frames(folder):
    """Vortex positions of one data set: list over hold times (1 s apart, from 0) of lists over shots of (n,2) arrays
    (X along the major axis, Y along the minor axis, in um, origin at the trap centre)."""
    import scipy.io as sio
    m = sio.loadmat(str(VORTEX_DIR / folder / "vortexData.mat"), squeeze_me=True, struct_as_record=False)
    sc = m["single_centroids"]
    out = []
    for i in range(sc.shape[0]):
        row = []
        for j in range(sc.shape[1]):
            p = np.atleast_2d(np.asarray(sc[i, j], float))
            if p.size == 0:
                row.append(np.zeros((0, 2))); continue
            u = (p[:, 0] - CENTRE_PX[0]) * UM_PER_PX; v = (p[:, 1] - CENTRE_PX[1]) * UM_PER_PX
            row.append(np.column_stack([(u + v) / math.sqrt(2), (-u + v) / math.sqrt(2)]))
        out.append(row)
    return out


def rho_ell(P, a=A_UM, b=B_UM):
    return np.sqrt((P[:, 0] / a) ** 2 + (P[:, 1] / b) ** 2)


def nn_ratio(P, a=A_UM, b=B_UM, area_factor=0.89):
    """Gauthier et al.'s clustering measure l/l0: mean nearest-neighbour distance over l0 = sqrt(0.89 a b / N)."""
    n = len(P)
    if n < 2:
        return np.nan
    d = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)); np.fill_diagonal(d, np.inf)
    return d.min(1).mean() / math.sqrt(area_factor * a * b / n)


# --------------------------------------------------------------------------------------------- the ellipse map
class Ellipse:
    """Conformal map of the ellipse x^2/a^2 + y^2/b^2 < 1 onto the unit disc and the point-vortex functions built on it."""

    def __init__(self, a=A_UM, b=B_UM, nterms=8):
        assert a > b > 0
        self.a, self.b = float(a), float(b)
        self.c = math.sqrt(a * a - b * b)
        self.q = ((a - b) / (a + b)) ** 2
        n = np.arange(nterms)
        self.k1 = 2 * n + 1                                         # theta_1: 2 sum (-1)^n q^{(n+1/2)^2} sin((2n+1) zeta)
        self.c1 = 2 * (-1.0) ** n * self.q ** ((n + 0.5) ** 2)
        m = np.arange(1, nterms + 1)
        self.k4 = 2 * m                                             # theta_4: 1 + 2 sum_{m>=1} (-1)^m q^{m^2} cos(2 m zeta)
        self.c4 = 2 * (-1.0) ** m * self.q ** (m ** 2)

    def zeta(self, z):
        return np.arcsin(np.asarray(z, complex) / self.c)

    def phi_derivs(self, zt):
        """phi = theta_1/theta_4 and its first two derivatives at zeta (array)."""
        zt = np.asarray(zt, complex)[..., None]
        s1 = np.sin(self.k1 * zt); co1 = np.cos(self.k1 * zt)
        t1 = (self.c1 * s1).sum(-1); t1p = (self.c1 * self.k1 * co1).sum(-1); t1pp = -(self.c1 * self.k1 ** 2 * s1).sum(-1)
        s4 = np.sin(self.k4 * zt); co4 = np.cos(self.k4 * zt)
        t4 = 1 + (self.c4 * co4).sum(-1); t4p = -(self.c4 * self.k4 * s4).sum(-1); t4pp = -(self.c4 * self.k4 ** 2 * co4).sum(-1)
        phi = t1 / t4
        php = (t1p * t4 - t1 * t4p) / t4 ** 2
        phpp = (t1pp * t4 - t1 * t4pp) / t4 ** 2 - 2 * t4p * (t1p * t4 - t1 * t4p) / t4 ** 3
        return phi, php, phpp

    def w(self, z):
        return self.phi_derivs(self.zeta(z))[0]

    def w_all(self, z):
        """w, w', w'' at z.  z = c sin(zeta), so d zeta/dz = 1/(c cos zeta) (consistent with the branch numpy chose)."""
        zt = self.zeta(z)
        phi, php, phpp = self.phi_derivs(zt)
        cz = self.c * np.cos(zt); sz = np.sin(zt)
        wp = php / cz
        wpp = phpp / cz ** 2 + php * self.c * sz / cz ** 3
        return phi, wp, wpp

    def inside(self, P, margin=0.0):
        return (P[..., 0] / self.a) ** 2 + (P[..., 1] / self.b) ** 2 < (1 - margin) ** 2


class Disc:
    """The disc of radius R, with the same interface (w = z/R)."""

    def __init__(self, R):
        self.R = float(R); self.a = self.b = float(R)

    def w_all(self, z):
        z = np.asarray(z, complex)
        return z / self.R, np.full_like(z, 1 / self.R), np.zeros_like(z)

    def w(self, z):
        return np.asarray(z, complex) / self.R

    def inside(self, P, margin=0.0):
        return P[..., 0] ** 2 + P[..., 1] ** 2 < (self.R * (1 - margin)) ** 2


def to_c(P):
    P = np.asarray(P, float)
    return P[..., 0] + 1j * P[..., 1]


def energy(dom, P, s):
    """Kirchhoff-Routh energy E/E0 (up to an N-dependent constant) of vortices at P (n,2) with signs s, in domain dom
    (Ellipse or Disc); dom=None is the unbounded plane (no Robin term)."""
    z = to_c(P); s = np.asarray(s, float); n = len(z)
    iu = np.triu_indices(n, 1)
    if dom is None:
        f = np.abs(z[:, None] - z[None, :])
        return float(-2 * np.sum((s[:, None] * s[None, :] * np.log(np.where(f > 0, f, 1)))[iu]))
    w, wp, _ = dom.w_all(z)
    f = np.abs((w[:, None] - w[None, :]) / (1 - np.conj(w[None, :]) * w[:, None]))
    pair = -2 * np.sum((s[:, None] * s[None, :] * np.log(np.where(f > 0, f, 1)))[iu])
    robin = np.sum(np.log((1 - np.abs(w) ** 2) / np.abs(wp)))
    return float(pair + robin)


def velocities(dom, P, s, Gamma=1.0):
    """Kirchhoff-Routh velocities (n,2) of vortices of circulations s_i * Gamma.  conj(dz_i/dt) = 2i [sum_{j!=i} Gamma_j d_1 G_ij
    + Gamma_i/2 dR_i],  d_1 G = -(1/4pi) w'_i [1/(w_i - w_j) + conj(w_j)/(1 - conj(w_j) w_i)],  dR = (1/2pi)[-conj(w) w'/(1-|w|^2) - w''/(2w')]."""
    z = to_c(P); s = np.asarray(s, float); n = len(z); G = s * Gamma
    if dom is None:
        dz = z[:, None] - z[None, :]; np.fill_diagonal(dz, 1.0)
        A = 1 / dz; np.fill_diagonal(A, 0.0)
        dG = -(1 / (4 * np.pi)) * A
        zbar_dot = 2j * (dG * G[None, :]).sum(1)
    else:
        w, wp, wpp = dom.w_all(z)
        dw = w[:, None] - w[None, :]; np.fill_diagonal(dw, 1.0)
        A = 1 / dw; np.fill_diagonal(A, 0.0)
        B = np.conj(w[None, :]) / (1 - np.conj(w[None, :]) * w[:, None])
        np.fill_diagonal(B, 0.0)
        dG = -(1 / (4 * np.pi)) * wp[:, None] * (A + B)
        dR = (1 / (2 * np.pi)) * (-np.conj(w) * wp / (1 - np.abs(w) ** 2) - 0.5 * wpp / wp)
        zbar_dot = 2j * ((dG * G[None, :]).sum(1) + 0.5 * G * dR)
    zdot = np.conj(zbar_dot)
    return np.column_stack([zdot.real, zdot.imag])


def grad_energy(dom, P, s, Gamma=1.0):
    """gradient of the PHYSICAL Kirchhoff-Routh function H_phys = Gamma^2 * E/(4 pi E0-units) w.r.t. positions, from the velocities:
    Gamma_i dx_i/dt = dH/dy_i, Gamma_i dy_i/dt = -dH/dx_i  =>  grad_i H = Gamma_i (-v_y, v_x)."""
    V = velocities(dom, P, s, Gamma); Gi = np.asarray(s, float) * Gamma
    return np.column_stack([-Gi * V[:, 1], Gi * V[:, 0]])


def dipole_moment(P, s):
    """Gauthier et al.'s order parameter D = N^{-1} |sum_j sgn(Gamma_j) x_j| (x along the major axis)."""
    return abs(np.sum(np.asarray(s) * P[:, 0])) / len(P)


def uniform_in(dom, n, rng, rho_max=1.0):
    """n points uniform in the domain (optionally restricted to the scaled region rho < rho_max)."""
    out = np.empty((0, 2))
    while len(out) < n:
        U = rng.uniform(-1, 1, size=(2 * n + 16, 2))
        U = U[(U ** 2).sum(1) < rho_max ** 2]
        out = np.vstack([out, U * np.array([dom.a, dom.b])])
    return out[:n]
