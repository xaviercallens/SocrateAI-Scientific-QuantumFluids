#!/usr/bin/env python3
"""KA-3, numpy side: independent energy and force of the dumped configurations (brute force over images, no
minimum-image shortcut, derivatives coded separately), compared with the Rust values in ka3_configs.json.

    python3 exploration/exciton/python/phase1_crosscheck.py exploration/exciton/results/phase1/ka3_configs.json
"""
import json, sys, math
import numpy as np

def kernel(kid):
    if kid == "K1":
        return (lambda t: np.exp(-t)), (lambda t: -np.exp(-t))
    if kid == "K2":
        return (lambda t: np.exp(-np.sqrt(t)) / np.sqrt(t)), (lambda t: -np.exp(-np.sqrt(t)) * (1 + np.sqrt(t)) / (2 * t ** 1.5))
    if kid == "K3":
        return (lambda t: t ** -1.5 * np.exp(-0.02 * t)), (lambda t: t ** -1.5 * np.exp(-0.02 * t) * (-1.5 / t - 0.02))
    if kid in ("K4", "K6"):
        eps = 0.02 if kid == "K4" else 0.0
        b = lambda t: 2 * (t ** -0.5 - (t + 1) ** -0.5)
        b1 = lambda t: -t ** -1.5 + (t + 1) ** -1.5
        return (lambda t: b(t) * np.exp(-eps * t)), (lambda t: (b1(t) - eps * b(t)) * np.exp(-eps * t))
    if kid == "K5":
        return (lambda t: t ** -1.5), (lambda t: -1.5 * t ** -2.5)
    if kid == "N1":
        return (lambda t: np.exp(-t * t)), (lambda t: -2 * t * np.exp(-t * t))
    raise KeyError(kid)

def energy_force(c):
    g, g1 = kernel(c["kernel"])
    lx, ly, n, rc = c["lx"], c["ly"], c["n"], c["rc"]
    x = np.array(c["x"]).reshape(n, 2)
    M = int(math.ceil(rc / min(lx, ly))) + 1
    ms = np.arange(-M, M + 1)
    MX, MY = np.meshgrid(ms, ms)
    sx = (MX * lx).ravel(); sy = (MY * ly).ravel()
    E = 0.0
    F = np.zeros((n, 2))
    for i in range(n):
        for j in range(n):
            dx = x[i, 0] - x[j, 0] + sx
            dy = x[i, 1] - x[j, 1] + sy
            t = dx * dx + dy * dy
            keep = t <= rc * rc
            if i == j:
                keep &= t > 1e-12                     # exclude the (i, i, 0) term only
            if not keep.any():
                continue
            tk, dxk, dyk = t[keep], dx[keep], dy[keep]
            if i < j:
                E += g(tk).sum()
            if i != j:
                c1 = 2 * g1(tk)
                F[i, 0] -= (c1 * dxk).sum(); F[i, 1] -= (c1 * dyk).sum()
    # self-images: 0.5 * sum_{m != 0} g(|L m|^2) per particle
    tt = sx * sx + sy * sy
    keep = (tt > 1e-12) & (tt <= rc * rc)
    self_const = 0.5 * g(tt[keep]).sum()
    return E / n + self_const + c["tail"], F.ravel()

def main():
    cfgs = json.load(open(sys.argv[1]))
    worst_e = 0.0; worst_f = 0.0; per = {}
    for c in cfgs:
        e, f = energy_force(c)
        er = abs(e - c["e"]) / abs(e)
        fr = np.max(np.abs(f - np.array(c["f"]))) / np.max(np.abs(f))
        worst_e = max(worst_e, er); worst_f = max(worst_f, fr)
        k = c["kernel"]; per[k] = (max(per.get(k, (0, 0))[0], er), max(per.get(k, (0, 0))[1], fr))
    for k, (er, fr) in per.items():
        print(f"{k}: energy rel {er:.2e}   force rel (max-norm) {fr:.2e}")
    ok = bool(worst_e <= 1e-12 and worst_f <= 1e-10)
    print(json.dumps({"KA3_numpy_side": {"worst_energy_rel": float(worst_e), "worst_force_rel": float(worst_f), "pass": ok,
                                         "n_configs": len(cfgs)}}))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
