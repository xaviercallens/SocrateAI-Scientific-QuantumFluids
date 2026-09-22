# Pre-registration: the cellular Wasserstein stability bound on the seven closed-loop pairs

Direction 1 of `paper/closed_loop.tex` §7.1 (published as v1.8.1, DOI 10.5281/zenodo.22895282), taken
through its gate. Committed **before** any script is written or any number on the left-hand side is
computed. Changes after this commit are dated amendments, as in `CLOSED_LOOP_PREREG.md`.

## 0. The theorem, as read from the primary source

Skraba and Turner, *Wasserstein stability for persistence diagrams*, arXiv:2006.16824 (v7, 10 July
2025), Theorem 4.6 (Cellular Wasserstein Stability), read from the PDF, not recalled:

> Let `f, g : K → ℝ` be two monotone functions on a finite CW complex `K`. Then
> (i) `W_p(Dgm f, Dgm g) ≤ ‖f − g‖_p`, with `‖f − g‖_p^p = Σ_{σ ∈ K} |f(σ) − g(σ)|^p` over **all** cells;
> (ii) `W_p(Dgm_k f, Dgm_k g)^p ≤ Σ_{dim σ ∈ {k, k+1}} |f(σ) − g(σ)|^p`.

Conventions that the theorem carries and that this round adopts *as its own metric* (§2.1 of the paper):

* distances in the plane are `ℓ_p`; the distance from `(a, b)` to the diagonal is the perpendicular
  `ℓ_p` distance `2^{(1−p)/p} |b − a|` (so `|b − a|` for `p = 1`, `|b − a|/√2` for `p = 2`);
* essential classes: `‖(a, ∞) − (b, ∞)‖_p = |a − b|`, and an essential class is never matched to a
  finite one or to the diagonal (cost `∞`);
* `W_p(Dgm f, Dgm g)` in (i) is the *total* distance, `(Σ_k W_p(Dgm_k f, Dgm_k g)^p)^{1/p}` over all
  degrees, each degree matched separately (Definition 2.5 of the source).

This is **not** the `ℓ^∞` ground cost used by the certificates of `CLOSED_LOOP_RESULTS.md` P5. For
`p = 1` the `ℓ_1` ground cost dominates `ℓ^∞`, so the theorem also bounds the earlier certified numbers,
but the comparison is made here in the theorem's own metric, and the earlier `ℓ^∞` values are reported
alongside only as a cross-check, never as the left-hand side.

Not used: Cohen-Steiner–Edelsbrunner–Harer–Mileyko (FoCM 10:127, 2010). Its right-hand side is the sup
norm to a fractional power, which the closed-loop round already showed is set by vortex-core pixels.

## 1. The cell complex and the cell values

GUDHI's `PeriodicCubicalComplex(top_dimensional_cells=ρ, periodic_dimensions=…)` is the
*T-construction*: each pixel is a 2-cell carrying its own value; every lower cell carries the **minimum**
of the values of the top cells containing it (Bleile–Garin–Heiss–Maggs–Robins, arXiv:2102.11397, and
`src/quantumfluids/tda/cubical.py`). On an `N × M` array with both axes periodic that is `NM` pixels,
`2NM` edges, `NM` vertices; along a non-periodic axis of length `M` there are `M + 1` vertex positions
and boundary cells take the minimum over the pixels that exist. The seven pairs all live on one
complex each (the resolution pairs by the restriction rule of `CLOSED_LOOP_PLAN.md`: fine field
restricted to the coarse grid), so `f` and `g` are two monotone functions on the *same* `K` and the
theorem applies literally.

`‖f − g‖_p` is therefore an exact finite sum, computed once per pair from the two arrays, **before** the
diagrams are compared.

## 2. Controls (all must pass exactly before any pair's left-hand side is looked at)

* **C1 (the cell values are GUDHI's).** An independent union-find over the 1-skeleton I build (vertices
  and edges with the values of §1, elder rule) must reproduce GUDHI's `Dgm_0` (T, same periodicity)
  **exactly** — same multiset of finite `(birth, death)` pairs, same essential birth — on every field
  used in this round (all 12 arrays of the seven pairs). This is the D0-style known-answer control: if
  the cell values were not GUDHI's, the diagrams would not agree.
