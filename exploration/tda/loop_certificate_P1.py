#!/usr/bin/env python
"""
Wasserstein-1 duality certificate (primal matching + dual potentials)
for persistence diagram pair P1.

Self-contained: does not import from any other exploration script.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment, linprog


def truncate_k(diagram, k=30):
    """Truncate a diagram (list of (birth,death)) to the k longest bars.
    Returns (truncated_list, n_dropped)."""
    pts = list(diagram)
    n_total = len(pts)
    if n_total <= k:
        return pts, 0
    # sort by persistence (death-birth) descending, keep top k
    pts_sorted = sorted(pts, key=lambda p: (p[1] - p[0]), reverse=True)
    kept = pts_sorted[:k]
    dropped = n_total - k
    return kept, dropped


def linf(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def cost_to_diag(p):
    return (p[1] - p[0]) / 2.0


def build_cost_matrix(X, Y):
    n = len(X)
    m = len(Y)
    BIG = 1e9
    size = n + m
    C = np.zeros((size, size))
    # rows 0..n-1 = X points ; rows n..n+m-1 = diagonal slots reserved for Y points
    # cols 0..m-1 = Y points ; cols m..m+n-1 = diagonal slots reserved for X points
    for i in range(n):
        for j in range(m):
            C[i, j] = linf(X[i], Y[j])
    for i in range(n):
        for jj in range(n):  # cols m..m+n-1 -> jj = j - m
            j = m + jj
            C[i, j] = cost_to_diag(X[i]) if jj == i else BIG
    for ii in range(m):  # rows n..n+m-1 -> ii = i - n
        i = n + ii
        for j in range(m):
            C[i, j] = cost_to_diag(Y[j]) if ii == j else BIG
    for ii in range(m):
        i = n + ii
        for jj in range(n):
            j = m + jj
            C[i, j] = 0.0
    return C, n, m


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    w1 = C[row_ind, col_ind].sum()
    return w1, row_ind, col_ind


def solve_dual(C, n, m):
    """Solve the transportation LP explicitly and extract dual potentials.
    Variables x_ij, i in 0..n+m-1 (rows), j in 0..m+n-1 (cols), flattened
    row-major: var index = i*(m+n) + j.
    Row constraints: sum_j x_ij = 1 for each i (n+m constraints)
    Col constraints: sum_i x_ij = 1 for each j (m+n constraints)
    Drop the LAST row constraint (redundant).
    """
    R = n + m  # number of rows
    Cc = m + n  # number of cols (same value, kept separate name for clarity)
    nvars = R * Cc

    c = C.reshape(-1)

    A_rows = []
    b_rows = []
    for i in range(R):
        row = np.zeros(nvars)
        row[i * Cc:(i + 1) * Cc] = 1.0
        A_rows.append(row)
        b_rows.append(1.0)

    A_cols = []
    b_cols = []
    for j in range(Cc):
        col = np.zeros(nvars)
        for i in range(R):
            col[i * Cc + j] = 1.0
        A_cols.append(col)
        b_cols.append(1.0)

    # drop last row constraint
    A_rows_kept = A_rows[:-1]
    b_rows_kept = b_rows[:-1]

    A_eq = np.vstack(A_rows_kept + A_cols)
    b_eq = np.array(b_rows_kept + b_cols)

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")

    n_row_kept = len(A_rows_kept)
    n_col = len(A_cols)
    marginals = res.eqlin.marginals
    row_marg_kept = marginals[:n_row_kept]
    col_marg = marginals[n_row_kept:n_row_kept + n_col]

    u = np.zeros(R)
    u[:n_row_kept] = row_marg_kept
    u[-1] = 0.0  # dropped row constraint dual set to 0
    v = col_marg.copy()

    return res, u, v


def check_and_fix_signs(u, v, C, tol=1e-7):
    """Check u_i + v_j <= C[i,j] + tol for all entries. If it fails broadly,
    negate both u and v and re-check. Returns (u, v, sign_used, max_violation)."""
    R, Cc = C.shape

    def max_violation(u_, v_):
        U = u_.reshape(-1, 1)
        V = v_.reshape(1, -1)
        viol = (U + V) - C
        return np.max(viol)

    mv_pos = max_violation(u, v)
    # count fraction of entries violating under "as-is" sign
    U = u.reshape(-1, 1)
    V = v.reshape(1, -1)
    viol_mask_pos = (U + V) > (C + tol)
    frac_pos = viol_mask_pos.sum() / viol_mask_pos.size

    u_neg, v_neg = -u, -v
    mv_neg = max_violation(u_neg, v_neg)
    viol_mask_neg = (u_neg.reshape(-1, 1) + v_neg.reshape(1, -1)) > (C + tol)
    frac_neg = viol_mask_neg.sum() / viol_mask_neg.size

    if mv_pos <= tol:
        return u, v, "as-is", mv_pos
    elif mv_neg <= tol:
        return u_neg, v_neg, "negated", mv_neg
    else:
        # neither fully satisfies; pick whichever has fewer violations / smaller max violation
        if frac_neg < frac_pos or (frac_neg == frac_pos and mv_neg < mv_pos):
            return u_neg, v_neg, "negated (still violating)", mv_neg
        else:
            return u, v, "as-is (still violating)", mv_pos


def run_certificate(X, Y, label="", k=30, verbose=True):
    X_t, dropped_x = truncate_k(X, k=k)
    Y_t, dropped_y = truncate_k(Y, k=k)

    C, n, m = build_cost_matrix(X_t, Y_t)
    w1_primal, row_ind, col_ind = solve_primal(C)
    res, u, v = solve_dual(C, n, m)
    w1_lp = res.fun

    u_final, v_final, sign_used, max_viol = check_and_fix_signs(u, v, C)
    dual_sum = u_final.sum() + v_final.sum()

    rel_tol = 1e-6
    cond_a = max_viol <= 1e-6
    cond_b = abs(dual_sum - w1_primal) <= rel_tol * max(1.0, abs(w1_primal))
    certificate_pass = bool(cond_a and cond_b)

    if verbose:
        print(f"--- {label} ---")
        print(f"n (after truncation) = {n}  (dropped {dropped_x})")
        print(f"m (after truncation) = {m}  (dropped {dropped_y})")
        print(f"W1_primal = {w1_primal!r}")
        print(f"W1_lp     = {w1_lp!r}")
        print(f"sign convention used: {sign_used}")
        print(f"max dual violation = {max_viol!r}")
        print(f"sum(u)+sum(v) = {dual_sum!r}")
        print(f"cond (a) feasibility <=1e-6 : {cond_a}")
        print(f"cond (b) sum(u)+sum(v)==W1_primal (rel 1e-6) : {cond_b}")
        print(f"CERTIFICATE PASS: {certificate_pass}")
        print()

    return {
        "n": n,
        "m": m,
        "dropped_x": dropped_x,
        "dropped_y": dropped_y,
        "W1_primal": w1_primal,
        "W1_lp": w1_lp,
        "sign_used": sign_used,
        "max_dual_violation": max_viol,
        "dual_sum": dual_sum,
        "certificate_pass": certificate_pass,
    }


if __name__ == "__main__":
    # ---- Step 0: inline sanity check on the toy example ----
    X_toy = [(2, 5), (3, 6), (4, 7)]
    Y_toy = [(2, 5), (3, 6), (4, 4.5)]

    toy_result = run_certificate(X_toy, Y_toy, label="TOY CHECK", k=30)

    toy_w1 = toy_result["W1_primal"]
    toy_ok = (
        abs(toy_result["W1_primal"] - 1.75) < 1e-6
        and abs(toy_result["W1_lp"] - 1.75) < 1e-6
        and toy_result["certificate_pass"]
    )

    if not toy_ok:
        print("TOY CHECK FAILED. Discrepancy detected -- STOPPING, not proceeding to real data.")
        print(toy_result)
        raise SystemExit(1)
    else:
        print("TOY CHECK PASSED: W1_primal = W1_lp = 1.75, certificate passes.\n")

    # ---- Step 1: real diagrams A (X) vs B (Y), pair P1 ----
    A = [
        [-3.12981225392777e-8, 0.19213870429343372],
        [-2.958916501099203e-8, 0.19213870292978158],
        [-0.008641586445015828, 0.13059930670034287],
        [0.009563304563498735, 0.13059930526886052],
        [0.009563305649525233, 0.12346750044644655],
    ]
    B = [
        [-5.774693004739577e-8, 0.18025185564446972],
        [-5.812801617110371e-8, 0.18025185339568497],
        [-0.013922010532257223, 0.1336194114690975],
        [-0.007510891321447673, 0.13496367476114865],
        [-0.007510891321447673, 0.13496367476114865],
    ]

    real_result = run_certificate(A, B, label="PAIR P1 (A vs B)", k=30)

    print("=== SUMMARY ===")
    print(f"pair_id = P1")
    print(f"toy_check_pass = {toy_ok}, toy_check_w1 = {toy_w1}")
    print(f"n = {real_result['n']} (dropped {real_result['dropped_x']})")
    print(f"m = {real_result['m']} (dropped {real_result['dropped_y']})")
    print(f"W1_primal = {real_result['W1_primal']}")
    print(f"W1_lp = {real_result['W1_lp']}")
    print(f"max_dual_violation = {real_result['max_dual_violation']}")
    print(f"dual_sum = {real_result['dual_sum']}")
    print(f"certificate_pass = {real_result['certificate_pass']}")
