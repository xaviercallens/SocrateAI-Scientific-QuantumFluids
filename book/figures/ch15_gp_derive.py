"""Chapter ch15 (quantum turbulence): derived quantities of a three-dimensional Gross--Pitaevskii turbulence field.

Input (not modified): data/external/polanco_2021_gp_turbulence/{ReaPsi,ImaPsi}.001.dat, the sample field of Zenodo record 5510351
(Polanco, Mueller & Krstulovic; CC BY 4.0; see README.meta there): psi on a 256^3 periodic grid, box L = 2 pi, float64,
column-major.  Conventions of the authors' analysis code (README.meta): c = 1, xi = 1.5 dx.

Computes, and writes to figures/ch15_raw/gp_derived.npz (+ prints a summary):
  * the density-weighted velocity w = sqrt(rho) v = (hbar/m) Im(conj(psi) grad psi)/|psi| (in units of hbar/m = 1: only the SHAPE
    of the spectra is used), its Helmholtz split into incompressible and compressible parts (FFT), and the shell spectra
    E_i(k), E_c(k), plus the quantum-pressure spectrum E_q(k) of (hbar/m) grad sqrt(rho); Parseval is checked;
  * the vortex lines: every grid face (plaquette) around which the phase winds by +-2 pi (sum of principal differences, the
    rule of chapter ch09 and of VortexWinding.pdiff), counted for the three face orientations; line length L ~ (2/3) N_faces dx
    for an isotropic tangle (exercise 2 of the chapter), line density L/V and mean inter-vortex distance ell = (L/V)^(-1/2);
  * the face centres (for the 3D picture) and one density/phase slice.
Run:  .venv/bin/python book/figures/ch15_gp_derive.py   (about one minute; ~3 GB of memory)."""
import json, time, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "data" / "external" / "polanco_2021_gp_turbulence"
OUT = HERE / "ch15_raw"; OUT.mkdir(exist_ok=True)
NG = 256
L = 2 * np.pi
dx = L / NG
xi = 1.5 * dx

t0 = time.time()
re = np.fromfile(SRC / "ReaPsi.001.dat", dtype="<f8").reshape(NG, NG, NG, order="F")
im = np.fromfile(SRC / "ImaPsi.001.dat", dtype="<f8").reshape(NG, NG, NG, order="F")
psi = re + 1j * im
del re, im
rho = np.abs(psi) ** 2
rho0 = float(rho.mean())
print(f"loaded {time.time() - t0:.1f}s  <rho> = {rho0:.6f}  min rho = {rho.min():.3e}  max rho = {rho.max():.4f}", flush=True)

k1 = np.fft.fftfreq(NG, d=dx) * 2 * np.pi            # integers -128..127 for L = 2 pi
KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
KK = np.sqrt(KX ** 2 + KY ** 2 + KZ ** 2)
shell = np.rint(KK).astype(np.int32)
kmax = NG // 2
nsh = int(shell.max()) + 1

def spectrum(fhat_list):
    """shell sum of (1/2)|f_hat|^2 / N^6 (so that the sum over shells is (1/2)<|f|^2>)."""
    s = np.zeros(nsh)
    for fh in fhat_list:
        s += np.bincount(shell.ravel(), weights=(np.abs(fh) ** 2).ravel(), minlength=nsh)
    return 0.5 * s / NG ** 6

psih = np.fft.fftn(psi)
amp = np.abs(psi)
safe = amp > 1e-12
w = []
for Kj in (KX, KY, KZ):
    dpsi = np.fft.ifftn(1j * Kj * psih)
    wj = np.zeros(psi.shape)
    wj[safe] = np.imag(np.conj(psi[safe]) * dpsi[safe]) / amp[safe]
    w.append(wj)
    del dpsi
print(f"w computed {time.time() - t0:.1f}s", flush=True)
mean_w2 = float(sum((wj ** 2).mean() for wj in w))
wh = [np.fft.fftn(wj) for wj in w]
del w
K2 = KK ** 2
K2[0, 0, 0] = 1.0
div = (KX * wh[0] + KY * wh[1] + KZ * wh[2]) / K2
wc = [KX * div, KY * div, KZ * div]
wi = [wh[j] - wc[j] for j in range(3)]
Ei = spectrum(wi)
Ec = spectrum(wc)
del wh, wc, wi, div
parseval = float((Ei.sum() + Ec.sum()) / (0.5 * mean_w2))
# quantum-pressure field (hbar/m) grad sqrt(rho)
ah = np.fft.fftn(amp)
q = [np.real(np.fft.ifftn(1j * Kj * ah)) for Kj in (KX, KY, KZ)]
Eq = spectrum([np.fft.fftn(qj) for qj in q])
del q, ah
print(f"spectra {time.time() - t0:.1f}s  Parseval (Ei+Ec)/(<w^2>/2) = {parseval:.12f}", flush=True)

