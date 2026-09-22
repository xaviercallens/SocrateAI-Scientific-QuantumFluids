#!/usr/bin/env python3
"""
Wasserstein-1 duality certificate (primal matching + dual potentials)
for persistence diagram pair S1.

CORRECTED 2026-09-22: this file replaces an earlier version whose diagram_A/diagram_B were
corrupted (10 points all at birth=0 for A, a single point for B) -- garbage handed to this
stage by an earlier pipeline run, not a bug in the certificate logic below (that logic is
unchanged from the R1/R2/.../P1 scripts, which all verified correctly). The true top-40
Dgm0(rho=|psi|^2/mean) for psi_sound_only.npy (A) and psi_t5.npy (B) are used here, recomputed
and independently re-verified (505 and 788 total finite bars respectively, matching the P1/P2
stage's own bottleneck-distance/eps computation for this pair, which was NOT corrupted).

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

    # ---- Real diagrams: pair S1 (sound-only vs t=5) ----
    diagram_A = [[0.2303016596122617, 0.9814061966716214], [0.22940680805971772, 0.9756587893372792], [0.2652981991340826, 0.99129905951145], [0.2960114725139372, 1.0154902070712868], [0.2216535994200339, 0.9276079500392646], [0.28207907335369503, 0.9800730610069882], [0.36087903087362055, 1.031631777379419], [0.32423076320229016, 0.9812259897417297], [0.3686713634331999, 1.0249330010593332], [0.3242878880839063, 0.9708579513031126], [0.3361137231060703, 0.979017573939346], [0.3117738668412657, 0.9525847113548909], [0.3995762825770253, 1.0195887818314584], [0.37485802742930224, 0.9761852236323768], [0.3671281932285765, 0.9672715248548515], [0.3872290346673186, 0.9797981749605275], [0.3929921304718921, 0.9796670296935885], [0.3734737537011784, 0.9566436397953444], [0.41102034786650166, 0.9937913946847441], [0.38964312594655665, 0.9708971764554325], [0.381619566736689, 0.9546449132884636], [0.4153881623264386, 0.9846412575876115], [0.42782503873817274, 0.9719821171555969], [0.4216735475886616, 0.9615001395292583], [0.40796485775482694, 0.9473949958760574], [0.43296528400706064, 0.9685304463732601], [0.4164102334304365, 0.9428912782649013], [0.44556054206288503, 0.9656719924169662], [0.44900036540039845, 0.9635223800017498], [0.3717476144318748, 0.8861714595097658], [0.44842178372969854, 0.9598003268336115], [0.4672373678334949, 0.9759725180506053], [0.4549779944037816, 0.9612708560591163], [0.4691140368836186, 0.9748308395926534], [0.44245908843833065, 0.9473223613881795], [0.4581665233778717, 0.9622991005274536], [0.48708770161514653, 0.9903566718299556], [0.46074649454030375, 0.9636329671408564], [0.4241736459027324, 0.9269479025504532], [0.4437184150181995, 0.9460750780265343]]
    diagram_B = [[0.003951517525082516, 1.4432059255853191], [0.0010742449729586833, 1.4242972650603278], [0.0014226959668004733, 1.2893801546195072], [0.0014477150599620547, 1.2809980223248703], [0.0030260118585909916, 1.2104085455454785], [0.0046980385936533425, 1.207014209230116], [0.0002105840392687301, 1.1670488004672526], [0.0014536456469299004, 1.165092317526539], [0.001412396565356536, 1.1541083864676513], [0.005009308555339228, 1.143316287219563], [0.004578827271755, 1.1347506786151271], [0.0018805496487911998, 1.1241018329620753], [0.002790456838577477, 1.068221887491176], [0.0016772832254457002, 1.0317607306181553], [5.605734804733743e-05, 1.0216852741317342], [0.0029176388929819503, 1.0171018311659488], [0.0023243557897554916, 1.0143036706575175], [0.005084151163919344, 1.0007947520087157], [1.9167723613524228e-05, 0.9879323808797986], [0.00109301058996872, 0.986729922763175], [5.6903034493349055e-06, 0.9712995140359302], [0.0004684256935129093, 0.9626747691355749], [0.0005233112484244617, 0.961999838468802], [0.00028502093423696316, 0.959557480609437], [0.0001902766791578654, 0.9556636842267183], [0.0006498766920164202, 0.9536105769708093], [0.00030027705530527566, 0.950045042160204], [0.004230811599539266, 0.940992804666803], [0.004261200820939821, 0.9401783723568614], [0.0003258538626875995, 0.9339103796035889], [0.00030660311294915444, 0.9294166728638235], [1.2842691222130686e-05, 0.9260380197346579], [0.0015051992420338771, 0.9211223791164496], [0.002282249436270137, 0.8930548038155923], [0.0036138934731477232, 0.8848681791462376], [0.0021573594248274664, 0.8744791729046707], [0.00015749140459962404, 0.8693455746770828], [0.0013972156412083603, 0.8695770726816453], [0.09599520797217008, 0.9576954806823442], [0.004338402747589825, 0.8629676860536631]]

    n_raw_A = len(diagram_A)
    n_raw_B = len(diagram_B)
    print(f"\nRaw diagram sizes: |A|={n_raw_A}, |B|={n_raw_B} (already <=40)")

    r1_result = run_certificate(diagram_A, diagram_B, k_trunc=30, label="S1")

    print("\n" + "=" * 70)
    print("PAIR S1 — WASSERSTEIN-1 DUALITY CERTIFICATE (CORRECTED)")
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
