#!/usr/bin/env python3
"""
Wasserstein-1 duality certificate (primal matching + dual potentials)
for persistence diagram pair R1.

Self-contained: does not import from any other exploration script.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment, linprog


def truncate_topk(points, k=30):
    """Truncate a diagram to the k longest bars (death-birth). Returns
    (truncated_points, n_dropped)."""
    pts = np.asarray(points, dtype=float)
    n = len(pts)
    if n <= k:
        return pts, 0
    pers = pts[:, 1] - pts[:, 0]
    order = np.argsort(-pers)  # descending persistence
    keep = order[:k]
    dropped = n - k
    return pts[keep], dropped


def build_cost_matrix(X, Y):
    """Build the (n+m)x(m+n) cost matrix per the recipe."""
    n = len(X)
    m = len(Y)
    BIG = 1e9
    size_r = n + m
    size_c = m + n
    C = np.zeros((size_r, size_c), dtype=float)

    # Off-diagonal block: rows 0..n-1 (X), cols 0..m-1 (Y) -> Linf
    if n > 0 and m > 0:
        # Linf(p,q) = max(|b1-b2|,|d1-d2|)
        Xb = X[:, 0][:, None]
        Xd = X[:, 1][:, None]
        Yb = Y[:, 0][None, :]
        Yd = Y[:, 1][None, :]
        C[:n, :m] = np.maximum(np.abs(Xb - Yb), np.abs(Xd - Yd))

    # X[i] -> its own dedicated diagonal column (cols m..m+n-1)
    x_diag_cost = (X[:, 1] - X[:, 0]) / 2.0 if n > 0 else np.array([])
    for i in range(n):
        for j in range(m, m + n):
            C[i, j] = x_diag_cost[i] if (j - m) == i else BIG

    # Y[j] -> its own dedicated diagonal row (rows n..n+m-1)
    y_diag_cost = (Y[:, 1] - Y[:, 0]) / 2.0 if m > 0 else np.array([])
    for i in range(n, n + m):
        for j in range(m):
            C[i, j] = y_diag_cost[i - n] if (i - n) == j else BIG

    # dummy-to-dummy block: rows n..n+m-1, cols m..m+n-1 -> 0
    C[n:n + m, m:m + n] = 0.0

    return C, n, m


def solve_primal(C):
    row_ind, col_ind = linear_sum_assignment(C)
    w1_primal = C[row_ind, col_ind].sum()
    return w1_primal, row_ind, col_ind


def solve_dual(C):
    """Solve the transportation LP and extract dual potentials u_i, v_j."""
    R, Cc = C.shape  # R = n+m rows, Cc = m+n cols
    nvars = R * Cc

    # Row constraints: sum_j x_ij = 1 for each i (flattened index i*Cc+j)
    # Col constraints: sum_i x_ij = 1 for each j
    A_rows = np.zeros((R, nvars))
    for i in range(R):
        A_rows[i, i * Cc:(i + 1) * Cc] = 1.0

    A_cols = np.zeros((Cc, nvars))
    for j in range(Cc):
        A_cols[j, j::Cc] = 1.0

    # Drop the LAST row constraint (redundant), keep all column constraints
    A_eq = np.vstack([A_rows[:-1, :], A_cols])
    b_eq = np.ones(A_eq.shape[0])

    c = C.flatten()

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"linprog failed: {res.message}")

    w1_lp = res.fun

    marginals = res.eqlin.marginals
    # first R-1 marginals -> u_0..u_{R-2}; dual of dropped row (u_{R-1}) = 0
    u = np.zeros(R)
    u[:R - 1] = marginals[:R - 1]
    u[R - 1] = 0.0
    v = marginals[R - 1:]  # length Cc

    return w1_lp, u, v, res


def check_and_fix_sign(C, u, v, n, m):
    """Verify u_i + v_j <= C[i,j] + tol broadly; if it fails broadly, negate
    both u and v and re-check. Returns (u, v, sign_used, max_violation)."""
    R, Cc = C.shape
    tol = 1e-7

    def max_violation(u_, v_):
        UV = u_[:, None] + v_[None, :]
        viol = UV - C
        return np.max(viol)  # want <= tol

    mv_pos = max_violation(u, v)
    # "fails broadly" heuristic: check fraction of entries violating
    def frac_violating(u_, v_):
        UV = u_[:, None] + v_[None, :]
        viol = UV - C
        return np.mean(viol > tol)

    frac_pos = frac_violating(u, v)

    if frac_pos > 0.5:
        # try negated
        u_neg, v_neg = -u, -v
        mv_neg = max_violation(u_neg, v_neg)
        frac_neg = frac_violating(u_neg, v_neg)
        if frac_neg < frac_pos:
            return u_neg, v_neg, "negated", mv_neg
        else:
            return u, v, "as-is", mv_pos
    else:
        return u, v, "as-is", mv_pos


def run_certificate(X_raw, Y_raw, k_trunc=30, label=""):
    X, dropped_x = truncate_topk(X_raw, k=k_trunc)
    Y, dropped_y = truncate_topk(Y_raw, k=k_trunc)
    n = len(X)
    m = len(Y)

    C, n, m = build_cost_matrix(X, Y)

    w1_primal, row_ind, col_ind = solve_primal(C)
    w1_lp, u, v, res = solve_dual(C)

    u, v, sign_used, mv_before_report = check_and_fix_sign(C, u, v, n, m)

    # final max violation report (after sign fix)
    UV = u[:, None] + v[None, :]
    viol = UV - C
    max_violation = np.max(viol)

    dual_sum = u.sum() + v.sum()

    rel_tol = 1e-6
    cert_a = max_violation <= 1e-6
    denom = max(abs(w1_primal), 1e-12)
    cert_b = abs(dual_sum - w1_primal) <= rel_tol * denom
    cert_pass = bool(cert_a and cert_b)

    return {
        "label": label,
        "n": n,
        "m": m,
        "dropped_x": dropped_x,
        "dropped_y": dropped_y,
        "W1_primal": w1_primal,
        "W1_lp": w1_lp,
        "sign_used": sign_used,
        "max_dual_violation": max_violation,
        "dual_sum": dual_sum,
        "cert_a_pass": bool(cert_a),
        "cert_b_pass": bool(cert_b),
        "cert_pass": cert_pass,
    }


def main():
    # ---- Inline sanity check (toy example) ----
    X_toy = [(2, 5), (3, 6), (4, 7)]
    Y_toy = [(2, 5), (3, 6), (4, 4.5)]

    toy_result = run_certificate(X_toy, Y_toy, k_trunc=30, label="toy")

    print("=" * 70)
    print("TOY EXAMPLE SELF-CHECK")
    print("=" * 70)
    for key in ["n", "m", "W1_primal", "W1_lp", "sign_used",
                "max_dual_violation", "dual_sum", "cert_pass"]:
        print(f"  {key}: {toy_result[key]}")

    toy_ok = (
        abs(toy_result["W1_primal"] - 1.75) < 1e-6
        and abs(toy_result["W1_lp"] - 1.75) < 1e-6
        and toy_result["cert_pass"]
    )

    if not toy_ok:
        print("\nTOY CHECK FAILED. STOPPING before real data.")
        print(f"Expected W1_primal=W1_lp=1.75, got "
              f"W1_primal={toy_result['W1_primal']}, W1_lp={toy_result['W1_lp']}, "
              f"cert_pass={toy_result['cert_pass']}")
        return toy_result, None

    print("\nTOY CHECK PASSED (W1_primal = W1_lp = 1.75, certificate holds).")

    # ---- Real diagrams: pair R1 ----
    diagram_A = [[0.023293934304229196,1.440217023595901],[0.010746474609300616,1.4237408613002787],[0.00142269596680047,1.2875166509734148],[0.023255858603355717,1.2809980223248674],[0.009534170107634283,1.210601454967373],[0.01281981824864616,1.20401129465375],[0.0003894465572535744,1.1613583861497343],[0.0075592065314702885,1.1638807729547558],[0.01075405288481696,1.152452349224507],[0.0063320171440933645,1.1385212101012645],[0.010216966750692216,1.1347506786151247],[0.006381590112589404,1.1241018329620729],[0.006284874934236174,1.0688417206042233],[0.0016772832254456965,1.0325229805385507],[0.00005605734804733731,1.0216852741317317],[0.00945061111167234,1.0168409345659424],[0.011003794243261717,1.0113974947869937],[0.00651380255718168,0.9997379829775518],[0.0010479765169803205,0.9879323808797964],[0.0010930105899687177,0.978907316444944],[0.00038626181573234603,0.9707474216554236],[0.0004684256935129082,0.9602300582939547],[0.0013700729994731938,0.9575093219647088],[0.005382705589858535,0.9590686754321907],[0.0036543880655785935,0.9571971070321637],[0.0014114494107402193,0.9525593759559748],[0.001605596496061319,0.9500450421602019],[0.005397418380719792,0.943295745465326],[0.00032585386268759874,0.9310611975433228],[0.000850658224281908,0.9295052008749903],[0.016562830345442443,0.940992804666801],[0.004719840498350189,0.9131560377869214],[0.01631729304167431,0.9217000594444462],[0.00368495996561092,0.8840660282893088],[0.014103688076639014,0.8930548038155903],[0.0013972156412083573,0.8738034713510098],[0.0031526903216783247,0.8732222725268329],[0.000565363624484252,0.8675100065909125],[0.09599520797216986,0.9585034278402893],[0.0006548165404121448,0.8575515256146676]]
    diagram_B = [[0.018435544570044995,1.1806491381036466],[0.00272166738163199,1.1501935745228107],[0.003403056652764537,1.1113263173817443],[0.009601774630152656,1.097036529200369],[0.014929527870783542,1.0930398751757948],[0.006944611258727092,1.0782771189232112],[0.008551024165125199,1.0547992743390489],[0.13897315046627912,1.176082426482938],[0.022130617195879693,1.0246592874458051],[0.0005180714805987715,0.9935886673794896],[0.0004393212838180944,0.9922205769252017],[0.006326611749710959,0.9974595261647686],[0.01132072316832485,0.993883383149311],[0.00012149981667654091,0.979458768885795],[0.006096461166225905,0.9814903342206208],[0.0021057948537137844,0.975034763622293],[0.006736262986556395,0.9757628518623532],[0.0039403161800133524,0.971838919132689],[0.029542704237829148,0.9944614745543546],[0.010558891770570332,0.972894021272901],[0.01613610163555309,0.977352248656522],[0.011452645350991171,0.9659206435619623],[0.00027030289166283026,0.9445103628308749],[0.00020690067777342336,0.9368709694792765],[0.6966375681020408,1.6325248515567408],[0.015109765302732068,0.9493415029614659],[0.013701442288511303,0.944969901175267],[0.0011415266194136375,0.9281062988187111],[0.004523025945546988,0.9290668605537215],[0.00004457445924849096,0.9242245522843142],[0.0023163774119063963,0.9151183520252129],[0.00047709253920874333,0.8897998042655201],[0.011611426549404294,0.8958001925336053],[0.0010860215837102355,0.8791654569667544],[0.004375837731597704,0.8818878514994832],[0.00006225928896505264,0.8769441950596931],[0.005526295876924759,0.8814372768856342],[0.0038148434067675047,0.8774716459419685],[0.0019837493867008726,0.8752870978907061],[0.006861091007798075,0.8699024009143153]]

    n_raw_A = len(diagram_A)
    n_raw_B = len(diagram_B)
    print(f"\nRaw diagram sizes: |A|={n_raw_A}, |B|={n_raw_B} (already <=40)")

    r1_result = run_certificate(diagram_A, diagram_B, k_trunc=30, label="R1")

    print("\n" + "=" * 70)
    print("PAIR R1 — WASSERSTEIN-1 DUALITY CERTIFICATE")
    print("=" * 70)
    print(f"  dropped from A (beyond 30 longest bars): {r1_result['dropped_x']}")
    print(f"  dropped from B (beyond 30 longest bars): {r1_result['dropped_y']}")
    print(f"  n (points used from A): {r1_result['n']}")
    print(f"  m (points used from B): {r1_result['m']}")
    print(f"  W1_primal: {r1_result['W1_primal']!r}")
    print(f"  W1_lp:     {r1_result['W1_lp']!r}")
    print(f"  sign convention used for duals: {r1_result['sign_used']}")
    print(f"  max dual-feasibility violation: {r1_result['max_dual_violation']!r}")
    print(f"  sum(u)+sum(v): {r1_result['dual_sum']!r}")
    print(f"  certificate (a) feasibility holds: {r1_result['cert_a_pass']}")
    print(f"  certificate (b) sum(u)+sum(v)==W1_primal: {r1_result['cert_b_pass']}")
    print(f"  CERTIFICATE PASS/FAIL: {'PASS' if r1_result['cert_pass'] else 'FAIL'}")

    return toy_result, r1_result


if __name__ == "__main__":
    main()
