"""Thermal base states at other cutoffs for the friction-law campaign (PGPE_FRICTION_LAW_PREREG.md).

Route: the equilibrated vortex-free L = 64 state (sweep/e0.60_s11_t4000, N = 128, k_cut = pi) is re-projected under the new
cutoff (and Fourier-resampled to N = 256 for dx = xi/4), heated to a target energy per particle by round2.heat, then
evolved t_tr time units (new modes thermalise) and measured over the remaining window (T, n_s/n, raw vortex count).

    .venv/bin/python exploration/pgpe/make_friction_bases.py --kcut-frac 0.3333 --N 128 --e 0.56 --t-end 1500 --t-tr 1000
    .venv/bin/python exploration/pgpe/make_friction_bases.py --kcut-frac 0.5    --N 256 --e 1.10 --t-end 2500 --t-tr 2000
-> data/generated/pgpe/transport/fl/base_k{kcut:.3f}_N{N}_e{e:.2f}.{json,npy}
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pgpe import PGPE
from round2 import heat, run_blocks

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "data/generated/pgpe/transport/fl"


def resample(psi: np.ndarray, N: int) -> np.ndarray:
    """Fourier zero-padding / truncation of a periodic field from its grid to N x N (same box)."""
    n = psi.shape[0]
    if n == N:
        return psi
    F = np.fft.fftshift(np.fft.fft2(psi)); G = np.zeros((N, N), complex)
    if N > n:
        o = (N - n) // 2; G[o:o + n, o:o + n] = F
    else:
        o = (n - N) // 2; G = F[o:o + N, o:o + N]
    return np.fft.ifft2(np.fft.ifftshift(G)) * (N / n) ** 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kcut-frac", type=float, required=True); ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--e", type=float, required=True); ap.add_argument("--t-end", type=float, default=1500.0)
    ap.add_argument("--t-tr", type=float, default=1000.0); ap.add_argument("--L", type=float, default=64.0)
    ap.add_argument("--base", default=str(ROOT / "data/generated/pgpe/sweep/e0.60_s11_t4000_final.npy"))
    a = ap.parse_args(); t0 = time.time()
    s0 = PGPE(N=128, L=a.L); c0 = np.load(a.base)
    s = PGPE(N=a.N, L=a.L, kcut_frac=a.kcut_frac)
    c = s.modes(resample(s0.psi(c0), a.N))                       # re-projected (and resampled) start, norm preserved up to the projector
    c *= np.sqrt(s0.norm(c0) / s.norm(c))
    e_start = s.energy(c) / s.norm(c)
    rng = np.random.default_rng(int(round(1000 * a.e)) + a.N)
    c = heat(s, c, a.e * s.norm(c), rng)
    E0 = s.energy(c); c, blocks, whole = run_blocks(s, c, a.t_end, a.t_tr, seed=int(round(100 * a.e)) + a.N)
    res = {"kcut_frac": a.kcut_frac, "kcut": float(s.kcut), "N": a.N, "L": a.L, "dx": a.L / a.N, "e": a.e, "e_start_after_projection": e_start,
           "E_per_particle": E0 / s.norm(c), "drift_E": abs(s.energy(c) - E0) / E0, "t_end": a.t_end, "t_tr": a.t_tr, "blocks": blocks, "whole": whole,
           "T": whole["T"], "ns_over_n": whole["ns_over_n"], "n_v": whole["n_v"], "admitted": bool(whole["n_v"] < 0.5), "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True); tag = f"base_k{s.kcut:.3f}_N{a.N}_e{a.e:.2f}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1, default=float)); np.save(OUT / f"{tag}_final.npy", c)
    print(f"{tag}: T = {whole['T']:.4f}, n_s/n = {whole['ns_over_n']:.4f}, raw n_v = {whole['n_v']:.2f}, e_start {e_start:.3f}, drift {res['drift_E']:.1e}, {res['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
