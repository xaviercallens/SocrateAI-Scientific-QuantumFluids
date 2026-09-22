#!/usr/bin/env python3
"""
Wasserstein-1 duality certificate (primal matching + dual potentials) for
persistence diagram pair T2. Self-contained; does not import from any other
exploration script.

Recipe implemented exactly as specified by the task:
  1. Truncate each diagram to the k=30 longest bars (by death-birth), report drops.
  2. Ground cost: Linf between off-diagonal points; (d-b)/2 to the diagonal.
  3. Primal: (n+m)x(n+m) cost matrix, linear_sum_assignment.
  4. Dual: same transportation problem as an LP, drop last row constraint,
     read res.eqlin.marginals, check sign convention, verify feasibility and
     strong duality.
  5. Report n, m, W1_primal, W1_lp, max dual violation, sum(u)+sum(v), PASS/FAIL.

Toy self-check must reproduce W1_primal = W1_lp = 1.75 before touching real data.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment, linprog

BIG = 1e9
K = 30


def truncate_k_longest(diagram, k=K):
    """diagram: list of (birth, death). Return (truncated_list, n_dropped)."""
    pts = np.array(diagram, dtype=float)
    n = len(pts)
    if n <= k:
        return pts, 0
    persistence = pts[:, 1] - pts[:, 0]
    order = np.argsort(-persistence)  # descending
    keep_idx = order[:k]
    dropped = n - k
    return pts[keep_idx], dropped


def build_cost_matrix(X, Y):
    """X: (n,2) array, Y: (m,2) array. Returns (n+m)x(n+m) cost matrix C."""
    n = len(X)
    m = len(Y)
    size = n + m
    C = np.full((size, size), BIG, dtype=float)

    # off-diagonal block: rows 0..n-1 (X), cols 0..m-1 (Y) -> Linf
    if n > 0 and m > 0:
        # broadcast Linf
        diff = np.abs(X[:, None, :] - Y[None, :, :])  # (n,m,2)
        linf = diff.max(axis=2)  # (n,m)
        C[0:n, 0:m] = linf

    # X[i] -> its own dedicated diagonal column (cols m..m+n-1)
    x_diag_cost = (X[:, 1] - X[:, 0]) / 2.0 if n > 0 else np.array([])
    for i in range(n):
        C[i, m + i] = x_diag_cost[i]

    # Y[j] -> its own dedicated diagonal row (rows n..n+m-1)
    y_diag_cost = (Y[:, 1] - Y[:, 0]) / 2.0 if m > 0 else np.array([])
    for j in range(m):
        C[n + j, j] = y_diag_cost[j]

    # dummy-to-dummy block: rows n..n+m-1, cols m..m+n-1 -> 0
    C[n:n + m, m:m + n] = 0.0

    return C


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    w1 = C[row_ind, col_ind].sum()
    return w1, row_ind, col_ind


def solve_dual(C):
    """Transportation LP with equality constraints:
       every row sums to 1, every column sums to 1.
       Variables x_ij, i in 0..size-1 (rows), j in 0..size-1 (cols), flattened
       row-major: var index = i*size + j.
       Drop the LAST row constraint (redundant), keep all column constraints
       and all but the last row constraint.
    """
    size = C.shape[0]  # = n+m = m+n (square, since rows=n+m, cols=m+n)
    num_vars = size * size
    c = C.flatten()  # row-major: c[i*size+j] = C[i,j]

    # Row constraints: sum_j x_ij = 1 for each i (drop last row i = size-1)
    row_constraints = []
    for i in range(size - 1):  # drop last row
        a = np.zeros(num_vars)
        a[i * size:(i + 1) * size] = 1.0
        row_constraints.append(a)

    # Column constraints: sum_i x_ij = 1 for each j (keep all)
    col_constraints = []
    for j in range(size):
        a = np.zeros(num_vars)
        a[j::size] = 1.0
        col_constraints.append(a)

    A_eq = np.array(row_constraints + col_constraints)
    b_eq = np.ones(A_eq.shape[0])

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")

    n_row_kept = size - 1
    n_col = size

    marginals = res.eqlin.marginals  # length n_row_kept + n_col

    u_kept = marginals[:n_row_kept]
    v = marginals[n_row_kept:n_row_kept + n_col]

    # dual of dropped row (last row) = 0
    u = np.concatenate([u_kept, [0.0]])

    return res, u, v


def check_sign_and_feasibility(C, u, v):
    """Check u_i + v_j <= C[i,j] + 1e-7 for all i,j.
       If broadly violated, try negating both u and v.
       Returns (u_final, v_final, sign_used, max_violation)
    """
    size = C.shape[0]

    def max_violation(u_, v_):
        # u_i + v_j - C[i,j], want <= 1e-7; violation = max(0, that)
        lhs = u_[:, None] + v_[None, :]
        viol = lhs - C
        return viol.max()  # if <=1e-7 everywhere, this is <=1e-7

    viol_pos = max_violation(u, v)
    viol_neg = max_violation(-u, -v)

    if viol_pos <= 1e-7:
        return u, v, "as-read (no negation)", viol_pos
    elif viol_neg <= 1e-7:
        return -u, -v, "negated", viol_neg
    else:
        # neither works cleanly; pick the smaller violation, report it
        if viol_pos <= viol_neg:
            return u, v, "as-read (FAILED feasibility, smaller violation kept)", viol_pos
        else:
            return -u, -v, "negated (FAILED feasibility, smaller violation kept)", viol_neg


def run_certificate(X_list, Y_list, label="", truncate=True):
    print(f"\n=== {label} ===")
    if truncate:
        X, n_dropped_x = truncate_k_longest(X_list, K)
        Y, n_dropped_y = truncate_k_longest(Y_list, K)
    else:
        X = np.array(X_list, dtype=float)
        Y = np.array(Y_list, dtype=float)
        n_dropped_x = 0
        n_dropped_y = 0

    n = len(X)
    m = len(Y)
    print(f"n (X points used) = {n}, dropped from X = {n_dropped_x}")
    print(f"m (Y points used) = {m}, dropped from Y = {n_dropped_y}")

    C = build_cost_matrix(X, Y)

    w1_primal, row_ind, col_ind = solve_primal(C)
    print(f"W1_primal = {w1_primal!r}")

    res, u_raw, v_raw = solve_dual(C)
    w1_lp = res.fun
    print(f"W1_lp = {w1_lp!r}")

    u, v, sign_used, max_viol = check_sign_and_feasibility(C, u_raw, v_raw)
    print(f"Sign convention used: {sign_used}")
    print(f"Max dual-feasibility violation (u_i+v_j - C[i,j]) = {max_viol!r}")

    dual_sum = u.sum() + v.sum()
    print(f"sum(u)+sum(v) = {dual_sum!r}")

    rel_tol = 1e-6
    strong_duality_ok = abs(dual_sum - w1_primal) <= rel_tol * max(1.0, abs(w1_primal))
    feasibility_ok = max_viol <= 1e-6

    cert_pass = strong_duality_ok and feasibility_ok
    print(f"Strong duality check (sum(u)+sum(v) == W1_primal, rel_tol 1e-6): {strong_duality_ok}")
    print(f"Feasibility check (max violation <= 1e-6): {feasibility_ok}")
    print(f"CERTIFICATE: {'PASS' if cert_pass else 'FAIL'}")

    return {
        "n": n,
        "m": m,
        "n_dropped_x": n_dropped_x,
        "n_dropped_y": n_dropped_y,
        "W1_primal": w1_primal,
        "W1_lp": w1_lp,
        "max_dual_violation": max_viol,
        "dual_sum": dual_sum,
        "sign_used": sign_used,
        "cert_pass": cert_pass,
    }


def main():
    # ---------- TOY SELF-CHECK ----------
    X_toy = [(2, 5), (3, 6), (4, 7)]
    Y_toy = [(2, 5), (3, 6), (4, 4.5)]

    toy_result = run_certificate(X_toy, Y_toy, label="TOY SELF-CHECK", truncate=False)

    toy_w1_primal = toy_result["W1_primal"]
    toy_w1_lp = toy_result["W1_lp"]

    toy_ok = (
        abs(toy_w1_primal - 1.75) < 1e-6
        and abs(toy_w1_lp - 1.75) < 1e-6
        and toy_result["cert_pass"]
    )

    print(f"\nTOY CHECK EXPECTED W1 = 1.75; got W1_primal={toy_w1_primal}, W1_lp={toy_w1_lp}")
    print(f"TOY CHECK: {'PASS' if toy_ok else 'FAIL'}")

    if not toy_ok:
        print("\nTOY CHECK FAILED. STOPPING before real data as instructed.")
        return {"toy_ok": False, "toy_result": toy_result}

    # ---------- REAL DIAGRAMS: PAIR T2 ----------
    diagram_A = [[0.000050293837371522824,1.1382681482195758],[0.003511875034467488,1.0956808830142761],[0.0003233938999536967,1.0670519953556794],[0.0006372495567582561,1.0561431507602534],[0.005351206006931498,1.0594552372614965],[0.0007071961705353691,1.0486170452310137],[0.0014215590077940115,1.036134574586047],[0.0002317715753286388,1.0319561384285925],[0.0012095139605283413,1.0268986497778576],[0.0003653966941567544,1.0246714180183678],[0.00287875422622102,1.0210107767153747],[0.0032815689692532023,1.0023646745839199],[0.0017758860890792834,0.9980846776817386],[0.0007846679504800452,0.9958430126378428],[0.00007805872489132091,0.9928927732574877],[0.0015859537563003478,0.9772443118201519],[0.001822202112881377,0.9769741915642243],[0.0011244302511545267,0.9753126052558304],[0.0007440493422807525,0.9740885312861],[0.002499706389554631,0.9716582307127061],[0.000002485264489894843,0.9687313671354666],[0.0015420541889926745,0.9607902054895392],[0.00006494944432195316,0.9515878352717637],[0.002837232218849916,0.9471118762088171],[0.002585881096012618,0.9406062217921798],[0.07253815808196022,1.0076863836774315],[0.011173806051945808,0.9435145231150543],[0.00021389021347506388,0.9266691169426394],[0.0012612817134498736,0.9269820185126031],[0.00019476113356032177,0.919875793770131],[0.0025472097561662177,0.9177216111850969],[0.1300614636381208,1.0389517703706272],[0.001229029158607209,0.9067570006601741],[0.0010518100516508188,0.9030579835157052],[0.0013475363235903562,0.9019875227603585],[0.0009363471527227778,0.8965302979597461],[0.0005672155388582227,0.8961301453286061],[0.00011527668382481086,0.891593823466948],[0.0002237934817076355,0.8780808932882517],[0.00024459417390378953,0.8720177222983059]]

    diagram_B = [[0.0026908844056361537,1.3116148322499959],[0.00004479261514036861,1.1855128878784158],[0.0004134011348233248,1.1060147818908383],[0.0003781875143761103,1.0867696482248106],[0.0002656704902778111,1.0499727072242786],[0.00003880928512232809,1.0424072343968502],[0.032519874579376704,1.0374981146682547],[0.00010185408084855037,0.9987510063805136],[0.0014692472236984562,0.9933589987155068],[0.002822584755591381,0.9855713384641352],[0.0005174905897253564,0.9831444475240579],[0.0005926656373805199,0.9815540838198265],[0.0004918505199709565,0.9728984777248189],[0.00005928872838872267,0.97168231281593],[0.00018402928692900136,0.9645080828718162],[0.00013620135029294257,0.9514208889485758],[0.003969212027780608,0.9500796282958114],[0.00015871831245392753,0.943180054538393],[0.00014250666728813093,0.9420074045973865],[0.0060169791877018475,0.9475005752863593],[0.0009143014682049545,0.9423493042704569],[0.004165262023321631,0.9454065542028022],[0.0013355795072768596,0.9366520133929706],[0.0008833743988439491,0.9278310053247245],[0.0011467665301693024,0.9273192171925266],[0.0006249058464040998,0.9262835058736258],[0.0010304083577638795,0.9252415842229069],[0.0006083423234520717,0.9239882388160016],[0.0005510332436840307,0.9221553620542695],[0.0010829190466054518,0.9159058181769049],[0.0030521820950065548,0.9096632105118645],[0.005470564102362882,0.9104332006834299],[0.002159550810071317,0.9070840192823898],[0.00032361884422996997,0.9025578646751697],[0.0026417956801561768,0.8971266924491902],[0.0008156964777124756,0.8928516551485962],[0.0008884762844731266,0.8898283905784915],[0.03861696112863763,0.9003644007109833],[0.022847158439949274,0.8819585140550246],[0.00033879032716486687,0.8568384029598481]]

    real_result = run_certificate(diagram_A, diagram_B, label="PAIR T2: Diagram A vs Diagram B", truncate=True)

    print("\n" + "=" * 60)
    print("FINAL SUMMARY - PAIR T2")
    print("=" * 60)
    print(f"toy self-check: {'PASS' if toy_ok else 'FAIL'} (W1={toy_w1_primal})")
    print(f"n (from A, after truncation to k={K}) = {real_result['n']} (dropped {real_result['n_dropped_x']})")
    print(f"m (from B, after truncation to k={K}) = {real_result['m']} (dropped {real_result['n_dropped_y']})")
    print(f"W1_primal = {real_result['W1_primal']}")
    print(f"W1_lp = {real_result['W1_lp']}")
    print(f"max dual-feasibility violation = {real_result['max_dual_violation']}")
    print(f"sum(u)+sum(v) = {real_result['dual_sum']}")
    print(f"CERTIFICATE: {'PASS' if real_result['cert_pass'] else 'FAIL'}")

    return {"toy_ok": toy_ok, "toy_result": toy_result, "real_result": real_result}


if __name__ == "__main__":
    main()
