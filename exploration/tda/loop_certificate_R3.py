"""
Wasserstein-1 duality certificate (primal matching + dual potentials).

Self-contained script implementing WASSERSTEIN_RECIPE exactly as specified.
Does not import from any other exploration script.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment, linprog


def truncate_to_k_longest(diagram, k=30):
    """Truncate a list of (birth, death) pairs to the k longest bars
    (by death-birth), before anything else. Returns (truncated_list, n_dropped)."""
    n = len(diagram)
    if n <= k:
        return list(diagram), 0
    pts = sorted(diagram, key=lambda p: (p[1] - p[0]), reverse=True)
    kept = pts[:k]
    dropped = n - k
    return kept, dropped


def linf(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def diag_cost(p):
    return (p[1] - p[0]) / 2.0


def build_cost_matrix(X, Y):
    n = len(X)
    m = len(Y)
    BIG = 1e9
    size = n + m
    C = np.zeros((size, size), dtype=float)

    # rows 0..n-1 = X points ; rows n..n+m-1 = diagonal slots reserved for Y points
    # cols 0..m-1 = Y points ; cols m..m+n-1 = diagonal slots reserved for X points

    # block i<n, j<m : Linf(X[i], Y[j])
    for i in range(n):
        for j in range(m):
            C[i, j] = linf(X[i], Y[j])

    # block i<n, j>=m : cost(X[i], Delta) if (j-m)==i else BIG
    for i in range(n):
        for j in range(m, m + n):
            C[i, j] = diag_cost(X[i]) if (j - m) == i else BIG

    # block i>=n, j<m : cost(Y[j], Delta) if (i-n)==j else BIG
    for i in range(n, n + m):
        for j in range(m):
            C[i, j] = diag_cost(Y[j]) if (i - n) == j else BIG

    # block i>=n, j>=m : 0 (dummy-to-dummy)
    for i in range(n, n + m):
        for j in range(m, m + n):
            C[i, j] = 0.0

    return C


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    w1 = C[row_ind, col_ind].sum()
    return w1, row_ind, col_ind


def solve_dual(C, n, m):
    """Solve the transportation LP: variables x_ij >= 0, i in 0..n+m-1 (rows),
    j in 0..m+n-1 (cols), minimize sum(C*x), s.t. every row sums to 1 and every
    column sums to 1. Drop the LAST row constraint (redundant). Read
    res.eqlin.marginals for duals of kept constraints; dual of dropped row = 0.
    """
    nrows = n + m  # number of row-constraints (= size)
    ncols = m + n  # number of col-constraints (= size), same as size
    size = n + m
    assert C.shape == (size, size)

    nvars = size * size
    c = C.flatten()  # x_ij flattened row-major: index = i*size + j

    # Row constraints: for each i, sum_j x_ij = 1  -> nrows constraints
    # Col constraints: for each j, sum_i x_ij = 1  -> ncols constraints
    # Drop the LAST row constraint (index nrows-1)

    A_rows = []
    b_rows = []
    for i in range(nrows):
        if i == nrows - 1:
            continue  # drop last row constraint
        row = np.zeros(nvars)
        row[i * size:(i + 1) * size] = 1.0
        A_rows.append(row)
        b_rows.append(1.0)

    for j in range(ncols):
        row = np.zeros(nvars)
        row[j::size] = 1.0  # column j: entries i*size+j for i in 0..size-1
        A_rows.append(row)
        b_rows.append(1.0)

    A_eq = np.array(A_rows)
    b_eq = np.array(b_rows)

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"linprog failed: {res.message}")

    marginals = res.eqlin.marginals
    n_row_constraints_kept = nrows - 1

    u = np.zeros(nrows)
    u[:nrows - 1] = marginals[:n_row_constraints_kept]
    u[nrows - 1] = 0.0

    v = np.zeros(ncols)
    v[:] = marginals[n_row_constraints_kept:n_row_constraints_kept + ncols]

    return res.fun, u, v


def check_dual_feasibility(C, u, v, tol=1e-7):
    size = C.shape[0]
    max_violation = -np.inf
    for i in range(size):
        for j in range(size):
            slack = C[i, j] - (u[i] + v[j])
            viol = -slack  # positive if u_i+v_j > C[i,j] (violation)
            if viol > max_violation:
                max_violation = viol
    return max_violation


def compute_certificate(X, Y, label="", k_truncate=30, verbose=True):
    n_orig = len(X)
    m_orig = len(Y)

    X_t, dropped_x = truncate_to_k_longest(X, k=k_truncate)
    Y_t, dropped_y = truncate_to_k_longest(Y, k=k_truncate)

    n = len(X_t)
    m = len(Y_t)

    if verbose:
        print(f"--- {label} ---")
        print(f"Diagram A: {n_orig} points -> truncated to {n} (dropped {dropped_x})")
        print(f"Diagram B: {m_orig} points -> truncated to {m} (dropped {dropped_y})")

    C = build_cost_matrix(X_t, Y_t)

    w1_primal, row_ind, col_ind = solve_primal(C)

    w1_lp, u, v = solve_dual(C, n, m)

    # Check sign convention: u_i + v_j <= C[i,j] + tol
    max_viol_pos = check_dual_feasibility(C, u, v)
    sign_used = "as-is"
    if max_viol_pos > 1e-6:
        # try negating both
        u_neg = -u
        v_neg = -v
        max_viol_neg = check_dual_feasibility(C, u_neg, v_neg)
        if max_viol_neg < max_viol_pos:
            u, v = u_neg, v_neg
            max_viol_pos = max_viol_neg
            sign_used = "negated"

    dual_sum = u.sum() + v.sum()

    pass_a = max_viol_pos <= 1e-6
    rel_tol = 1e-6 * max(abs(w1_primal), 1.0)
    pass_b = abs(dual_sum - w1_primal) <= rel_tol

    cert_pass = pass_a and pass_b

    if verbose:
        print(f"n={n}, m={m}")
        print(f"W1_primal = {w1_primal}")
        print(f"W1_lp     = {w1_lp}")
        print(f"sign convention used: {sign_used}")
        print(f"max dual-feasibility violation = {max_viol_pos}")
        print(f"sum(u)+sum(v) = {dual_sum}")
        print(f"certificate (a) feasibility holds: {pass_a}")
        print(f"certificate (b) sum(u)+sum(v)==W1_primal (rel 1e-6): {pass_b}")
        print(f"CERTIFICATE PASS: {cert_pass}")
        print()

    return {
        "n": n, "m": m,
        "dropped_x": dropped_x, "dropped_y": dropped_y,
        "w1_primal": w1_primal, "w1_lp": w1_lp,
        "sign_used": sign_used,
        "max_dual_violation": max_viol_pos,
        "dual_sum": dual_sum,
        "pass_a": pass_a, "pass_b": pass_b,
        "cert_pass": cert_pass,
    }


def main():
    # --- Toy example self-check (from recipe's own test paragraph) ---
    X_toy = [(2, 5), (3, 6), (4, 7)]
    Y_toy = [(2, 5), (3, 6), (4, 4.5)]

    toy_result = compute_certificate(X_toy, Y_toy, label="TOY SELF-CHECK", k_truncate=30)

    toy_pass = (
        abs(toy_result["w1_primal"] - 1.75) < 1e-6
        and abs(toy_result["w1_lp"] - 1.75) < 1e-6
        and toy_result["cert_pass"]
    )

    print(f"TOY CHECK: W1_primal={toy_result['w1_primal']}, W1_lp={toy_result['w1_lp']}, "
          f"expected 1.75, cert_pass={toy_result['cert_pass']} -> "
          f"{'PASS' if toy_pass else 'FAIL'}")
    print()

    if not toy_pass:
        print("TOY CHECK FAILED. STOPPING — not proceeding to real diagrams.")
        return {"toy_pass": toy_pass, "toy_result": toy_result}

    # --- Real diagrams A vs B, pair R3 ---
    diagram_A = [[0.0077121145056996375,1.3129249337115483],[0.003135985893335008,1.185512887878427],[0.0004134011348233287,1.1058379577128912],[0.007237531846234516,1.0840706683045942],[0.00037702780420224423,1.0502172072802765],[0.0002656704902778136,1.0461266798726168],[0.00010185408084855131,1.0037345018827852],[0.03775231187945199,1.0293333713894663],[0.0005174905897253613,0.9842619596077052],[0.007155483570037625,0.990727883629545],[0.003504584422770233,0.9797085280671073],[0.0026417956801562015,0.9756790951178675],[0.0007013951182646775,0.9728984777248278],[0.0005632432692091272,0.9700473235523881],[0.0009217715681267945,0.9699738987738119],[0.002821213305863299,0.9496492664598322],[0.0012335774432453597,0.947236575037191],[0.015149662341917988,0.9594275240017011],[0.0006875621425977051,0.9434771137229919],[0.0006459279765837185,0.9431800545384019],[0.005601293596688022,0.9466480233498226],[0.006098962290201526,0.9366520133929792],[0.0015254510551603155,0.927731457808752],[0.001146766530169313,0.9249293671920059],[0.002715405028676788,0.9239504702374676],[0.0030541153548575097,0.9239882388160101],[0.003345941662964952,0.9213514488732228],[0.020295246468472156,0.9368742987931035],[0.011324700334308503,0.9278310053247332],[0.002764081318049204,0.9122271765882085],[0.0035696237975834477,0.9115179540262255],[0.006399776011357374,0.9104332006834384],[0.0010629288478293587,0.899687926225237],[0.016304393048452024,0.9070840192823982],[0.0008156964777124832,0.8881867024843457],[0.004320464507118938,0.8898283905784998],[0.012973113300201001,0.8942088833970134],[0.03861696112863799,0.8968129978791228],[0.023504058509536224,0.8759448997232723],[0.005606450605139051,0.8573367523971439]]

    diagram_B = [[0.0019169460283184696,1.1493047191945591],[0.009823081211180676,1.1099373162305517],[0.0024252211753534973,1.0876010328853492],[0.0024776287083850073,1.0817919487632297],[0.03878291068195416,1.110755769216339],[0.011509803022503325,1.0717746036130633],[0.010228845359855797,1.0565228784118945],[0.0035529372118163005,1.012723489440503],[0.004771002161254158,1.011806645071668],[0.003361797177149024,0.9977063392151528],[0.013083648923647499,1.006726414047654],[0.02046016943489374,1.008819599832337],[0.0015003124111136418,0.9887520809332571],[0.0031463316186796193,0.9887817147825849],[0.13831630916768262,1.1169291531283774],[0.0001383622066485923,0.9770096728785679],[0.011870755343337844,0.985281369802806],[0.000692310903716708,0.9618957465718222],[0.0015062886527829598,0.9618581575802689],[0.00005754916951288425,0.9568479142295262],[0.0018204319752176336,0.9548396679699152],[0.008610374704487986,0.9606995838947667],[0.00035604515105020157,0.9415054185572139],[0.00009239286839765865,0.9409935463060182],[0.0024853350649058545,0.9424972330865342],[0.00005341062116382521,0.9395724217159719],[0.001234090799874947,0.922193928200903],[0.00689161283453767,0.9265849377172408],[0.00801215203825364,0.926529674001393],[0.002145385573543458,0.9091373091507562],[0.00005794797106851123,0.9045735875609875],[0.0001905692901860312,0.9044455782331371],[0.0006235071152995875,0.9034316057295497],[0.0004116829860338558,0.9021490476421752],[0.10775900383696452,1.0071604998227053],[0.000032732293710481965,0.8991237402559329],[0.001254558815437946,0.8971152848337328],[0.0022268515925870044,0.8974507766690363],[0.00007422227976040144,0.893860207886181],[0.015297351898365152,0.9068069979167078]]

    real_result = compute_certificate(diagram_A, diagram_B, label="PAIR R3 (A vs B)", k_truncate=30)

    print("=== FINAL SUMMARY ===")
    print(f"Toy self-check: {'PASS' if toy_pass else 'FAIL'} (W1={toy_result['w1_primal']})")
    print(f"Pair R3: n={real_result['n']}, m={real_result['m']}")
    print(f"  dropped from A: {real_result['dropped_x']}, dropped from B: {real_result['dropped_y']}")
    print(f"  W1_primal = {real_result['w1_primal']}")
    print(f"  W1_lp     = {real_result['w1_lp']}")
    print(f"  sign convention: {real_result['sign_used']}")
    print(f"  max dual violation = {real_result['max_dual_violation']}")
    print(f"  sum(u)+sum(v) = {real_result['dual_sum']}")
    print(f"  CERTIFICATE PASS: {real_result['cert_pass']}")

    return {"toy_pass": toy_pass, "toy_result": toy_result, "real_result": real_result}


if __name__ == "__main__":
    main()
