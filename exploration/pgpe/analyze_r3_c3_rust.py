#!/usr/bin/env python3
"""Post-analysis for round-3 Part C3 (amendment R3-A3), run by the Rust driver
(rusty-SUNDIALS crates/qf-pgpe/examples/round3_finite_size.rs) instead of run_r3.py's Python
integration -- see docs/designs/PGPE_R3_PREREG.md and memory/pgpe-r3-c3-rust-rewrite-after-oom.md
for why.

The Rust driver does the expensive part (stepping) and writes raw field snapshots
(`<name>_sample_t*.raw`, complex128, numpy-loadable) every 10 time units during the observation
window, plus a `<name>_meta.json` with the run's provenance. This script does NOT reimplement the
observable pipeline -- it reuses round2.py/observables.py exactly as run_r3.py did, replaying the
same block-averaging logic (`run_blocks_positions`'s cb()) over the saved snapshots instead of a
live simulation callback.

One data-format subtlety, worth stating plainly: the Rust driver saves `psi = field.psi(c)`
(real-space wavefunction), but every observable function in observables.py operates on `c`
(the PROJECTED FOURIER-SPACE mode array) -- `condensate_fraction` indexes `c[0, 0]` directly.
This script recovers `c` exactly via `s.modes(psi)`, which is lossless: the dynamics always keep
`c` inside the projector's support, so `modes(psi(c)) == c` to floating-point round-off.

Run:  PYTHONPATH=src python3 exploration/pgpe/analyze_r3_c3_rust.py <rust_output_dir> [--names NAME,NAME,...]
Writes data/generated/pgpe/r3/<name>.json, matching run_r3.py's own output format exactly, so the
rest of the pipeline (LEDGER, roadmap decision rules) needs no changes.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from pgpe import PGPE
from round2 import fit_g1_window
from observables import condensate_fraction, current_correlators, dipole_matching, g1_radial, thermometer, vortices
from vortex_thermometer import energy as pv_energy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/generated/pgpe/r3")

SAMPLE_RE = re.compile(r"^(?P<name>.+)_sample_t(?P<t>[0-9]+\.[0-9])\.raw$")


def load_field(path: str, n: int) -> np.ndarray:
    """A raw complex128 file written by the Rust driver, reshaped row-major to (n, n)."""
    flat = np.fromfile(path, dtype=np.complex128)
    if flat.size != n * n:
        raise ValueError(f"{path}: expected {n * n} complex values, got {flat.size}")
    return flat.reshape(n, n)


def find_snapshots(rust_dir: str, name: str) -> list[tuple[float, str]]:
    out = []
    for path in glob.glob(os.path.join(rust_dir, f"{name}_sample_t*.raw")):
        m = SAMPLE_RE.match(os.path.basename(path))
        if m and m.group("name") == name:
            out.append((float(m.group("t")), path))
    out.sort(key=lambda x: x[0])
    return out


def analyze_one(s: PGPE, meta: dict, snapshots: list[tuple[float, str]], seed: int, block: float = 100.0, every_t: float = 10.0):
    """Replays run_blocks_positions' cb() over pre-computed snapshots instead of a live run.
    Returns (blocks, samples), matching that function's own return values exactly."""
    t_tr = meta["t_tr"]
    t_end = meta["t_end"]
    nb = int(round((t_end - t_tr) / block))
    per = int(round(block / every_t))
    if len(snapshots) != nb * per:
        print(
            f"  WARNING: {meta['name']}: expected {nb * per} snapshots ({nb} blocks x {per}), "
            f"found {len(snapshots)}. Run is incomplete or every_t/block mismatch.",
            file=sys.stderr,
        )

    rng = np.random.default_rng(10_000 + seed)
    kk = np.sqrt(s.k2)
    w = s.dx**2 / s.N**2
    blocks = [dict(occ=np.zeros_like(s.k2), g1=None, cond=[], nv=[], Q=[], JL=[], JT=[], E_pv=[], budget=[]) for _ in range(nb)]
    samples = []

    def budget(cc):
        psi = s.psi(cc)
        rho = np.abs(psi) ** 2
        kin_k = 0.5 * s.k2 * np.abs(cc) ** 2 * w
        gx = np.fft.ifft2(1j * s.kx * cc)
        gy = np.fft.ifft2(1j * s.ky * cc)
        jx = (np.conj(psi) * gx).imag
        jy = (np.conj(psi) * gy).imag
        sr = np.sqrt(rho + 1e-30)
        Ux, Uy = np.fft.fft2(jx / sr), np.fft.fft2(jy / sr)
        k2 = np.where(s.k2 == 0, 1, s.k2)
        div = (s.kx * Ux + s.ky * Uy) / k2
        Ic = 0.5 * np.sum(np.abs(s.kx * div) ** 2 + np.abs(s.ky * div) ** 2) * w
        It = 0.5 * np.sum(np.abs(Ux) ** 2 + np.abs(Uy) ** 2) * w
        return {
            "kin_bath": float(kin_k[(kk >= 0.4 * s.kcut) & s.P].sum()),
            "kin_lowk": float(kin_k[(kk < 0.4 * s.kcut)].sum()),
            "E_inc": float(It - Ic),
            "E_comp": float(Ic),
            "interaction": float(0.5 * s.g * np.sum(rho**2) * s.dx**2),
        }

    for i, (t_sim, path) in enumerate(snapshots):
        psi = load_field(path, s.N)
        cc = s.modes(psi)
        b = blocks[min(i // per, nb - 1)]
        b["occ"] += np.abs(cc) ** 2 * w
        r, g = g1_radial(s, cc)
        b["g1"] = g if b["g1"] is None else b["g1"] + g
        b["r"] = r
        b["cond"].append(condensate_fraction(s, cc))
        pos, q = vortices(s, cc)
        b["nv"].append(len(q))
        b["Q"].append(dipole_matching(s, pos, q, rng)[2])
        neutral = len(q) >= 4 and (q > 0).sum() == (q < 0).sum()
        b["E_pv"].append(pv_energy(pos, q, s.L) if neutral else float("nan"))
        cr = current_correlators(s, cc)
        b["JL"].append(np.mean([v[0] for v in cr.values()]))
        b["JT"].append(np.mean([v[1] for v in cr.values()]))
        bud = budget(cc)
        b["budget"].append(bud)
        samples.append({"t": t_sim, "pos": pos.tolist(), "q": q.tolist(), "E_pv": b["E_pv"][-1], **bud})

    out = []
    for i, b in enumerate(blocks):
        n = len(b["cond"])
        if n == 0:
            continue
        occ = b["occ"] / n
        g = b["g1"] / n
        T = thermometer(s, occ, 0.6, 1.0)[0]
        fit = fit_g1_window(b["r"], g, s.L)
        Epv = np.array(b["E_pv"])
        nv = np.array(b["nv"])
        keys = b["budget"][0].keys()
        out.append(
            {
                "t0": t_tr + i * block,
                "T": T,
                "cond": float(np.mean(b["cond"])),
                "n_v": float(nv.mean()),
                "Q": float(np.nanmean(b["Q"])) if np.any(np.isfinite(b["Q"])) else float("nan"),
                "JL": float(np.mean(b["JL"])),
                "JT": float(np.mean(b["JT"])),
                "eta": fit["eta"],
                "law": fit["law"],
                "E_pv_mean": float(np.nanmean(Epv)) if np.any(np.isfinite(Epv)) else float("nan"),
                "N_mode": int(np.round(np.median(nv[np.isfinite(Epv)]))) if np.any(np.isfinite(Epv)) else 0,
                **{k2: float(np.mean([bb[k2] for bb in b["budget"]])) for k2 in keys},
            }
        )
    return out, samples


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rust_dir", help="directory the Rust driver wrote snapshots/meta.json into")
    ap.add_argument("--names", default=None, help="comma-separated config names; default: all *_meta.json found")
    ap.add_argument("--block", type=float, default=100.0, help="block size in time units (default matches run_r3.py)")
    ap.add_argument("--out-dir", default=OUT, help="where to write <name>.json / <name>_samples.npz (default: the real r3 output dir)")
    a = ap.parse_args()

    if a.names:
        names = a.names.split(",")
    else:
        names = sorted(
            os.path.basename(p)[: -len("_meta.json")] for p in glob.glob(os.path.join(a.rust_dir, "*_meta.json"))
        )
    if not names:
        print(f"no *_meta.json found in {a.rust_dir}", file=sys.stderr)
        return 2

    os.makedirs(a.out_dir, exist_ok=True)
    for name in names:
        t0 = time.time()
        meta_path = os.path.join(a.rust_dir, f"{name}_meta.json")
        if not os.path.exists(meta_path):
            print(f"SKIP {name}: no {meta_path}", file=sys.stderr)
            continue
        meta = json.load(open(meta_path))
        snapshots = find_snapshots(a.rust_dir, name)
        if not snapshots:
            print(f"SKIP {name}: no snapshots found in {a.rust_dir}", file=sys.stderr)
            continue

        s = PGPE(N=meta["N"], L=meta["L"], g=meta["g"], dt=meta["dt"])
        blocks, samples = analyze_one(s, meta, snapshots, seed=meta["seed"], block=a.block, every_t=meta["snapshot_every_t"])

        # E_per_particle: energy_initial (from the Rust meta) over the norm of the LAST snapshot's
        # recovered Fourier state -- norm is conserved by this model to the same tolerance energy
        # is (see qf-pgpe's own tests), so this matches what run_r3.py itself computed
        # (E0 / s.norm(c) where c was already the post-run final state by the time it was called).
        last_psi = load_field(snapshots[-1][1], s.N)
        last_cc = s.modes(last_psi)
        norm_final = s.norm(last_cc)

        res = {
            "kind": "C3",
            "e": meta["e_target"],
            "seed": meta["seed"],
            "name": name,
            "E_per_particle": meta["energy_initial"] / norm_final,
            "drift_E": meta["drift_E"],
            "L": meta["L"],
            "blocks": blocks,
            "seconds": meta["wall_seconds"],
            "rust_steps": meta["steps"],
            "analysis_seconds": None,  # filled below
        }
        res["analysis_seconds"] = round(time.time() - t0, 1)

        out_path = os.path.join(a.out_dir, f"{name}.json")
        with open(out_path, "w") as f:
            json.dump(res, f, indent=1, default=float)
        np.savez_compressed(
            os.path.join(a.out_dir, f"{name}_samples.npz"),
            t=np.array([x["t"] for x in samples]),
            pos=np.array([np.array(x["pos"], dtype=float) for x in samples], dtype=object),
            q=np.array([np.array(x["q"], dtype=int) for x in samples], dtype=object),
            E_pv=np.array([x["E_pv"] for x in samples]),
            kin_bath=np.array([x["kin_bath"] for x in samples]),
            E_inc=np.array([x["E_inc"] for x in samples]),
            E_comp=np.array([x["E_comp"] for x in samples]),
        )
        b1, bl = blocks[0], blocks[-1]
        print(
            f"{name}: {len(snapshots)} snapshots -> {len(blocks)} blocks. "
            f"T_b {b1['T']:.3f}->{bl['T']:.3f} cond {b1['cond']:.3f}->{bl['cond']:.3f} "
            f"n_v {b1['n_v']:.1f}->{bl['n_v']:.1f} E_inc {b1['E_inc']:.1f}->{bl['E_inc']:.1f} "
            f"[{res['analysis_seconds']:.1f}s]",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
