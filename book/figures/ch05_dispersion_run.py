"""Chapter 5, heavy computation: the Bogoliubov dispersion measured on the projected GPE of the Rust engine `qf_pgpe`.

Run (shared machine: take the heavy-job lock; load was 10-36 while this was written):
    cd book && flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice env PYTHONPATH=/mnt/data/xdev-cache/qf_ext \
        OMP_NUM_THREADS=1 ../.venv/bin/python figures/ch05_dispersion_run.py            # full
    ... figures/ch05_dispersion_run.py --quick                                          # smoke test, ~1 min

Runs (all hbar = m = n0 = 1, sharp circular cutoff k_cut = k_max/2, integrating-factor RK4):
  R1  main      N = 128, L = 64, g = 1, dt = 0.02, T = 300, sample every 0.4   (3208 modes fitted at once)
  R2  g = 2     N = 64,  L = 32, g = 2, dt = 0.02, T = 300                     (universality: c = sqrt 2)
  R3  ladder    N = 64,  L = 32, g = 1, dt in {0.04, 0.02, 0.01, 0.005}, T = 150, same initial pulse in all four
  R4  amplitude N = 64,  L = 32, g = 1, one mode (m,0), eps in {0.01, 0.1, 0.3}, T = 100 (nonlinear frequency shift)
Every pulse run starts from  psi = 1 + weak random amplitude eta*xi_k on every retained mode (eta = 1e-6).
Outputs: book/figures/ch05_results.npz (compact), book/figures/ch05_run_log.json, big series under
/mnt/data/xdev-cache/book_ch05/.
"""
import sys, json, time
from pathlib import Path
import numpy as np
import qf_pgpe

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ch05_common import *

BIG = Path("/mnt/data/xdev-cache/book_ch05"); BIG.mkdir(exist_ok=True)
QUICK = "--quick" in sys.argv
LOG = {"quick": QUICK, "machine_note": "shared 8-core machine, load average 10-36 during the runs"}
RES = {}


def pulse_run(tag, N, L, g, dt, T, dts, eta, seed, keep_lab=None, save_series=False):
    t_start = time.time()
    eng = qf_pgpe.Pgpe(N, L, g, dt, 0.5)
    c0, mask = initial_pulse(eng, N, eta, seed)
    ns = int(round(T / dts)) + 1
    t = np.arange(ns) * dts
    S, lab = record_condensate_frame(lambda c: eng.run(c, dts), c0, mask, ns, N, keep_lab=keep_lab)
    t_run = time.time() - t_start
    kx, ky = wavevectors(N, L)
    k = np.sqrt(kx ** 2 + ky ** 2)[mask]
    ix, iy = np.nonzero(mask)
    keep = k > 0
    t_fit0 = time.time()
    fit = fit_all(t, S[:, keep], split=True)
    t_fit = time.time() - t_fit0
    kk = k[keep]
    wb = bog(kk, g)
    dev = fit["omega"] / wb - 1.0
    half = np.abs(fit["omega_first"] - fit["omega_second"]) / wb
    info = dict(tag=tag, N=N, L=L, g=g, c=float(np.sqrt(g)), dt=dt, T=T, dts=dts, eta=eta, seed=seed,
                n_modes_fitted=int(keep.sum()), n_samples=int(ns), kcut=float(eng.kcut),
                seconds_run=round(t_run, 1), seconds_fit=round(t_fit, 1),
                median_abs_dev=float(np.median(np.abs(dev))), max_abs_dev=float(np.abs(dev).max()),
                p99_abs_dev=float(np.quantile(np.abs(dev), 0.99)),
                median_split=float(np.median(half)), max_split=float(half.max()),
                max_rel_resid=float(fit["rel_resid"].max()), median_rel_resid=float(np.median(fit["rel_resid"])))
    # the same statistics for k above 0.3 (the two lowest shells have only 3-5 periods in the record)
    sel = kk > 0.3
    info.update(median_abs_dev_k_gt_0p3=float(np.median(np.abs(dev[sel]))), max_abs_dev_k_gt_0p3=float(np.abs(dev[sel]).max()),
                n_modes_k_gt_0p3=int(sel.sum()))
    # energy / norm drift of the engine over the run is not needed here (checked in chapter 2 / the software paper)
    print(tag, json.dumps({k_: v for k_, v in info.items() if k_ not in ("tag",)}), flush=True)
    LOG[tag] = info
    for key, val in dict(k=kk, mx=ix[keep], my=iy[keep], omega=fit["omega"], omega_first=fit["omega_first"],
                         omega_second=fit["omega_second"], rel_resid=fit["rel_resid"],
                         beta_over_alpha=fit["beta_over_alpha"], omega_prony=fit["omega_prony"]).items():
        RES[f"{tag}_{key}"] = np.asarray(val)
    if save_series:
        np.savez_compressed(BIG / f"series_{tag}.npz", t=t, S=S[:, keep].astype(np.complex64), k=kk,
                            mx=ix[keep], my=iy[keep])
    return dict(t=t, S=S, lab=lab, keep=keep, k=k, mask=mask, eng=eng, fit=fit, info=info)


