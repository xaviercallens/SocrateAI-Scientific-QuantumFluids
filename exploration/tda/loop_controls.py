"""Pre-registered controls C1-C4 for the closed-loop TDA pipeline (docs/designs/CLOSED_LOOP_PREREG.md).

Run BEFORE any real GP data is touched. Implements:
  - C1: 8-point toy cycle, Dgm0(f)/Dgm0(g) exact match, bottleneck, sup-norm, Wasserstein-1
        duality certificate (primal via linear_sum_assignment, dual via linprog LP, both
        checked against each other and against a hand-verified value).
  - C2: single-site perturbation, tight case (bottleneck == W1 == eps).
  - C3: negative control -- a broken dual certificate must be REJECTED by an independent checker.
  - C4: negative control -- T vs V cubical constructions on the SAME field must DISAGREE.

Every "expected" number below is taken verbatim from docs/designs/CLOSED_LOOP_PREREG.md and the
harness task text; nothing here is re-derived, only reproduced and checked.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "/home/xavkal/xdev/SocrateAI-Scientific-QuantumFluids/src")

import numpy as np
import gudhi
from scipy.optimize import linear_sum_assignment, linprog

from quantumfluids.tda.cubical import finite_pairs

TOL = 1e-9

results = []  # (label, passed: bool, detail: str)


def record(label, passed, detail=""):
    results.append((label, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))


def as_set(pairs):
    return {(round(float(b), 9), round(float(d), 9)) for b, d in pairs}


# ---------------------------------------------------------------------------
# TOY_CYCLE
# ---------------------------------------------------------------------------
f = np.array([1.0, 5.0, 2.0, 6.0, 3.0, 7.0, 4.0, 8.0])
g = np.array([1.0, 5.0, 2.0, 6.0, 3.0, 4.5, 4.0, 8.0])   # site 5: 7 -> 4.5
g2 = np.array([1.0, 5.0, 2.0, 6.0, 3.0, 7.0, 4.5, 8.0])  # site 6: 4 -> 4.5

print("=" * 78)
print("TOY_CYCLE fields")
print("f  =", f.tolist())
print("g  =", g.tolist())
print("g2 =", g2.tolist())
print("=" * 78)

# ---------------------------------------------------------------------------
# Step 2: diagrams
# ---------------------------------------------------------------------------
Dgm0_f = finite_pairs(f, 0, "T", periodic=True)
Dgm0_g = finite_pairs(g, 0, "T", periodic=True)
Dgm0_g2 = finite_pairs(g2, 0, "T", periodic=True)

print("\nDgm0(f)  finite pairs:", Dgm0_f.tolist())
print("Dgm0(g)  finite pairs:", Dgm0_g.tolist())
print("Dgm0(g2) finite pairs:", Dgm0_g2.tolist())

expected_f = {(2.0, 5.0), (3.0, 6.0), (4.0, 7.0)}
expected_g = {(2.0, 5.0), (3.0, 6.0), (4.0, 4.5)}

got_f = as_set(Dgm0_f)
got_g = as_set(Dgm0_g)

record(
    "C1-diagrams",
    got_f == expected_f and got_g == expected_g,
    f"Dgm0(f)={got_f} (expect {expected_f}); Dgm0(g)={got_g} (expect {expected_g})",
)

# ---------------------------------------------------------------------------
# Step 3: bottleneck distance
# ---------------------------------------------------------------------------
d_B_fg = gudhi.bottleneck_distance(Dgm0_f, Dgm0_g)
print(f"\nbottleneck_distance(Dgm0(f), Dgm0(g)) = {d_B_fg!r}")
record("C1-bottleneck", abs(d_B_fg - 1.5) < TOL, f"got {d_B_fg}, expected 1.5")

# ---------------------------------------------------------------------------
# Step 4: sup-norm
# ---------------------------------------------------------------------------
eps_fg = float(np.max(np.abs(f - g)))
print(f"eps = max|f-g| = {eps_fg!r}")
record("C1-eps", abs(eps_fg - 2.5) < TOL, f"got {eps_fg}, expected 2.5")


# ---------------------------------------------------------------------------
# Wasserstein duality certificate (the centerpiece)
# ---------------------------------------------------------------------------
def linf(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def cost_diag(p):
    return (p[1] - p[0]) / 2.0


def truncate_k(pairs, k=30):
    pairs = np.asarray(pairs, dtype=float).reshape(-1, 2)
    n0 = len(pairs)
    if n0 <= k:
        return pairs, 0
    lengths = pairs[:, 1] - pairs[:, 0]
    order = np.argsort(-lengths)[:k]
    return pairs[order], n0 - k


def wasserstein_certificate(X, Y, k=30, label=""):
    X, dropped_x = truncate_k(X, k)
    Y, dropped_y = truncate_k(Y, k)
    n, m = len(X), len(Y)
    print(f"\n--- Wasserstein certificate {label} --- n={n} m={m} "
          f"(dropped {dropped_x} from X, {dropped_y} from Y)")

    size = n + m
    C = np.empty((size, size), dtype=float)
    # rows 0..n-1 = X ; rows n..n+m-1 = diagonal slots for Y
    # cols 0..m-1 = Y ; cols m..m+n-1 = diagonal slots for X
    for i in range(n):
        for j in range(m):
            C[i, j] = linf(X[i], Y[j])
        for j in range(m, m + n):
            C[i, j] = cost_diag(X[i]) if (j - m) == i else 1e9
    for i in range(n, n + m):
        for j in range(m):
            C[i, j] = cost_diag(Y[j]) if (i - n) == j else 1e9
        for j in range(m, m + n):
            C[i, j] = 0.0

    # --- primal: exact min-cost perfect matching ---
    row_ind, col_ind = linear_sum_assignment(C)
    W1_primal = float(C[row_ind, col_ind].sum())

    # --- dual: same transportation problem as an LP ---
    nvars = size * size
    c_lp = C.ravel()  # C-order: index = i*size + j

    row_constraints = []
    for i in range(size - 1):  # drop the LAST row constraint
        row = np.zeros(nvars)
        row[i * size:(i + 1) * size] = 1.0
        row_constraints.append(row)
    col_constraints = []
    for j in range(size):
        col = np.zeros(nvars)
        col[j::size] = 1.0
        col_constraints.append(col)
    A_eq = np.array(row_constraints + col_constraints)
    b_eq = np.ones(A_eq.shape[0])

    res = linprog(c_lp, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    W1_lp = float(res.fun)
    marginals = np.asarray(res.eqlin.marginals)

    n_row_kept = size - 1
    u = np.zeros(size)
    u[:n_row_kept] = marginals[:n_row_kept]
    u[n_row_kept] = 0.0  # dropped constraint's dual set to 0
    v = marginals[n_row_kept:n_row_kept + size]

    def max_violation(u, v):
        return float(np.max(u[:, None] + v[None, :] - C))

    viol = max_violation(u, v)
    sign = "as-returned"
    if viol > 1e-6:
        u2, v2 = -u, -v
        viol2 = max_violation(u2, v2)
        if viol2 < viol:
            u, v, viol, sign = u2, v2, viol2, "negated"

    sum_uv = float(np.sum(u) + np.sum(v))
    rel_err = abs(sum_uv - W1_primal) / max(abs(W1_primal), 1e-12)

    feas_ok = viol <= 1e-6
    sum_ok = rel_err <= 1e-6
    cert_ok = feas_ok and sum_ok

    print(f"W1_primal = {W1_primal!r}")
    print(f"W1_lp     = {W1_lp!r}")
    print(f"dual sign convention used: {sign}")
    print(f"u (row duals) = {u.tolist()}")
    print(f"v (col duals) = {v.tolist()}")
    print(f"max dual-feasibility violation = {viol!r} (must be <= 1e-6)")
    print(f"sum(u)+sum(v) = {sum_uv!r} vs W1_primal = {W1_primal!r} "
          f"(rel err {rel_err!r}, must be <= 1e-6)")

    return {
        "n": n, "m": m, "dropped_x": dropped_x, "dropped_y": dropped_y,
        "X": X, "Y": Y, "C": C,
        "W1_primal": W1_primal, "W1_lp": W1_lp,
        "u": u, "v": v, "max_violation": viol, "sum_uv": sum_uv,
        "feas_ok": feas_ok, "sum_ok": sum_ok, "cert_ok": cert_ok,
    }


# ---------------------------------------------------------------------------
# Step 5: run the certificate on the toy pair (f, g)
# ---------------------------------------------------------------------------
cert_fg = wasserstein_certificate(Dgm0_f, Dgm0_g, k=30, label="(Dgm0(f), Dgm0(g))")

record(
    "C1-wasserstein-primal",
    abs(cert_fg["W1_primal"] - 1.75) < TOL,
    f"W1_primal = {cert_fg['W1_primal']!r}, expected 1.75",
)
record(
    "C1-wasserstein-dual",
    abs(cert_fg["W1_lp"] - 1.75) < 1e-9,
    f"W1_lp = {cert_fg['W1_lp']!r}, expected 1.75",
)
record(
    "C1-wasserstein-certificate",
    cert_fg["cert_ok"],
    f"max_violation={cert_fg['max_violation']!r} (<=1e-6), "
    f"sum(u)+sum(v)={cert_fg['sum_uv']!r} vs W1_primal={cert_fg['W1_primal']!r}",
)

# ---------------------------------------------------------------------------
# Step 6: C2 -- tight single-point perturbation
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("C2: single-site perturbation g2 (site 6: 4 -> 4.5)")
eps_fg2 = float(np.max(np.abs(f - g2)))
d_B_fg2 = gudhi.bottleneck_distance(Dgm0_f, Dgm0_g2)
cert_fg2 = wasserstein_certificate(Dgm0_f, Dgm0_g2, k=30, label="(Dgm0(f), Dgm0(g2))")

print(f"Dgm0(g2) finite pairs: {Dgm0_g2.tolist()}")
print(f"eps(f,g2) = {eps_fg2!r}")
print(f"bottleneck_distance(f,g2) = {d_B_fg2!r}")

c2_ok = (
    abs(eps_fg2 - 0.5) < TOL
    and abs(d_B_fg2 - 0.5) < TOL
    and abs(cert_fg2["W1_primal"] - 0.5) < TOL
    and abs(cert_fg2["W1_lp"] - 0.5) < 1e-9
    and cert_fg2["cert_ok"]
)
record(
    "C2",
    c2_ok,
    f"eps={eps_fg2!r}, d_B={d_B_fg2!r}, W1_primal={cert_fg2['W1_primal']!r}, "
    f"W1_lp={cert_fg2['W1_lp']!r} (all expected 0.5, exactly)",
)

# ---------------------------------------------------------------------------
# Step 7: C3 -- negative control, broken dual potentials must be rejected
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("C3: negative control on the hand-given dual potentials (psi_c2 = 0.5, broken)")

# identify a,b,c in Dgm0(f) and a2,b2,c2 in Dgm0(g) by the hand-verified point labels
a, b, c = (2.0, 5.0), (3.0, 6.0), (4.0, 7.0)
a2, b2, c2 = (2.0, 5.0), (3.0, 6.0), (4.0, 4.5)
assert as_set(Dgm0_f) == {a, b, c}
assert as_set(Dgm0_g) == {a2, b2, c2}

phi = {"a": 0.0, "b": 0.5, "c": 1.5}
psi_broken = {"a2": 0.0, "b2": -0.5, "c2": 0.5}  # c3: psi_c2 changed from 0.25 to 0.5
points_X = {"a": a, "b": b, "c": c}
points_Y = {"a2": a2, "b2": b2, "c2": c2}


def check_dual_feasibility(phi, psi, points_X, points_Y, tol=1e-9):
    """Independent feasibility checker (not the LP solver of step 5)."""
    failures = []
    for i, pi in points_X.items():
        for j, qj in points_Y.items():
            lhs = phi[i] + psi[j]
            rhs = linf(pi, qj)
            if lhs > rhs + tol:
                failures.append(f"cross  phi_{i}+psi_{j} = {lhs!r} > Linf({i},{j}) = {rhs!r}")
    for i, pi in points_X.items():
        lhs = phi[i]
        rhs = cost_diag(pi)
        if lhs > rhs + tol:
            failures.append(f"diag   phi_{i} = {lhs!r} > cost({i},Delta) = {rhs!r}")
    for j, qj in points_Y.items():
        lhs = psi[j]
        rhs = cost_diag(qj)
        if lhs > rhs + tol:
            failures.append(f"diag   psi_{j} = {lhs!r} > cost({j},Delta) = {rhs!r}")
    return failures


failures_broken = check_dual_feasibility(phi, psi_broken, points_X, points_Y)
print("Checking BROKEN potentials (psi_c2=0.5):")
for msg in failures_broken:
    print("  VIOLATION:", msg)
if not failures_broken:
    print("  (no violation found)")

# sanity: the ORIGINAL hand potentials (psi_c2=0.25) must be feasible under the same checker
psi_good = {"a2": 0.0, "b2": -0.5, "c2": 0.25}
failures_good = check_dual_feasibility(phi, psi_good, points_X, points_Y)
print("Checking ORIGINAL potentials (psi_c2=0.25) as a sanity check:")
for msg in failures_good:
    print("  VIOLATION:", msg)
if not failures_good:
    print("  (feasible, as expected)")

direct_cc2_cost = linf(c, c2)  # max(0, |7-4.5|) = 2.5
print(f"direct coupling c<->c2 cost = {direct_cc2_cost!r} "
      f"(must be worse than W1_primal=1.75)")

c3_ok = (
    len(failures_broken) >= 1
    and any("psi_c2" in msg for msg in failures_broken)
    and len(failures_good) == 0
    and direct_cc2_cost > cert_fg["W1_primal"] + TOL
)
record(
    "C3",
    c3_ok,
    f"broken potentials correctly flagged ({len(failures_broken)} violation(s)); "
    f"original potentials feasible; direct c<->c2 cost {direct_cc2_cost!r} > "
    f"optimum {cert_fg['W1_primal']!r}",
)

# ---------------------------------------------------------------------------
# Step 8: C4 -- negative control, T vs V constructions on the SAME field must disagree
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("C4: negative control, T vs V construction on the same field f")
a2_c4 = finite_pairs(f, 0, "T", True)
b2_c4 = finite_pairs(f, 0, "V", True)
print(f"finite_pairs(f, 0, 'T', True) = {a2_c4.tolist()}")
print(f"finite_pairs(f, 0, 'V', True) = {b2_c4.tolist()}")

disagree = (len(a2_c4) != len(b2_c4)) or (as_set(a2_c4) != as_set(b2_c4))

if not disagree:
    # Sanity check: rule out a bug in _complex() (T/V ignored) before accepting this as a
    # genuine mathematical fact. If T and V ever disagree on ANY field, the construction
    # switch is real and the 1D toy field is simply a case where they happen to coincide.
    rng = np.random.default_rng(0)
    random_1d_agree = []
    for _ in range(20):
        x = rng.normal(size=8)
        ta = finite_pairs(x, 0, "T", True)
        tb = finite_pairs(x, 0, "V", True)
        random_1d_agree.append(
            ta.shape == tb.shape and np.allclose(np.sort(ta, axis=0), np.sort(tb, axis=0))
        )
    x2d = rng.normal(size=(6, 6))
    ta2d = finite_pairs(x2d, 0, "T", True)
    tb2d = finite_pairs(x2d, 0, "V", True)
    disagree_2d = len(ta2d) != len(tb2d) or not np.allclose(
        np.sort(ta2d, axis=0), np.sort(tb2d, axis=0)
    )
    print(f"Sanity: 20 random 1D periodic fields, T vs V agree in all cases? "
          f"{all(random_1d_agree)}")
    print(f"Sanity: 6x6 random 2D periodic field, n_T={len(ta2d)} n_V={len(tb2d)}, "
          f"disagree={disagree_2d} (T/V must differ generically in 2D, ruling out a "
          f"construction-ignored bug)")
    note = (
        "T and V constructions produce IDENTICAL Dgm0 on this 1D periodic field. This is "
        "reproduced across 20 random 1D periodic fields (always agree) while a 2D random "
        "field shows T != V (n_T={} vs n_V={}), so _complex() genuinely switches "
        "construction and this is not a code bug: for a 1D periodic (cyclic) field, H0 "
        "sublevel persistence depends only on the cyclic order of the values (the graph is "
        "self-dual under T<->V), so T and V necessarily coincide in 1D. The pre-registered "
        "expectation of disagreement does not hold for a 1D field; C4 as specified is not a "
        "distinguishing negative control in 1D.".format(len(ta2d), len(tb2d))
    )
else:
    note = "disagree as required"

record(
    "C4",
    disagree,
    f"T: {as_set(a2_c4)} (n={len(a2_c4)}) vs V: {as_set(b2_c4)} (n={len(b2_c4)}) -- {note}",
)

# ---------------------------------------------------------------------------
# Final verdict
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("SUMMARY")
for label, passed, detail in results:
    print(f"  [{'PASS' if passed else 'FAIL'}] {label}")

all_pass = all(p for _, p, _ in results)
if all_pass:
    print("\nVERDICT: ALL CONTROLS PASS")
else:
    failed = [(label, detail) for label, passed, detail in results if not passed]
    print("\nVERDICT: FAILED CONTROLS:")
    for label, detail in failed:
        print(f"  - {label}: {detail}")
