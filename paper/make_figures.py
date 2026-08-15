#!/usr/bin/env python3
"""Generate the paper's figures from the repository's own recorded data."""
import sys, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from quantumfluids.w4_shell_model.shell_dynamics import (
    k_shells, nonlinear_conj, nonlinear_real, rhs, enstrophy_sum)
from quantumfluids.w4_shell_model.integrate import integrate, make_profile

OUT = os.path.join(os.path.dirname(__file__), "figures")
plt.rcParams.update({"font.size": 9, "figure.dpi": 200,
                     "axes.grid": True, "grid.alpha": 0.3})

# ---------------------------------------------------------------- Fig 1
def fig_liouville():
    """Phase-space divergence: real model contracts, complexified does not."""
    def realify(v): return np.concatenate([v.real, v.imag])
    def complexify(s):
        m = len(s)//2; return s[:m] + 1j*s[m:]
    def trace_jac(f, s, h=1e-6):
        tr = 0.0
        for i in range(len(s)):
            sp = s.copy(); sp[i] += h; sm = s.copy(); sm[i] -= h
            tr += (f(sp)[i] - f(sm)[i])/(2*h)
        return tr
    N = 6; k = k_shells(N); rng = np.random.default_rng(5)
    cx, rl = [], []
    for _ in range(40):
        s = realify(rng.normal(size=N+1) + 1j*rng.normal(size=N+1))
        cx.append(abs(trace_jac(lambda z: realify(rhs(complexify(z), k, 0.0, 0.03)), s)))
        a = rng.normal(size=N+1)
        rl.append(abs(trace_jac(lambda z: nonlinear_real(z, k), a)))
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ax.semilogy(rl, "o", ms=3.5, color="#C44E52", label=r"real Katz--Pavlovi\'c")
    ax.semilogy(np.maximum(cx, 1e-16), "s", ms=3.5, color="#4C72B0",
                label=r"conjugated complexification")
    ax.axhline(1e-8, color="k", ls=":", lw=0.8)
    ax.text(0.5, 1.6e-8, "numerical zero", fontsize=7)
    ax.set_xlabel("random state index"); ax.set_ylabel(r"$|\mathrm{div}\,F|$")
    ax.set_ylim(1e-12, 1e3); ax.legend(fontsize=7.5, loc="center right")
    ax.set_title("Phase-space divergence (N=6)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{OUT}/liouville.pdf"); plt.close(fig)
    print("  liouville.pdf")

# ---------------------------------------------------------------- Fig 2
def fig_degeneracy():
    """sup_t Omega climbs to the k_N^2 E ceiling for conservative regulators."""
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    Ts = [2, 4, 8, 16]
    for N, c in [(4, "#4C72B0"), (5, "#55A868")]:
        sups = [integrate(N=N, nu=0.0, D=0.0, profile="P3",
                          t_horizon=float(T), dt=3e-3).sup_enstrophy_sum for T in Ts]
        ceil = (2.0**N)**2 * 0.625
        ax.plot(Ts, np.array(sups)/ceil, "o-", ms=4, color=c, label=f"N={N}")
    ax.axhline(1.0, color="k", ls="--", lw=1)
    ax.text(2.2, 1.02, r"ceiling $k_N^2E$", fontsize=7.5)
    ax.set_xscale("log", base=2); ax.set_xlabel("horizon $T$")
    ax.set_ylabel(r"$\sup_{t\leq T}\Omega \;/\; k_N^2E$")
    ax.set_ylim(0, 1.15); ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("Truncation control, $\\nu=D=0$", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{OUT}/degeneracy.pdf"); plt.close(fig)
    print("  degeneracy.pdf")

# ---------------------------------------------------------------- Fig 3
def fig_scatter():
    """Ensemble scatter: the finding that retracted the measurements."""
    from quantumfluids.w4_shell_model.observable import crossing_time
    N, f, T = 4, 0.125, 20.0
    rng = np.random.default_rng(11)
    data = {}
    for D in (0.0, 0.018, 0.05, 0.1):
        ts = []
        for i in range(5):
            ph = 0.7*np.arange(N+1) if i == 0 else rng.uniform(0, 2*np.pi, N+1)
            a = make_profile("P3", N).astype(complex)*np.exp(1j*ph)
            r = integrate(N=N, nu=0.0, D=D, t_horizon=T, trace_every=1, a0=a)
            ceil = (2.0**N)**2 * r.energy_initial
            try: ts.append(crossing_time(r.trace_t, r.trace_omega_sum, f*ceil).time)
            except ValueError: ts.append(np.nan)
        data[D] = np.array(ts)
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    for j, (D, ts) in enumerate(data.items()):
        good = ts[np.isfinite(ts)]
        ax.plot([j]*len(good), good, "o", ms=5, color="#4C72B0", alpha=0.75)
        n_cens = int(np.sum(~np.isfinite(ts)))
        if len(good): ax.plot(j, good.mean(), "_", ms=22, color="#C44E52", mew=2)
        if n_cens: ax.annotate(f"{n_cens} censored", (j, T*0.94), ha="center",
                               fontsize=7, color="#C44E52")
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels([f"D={D}" for D in data])
    ax.set_ylabel(r"$\tau_{1/8}$"); ax.set_ylim(0, T)
    ax.set_title("Fixed-parameter ensemble scatter (5 phase realisations)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{OUT}/scatter.pdf"); plt.close(fig)
    print("  scatter.pdf")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("generating figures:")
    import sys as _s
    which = _s.argv[1] if len(_s.argv) > 1 else "all"
    if which in ("all", "liouville"): fig_liouville()
    if which in ("all", "degeneracy"): fig_degeneracy()
    if which in ("all", "scatter"): fig_scatter()

# NOTE (2026-08-15): matplotlib's mathtext rejects \le; use \leq. This bit once,
# silently: a sed fix mis-escaped, the figure was not regenerated, and a
# placeholder copy of another figure sat in its place with the build still
# green. Verify figure fixes by rendering the label READ FROM THIS FILE, and
# check md5sums differ between figures -- identical sizes are the tell.