def sqw_map(t, S, k, nkbins, w_max, nw=360):
    """Spectral-intensity map from the pulse record: for every mode the power spectrum of the Hann-windowed complex
    series (frequencies +-w are both folded onto w > 0), averaged over the modes in each |k| bin and normalised bin by bin
    (the intensity along the ridge is set by our random pulse, NOT by physics; only the ridge position is physical)."""
    n = S.shape[0]
    dt = t[1] - t[0]
    win = np.hanning(n)[:, None]
    pad = 4 * n
    F = np.fft.fft(S * win, n=pad, axis=0)
    P = np.abs(F) ** 2
    fr = 2 * np.pi * np.fft.fftfreq(pad, d=dt)
    # fold: power at +w plus power at -w
    idx_pos = np.nonzero(fr > 0)[0]
    idx_neg = (-idx_pos) % pad
    Pfold = P[idx_pos] + P[idx_neg]
    wf = fr[idx_pos]
    wgrid = np.linspace(0.0, w_max, nw)
    kb = np.linspace(0.0, k.max() + 1e-9, nkbins + 1)
    M = np.zeros((nkbins, nw))
    for b in range(nkbins):
        sel = (k >= kb[b]) & (k < kb[b + 1])
        if not np.any(sel):
            continue
        spec = Pfold[:, sel].mean(axis=1)
        M[b] = np.interp(wgrid, wf, spec)
        m = M[b].max()
        if m > 0:
            M[b] /= m
    return M.astype(np.float32), kb, wgrid