* **C2 (hand-computed known answer, tight case).** The eight-point cycle of `CLOSED_LOOP_PREREG.md` C1:
  `f = (1,5,2,6,3,7,4,8)`, `g = f` with `v₆ := 4.5` (1D periodic, T-construction: 8 pixels-as-edges,
  8 vertices with the minimum of their two pixels). Hand values, exact:
  `Dgm_0 f = {(2,5),(3,6),(4,7)}`, `Dgm_0 g = {(2,5),(3,6),(4,4.5)}`, essential `(1,∞)` on both.
  Cell differences: pixel 6 changes by `5/2`; both neighbouring vertices keep their value
  (`min(3,7) = min(3,4.5) = 3`, `min(7,4) = min(4.5,4) = 4`). So `‖f − g‖_1 = ‖f − g‖_2 = 5/2`.
  `W_1` (ℓ₁ ground): match `(4,7) ↔ (4,4.5)` at cost `5/2` (the alternative, both to the diagonal,
  costs `3 + 1/2`), so `W_1 = 5/2`; `W_2 = 5/2` likewise. **The bound is tight on this example**:
  `W_1 = ‖f − g‖_1`, `W_2 = ‖f − g‖_2`. Pass = these four numbers exactly (rational arithmetic).
  For contrast, the `ℓ^∞`-ground `W_1` of the previous round on the same example was `7/4` (certified
  in `lean_src/WassersteinCertificate.lean`); the script must reproduce that too when told to use
  `ℓ^∞`, as the check that the two conventions are the ones I think they are.
* **C3 (exact known answer on real data).** Take `f = ρ` of pair T1's first field, find the birth pixel
  of its deepest finite `H_0` bar (largest `death − birth`), and set `g = f` with that pixel raised by
  `δ = 0.01 · (death − birth)`. That pixel is a strict local minimum, so all nine cells it touches (the
  pixel, four edges, four vertices) have it as their minimum and all change by exactly `δ`:
  `‖f − g‖_1 = 9δ`, `‖f − g‖_2 = 3δ`, and the part-(ii) `k = 0` sums are `8δ` and `√8 δ`. The diagram
  changes by moving that one birth: `W_1 = W_2 = δ` (ℓ_p ground, birth moves horizontally). Pass =
  these values to `1e-12` relative, and the bound (i) holds with slack exactly `9` (`p = 1`) and `3`
  (`p = 2`). If the perturbed pixel is not a strict local minimum in 8-connectivity, or `δ` exceeds the
  gap to the next value in its basin, the control is re-chosen (deepest bar whose birth pixel is a
  strict minimum) and that is recorded, not silently done.
