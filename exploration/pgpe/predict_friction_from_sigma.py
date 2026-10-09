"""alpha/T predicted from a transport cross-section sigma_par(k) (PGPE_VORTEX_SCATTERING_PREREG.md, P4).

alpha/T = 1/(rho_s kappa) * 1/(4 pi) * Int_0^{k_c} k^3 c_g(k) sigma(k) / eps_k^2 dk,   eps_k = sqrt(k^2 + k^4/4), c_g = d eps/dk, kappa = 2 pi, c = 1.
    .venv/bin/python exploration/pgpe/predict_friction_from_sigma.py --born          # Born law sigma = kappa^2 k/8   (recorded before the scan)
    .venv/bin/python exploration/pgpe/predict_friction_from_sigma.py --file sigma.json  # {"k": [...], "sigma": [...]} measured points
"""
import argparse, json
import numpy as np

KAPPA = 2 * np.pi


def eps(k): return np.sqrt(k ** 2 + k ** 4 / 4)
def cg(k): return (k + k ** 3 / 2) / eps(k)


def integral(sig, kc, rho_s=0.96, n=20000):
    k = np.linspace(1e-6, kc, n); f = k ** 3 * cg(k) * sig(k) / eps(k) ** 2
    return float(np.trapezoid(f, k) / (4 * np.pi) / (rho_s * KAPPA))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--born", action="store_true"); ap.add_argument("--file"); ap.add_argument("--kmax-meas", type=float, default=2.75)
    a = ap.parse_args()
    if a.born:
        born = lambda k: KAPPA ** 2 * k / 8
        ab = lambda k: 2 / k * np.sin(np.pi * k) ** 2          # exact Aharonov-Bohm transport cross-section of flux gamma = k (c = 1): for orientation only
        for kc in (2.0944, np.pi, 2 * np.pi):
            print(f"k_c = {kc:.3f}:  Born sigma = kappa^2 k/8  -> alpha/T = {integral(born, kc):.3f}   (measured 0.054)   |  AB (2/k) sin^2(pi k) -> {integral(ab, kc):.4f}")
    else:
        d = json.load(open(a.file)); k, s = np.array(d["k"]), np.array(d["sigma"])
        def sig(x, tail=True):
            out = np.interp(x, k, s)
            return np.where(x > k.max(), s[-1] * k.max() / x if tail else 0.0, out)
        for kc in (2.0944, np.pi, 2 * np.pi):
            print(f"k_c = {kc:.3f}: alpha/T = {integral(sig, kc):.4f} (1/k tail), {integral(lambda x: sig(x, False), kc):.4f} (zero tail)")


if __name__ == "__main__":
    main()
