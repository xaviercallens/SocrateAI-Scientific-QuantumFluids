# Study-only numerical checks for the exciton-fluid plan (not part of the repository).
import mpmath as mp, numpy as np
mp.mp.dps = 30

# --- (a) Epstein zeta of the triangular lattice: sum' (m^2+mn+n^2)^(-s) = 6 zeta(s) L(s, chi_-3)
chi = [0, 1, -1]                      # Dirichlet character mod 3
def L3(s): return mp.dirichlet(s, chi)
def lattice_sum_direct(s, R=400):
    m = np.arange(-R, R+1)
    M, N = np.meshgrid(m, m)
    Q = (M*M + M*N + N*N).astype(float)
    Q = Q[Q > 0]
    return float(np.sum(Q**(-s)))
for s in (2.0, 3.0):
    print(f"s={s}: direct {lattice_sum_direct(s):.12f}   6*zeta(s)*L(s,chi_-3) = {6*mp.zeta(s)*L3(s)}")

# --- (b) dipolar (1/r^3) triangular-lattice constant, nearest-neighbour distance a = 1:
#         sum' r^-3 = 6 zeta(3/2) L(3/2, chi_-3)
c3 = 6*mp.zeta(1.5)*L3(1.5)
print("sum' r^-3 (a=1) =", c3)

# --- (c) bilayer dipole kernel in units e^2/(4 pi eps0 eps) = 1, d = 1:  V(r) = 2/r - 2/sqrt(r^2+1)
#     Hartree integral  int V d^2r = 4 pi d  (=> g = e^2 d/(eps0 eps)),  checked by quadrature
V = lambda r: 2/r - 2/mp.sqrt(r*r+1)
I = 2*mp.pi*mp.quad(lambda r: V(r)*r, [0, 1, 10, mp.inf])
print("int V d^2r =", I, "  4*pi =", 4*mp.pi)

# --- (d) Keldysh kernel: H0(x) - Y0(x) = (2/pi) int_0^inf exp(-x u)/sqrt(1+u^2) du
for x in (0.1, 1.0, 5.0):
    lhs = mp.struveh(0, x) - mp.bessely(0, x)
    rhs = (2/mp.pi)*mp.quad(lambda u: mp.e**(-x*u)/mp.sqrt(1+u*u), [0, 1, 10, mp.inf])
    print(f"x={x}: H0-Y0 = {lhs}   integral rep = {rhs}   diff = {float(abs(lhs-rhs)):.2e}")

# --- (e) complete monotonicity in t=r^2 of the bilayer kernel g(t)=2(t^-1/2-(t+1)^-1/2): (-1)^k g^(k)(t) >= 0
g = lambda t: 2*(t**mp.mpf(-0.5) - (t+1)**mp.mpf(-0.5))
ok = True
for t0 in (0.01, 0.3, 1.0, 7.0, 100.0):
    for k in range(0, 9):
        val = (-1)**k * mp.diff(g, t0, k)
        if val < 0: ok = False; print("VIOLATION", t0, k, val)
print("bilayer kernel: (-1)^k g^(k)(t) >= 0 for k<=8 at 5 points:", ok)

# --- (f) lattice energy vs Hartree for the bilayer kernel (units: e^2/(4 pi eps0 eps) = 1, d = 1)
#     e_H = (rho/2) * int V = 2 pi rho ;  e_lat = (1/2) sum'_{a in A_rho} V(|a|);  rho in units d^-2
def e_lat(rho, R=60):
    a = (2/(np.sqrt(3)*rho))**0.5        # nearest-neighbour distance of the triangular lattice of density rho
    n = int(R/a) + 2
    m = np.arange(-n, n+1)
    M, N = np.meshgrid(m, m)
    X = a*(M + 0.5*N); Y = a*(np.sqrt(3)/2*N)
    r = np.hypot(X, Y); r = r[(r > 0) & (r < R)]
    s = np.sum(2/r - 2/np.sqrt(r*r+1))
    # tail beyond R: density rho, V ~ 1/r^3 (d^2 = 1): int_R^inf rho 2 pi r (1/r^3) dr = 2 pi rho / R
    s += 2*np.pi*rho/R
    return 0.5*s
print("\n rho*d^2    a/d     e_lat       e_H        e_H/e_lat")
for rho in (1e-3, 1e-2, 1e-1, 0.3, 1.0, 3.0):
    el = e_lat(rho); eh = 2*np.pi*rho
    a = (2/(np.sqrt(3)*rho))**0.5
    print(f" {rho:7.3g}  {a:7.3f}  {el:10.5f}  {eh:10.5f}  {eh/el:8.3f}")