* **C4 (negative).** The certificate machinery must *reject* a wrong left-hand side: feeding the
  Hungarian plan of pair T1 with the dual potentials of pair T2 must fail feasibility or tightness.
  (Same role as the previous round's C3.)

**Stop rule.** If any of C1–C4 fails, the bug is found first; no pair's `W_p` is reported.

## 3. Pairs, quantities, and what "informative" means

Pairs: exactly the seven of `CLOSED_LOOP_PREREG.md` (R1, R2, R3, T1, T2, S1, P1), same arrays
(`data/generated/kinetic_tda/psi_t{5,10,20}.npy`, `psi_n512_t{5,10,20}.npy`, `psi_sound_only.npy`,
`f_S1_t80.npy`, `f_S2_t80.npy`), same normalisation `ρ = |ψ|²/⟨|ψ|²⟩`, same restriction rule for R1–R3,
P1 periodic in `x` only. No pair is added or dropped after this commit.

For each pair and `p ∈ {1, 2}`:

* `B_p^(i) = ‖f − g‖_p` over all cells; `B_p^(ii,0)` = the part-(ii) sum for `k = 0` (vertices and edges)
  to the power `1/p`;
* `W_p^(0) = W_p(Dgm_0 f, Dgm_0 g)` on the **full** diagrams (all finite bars plus the essential class),
  `W_p^(1)` likewise for `Dgm_1` (finite bars plus its essential classes), and the total `W_p`;
* every `W_p^(k)` is computed as a primal assignment (`scipy.optimize.linear_sum_assignment` on the
  augmented `(n+m) × (m+n)` matrix of `p`-th powers of `ℓ_p` costs) **and** certified by dual potentials
  from the LP (`scipy.optimize.linprog`, HiGHS, sparse constraint matrix), feasibility and tightness
  checked by an independent function exactly as in `loop_certificate_*.py`; if the full-diagram LP is
  too large for the machine, the certificate is done on the `k = 100` longest bars and the primal on the
  full diagram, and that limitation is written down as such;
* the **trivial bound** `Z_p = W_p(Dgm f, ∅) + W_p(Dgm g, ∅)` (each term the `ℓ_p` cost of sending
  every point to the diagonal, plus nothing for essential classes, which both diagrams share), which
  bounds `W_p(Dgm f, Dgm g)` by the triangle inequality with no theorem at all;
* the **slack** `S_p = B_p / W_p` and the **vacuity ratio** `V_p = B_p / Z_p`. The theorem's bound is
  *informative* on a pair iff `V_p < 1`: it says something the triangle inequality did not.

Predictions, pass/fail fixed now:

| # | Statement | Criterion |
|---|---|---|
| P1 | `W_p ≤ B_p^(i)` and `W_p^(0) ≤ B_p^(ii,0)` for every pair, `p = 1, 2` | holds; a violation is a bug in this pipeline, not in the theorem, and stops the round |
| P2 | R1–R3 (resolution): `V_1 ≥ 1` on all three — the `ℓ_1` cell norm of the resolution difference exceeds the total persistence of both diagrams | reported as PASS if all three `V_1 ≥ 1`; this is the **negative** expectation that the kill of §7.1 anticipated |
| P3 | R1–R3: `V_2 ≥ 1` as well | reported; if `V_2 < 1` on any resolution pair, the `p = 2` bound is informative where the bottleneck bound was not, and P2's kill does not apply |
| P4 | P1 (phase space, the only informative bottleneck pair): `V_1 < 1` | PASS/FAIL |
| P5 | T1, T2, S1: reported, no prediction; `S_p` and `V_p` tabulated | reported |
| P6 | slack: `S_1 ≥ 10` on every GP pair (the diagrams are at least an order of magnitude closer than the fields, in the theorem's own metric) | reported as PASS if all seven; this is the measurable statement about *looseness* that survives even when P2 makes the bound vacuous |
| P7 | the `ℓ^∞`-ground `W_1` on the top-30 truncation of the previous round is ≤ the `ℓ_1`-ground full-diagram `W_1` of this round on every pair | consistency; a violation is a bug |

**Kill (written into §7.1 of the published paper, honoured here).** If P2 and P3 both PASS, no
Wasserstein stability theorem makes the `ξ/Δx = 4` vs `8` comparison informative, and the conclusion to
write is that one: the resolution comparison is not a perturbation in any `ℓ_p` sense, only a
measurement of how loose the bound is (P6). If P2 FAILS (some `V_1 < 1`), the bound is informative and
the paper's next question is which bars it protects — but that question is *not* pre-registered here
and would need its own document.

## Amendment A1 (2026-09-22, after the first control run, before any pair was opened)

C2's hand value for `W_2` was wrong. The script (its first run, controls only) returned
`W_2 = 2.1506…`, not `5/2`; checked by hand again: for `p = 2` matching `(4,7) ↔ (4,4.5)` costs
`5/2`, but sending both to the diagonal costs `((3/√2)² + (1/(2√2))²)^{1/2} = (37/8)^{1/2} = 2.1506…`,
which is cheaper. The correct hand value is `W_2 = √(37/8)`, the bound `W_2 ≤ ‖f − g‖_2 = 5/2` holds
and is **not** tight for `p = 2` (it is tight for `p = 1`). The script's expected value is corrected
to `√(37/8)`; nothing else changes. The pipeline caught my arithmetic, which is what C2 is for.

## 4. What is not done in this round

* No Lean. The general weak-duality theorem of `WassersteinCertificate.lean` already covers every
  certificate produced here; formalising Theorem 4.6 itself (a statement about persistence modules over
  a CW complex) is out of reach of the current library and is not attempted.
* No new simulation. Directions 2 (BKT: needs a finite-temperature run) and 3 (Fricke/K3: a literature
  gate) are handled in the paper's discussion only, with their gate results, not with numbers.
* No workflow agents between stages: after the S1 lesson, one script computes and one script checks,
  and the check reads the arrays again from disk.