if __name__ == "__main__":
    t_all = time.time()
    if QUICK:
        cfg = dict(R1=(32, 16.0, 1.0, 0.02, 40.0), R2=(16, 8.0, 2.0, 0.02, 40.0), R3_T=20.0, R4_T=20.0)
    else:
        cfg = dict(R1=(128, 64.0, 1.0, 0.02, 300.0), R2=(64, 32.0, 2.0, 0.02, 300.0), R3_T=150.0, R4_T=100.0)
    dts = 0.4
    eta = 1e-6

    # ---- R1: the main broadband run --------------------------------------------------------------------------
    N, L, g, dt, T = cfg["R1"]
    lab_idx = (N // 8, 0)                                       # k = 2 pi (N/8)/L = pi/4 ... for N=128, L=64: 0.785
    r1 = pulse_run("R1", N, L, g, dt, T, dts, eta, seed=1, keep_lab=lab_idx, save_series=True)
    M, kb, wgrid = sqw_map(r1["t"], r1["S"][:, r1["keep"]], r1["k"][r1["keep"]], nkbins=int(N / 4 if not QUICK else 8),
                           w_max=6.2)
    RES["R1_map"] = M; RES["R1_map_kbins"] = kb; RES["R1_map_w"] = wgrid
    # the lesson of the pre-registered known answer K5: the lab-frame amplitude of one mode oscillates at mu +- omega
    t = r1["t"]; lab = r1["lab"]
    pad = 16 * len(t)
    F = np.abs(np.fft.fft(lab - lab.mean(), n=pad))
    fr = 2 * np.pi * np.fft.fftfreq(pad, d=t[1] - t[0])
    order = np.argsort(F)[::-1]
    peaks = []
    for i in order:
        if all(abs(fr[i] - p) > 0.15 for p in peaks):
            peaks.append(float(fr[i]))
        if len(peaks) == 2:
            break
    kmode = float(2 * np.pi * lab_idx[0] / L)
    LOG["R1_lab_frame"] = dict(mode=list(lab_idx), k=kmode, omega_bog=float(bog(kmode, g)), lab_frame_peaks_rad_per_t=peaks,
                               expected_minus_mu_pm_omega=[float(-(g) - bog(kmode, g)), float(-(g) + bog(kmode, g))])
    RES["R1_lab_t"] = t; RES["R1_lab_re"] = lab.real; RES["R1_lab_im"] = lab.imag
    print("lab-frame peaks", peaks, "expected", LOG["R1_lab_frame"]["expected_minus_mu_pm_omega"], flush=True)
    del r1

    # ---- R2: g = 2 -------------------------------------------------------------------------------------------
    N, L, g, dt, T = cfg["R2"]
    r2 = pulse_run("R2", N, L, g, dt, T, dts, eta, seed=2)
    del r2

    # ---- R3: time-step ladder (same pulse) ---------------------------------------------------------------------
    for dt in (0.04, 0.02, 0.01, 0.005):
        r3 = pulse_run(f"R3_dt{dt}", 64 if not QUICK else 16, 32.0 if not QUICK else 8.0, 1.0, dt, cfg["R3_T"], dts, eta, seed=3,
                       save_series=(dt == 0.01))
        del r3

    # ---- R4: finite amplitude, single mode (m, 0) -------------------------------------------------------------
    N, L = (64, 32.0) if not QUICK else (16, 8.0)
    R4 = {}
    for m in ((2, 8) if not QUICK else (1, 2)):
        for eps in (0.01, 0.1, 0.3):
            eng = qf_pgpe.Pgpe(N, L, 1.0, 0.02, 0.5)
            x = np.arange(N) * (L / N)
            X, Y = np.meshgrid(x, x, indexing="ij")
            kx_ = 2 * np.pi * m / L
            psi0 = (1.0 + eps * np.cos(kx_ * X)).astype(complex)
            c0 = np.ascontiguousarray(eng.modes(psi0))
            mask = mode_set(eng, N)
            ns = int(round(cfg["R4_T"] / 0.2)) + 1
            t = np.arange(ns) * 0.2
            S, _ = record_condensate_frame(lambda c: eng.run(c, 0.2), c0, mask, ns, N)
            ix, iy = np.nonzero(mask)
            col = int(np.nonzero((ix == m) & (iy == 0))[0][0])
            w, rel, ratio = fit_columns(t, S[:, [col]])
            R4[f"m{m}_eps{eps}"] = dict(k=float(kx_), eps=eps, omega=float(w[0]), omega_bog=float(bog(kx_, 1.0)),
                                       rel_shift=float(w[0] / bog(kx_, 1.0) - 1.0), rel_resid=float(rel[0]))
            print("R4", m, eps, R4[f"m{m}_eps{eps}"], flush=True)
    LOG["R4"] = R4
    LOG["wall_seconds_total"] = round(time.time() - t_all, 1)
    out = HERE / ("ch05_results_quick.npz" if QUICK else "ch05_results.npz")
    np.savez_compressed(out, **RES)
    (HERE / ("ch05_run_log_quick.json" if QUICK else "ch05_run_log.json")).write_text(json.dumps(LOG, indent=1))
    print("wrote", out, "total", LOG["wall_seconds_total"], "s")
