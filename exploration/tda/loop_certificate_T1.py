#!/usr/bin/env python3
"""
Wasserstein-1 duality certificate (primal matching + dual potentials)
between two persistence diagrams, pair T1.

Self-contained: does not import from any other exploration script.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment, linprog


def truncate_to_k_longest(points, k=30):
    """Truncate a list of (birth, death) points to the k longest bars
    (by death-birth). Returns (truncated_points, n_dropped)."""
    pts = np.asarray(points, dtype=float)
    n = len(pts)
    if n <= k:
        return pts, 0
    pers = pts[:, 1] - pts[:, 0]
    order = np.argsort(-pers)  # descending persistence
    keep = order[:k]
    dropped = n - k
    return pts[keep], dropped


def linf(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1]))


def cost_to_diag(p):
    return (p[1] - p[0]) / 2.0


def build_cost_matrix(X, Y):
    n = len(X)
    m = len(Y)
    size = n + m
    C = np.full((size, size), 1e9, dtype=float)

    # i<n, j<m : X[i] to Y[j]
    for i in range(n):
        for j in range(m):
            C[i, j] = linf(X[i], Y[j])

    # i<n, j>=m : X[i] to its own dedicated diagonal column (j-m)==i
    for i in range(n):
        j = m + i
        C[i, j] = cost_to_diag(X[i])

    # i>=n, j<m : Y[j] to its own dedicated diagonal row (i-n)==j
    for j in range(m):
        i = n + j
        C[i, j] = cost_to_diag(Y[j])

    # i>=n, j>=m : dummy-to-dummy, free
    C[n:, m:] = 0.0

    return C


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    W1_primal = C[row_ind, col_ind].sum()
    return W1_primal, row_ind, col_ind


def solve_dual(C):
    """Solve the transportation LP and extract dual potentials.

    Variables x_ij >= 0 for i in 0..size-1 (rows), j in 0..size-1 (cols),
    flattened row-major: var index = i*size + j.
    Row constraint i: sum_j x_ij = 1  (size constraints)
    Col constraint j: sum_i x_ij = 1  (size constraints)
    Drop the LAST row constraint (redundant), keep all size-1 remaining
    row constraints and all size col constraints => size-1+size total.
    """
    size = C.shape[0]
    n_vars = size * size

    c = C.flatten()

    A_rows = []
    b_rows = []
    # row constraints, drop the last one (index size-1)
    for i in range(size - 1):
        row = np.zeros(n_vars)
        row[i * size:(i + 1) * size] = 1.0
        A_rows.append(row)
        b_rows.append(1.0)
    # column constraints, all of them
    for j in range(size):
        row = np.zeros(n_vars)
        row[j::size] = 1.0
        A_rows.append(row)
        b_rows.append(1.0)

    A_eq = np.array(A_rows)
    b_eq = np.array(b_rows)

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")

    n_row_kept = size - 1
    n_col = size

    marginals = res.eqlin.marginals
    u_kept = marginals[:n_row_kept]
    v = marginals[n_row_kept:n_row_kept + n_col]

    u = np.zeros(size)
    u[:n_row_kept] = u_kept
    u[n_row_kept] = 0.0  # dropped row constraint's dual set to 0

    return res, u, v


def check_and_fix_sign(u, v, C, tol=1e-7):
    size = C.shape[0]
    U = u.reshape(-1, 1)
    V = v.reshape(1, -1)
    viol = U + V - C
    max_viol = viol.max()
    sign_used = "as-is (u,v)"
    if max_viol > tol:
        # try negating both
        u2, v2 = -u, -v
        U2 = u2.reshape(-1, 1)
        V2 = v2.reshape(1, -1)
        viol2 = U2 + V2 - C
        max_viol2 = viol2.max()
        if max_viol2 < max_viol:
            u, v = u2, v2
            max_viol = max_viol2
            sign_used = "negated (-u,-v)"
    return u, v, max_viol, sign_used


def certificate(X, Y, verbose_label=""):
    C = build_cost_matrix(X, Y)
    W1_primal, row_ind, col_ind = solve_primal(C)
    res, u, v = solve_dual(C)
    W1_lp = res.fun

    u, v, max_viol, sign_used = check_and_fix_sign(u, v, C)
    dual_sum = u.sum() + v.sum()

    feas_ok = max_viol <= 1e-6
    rel_tol = 1e-6
    dual_ok = abs(dual_sum - W1_primal) <= rel_tol * max(1.0, abs(W1_primal))

    passed = feas_ok and dual_ok

    print(f"--- {verbose_label} ---")
    print(f"n={len(X)}, m={len(Y)}")
    print(f"W1_primal = {W1_primal!r}")
    print(f"W1_lp     = {W1_lp!r}")
    print(f"sign convention used: {sign_used}")
    print(f"max dual-feasibility violation = {max_viol!r}")
    print(f"sum(u)+sum(v) = {dual_sum!r}")
    print(f"feasibility OK: {feas_ok}, dual==primal OK: {dual_ok}")
    print(f"CERTIFICATE PASS: {passed}")
    print()

    return {
        "n": len(X),
        "m": len(Y),
        "W1_primal": W1_primal,
        "W1_lp": W1_lp,
        "sign_used": sign_used,
        "max_dual_violation": max_viol,
        "dual_sum": dual_sum,
        "pass": passed,
    }


def main():
    # ------------------------------------------------------------------
    # Step 0: toy sanity check from the recipe's own test paragraph
    # X=[(2,5),(3,6),(4,7)], Y=[(2,5),(3,6),(4,4.5)] -> W1_primal=W1_lp=1.75
    # ------------------------------------------------------------------
    toy_X = [(2, 5), (3, 6), (4, 7)]
    toy_Y = [(2, 5), (3, 6), (4, 4.5)]
    toy_result = certificate(toy_X, toy_Y, verbose_label="TOY SANITY CHECK")

    toy_pass = (
        abs(toy_result["W1_primal"] - 1.75) < 1e-6
        and abs(toy_result["W1_lp"] - 1.75) < 1e-6
        and toy_result["pass"]
    )

    if not toy_pass:
        print("TOY CHECK FAILED. STOPPING before real data.")
        print(toy_result)
        return

    print("Toy check PASSED (W1_primal = W1_lp = 1.75, certificate holds).")
    print()

    # ------------------------------------------------------------------
    # Real diagrams A and B for pair T1
    # ------------------------------------------------------------------
    diagram_A = [[0.003951517525082516,1.4432059255853191],[0.0010742449729586833,1.4242972650603278],[0.0014226959668004733,1.2893801546195072],[0.0014477150599620547,1.2809980223248703],[0.0030260118585909916,1.2104085455454785],[0.0046980385936533425,1.207014209230116],[0.0002105840392687301,1.1670488004672526],[0.0014536456469299004,1.165092317526539],[0.001412396565356536,1.1541083864676513],[0.005009308555339228,1.143316287219563],[0.004578827271755,1.1347506786151271],[0.0018805496487911998,1.1241018329620753],[0.002790456838577477,1.068221887491176],[0.0016772832254457002,1.0317607306181553],[0.00005605734804733743,1.0216852741317342],[0.0029176388929819503,1.0171018311659488],[0.0023243557897554916,1.0143036706575175],[0.005084151163919344,1.0007947520087157],[0.000019167723613524228,0.9879323808797986],[0.00109301058996872,0.986729922763175],[0.0000056903034493349055,0.9712995140359302],[0.0004684256935129093,0.9626747691355749],[0.0005233112484244617,0.961999838468802],[0.00028502093423696316,0.959557480609437],[0.0001902766791578654,0.9556636842267183],[0.0006498766920164202,0.9536105769708093],[0.00030027705530527566,0.950045042160204],[0.004230811599539266,0.940992804666803],[0.004261200820939821,0.9401783723568614],[0.0003258538626875995,0.9339103796035889],[0.00030660311294915444,0.9294166728638235],[0.000012842691222130686,0.9260380197346579],[0.0015051992420338771,0.9211223791164496],[0.002282249436270137,0.8930548038155923],[0.0036138934731477232,0.8848681791462376],[0.0021573594248274664,0.8744791729046707],[0.00015749140459962404,0.8693455746770828],[0.0013972156412083603,0.8695770726816453],[0.09599520797217008,0.9576954806823442],[0.004338402747589825,0.8629676860536631]]
    diagram_B = [[0.000050293837371522824,1.1382681482195758],[0.003511875034467488,1.0956808830142761],[0.0003233938999536967,1.0670519953556794],[0.0006372495567582561,1.0561431507602534],[0.005351206006931498,1.0594552372614965],[0.0007071961705353691,1.0486170452310137],[0.0014215590077940115,1.036134574586047],[0.0002317715753286388,1.0319561384285925],[0.0012095139605283413,1.0268986497778576],[0.0003653966941567544,1.0246714180183678],[0.00287875422622102,1.0210107767153747],[0.0032815689692532023,1.0023646745839199],[0.0017758860890792834,0.9980846776817386],[0.0007846679504800452,0.9958430126378428],[0.00007805872489132091,0.9928927732574877],[0.0015859537563003478,0.9772443118201519],[0.001822202112881377,0.9769741915642243],[0.0011244302511545267,0.9753126052558304],[0.0007440493422807525,0.9740885312861],[0.002499706389554631,0.9716582307127061],[0.000002485264489894843,0.9687313671354666],[0.0015420541889926745,0.9607902054895392],[0.00006494944432195316,0.9515878352717637],[0.002837232218849916,0.9471118762088171],[0.002585881096012618,0.9406062217921798],[0.07253815808196022,1.0076863836774315],[0.011173806051945808,0.9435145231150543],[0.00021389021347506388,0.9266691169426394],[0.0012612817134498736,0.9269820185126031],[0.00019476113356032177,0.919875793770131],[0.0025472097561662177,0.9177216111850969],[0.1300614636381208,1.0389517703706272],[0.001229029158607209,0.9067570006601741],[0.0010518100516508188,0.9030579835157052],[0.0013475363235903562,0.9019875227603585],[0.0009363471527227778,0.8965302979597461],[0.0005672155388582227,0.8961301453286061],[0.00011527668382481086,0.891593823466948],[0.0002237934817076355,0.8780808932882517],[0.00024459417390378953,0.8720177222983059]]

    print(f"Diagram A raw count: {len(diagram_A)}")
    print(f"Diagram B raw count: {len(diagram_B)}")

    X, dropped_A = truncate_to_k_longest(diagram_A, k=30)
    Y, dropped_B = truncate_to_k_longest(diagram_B, k=30)

    print(f"Dropped from A (beyond 30 longest bars): {dropped_A}")
    print(f"Dropped from B (beyond 30 longest bars): {dropped_B}")
    print()

    result = certificate(X, Y, verbose_label="PAIR T1: Diagram A vs Diagram B")

    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"pair_id: T1")
    print(f"toy_check: PASS, W1={toy_result['W1_primal']!r}")
    print(f"n (A after truncation) = {result['n']}")
    print(f"m (B after truncation) = {result['m']}")
    print(f"W1_primal = {result['W1_primal']!r}")
    print(f"W1_lp     = {result['W1_lp']!r}")
    print(f"max dual-feasibility violation = {result['max_dual_violation']!r}")
    print(f"sum(u)+sum(v) = {result['dual_sum']!r}")
    print(f"CERTIFICATE: {'PASS' if result['pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
