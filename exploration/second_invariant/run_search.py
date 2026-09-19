"""DUAL_SCALE_SECOND_INVARIANT.md §3 + addendum A1. Deterministic, seeded.

SCOPE NOTE (2026-09-20): the pre-registered N in (6, 8, 10) was NOT completed -- the first
attempt was killed by its own 50-min budget (exit 143), a bookkeeping stop, not a finding (LL-18).
Cause: a monomial cache of S*J complex entries (~1.25 GB at N=10). Cache removed; scope reduced to
N in (4, 5, 6) with a per-case budget. N = 8, 10 are NOT attempted and nothing is claimed for them.
"""
import json, sys, time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.w4_shell_model import invariant_search as S

rng = np.random.default_rng(20260919)
res = {"scope_note": "N in (4,5,6); pre-registered N=8,10 not attempted (see module docstring)",
       "controls": {}, "preregistered": [], "extension_E1": []}

modes = [-2, -1, 0, 1, 2]; omega = np.array([m * m for m in modes], float); g = 0.7
basis = S.quadratic_basis(5) + S.quartic_basis(5)
P = S.sample_states(3 * len(basis), 5, rng)
null, _ = S.nullspace(S.lie_matrix(basis, P, S.gp_rhs(P, modes, omega, g)))
res["controls"]["positive_GP_energy_dist"] = S.in_span(S.gp_energy_coeffs(basis, modes, omega, g), null)

N = 5; k = 2.0 ** np.arange(N + 1)
basis = S.quadratic_basis(N + 1) + S.quartic_basis(N + 1) + S.cubic_basis(N + 1)
V = S.sample_states(2 * len(basis), N + 1, rng)
null, _ = S.nullspace(S.lie_matrix(basis, V, S.shell_rhs(V, k, "leak")))
mass = np.array([1.0 if b.label.startswith("|v") else 0.0 for b in basis])
res["controls"]["negative_leak_mass_dist"] = S.in_span(mass, null)
print("controls:", json.dumps(res["controls"]), flush=True)

def known(basis, k, mu, D, cubic):
    idx = {b.label: j for j, b in enumerate(basis)}
    n = max(int(b.label[2:-3]) for b in basis if b.label.startswith("|v")) + 1
    mass = np.array([1.0 if b.label.startswith("|v") else 0.0 for b in basis])
    m2 = np.zeros(len(basis))
    for a in range(n):
        for b in range(n):
            lo, hi = min(a, b), max(a, b); m2[idx[f"Re c{lo}c{hi}v{lo}v{hi}"]] += 1.0
    cols = [mass, m2] + ([S.predicted_H(basis, k, mu, D)] if cubic else [])
    return np.stack(cols, axis=1)

def run(N, seam, mu, D, cubic, factor=2):
    k = 2.0 ** np.arange(N + 1)
    basis = S.quadratic_basis(N + 1) + S.quartic_basis(N + 1) + (S.cubic_basis(N + 1) if cubic else [])
    out = {"N": N, "seam": seam, "mu": mu, "D": D, "cubic": cubic, "basis": len(basis)}
    for f in (factor, 2 * factor):
        t = time.time()
        V = S.sample_states(f * len(basis), N + 1, rng)
        null, s = S.nullspace(S.lie_matrix(basis, V, S.shell_rhs(V, k, seam, mu, D)))
        K = known(basis, k, mu if seam == "gpe" else 0.0, D, cubic)
        out[f"S={f}x"] = {
            "null_dim": int(null.shape[1]),
            "gap": float(s[len(s) - null.shape[1] - 1] / s[0]) if 0 < null.shape[1] < len(s) else None,
            "known_in_null": max(S.in_span(K[:, i], null) for i in range(K.shape[1])),
            "null_explained_by_known": (max(S.in_span(null[:, i], K) for i in range(null.shape[1]))
                                        if null.shape[1] else None),
            "sec": round(time.time() - t, 1)}
    return out

for N in (4, 5, 6):
    for seam, mu in (("trunc", 0.0), ("gpe", 0.5), ("gpe", 1.0)):
        r = run(N, seam, mu, 0.0, False); res["preregistered"].append(r); print(json.dumps(r), flush=True)
for N in (4, 5, 6):
    for seam, mu, D in (("trunc", 0.0, 0.0), ("gpe", 1.0, 0.0), ("trunc", 0.0, 0.3), ("gpe", 1.0, 0.3)):
        r = run(N, seam, mu, D, True); res["extension_E1"].append(r); print(json.dumps(r), flush=True)
k = 2.0 ** np.arange(9); Vr = rng.normal(size=(100, 9)).astype(complex)
res["P_c_H_on_real_data_max_abs"] = float(np.max(np.abs(
    np.sum((k[:-1] / 2.0 ** np.arange(8)) * np.imag(np.conj(Vr[:, :-1]) ** 2 * Vr[:, 1:]), axis=1))))
json.dump(res, open("exploration/second_invariant/results.json", "w"), indent=1)
print("P-c (H on real data):", res["P_c_H_on_real_data_max_abs"])
