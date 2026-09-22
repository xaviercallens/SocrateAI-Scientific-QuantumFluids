#!/usr/bin/env python
"""
Wasserstein-1 duality certificate (primal matching + dual potentials) for
persistence diagram pair R2. Self-contained: no imports from other
exploration scripts.

Recipe implemented exactly as specified in the task:
 1. Truncate each diagram to the k=30 longest bars before anything else.
 2. Ground cost: Linf off-diagonal; (d-b)/2 to the diagonal.
 3. Primal: min-cost perfect matching on an (n+m)x(n+m) cost matrix via
    scipy.optimize.linear_sum_assignment.
 4. Dual: same transportation problem as an LP (scipy.optimize.linprog,
    method="highs"), drop the last row equality constraint (redundant),
    read res.eqlin.marginals as duals, verify/fix sign convention, check
    feasibility u_i+v_j <= C[i,j] and sum(u)+sum(v) == W1_primal.
 5. Report n, m, W1_primal, W1_lp, max dual violation, sum(u)+sum(v), PASS/FAIL.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment, linprog

BIG = 1e9


def truncate_k_longest(diagram, k=30):
    """Truncate a list of (birth, death) pairs to the k longest bars
    (death - birth). Returns (truncated_list, n_dropped)."""
    pts = list(diagram)
    n = len(pts)
    if n <= k:
        return pts, 0
    pts_sorted = sorted(pts, key=lambda p: (p[1] - p[0]), reverse=True)
    kept = pts_sorted[:k]
    return kept, n - k


def build_cost_matrix(X, Y):
    n = len(X)
    m = len(Y)
    size = n + m
    C = np.full((size, size), BIG, dtype=float)

    Xa = np.array(X, dtype=float)
    Ya = np.array(Y, dtype=float)

    # rows 0..n-1 = X points ; rows n..n+m-1 = diagonal slots for Y points
    # cols 0..m-1 = Y points ; cols m..m+n-1 = diagonal slots for X points

    # block i<n, j<m : Linf(X[i], Y[j])
    if n > 0 and m > 0:
        diff = np.abs(Xa[:, None, :] - Ya[None, :, :])  # (n, m, 2)
        linf = diff.max(axis=2)
        C[0:n, 0:m] = linf

    # block i<n, j>=m : cost(X[i], Delta) if (j-m)==i else BIG
    for i in range(n):
        cost_diag = (Xa[i, 1] - Xa[i, 0]) / 2.0
        C[i, m + i] = cost_diag

    # block i>=n, j<m : cost(Y[j], Delta) if (i-n)==j else BIG
    for j in range(m):
        cost_diag = (Ya[j, 1] - Ya[j, 0]) / 2.0
        C[n + j, j] = cost_diag

    # block i>=n, j>=m : dummy-to-dummy, free
    C[n:n + m, m:m + n] = 0.0

    return C


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    w1 = C[row_ind, col_ind].sum()
    return w1, row_ind, col_ind


def solve_dual(C):
    """Solve the transportation LP explicitly and extract dual potentials."""
    size = C.shape[0]  # = n+m = m+n (square)
    N = size  # number of "supply" nodes (rows), also number of "demand" nodes (cols)

    c = C.flatten()  # x_ij flattened row-major: index i*N + j

    # Row constraints: sum_j x_ij = 1 for each i, drop the LAST row constraint
    # Column constraints: sum_i x_ij = 1 for each j (keep all)
    n_row_constraints = N - 1
    n_col_constraints = N
    n_vars = N * N

    A_eq = np.zeros((n_row_constraints + n_col_constraints, n_vars))
    b_eq = np.ones(n_row_constraints + n_col_constraints)

    # row constraints i = 0..N-2
    for i in range(n_row_constraints):
        A_eq[i, i * N:(i + 1) * N] = 1.0

    # column constraints j = 0..N-1
    for j in range(n_col_constraints):
        row_idx = n_row_constraints + j
        A_eq[row_idx, j::N] = 1.0

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")

    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")

    w1_lp = res.fun

    marginals = res.eqlin.marginals  # length n_row_constraints + n_col_constraints
    u_kept = marginals[:n_row_constraints]
    v = marginals[n_row_constraints:]
    u = np.concatenate([u_kept, [0.0]])  # dual of dropped row constraint = 0

    return w1_lp, u, v, res


def check_and_fix_sign(u, v, C, tol=1e-7):
    """Check u_i + v_j <= C[i,j] + tol for all entries.
    If it fails broadly, negate both and re-check."""
    N = C.shape[0]

    def max_violation(u_, v_):
        S = u_[:, None] + v_[None, :]
        viol = S - C
        return viol.max()

    mv1 = max_violation(u, v)
    if mv1 <= tol:
        return u, v, mv1, "as-returned (no negation)"

    mv2 = max_violation(-u, -v)
    if mv2 <= tol:
        return -u, -v, mv2, "negated (u,v) -> (-u,-v)"

    # neither works within tolerance; return the better one, flagged
    if mv2 < mv1:
        return -u, -v, mv2, "negated (u,v) -> (-u,-v) [STILL VIOLATES TOL]"
    else:
        return u, v, mv1, "as-returned (no negation) [STILL VIOLATES TOL]"


def wasserstein_certificate(X, Y, k=30, verbose=True, label=""):
    X_trunc, dropped_x = truncate_k_longest(X, k=k)
    Y_trunc, dropped_y = truncate_k_longest(Y, k=k)

    n = len(X_trunc)
    m = len(Y_trunc)

    C = build_cost_matrix(X_trunc, Y_trunc)

    w1_primal, row_ind, col_ind = solve_primal(C)
    w1_lp, u_raw, v_raw, lp_res = solve_dual(C)

    u, v, max_viol, sign_used = check_and_fix_sign(u_raw, v_raw, C)

    dual_sum = u.sum() + v.sum()

    rel_tol = 1e-6
    cond_a = max_viol <= 1e-6
    cond_b = abs(dual_sum - w1_primal) <= rel_tol * max(1.0, abs(w1_primal))

    certificate_pass = bool(cond_a and cond_b)

    result = {
        "label": label,
        "n": n,
        "m": m,
        "dropped_x": dropped_x,
        "dropped_y": dropped_y,
        "W1_primal": w1_primal,
        "W1_lp": w1_lp,
        "max_dual_violation": max_viol,
        "dual_sum": dual_sum,
        "sign_convention": sign_used,
        "certificate_pass": certificate_pass,
        "cond_a_feasibility": cond_a,
        "cond_b_strong_duality": cond_b,
    }

    if verbose:
        print(f"--- {label} ---")
        print(f"n={n} (dropped {dropped_x}), m={m} (dropped {dropped_y})")
        print(f"W1_primal = {w1_primal!r}")
        print(f"W1_lp     = {w1_lp!r}")
        print(f"sign convention used: {sign_used}")
        print(f"max dual-feasibility violation = {max_viol!r}")
        print(f"sum(u)+sum(v) = {dual_sum!r}")
        print(f"cond (a) feasibility <=1e-6 : {cond_a}")
        print(f"cond (b) strong duality match: {cond_b}")
        print(f"CERTIFICATE: {'PASS' if certificate_pass else 'FAIL'}")
        print()

    return result


def main():
    # ---------------------------------------------------------------
    # TOY SELF-CHECK (mandatory, must pass before touching real data)
    # ---------------------------------------------------------------
    X_toy = [(2, 5), (3, 6), (4, 7)]
    Y_toy = [(2, 5), (3, 6), (4, 4.5)]

    toy_result = wasserstein_certificate(X_toy, Y_toy, k=30, verbose=True,
                                          label="TOY SELF-CHECK")

    toy_w1_primal = toy_result["W1_primal"]
    toy_w1_lp = toy_result["W1_lp"]
    toy_pass = (
        abs(toy_w1_primal - 1.75) < 1e-6
        and abs(toy_w1_lp - 1.75) < 1e-6
        and toy_result["certificate_pass"]
    )

    print(f"TOY CHECK: W1_primal={toy_w1_primal}, W1_lp={toy_w1_lp}, "
          f"expected 1.75, certificate={'PASS' if toy_result['certificate_pass'] else 'FAIL'}")

    if not toy_pass:
        print("TOY CHECK FAILED. STOPPING — not proceeding to real diagrams.")
        return {"toy_pass": False, "toy_result": toy_result, "real_result": None}

    print("TOY CHECK PASSED (W1 = 1.75 exactly, certificate holds). Proceeding to real data.\n")

    # ---------------------------------------------------------------
    # REAL DATA: pair R2
    # ---------------------------------------------------------------
    diagram_A = [[0.0000502938373715227,1.1338674306273389],[0.02374422275925721,1.098231215451977],[0.0006372495567582546,1.0670519953556767],[0.007967110088969605,1.0611165218251322],[0.014145622608898427,1.0595771024144012],[0.0075150967147227426,1.0475367812634515],[0.0018949829799719301,1.0288790836565291],[0.0053926350175577936,1.0282476922195325],[0.013864621799503917,1.0361345745860444],[0.010030107180330292,1.0207501419333973],[0.018126413682674782,1.0253633111364677],[0.002163943810455578,0.9980985425811332],[0.0037399033724849072,0.9990260645975523],[0.00007805872489132072,0.9913199607985458],[0.010227854677054296,0.9957540690236181],[0.001585953756300344,0.9801309009164466],[0.0038797109822143647,0.9712951744812466],[0.010316041757437493,0.9769741915642218],[0.007597311177484124,0.9732355686799167],[0.004416079699591509,0.9690765649051385],[0.00044352137353172275,0.9632551756227753],[0.0015420541889926709,0.9604206351193828],[0.0025702274741878786,0.9504427386520293],[0.002837232218849909,0.9446002296760216],[0.003293414085431917,0.9422148441387926],[0.07347005865572671,1.007972053933519],[0.011173806051945782,0.9436629248809438],[0.005150470132275059,0.9269820185126008],[0.0025472097561662116,0.9216075080319786],[0.0036912499726113194,0.9197540460951296],[0.00021389021347506336,0.915397295353684],[0.001229029158607206,0.9093982288033102],[0.13328353845404448,1.0389517703706248],[0.004625210139729134,0.9043522958365605],[0.0014958709396627992,0.8915938234669459],[0.004784071952238968,0.8947892398794471],[0.002081741303795869,0.8919422855331808],[0.011436630504290434,0.8954368993427316],[0.00022379348170763495,0.8754263403111365],[0.005334125963697235,0.8714554530095567]]
    diagram_B = [[0.015994367071813245,1.2658072114750065],[0.012053137657255065,1.164817727261911],[0.00446021485695098,1.1074281310733216],[0.0001360398028308027,1.0979734140725625],[0.006073810747707161,1.090002196171133],[0.002539325417600072,1.0709157714954682],[0.005550044154979358,1.0591844042903995],[0.0017574232922444113,1.0536798885135286],[0.01170080244868915,1.0308072831514232],[0.004370945208076778,1.0128487895053948],[0.018863028671065697,1.0242909588574753],[0.00015726068231039343,1.0034281317051028],[0.002422603816466497,1.0032092187681743],[0.0010821815515487717,0.9970907649206779],[0.003448715016970494,0.9887069191198622],[0.0006725755363547893,0.9760277754436821],[0.0003928970651064469,0.9708263032361502],[0.010698276135748199,0.9810260118988967],[0.0001429410462018913,0.9665612478941104],[0.0024463693853384334,0.9688346448616099],[0.021266090665110697,0.9785951699142567],[0.0004165417380835315,0.9486642243308655],[0.005182326730433263,0.943808540863243],[0.015529313480134558,0.9495706459095825],[0.00047754407707388573,0.9310363439764575],[0.0014949418152981565,0.9176216630099734],[0.0469498660459637,0.9585266097965166],[0.0002309748859919488,0.9097223857951007],[0.0365432605965695,0.9443755480657787],[0.000019269989704319666,0.906297926684163],[0.03704823811178215,0.9273943015933508],[0.00556586187854288,0.8946688827935491],[0.0009814904827904892,0.8810401717073323],[0.0000882905090537756,0.8684477949005054],[0.00039810409353463016,0.8647373129630598],[0.0018681724604038405,0.8617290931090735],[0.00017647399587214537,0.8591015352538869],[0.001967666527973909,0.8586692061303647],[0.00701991482241835,0.8618095722803255],[0.1497804260716642,1.0020919912123238]]

    real_result = wasserstein_certificate(diagram_A, diagram_B, k=30,
                                           verbose=True, label="PAIR R2 (A vs B)")

    print("=== FINAL SUMMARY: PAIR R2 ===")
    print(f"n (from A, after truncation) = {real_result['n']} "
          f"(dropped {real_result['dropped_x']} of {len(diagram_A)})")
    print(f"m (from B, after truncation) = {real_result['m']} "
          f"(dropped {real_result['dropped_y']} of {len(diagram_B)})")
    print(f"W1_primal = {real_result['W1_primal']}")
    print(f"W1_lp     = {real_result['W1_lp']}")
    print(f"max dual-feasibility violation = {real_result['max_dual_violation']}")
    print(f"sum(u)+sum(v) = {real_result['dual_sum']}")
    print(f"CERTIFICATE: {'PASS' if real_result['certificate_pass'] else 'FAIL'}")

    return {"toy_pass": True, "toy_result": toy_result, "real_result": real_result}


if __name__ == "__main__":
    main()
