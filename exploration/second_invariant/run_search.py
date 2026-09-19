"""Run of docs/designs/DUAL_SCALE_SECOND_INVARIANT.md (+ addendum A1). Deterministic, seeded. Output: results.json"""
import json, sys, time
import numpy as np
sys.path.insert(0, "src")
from quantumfluids.w4_shell_model import invariant_search as S

rng = np.random.default_rng(20260919)
res = {"controls": {}, "preregistered": [], "extension_E1": []}

# --- positive control: truncated GP, theorem-backed (GPGalerkin.energy_rate_zero)
modes = [-2, -1, 0, 1, 2]; omega = np.array([m * m for m in modes], float); g = 0.7
basis = S.quadratic_basis(5) + S.quartic_basis(5)
P = S.sample_states(3 * len(basis), 5, rng)
null, s = S.nullspace(S.lie_matrix(basis, P, S.gp_rhs(P, modes, omega, g)))
res["controls"]["positive_GP"] = {"basis": len(basis), "null_dim": int(null.shape[1]),
    "energy_dist_from_nullspace": S.in_span(S.gp_energy_coeffs(basis, modes, omega, g), null)}

# --- negative control: leaking seam, mass must NOT be conserved
N = 6; k = 2.0 ** np.arange(N + 1)
basis = S.quadratic_basis(N + 1) + S.quartic_basis(N + 1) + S.cubic_basis(N + 1)
V = S.sample_states(2 * len(basis), N + 1, rng)
null, s = S.nullspace(S.lie_matrix(basis, V, S.shell_rhs(V, k, "leak")))
mass = np.array([1.0 if b.label.startswith("|v") else 0.0 for b in basis])
res["controls"]["negative_leak"] = {"null_dim": int(null.shape[1]), "mass_dist_from_nullspace": S.in_span(mass, null)}
print(json.dumps(res["controls"], indent=1), flush=True)

def run(N, seam, mu, D, with_cubic, factor=2):
    k = 2.0 ** np.arange(N + 1)
    basis = S.quadratic_basis(N + 1) + S.quartic_basis(N + 1) + (S.cubic_basis(N + 1) if with_cubic else [])
    out = {"N": N, "seam": seam, "mu": mu, "D": D, "basis": len(basis)}
    for f in (factor, 2 * factor):  # stability under doubling S
        V = S.sample_states(f * len(basis), N + 1, rng)
        null, s = S.nullspace(S.lie_matrix(basis, V, S.shell_rhs(V, k, seam, mu, D)))
        omega_c = np.array([k[int(b.label[2:-3])] ** 2 if b.label.startswith("|v") else 0.0 for b in basis])
        mass = (omega_c > 0).astype(float)
        # Omega-coefficient: is there a null vector not orthogonal to the Omega direction beyond the mass part?
        q = np.linalg.qr(null)[0] if null.shape[1] else np.zeros((len(basis), 0))
        quad = [j for j, b in enumerate(basis) if b.label.startswith("|v")]
        quad_parts = q[quad, :]            # quadratic components of null vectors
        # remove the mass direction; what is left along quadratics?
        m = mass[quad] / np.linalg.norm(mass[quad])
        resid = quad_parts - np.outer(m, m @ quad_parts)
        out[f"S={f}x"] = {"null_dim": int(null.shape[1]), "gap": float(s[-null.shape[1]-1] / s[0]) if null.shape[1] < len(s) else None,
                          "mass_dist": S.in_span(mass, null), "non_mass_quadratic_norm": float(np.linalg.norm(resid)),
                          "H_dist": S.in_span(S.predicted_H(basis, k, mu if seam == "gpe" else 0.0, D), null) if with_cubic else None}
    return out

for N in (6, 8, 10):
    for seam, mu in (("trunc", 0.0), ("gpe", 0.5), ("gpe", 1.0)):
        t = time.time(); r = run(N, seam, mu, 0.0, False); r["sec"] = round(time.time() - t, 1)
        res["preregistered"].append(r); print(json.dumps(r), flush=True)
for N in (6, 8):
    for seam, mu, D in (("trunc", 0.0, 0.0), ("gpe", 0.5, 0.0), ("gpe", 1.0, 0.0), ("trunc", 0.0, 0.3), ("gpe", 1.0, 0.3)):
        t = time.time(); r = run(N, seam, mu, D, True); r["sec"] = round(time.time() - t, 1)
        res["extension_E1"].append(r); print(json.dumps(r), flush=True)
# P-c: H vanishes on real data
k = 2.0 ** np.arange(9); Vr = rng.normal(size=(100, 9)).astype(complex)
res["P_c_H_on_real_data_max_abs"] = float(np.max(np.abs(np.sum((k[:-1] / 2.0 ** np.arange(8)) * np.imag(np.conj(Vr[:, :-1]) ** 2 * Vr[:, 1:]), axis=1))))
json.dump(res, open("exploration/second_invariant/results.json", "w"), indent=1)
print("P-c:", res["P_c_H_on_real_data_max_abs"])
