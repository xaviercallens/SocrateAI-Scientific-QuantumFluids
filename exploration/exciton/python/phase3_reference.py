#!/usr/bin/env python3
"""Phase 3 independent reference (written and run BEFORE the Rust program): driven-dissipative GPE with an incoherent reservoir.
  i dpsi/dt = [-1/2 lap + V + g|psi|^2 + gR nR + i/2 (R nR - gamma)] psi ;  d nR/dt = P - (gammaR + R|psi|^2) nR
Closed-form uniform steady state, Bogoliubov-type (3x3 per k) linearisation, and the pump-budget identity.
Usage: phase3_reference.py <out.json>"""
import json, sys
import numpy as np

PAR = dict(g=0.04, gR=1.0, gamma=0.1, gammaR=200.0, R=1.0)   # dimensionless, hbar = m = 1
M, L = 16, 16.0

def steady(P, p=PAR):
    Pth = p["gamma"] * p["gammaR"] / p["R"]
    if P <= Pth:
        return dict(Pth=Pth, n=0.0, nR=P / p["gammaR"], omega=p["gR"] * P / p["gammaR"])
    n = P / p["gamma"] - p["gammaR"] / p["R"]
    nR = p["gamma"] / p["R"]
    return dict(Pth=Pth, n=n, nR=nR, omega=p["g"] * n + p["gR"] * nR)

def jac_k(k, P, p=PAR):
    """Real 3x3 linearisation about the uniform state in the frame rotating at omega.
    variables: (Re d psi, Im d psi, d nR) with psi0 = sqrt(n) real; k-mode of cos type (all fields even in x)."""
    s = steady(P, p); n = s["n"]; a = np.sqrt(n); e = 0.5 * k * k
    g, gR, R = p["g"], p["gR"], p["R"]
    # d(Re)/dt =  (e + 2 g n)?  derive: i psi' = (e + g|psi|^2 + gR nR - omega + i/2(R nR - gamma)) psi
    # psi' = -i (e + g n_tot + gR nR - omega) psi + 1/2 (R nR - gamma) psi ; with psi = a + dr + i di
    # real part: dr' = e*di... assemble below by linearising the real system
    # H0 = g n + gR nR - omega = 0 at steady state
    # F = -i (e + g|psi|^2 + gR nR - omega) psi + 1/2(R nR - gamma) psi
    # dF = -i (e + 2 g n) dr - i... do it explicitly:
    # Re F: (e + g|psi|^2 + gR nR - omega) * Im psi + 1/2 (R nR - gamma) Re psi
    # Im F: -(e + g|psi|^2 + gR nR - omega) * Re psi + 1/2 (R nR - gamma) Im psi
    nR0 = s["nR"]
    A = np.zeros((3, 3))
    # R nR - gamma = 0 at steady state; (g n + gR nR - omega) = 0
    # d(ReF)/d(Re psi) = (g * 2 a *0?) : Re F = X*Im psi + 1/2 G Re psi, X = e + g|psi|^2 + gR nR - omega, G = R nR - gamma
    # at base: Im psi = 0, X0 = e, G0 = 0
    # dReF = dX*0 + e*di + 1/2 dG * a ;   dX = 2 g a dr + gR dnR ;  dG = R dnR
    # dImF = -(dX) a - e dr + 1/2 dG * 0 ... = -(2 g a dr + gR dnR) a - e dr
    A[0] = [0.0, e, 0.5 * R * a]
    A[1] = [-(2 * g * n + e), 0.0, -gR * a]
    # d nR'/dt = P - (gammaR + R|psi|^2) nR : d = -R*2 a dr * nR0 - (gammaR + R n) dnR
    A[2] = [-2 * R * a * nR0, 0.0, -(p["gammaR"] + R * n)]
    return A

def spectrum(P, p=PAR):
    out = []
    for i in range(M):
        for j in range(M):
            kx = 2 * np.pi * (i if i <= M // 2 else i - M) / L
            ky = 2 * np.pi * (j if j <= M // 2 else j - M) / L
            k = np.hypot(kx, ky)
            ev = np.linalg.eigvals(jac_k(k, P, p))
            out.append((i, j, k, sorted(ev, key=lambda z: (-z.real, z.imag))))
    return out

if __name__ == "__main__":
    P_above, P_below = 1.05 * 20.0, 0.8 * 20.0
    res = dict(params=PAR, M=M, L=L, P_above=P_above, P_below=P_below,
               steady_above=steady(P_above), steady_below=steady(P_below))
    sp = spectrum(P_above)
    res["max_re_nonzero_k"] = max(max(z.real for z in ev) for (i, j, k, ev) in sp if k > 0)
    res["max_re_k0_nonGoldstone"] = max(z.real for z in jac_eigs) if (jac_eigs := np.linalg.eigvals(jac_k(0.0, P_above))) is not None else None
    res["eig_k0"] = [[z.real, z.imag] for z in np.linalg.eigvals(jac_k(0.0, P_above))]
    res["spectrum"] = [dict(i=i, j=j, k=k, ev=[[z.real, z.imag] for z in ev]) for (i, j, k, ev) in sp]
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    print("n_above", res["steady_above"]["n"], "omega", res["steady_above"]["omega"],
          "max Re (k>0)", res["max_re_nonzero_k"], "k0 eig", res["eig_k0"])