# ---------------------------------------------------------------- vortex lines: plaquette windings
theta = np.angle(psi)
del psih

def pdiff(a, b):
    d = (b - a + np.pi) % (2 * np.pi) - np.pi
    return np.where(d == -np.pi, np.pi, d)

steps = [pdiff(theta, np.roll(theta, -1, axis=ax)) for ax in range(3)]   # step along axis ax from each grid point
faces = {}
max_step = float(max(np.abs(s).max() for s in steps))
for normal, (a1, a2) in {2: (0, 1), 0: (1, 2), 1: (2, 0)}.items():
    s1, s2 = steps[a1], steps[a2]
    circ = s1 + np.roll(s2, -1, axis=a1) - np.roll(s1, -1, axis=a2) - s2   # counter-clockwise in the (a1, a2) plane
    qf = circ / (2 * np.pi)
    qi = np.rint(qf).astype(np.int8)
    faces[normal] = (qi, float(np.abs(qf - qi).max()))
    del circ, qf
n_faces = {ax: int(np.count_nonzero(faces[ax][0])) for ax in range(3)}
charge_sum = {ax: int(faces[ax][0].astype(np.int64).sum()) for ax in range(3)}
dev_int = max(faces[ax][1] for ax in range(3))
multi = int(sum(np.count_nonzero(np.abs(faces[ax][0]) > 1) for ax in range(3)))
NF = sum(n_faces.values())
Lline = (2.0 / 3.0) * NF * dx
V = L ** 3
ell = (Lline / V) ** -0.5
print(f"faces per normal {n_faces}, total {NF}, |q|>1: {multi}, max |q - round q| = {dev_int:.2e}, net charge per orientation {charge_sum}")
print(f"line length L ~ (2/3) N dx = {Lline:.2f} (bounds N dx/sqrt3 = {NF * dx / np.sqrt(3):.2f}, N dx = {NF * dx:.2f}); "
      f"L/V = {Lline / V:.4f}; ell = {ell:.4f} = {ell / xi:.2f} xi = {ell / dx:.1f} dx", flush=True)

# face centres for the 3D picture: face with normal ax at grid point p is centred at p + (dx/2)(e_a1 + e_a2)
pts = []
for normal, (a1, a2) in {2: (0, 1), 0: (1, 2), 1: (2, 0)}.items():
    idx = np.argwhere(faces[normal][0] != 0).astype(np.float64)
    idx[:, a1] += 0.5
    idx[:, a2] += 0.5
    pts.append(idx * dx)
pts = np.concatenate(pts)

# one slice through the box (z index 128): density and phase
zs = NG // 2
sl_rho = rho[:, :, zs].astype(np.float32)
sl_th = theta[:, :, zs].astype(np.float32)
sl_q = faces[2][0][:, :, zs].copy()

np.savez_compressed(OUT / "gp_derived.npz", k=np.arange(nsh), Ei=Ei, Ec=Ec, Eq=Eq, pts=pts.astype(np.float32),
                    sl_rho=sl_rho, sl_th=sl_th, sl_q=sl_q, zslice=zs)
summary = dict(grid=NG, box="2 pi", dx=dx, xi=xi, xi_over_dx=1.5, rho_mean=rho0, rho_min=float(rho.min()), rho_max=float(rho.max()),
               parseval=parseval, faces_per_normal={"x": n_faces[0], "y": n_faces[1], "z": n_faces[2]}, faces_total=NF,
               faces_multi=multi, max_dev_from_integer=dev_int, net_charge_per_orientation={str(k): v for k, v in charge_sum.items()},
               max_principal_step_over_pi=max_step / np.pi, line_length=Lline, line_length_lo=NF * dx / np.sqrt(3), line_length_hi=NF * dx,
               line_density=Lline / V, ell=ell, ell_over_xi=ell / xi, ell_over_dx=ell / dx,
               E_inc_total=float(Ei.sum()), E_comp_total=float(Ec.sum()), E_q_total=float(Eq.sum()), wall_s=time.time() - t0)
(OUT / "gp_derived.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
