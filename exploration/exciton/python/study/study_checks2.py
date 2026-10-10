import numpy as np
# --- sandwich ratio at the densities of Qi et al. (d = 2 nm; 1e12 cm^-2 = 0.01 nm^-2)
def e_lat(rho, R=80.0):                 # units: e^2/(4 pi eps0 eps)=1, d=1, V=2/r-2/sqrt(r^2+1); rho in d^-2
    a = (2/(np.sqrt(3)*rho))**0.5; n = int(R/a)+2; m = np.arange(-n, n+1)
    M, N = np.meshgrid(m, m); X = a*(M+0.5*N); Y = a*(np.sqrt(3)/2*N); r = np.hypot(X, Y); r = r[(r>0)&(r<R)]
    return 0.5*(np.sum(2/r-2/np.sqrt(r*r+1)) + 2*np.pi*rho/R)
d_nm = 2.0
print("n_x [1e12 cm^-2]   rho d^2    e_H/e_lat")
for n12 in (0.1, 0.3, 0.5, 0.75):
    rho_nm2 = n12*0.01; rd2 = rho_nm2*d_nm**2
    print(f"   {n12:5.2f}         {rd2:7.4f}    {2*np.pi*rd2/e_lat(rd2):7.2f}")

# --- four-flavour model (Qi et al., Eq. 2-3): closed forms and a brute-force check by minimisation
muB = 57.88  # micro-eV / T
Ry = 67e3    # micro-eV
aB = 1.5; d = 2.0
gH = 8*np.pi*d/aB          # in units Ry*aB^2   (g_H = 8 pi d, atomic units)
gX = 1.0; Delta = 1.0/Ry   # 1 micro-eV in Ry
gc, gv = 3.0, 6.0
nx = 0.5e12*(1e-14)*aB**2 # exciton density in aB^-2 (0.5e12 cm^-2)
mu = nx*(2*gH+gX)/2        # B=0 phase IIB total density N=2 mu/(2gH+gX)  -> mu in Ry
Bc2 = gX*Delta*(2*mu+Delta)/(4*gc*gv*(2*gH+gX))     # (mu_B B_c)^2 in Ry^2
Bc = np.sqrt(Bc2)*Ry/muB
print(f"\n g_H = {gH:.1f} (Ry aB^2), n_x aB^2 = {nx:.5f}, mu = {mu*Ry/1e3:.1f} meV, closed-form B_c = {Bc*1e3:.0f} mT")

from itertools import product
def H(n, B, mu):
    n1,n2,n3,n4 = n; N = n1+n2+n3+n4; b = muB*B/Ry
    E = [(gv-gc)*b-Delta, -(gv-gc)*b-Delta, -(gc+gv)*b, (gc+gv)*b]
    return sum((E[i]-mu)*n[i] for i in range(4)) + 0.5*(gH+gX)*N**2 - gX*(n1*n2+n3*n4)
from scipy.optimize import minimize
def groundstate(B, mu, tries=40, seed=1):
    rng = np.random.default_rng(seed); best=None
    for _ in range(tries):
        x0 = rng.uniform(0, 2*nx/ (1), 4)
        r = minimize(lambda x: H(np.abs(x),B,mu), x0, method="L-BFGS-B", bounds=[(0,None)]*4, options={"ftol":1e-18,"gtol":1e-14,"maxiter":2000})
        if best is None or r.fun < best.fun: best = r
    return np.abs(best.x), best.fun
for B in (0.01, 0.04, 0.056, 0.07, 0.2):
    n, f = groundstate(B, mu)
    ph = "IIA(KK+K'K')" if n[0]+n[1] > n[2]+n[3] else "IIB(KK'+K'K)"
    print(f" B={B*1e3:5.0f} mT  n=({n[0]:.5f},{n[1]:.5f},{n[2]:.5f},{n[3]:.5f})  {ph}  N={n.sum():.5f}")
print(" T_BKT (dilute, one flavour) at 0.5e12 cm^-2:", 1.3*7.62*0.5e12*1e-16/8.617e-5, "K")
