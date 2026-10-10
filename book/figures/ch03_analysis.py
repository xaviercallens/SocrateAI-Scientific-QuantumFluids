"""Chapter 3: analysis of Gross-Pitaevskii snapshots (fields of qf_pgpe).  Units hbar = m = g = n0 = 1, kappa = 2 pi.
Everything here reads a field c (projected Fourier amplitudes, numpy fft2 convention) and the tracked vortex positions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_lib import *          # noqa: F401,F403  (make, kvec, Evaluator, pdiff, circle_points, loop_winding, loop_circulation, ...)
import ch03_pv as PV


def refine(c, factor=4):
    """Exact spectral refinement of the band-limited field: zero-pad the modes and invert on a `factor` times finer grid.
    Returns (psi_fine, C_padded, k1_fine, dx_fine)."""
    n = c.shape[0]; nf = n * factor; h = n // 2
    C = np.zeros((nf, nf), complex)
    idx = np.r_[0:h, nf - h:nf]
    C[np.ix_(idx, idx)] = c
    dxf = L / nf
    k1 = 2 * np.pi * np.fft.fftfreq(nf, d=dxf)
    return np.fft.ifft2(C) * factor ** 2, C, k1, dxf


def madelung_fields(c, factor=4):
    """psi, density n, Madelung velocity u = Im(conj(psi) grad psi)/n, and the three energy densities
    (kinetic 1/2|grad psi|^2, quantum pressure 1/2|grad sqrt n|^2, flow 1/2 n|u|^2) on the refined grid."""
    psi, C, k1, dxf = refine(c, factor)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    f2 = factor ** 2
    px = np.fft.ifft2(1j * KX * C) * f2; py = np.fft.ifft2(1j * KY * C) * f2
    n = np.abs(psi) ** 2
    jx = np.imag(np.conj(psi) * px); jy = np.imag(np.conj(psi) * py)         # n u
    ax = np.real(np.conj(psi) * px); ay = np.real(np.conj(psi) * py)         # sqrt(n) grad sqrt(n) = grad n / 2
    nn = np.maximum(n, 1e-300)
    kin = 0.5 * (np.abs(px) ** 2 + np.abs(py) ** 2)
    q = 0.5 * (ax ** 2 + ay ** 2) / nn
    fl = 0.5 * (jx ** 2 + jy ** 2) / nn
    return dict(psi=psi, n=n, ux=jx / nn, uy=jy / nn, kin=kin, q=q, flow=fl, dx=dxf, k1=k1)


def energy_split(c, factor=4):
    """Integrals of the three densities on the coarse grid (factor 1) and on the refined grid, and the pointwise identity error."""
    out = {}
    for f in (1, factor):
        F = madelung_fields(c, f)
        d2 = F["dx"] ** 2
        out[f"x{f}"] = dict(E_kin=float(F["kin"].sum() * d2), E_q=float(F["q"].sum() * d2), E_flow=float(F["flow"].sum() * d2),
                            pointwise_max=float(np.max(np.abs(F["kin"] - F["q"] - F["flow"])) / np.max(F["kin"])))
    s = make()
    kx, ky = kvec(s)
    out["E_kin_parseval"] = float(np.sum(0.5 * (kx ** 2 + ky ** 2) * np.abs(c) ** 2) * s.dx ** 2 / s.n ** 2)
    out["E_gp_total"] = float(s.energy(c))
    out["E_int"] = float(0.5 * np.sum(np.abs(np.fft.ifft2(c)) ** 4) * s.dx ** 2)
    return out


def torus_windings(c):
    """Winding (in units of 2 pi) of the phase along every grid row (x direction) and every grid column (y direction):
    sums of principal differences around the two cycles of the torus."""
    th = np.angle(np.fft.ifft2(c))
    wx = pdiff(th, np.roll(th, -1, 0)).sum(0) / (2 * np.pi)            # one value per y index j
    wy = pdiff(th, np.roll(th, -1, 1)).sum(1) / (2 * np.pi)            # one value per x index i
    return wx, wy


def grid_phase_steps(c):
    """All principal phase differences over the grid edges: max |step| (in units of pi) and the plaquette charges."""
    psi = np.fft.ifft2(c)
    charges, w, dx_, dy_ = plaquette_charges(psi)
    return dict(max_step_over_pi=float(max(np.abs(dx_).max(), np.abs(dy_).max()) / np.pi),
                n_plus=int((charges == 1).sum()), n_minus=int((charges == -1).sum()), n_other=int((np.abs(charges) > 1).sum()),
                max_dev_from_integer=float(np.abs(w - np.rint(w)).max()))


def circulation_scan(c, centre, radii, M=1600):
    """Line-integral circulation Gamma/kappa and discrete winding (Lean detector) on circles of the given radii about `centre`."""
    s = make(); ev = Evaluator(s, c)
    gam = np.zeros(len(radii)); win = np.zeros(len(radii)); pmin = np.zeros(len(radii)); smax = np.zeros(len(radii))
    for i, r in enumerate(radii):
        gam[i] = loop_circulation(ev, centre[0], centre[1], r, M) / KAPPA
        w, pm, sm = loop_winding(ev, centre[0], centre[1], r, M)
        win[i] = w; pmin[i] = pm; smax[i] = sm / np.pi
    return gam, win, pmin, smax


def n0_scan(c, centre, r, M_list, Mmax=7200, phi0=0.0, degree_expected=None):
    """Smallest uniform sampling M0 such that the detected winding of the circle (radius r about `centre`, first sample at angle `phi0`)
    is the degree for EVERY M in M_list with M >= M0 (M_list must divide Mmax; the finest sampling defines the degree unless given).
    Returns (degree, M0, winding per M)."""
    s = make(); ev = Evaluator(s, c)
    x, y, t = circle_points(centre[0], centre[1], r, Mmax, phase0=phi0)
    th = np.angle(ev.psi(x, y))
    wins = []
    for M in M_list:
        sub = th[:: Mmax // M]
        wins.append(pdiff(sub, np.roll(sub, -1)).sum() / (2 * np.pi))
    degree = float(np.rint(wins[-1])) if degree_expected is None else float(degree_expected)
    ok = np.isclose(wins, degree, atol=1e-9)
    M0 = None
    for i in range(len(M_list) - 1, -1, -1):
        if ok[i]: M0 = M_list[i]
        else: break
    return degree, M0, np.array(wins)


def radial_cumulative(F, centre, edges):
    """Cumulative integrals of the energy densities and of the mass defect over the disks r < R about `centre` (periodic distance)."""
    n_ = F["n"].shape[0]; dxf = F["dx"]
    x = np.arange(n_) * dxf
    X, Y = np.meshgrid(x, x, indexing="ij")
    dxv = X - centre[0]; dyv = Y - centre[1]
    dxv -= L * np.round(dxv / L); dyv -= L * np.round(dyv / L)
    r = np.hypot(dxv, dyv).ravel()
    out = {}
    for key in ("kin", "q", "flow"):
        w = (F[key] * dxf ** 2).ravel()
        h, _ = np.histogram(r, bins=edges, weights=w)
        out[key] = np.cumsum(h)
    h, _ = np.histogram(r, bins=edges, weights=((1.0 - F["n"]) * dxf ** 2).ravel())
    out["deficit"] = np.cumsum(h)
    return out


def gp_rhs_modes(c):
    """dc/dt of the projected GP equation, exactly the right-hand side the engine integrates: -i [ (k^2/2) c + P fft2(|psi|^2 psi) ]."""
    s = make(); kx, ky = kvec(s); k2 = kx ** 2 + ky ** 2
    P = (np.sqrt(k2) <= s.kcut)
    psi = np.fft.ifft2(c)
    return -1j * (0.5 * k2 * c * P + P * np.fft.fft2(np.abs(psi) ** 2 * psi))


def madelung_dynamics(c, centres, factor=4):
    """Test of Madelung's equations on one snapshot, using d(psi)/dt from the engine's own right-hand side (no time stepping, no tracking).
    (i) continuity:  d_t n + div(n u) = 0, with  d_t n = 2 Re(conj(psi) psi_t)  and  div(n u) = Im(conj(psi) lap psi);
        for the projected equation the residual is  Im(conj(psi) P[n psi]) , the high-wavenumber part removed by the projector.
    (ii) rigid translation: least-squares fit of  psi_t = -(v . grad psi) - i mu psi  gives the velocity v of the whole pattern.
    `centres` are the vortex positions; regions are defined by the periodic distance to the nearest core."""
    psi, C, k1, dxf = refine(c, factor)
    cdot = gp_rhs_modes(c)
    psit, Ct, _, _ = refine(cdot, factor)
    KX, KY = np.meshgrid(k1, k1, indexing="ij"); f2 = factor ** 2
    px = np.fft.ifft2(1j * KX * C) * f2; py = np.fft.ifft2(1j * KY * C) * f2
    lap = np.fft.ifft2(-(KX ** 2 + KY ** 2) * C) * f2
    nt = 2 * np.real(np.conj(psi) * psit)
    divj = np.imag(np.conj(psi) * lap)
    res = nt + divj
    # the residual is the projector term: res = -2 Im( conj(psi) (1 - P)[n psi] )   (an identity of the projected equation, checked here)
    sm = make()
    G = np.fft.fft2(np.abs(psi) ** 2 * psi)
    hp = np.fft.ifft2((np.sqrt(KX ** 2 + KY ** 2) > sm.kcut) * G)
    pred = -2 * np.imag(np.conj(psi) * hp)
    nf = psi.shape[0]; x = np.arange(nf) * dxf
    X, Y = np.meshgrid(x, x, indexing="ij")
    rmin = np.full(X.shape, 1e9)
    for (cx, cy) in centres:
        dx_ = X - cx; dy_ = Y - cy; dx_ -= L * np.round(dx_ / L); dy_ -= L * np.round(dy_ / L)
        rmin = np.minimum(rmin, np.hypot(dx_, dy_))
    out = {}
    for rlo in (1.5, 3.0):
        m = rmin >= rlo
        out[f"continuity_rel_rms_r_ge_{rlo:g}"] = float(np.sqrt((res[m] ** 2).sum() / (nt[m] ** 2).sum()))
        out[f"continuity_max_over_max_nt_r_ge_{rlo:g}"] = float(np.abs(res[m]).max() / np.abs(nt[m]).max())
    out["max_abs_nt"] = float(np.abs(nt).max()); out["max_abs_divj"] = float(np.abs(divj).max())
    out["max_abs_residual"] = float(np.abs(res).max()); out["projector_identity_max_abs_diff"] = float(np.abs(res - pred).max())
    # rigid-translation fit
    for rlo in (2.5, 4.0):
        m = (rmin >= rlo).ravel()
        cols = [(-px).ravel()[m], (-py).ravel()[m], (-1j * psi).ravel()[m]]
        A = np.column_stack([np.concatenate([col.real, col.imag]) for col in cols])
        b = np.concatenate([psit.ravel()[m].real, psit.ravel()[m].imag])
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        resid = A @ sol - b
        out[f"pattern_velocity_fit_r_ge_{rlo:g}"] = dict(vx=float(sol[0]), vy=float(sol[1]), mu=float(sol[2]), speed=float(np.hypot(sol[0], sol[1])),
                                                         rel_residual=float(np.sqrt((resid ** 2).sum() / (b ** 2).sum())))
    return out


def longitudinal_fraction(dux, duy, mask, dx):
    """Fraction of the energy of the (masked) periodic vector field (dux, duy) that is curl-free (compressible, 'sound'), by the
    Helmholtz split in Fourier space; the field is set to zero where mask is False."""
    n2 = dux.shape[0]
    k1 = 2 * np.pi * np.fft.fftfreq(n2, d=dx)
    KX, KY = np.meshgrid(k1, k1, indexing="ij"); K2 = KX ** 2 + KY ** 2; K2[0, 0] = 1.0
    fx = np.fft.fft2(np.where(mask, dux, 0.0)); fy = np.fft.fft2(np.where(mask, duy, 0.0))
    dh = (KX * fx + KY * fy) / K2
    El = (np.abs(KX * dh) ** 2 + np.abs(KY * dh) ** 2).sum(); Et = (np.abs(fx - KX * dh) ** 2 + np.abs(fy - KY * dh) ** 2).sum()
    return float(El / (El + Et))
