#!/usr/bin/env python3
"""Spectral and Nore-Abid-Brachet energy budget of the round-2 Part I final states (t = 1500), arms V / P / 0.
Answers: where did the energy the high-k bath lost in arm V go? Writes data/generated/pgpe/r2_energy_budget.json.
Caveat recorded here: the torus point-vortex Hamiltonian (Weiss-McWilliams) carries an additive constant PER PAIR, so
energy differences between configurations with different vortex numbers are not meaningful; budgets use the field."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
ROOT = Path(__file__).resolve().parents[2]
s = PGPE(N=128, L=64.0); kk = np.sqrt(s.k2); w = s.dx**2 / s.N**2
BANDS = [(0, 0.05), (0.05, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.0)]

def budget(c):
    psi = s.psi(c); rho = np.abs(psi)**2
    kin_k = 0.5 * s.k2 * np.abs(c)**2 * w
    out = {f"kin[{a},{b})": float(kin_k[(kk >= a*s.kcut) & (kk < b*s.kcut) & s.P].sum()) for a, b in BANDS}
    out["interaction"] = float(0.5 * s.g * np.sum(rho**2) * s.dx**2); out["k0_frac"] = float(np.abs(c[0, 0])**2 * w / s.norm(c))
    gx = np.fft.ifft2(1j*s.kx*c); gy = np.fft.ifft2(1j*s.ky*c); jx = (np.conj(psi)*gx).imag; jy = (np.conj(psi)*gy).imag
    sr = np.sqrt(rho + 1e-30); Ux, Uy = np.fft.fft2(jx/sr), np.fft.fft2(jy/sr); k2 = np.where(s.k2 == 0, 1, s.k2)
    div = (s.kx*Ux + s.ky*Uy) / k2; Ic = 0.5*np.sum(np.abs(s.kx*div)**2 + np.abs(s.ky*div)**2)*w; It = 0.5*np.sum(np.abs(Ux)**2 + np.abs(Uy)**2)*w
    gsx = np.fft.ifft2(1j*s.kx*np.fft.fft2(sr)).real; gsy = np.fft.ifft2(1j*s.ky*np.fft.fft2(sr)).real
    out.update(E_compressible=float(Ic), E_incompressible=float(It - Ic), E_qpressure=float(0.5*np.sum(gsx**2 + gsy**2)*s.dx**2), E_total=s.energy(c))
    return out

res = {}
for base in ["e0.90_s11_t4000", "e0.90_s12_t4000", "e0.60_s11_t4000"]:
    res[base] = {}
    for arm in ("0", "P", "V"):
        f = ROOT / f"data/generated/pgpe/r2/I_{base}_{arm}_final.npy"
        if f.exists(): res[base][arm] = budget(np.load(f))
    ref = "0" if "0" in res[base] else "P"
    res[base]["diff_V_minus_" + ref] = {k: res[base]["V"][k] - res[base][ref][k] for k in res[base]["V"]}
    if ref == "0": res[base]["diff_P_minus_0"] = {k: res[base]["P"][k] - res[base]["0"][k] for k in res[base]["P"]}
    d = res[base]["diff_V_minus_" + ref]
    bath = d["kin[0.6,1.0)"] + d["kin[0.4,0.6)"]; lowk = d["kin[0,0.05)"] + d["kin[0.05,0.2)"] + d["kin[0.2,0.4)"]
    res[base]["summary"] = {"ref": ref, "bath_highk_change": bath, "lowk_kinetic_change": lowk, "interaction_change": d["interaction"],
                            "incompressible_change": d["E_incompressible"], "compressible_change": d["E_compressible"], "total_change": d["E_total"]}
    print(base, {k: round(v, 1) if isinstance(v, float) else v for k, v in res[base]["summary"].items()})
(ROOT / "data/generated/pgpe/r2_energy_budget.json").write_text(json.dumps(res, indent=1))
