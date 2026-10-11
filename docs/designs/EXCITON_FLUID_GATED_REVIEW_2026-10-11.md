# Independent hostile review: `paper/exciton_fluid_gated.tex` (Gated exciton fluids)

Date 2026-10-11. Reviewer: independent agent, instructed not to trust the author's text. Nothing in the paper, scripts or run
records was modified. All independent computations are in `/mnt/data/xdev-cache/tmp/rev/` (thm.py, u0.py, db.py, ss.py, diel.py,
lat2.py); they do not import any of the author's code.

Verdict in one line: the mathematics (Theorem 1, Eq. u0) is correct and the run-record numbers are reproduced; the paper has
two integrity statements that its own records contradict, a laboratory prediction (L1) that is wrong in the regime it names, an
L4 prediction that is a box-size artefact, and a mis-stated limit on dielectrics (the theorem is stronger than the paper says).

---------------------------------------------------------------------------------------------------------------------------

## BLOCKING (fix before any deposit)

### B1. Integrity statements about the pre-registration are not supported by the record

1. Abstract: "four amendments were written before the affected numbers existed"; Sec. 3 heading "Amendments, all before the
   numbers they affect". A4 in `EXCITON_FLUID_PHASE3_PREREG.md` says of itself: "recorded after the registered D-a/D-d runs and
   while D-g was still running". D-g seeds 1-3 were already on disk: `run_log_g.txt` mtime 09:26:11, the A4 text exists in git
   only in commit `3ed401f` (09:47:27), the same commit that contains the results and `summary.json`. So A4 is, by its own
   words and by git, after (some of) the numbers it affects. It changes no threshold, but the sentence in the abstract is false
   for A4. The same commit also adds the summariser change that reads D-g from the log (`phase3_summarise.py`, diff
   `ae8e43f..3ed401f`), so "made before D-g's own gate was evaluated" is asserted, not demonstrable.
   Fix: say "three amendments (A1-A3) before the numbers they affect; A4 (number of D-g seeds) was recorded while D-g was
   running and committed with the results".
2. Timeline I could verify: reference.json mtime 07:44:26, prereg + dd.rs + reference committed 07:49:52, first Rust output
   (`b.json`) 07:49:57 (5 s later; consistent). A2 committed 08:19:16 after D-b/c/e/f (07:49-07:55) and before any D-a/D-d
   (first 8x8 output `jac_V25.f64` 08:32:01). A3 committed 08:29:29, 2.5 min before the first 8x8 output (08:32:01) but
   *after* the 8x8 D-d runs had visibly been started (a seed takes ~250-430 s, so the first launched ~08:27). Consistent with "no
   number existed", but the margin is minutes and the earlier rotating-frame 16x16 attempt that A3 says was "started, then stopped"
   has no log in the repository (`run_log_attempt1.txt` covers only the laboratory-frame attempt, and was then deleted in
   `3ed401f` although A2 says "kept as `results/phase3/run_log_attempt1.txt`": dangling reference).
3. D-b was registered as "eigenvalue multiset ... sorted by (real, imaginary), to 1e-6 absolute". The registered sorted
   comparison, as implemented in `phase3_summarise.py`, returns **max_sorted_error = 18.2** (`summary.json`, D-b). The PASS is
   decided by a different, greedy nearest-neighbour matching (2.7e-9), introduced in the summariser with a comment that sorting "is
   fragile". I checked independently that the Jacobian is right (below), so the physics outcome stands, but the registered
   criterion as literally written was not met and the paper reports only the replacement ("equals the reference to 2.7e-9") with
   no amendment. Must be disclosed (an A5 note or a footnote in the table), not silently replaced.
4. `results/phase3/exploratory_invalid/` (T8000, T16000, T32000, rtol variants; seed 1 and 2 outputs identical to the t=4000
   values, i.e. the environment overrides were not honoured by the stale binary) is committed but mentioned nowhere. Exploratory
   runs that were discarded as invalid belong in the disclosure ("what failed or had to be changed").

### B2. L1 prediction `dE/dn = U~(0)` is wrong in the regime the protocol itself specifies, and the stated confounder is mischaracterised

Text (Sec. 6, L1): "`dE/dn = U~(0) = (4 pi e^2 d/eps)(1-d/D)` ... low T, below degeneracy", confounder "exchange and correlation
corrections (a *D-independent* offset)". U~(0) is the Hartree (mean-field, uniform-density) coefficient. In the cold / crystalline
regime that L2-L3 and "below degeneracy" refer to, the model's own classical limit gives a chemical-potential slope that is
neither U~(0) nor D-independent in its deviation. I computed d mu/dn = d^2(n E/N)/dn^2 for the classical triangular lattice with
the *exact gated kernel* (mode sum of K0, symmetric gates, d=1; verified that the mode sum reproduces 4 pi d (1-d/D) to 5e-3):

| D/d | n d^2 = 0.003 | 0.01 | 0.03 | 0.1 | 0.3 |
|---|---|---|---|---|---|
| 3  | 0.0   | 0.0   | 0.002 | 0.09 | 0.36 |
| 10 | 0.001 | 0.035 | 0.14  | 0.32 | 0.53 |
| 50 | 0.054 | 0.11  | 0.21  | 0.37 | 0.57 |

(entries are `(d mu/dn)_lattice / U~(0)`). So the ratio to the paper's prediction is 0 to 0.6 and depends on D by orders of
magnitude at low density (for a >> D the lattice energy is exponentially small while U~(0)(1-d/D) is not). The sign of the trend
with D is preserved, so the *fail rule* (slope not independent of D, wrong trend) survives, but the quantitative equality and the
"D-independent offset" sentence are false in the stated regime. The abstract also says U~(0) "fixes the experimental protocol".
Required: state that U~(0) is the mean-field coefficient valid for n d^2 >> 1 (or weak correlation), give the classical-lattice
alternative above as the strong-coupling limit, and delete "D-independent". Also (see M2) the uniform-eps formula is not the
formula for an hBN-encapsulated stack.

(I rate this BLOCKING for Sec. 6 only because a numerical prediction a referee or experimentalist can check is wrong by an
order of magnitude in the regime named; the theorem is unaffected.)

---------------------------------------------------------------------------------------------------------------------------

## MAJOR

### M1. L4 / Fig. 4b: the "shift smaller than V0" is the box average of the gate, a size artefact

I re-solved the stationary single-frequency states independently (own Newton solver on (psi, n_R, omega) with a phase gauge,
rotating-frame Jacobian eigenvalues for stability; `ss.py`, no author code). It reproduces the author's states:

| V0 | author omega - 0.5 (t=16000, exploratory) | mine (L=8, M=8, sigma=1.5) | author n_centre | mine |
|---|---|---|---|---|
| 0.25 | 0.04878 | 0.04878 | 7.068 | 7.068 |
| 0.5  | 0.08761 | 0.08761 | 4.581 | 4.581 |
| 1.0  | 0.14212 | 0.14212 | 1.493 | 1.493 |

Everything stable (largest Re lambda <= 1e-8 apart from the Goldstone zero). Then, the shift as a function of box size at fixed
gate width sigma = 1.5:

| box | V0=0.1 | 0.25 | 0.5 | 1.0 |
|---|---|---|---|---|
| L=8, 8x8   | 0.0208 | 0.0488 | 0.0876 | 0.1421 |
| L=16, 16x16 | 0.0051 | 0.0113 | 0.0182 | 0.0243 |
| L=32, 32x32 | 0.0013 | 0.0027 | 0.0043 | 0.0055 |

Delta omega falls like 1/L^2 and at small V0 equals the periodic-box mean of the gate, `V0 * 2 pi sigma^2 / L^2` (0.0106 vs 0.0110
at V0=0.05, L=8). "0 < Delta omega < V0" is therefore trivially implied by a bounded, non-negative potential averaged over the
box, and the number is a property of the box, not of the condensate. The paper's "increasing with the gate amplitude but smaller
than the local energy shift" is true but carries no information, and `Delta omega -> 0` for a device larger than the gate. L4 as
written ("fail if Delta omega exceeds the independently measured local Stark shift") has no discriminating power and the model
says nothing about whether a real extended condensate locks to one frequency. Also compare (L=16, sigma=3, i.e. the *registered*
geometry): Delta omega = 0.046, 0.077, 0.107, n_centre = 5.84, 2.38, 0.10 for V0 = 0.25, 0.5, 1. The 8x8 run (0.049, 0.088,
0.142; n_centre 7.07, 4.58, 1.49) is not equivalent to it at "the same sigma/L" as A3 asserts: 25 % different in the shift at
V0=1 and a factor 15 in the central density. The slowest stable mode of the registered geometry at V0=1 is 3.2e-4, so the
registered horizon t=4000 (e^{-1.3}) would have failed D-d(ii) far worse.

Resolution check (M=16 on L=8): shifts 0.04898, 0.08806, 0.1432 (0.4-0.8 % from the 8x8 values): grid error is small for these
smooth states; the "small box" is the issue, not the grid.

### M2. U~(0) with a uniform epsilon is not the formula of an hBN/TMD device

By Gauss's law with piecewise epsilon the correction factor is `1 - (d/eps_m)/sum_i(t_i/eps_i)`, not `1 - d/D`; for hBN (eps_z ~ 3)
around a TMD interlayer region the D-dependence over D/d in [3,20] is 0.4 -> 0.86 (eps_m = 1) or 0.82 -> 0.98 (eps_m = 7) rather
than 0.67 -> 0.95. The paper says dielectric mismatch is "outside the model, so the trend is the test", but the numerical size of
the trend, which sets the 10 % pass/fail threshold, is model-dependent.

### M3. The statement on dielectric images is wrong; Theorem 1 is more general than claimed

Sec. 2 "Consequences": Kagome/stripe states "must come from something the model leaves out, which includes dielectric image
charges of weight kappa^n ... *not proved, not tested*". They cannot. For any laterally homogeneous layered dielectric
eps(z) (isotropic or uniaxial, any number of hBN/TMD/vacuum slabs) between grounded planes, expand in the Sturm-Liouville modes
`-(eps phi')' = lambda eps phi`, Dirichlet at the planes: `U(r) = 2 sum_m (phi_m(z_e)-phi_m(z_h))^2 K_0(sqrt(lambda_m) r)` with
`K_0(kappa r) = (1/2) int_0^inf exp(-u - kappa^2 r^2/(4u)) du/u`, a positive combination of functions that are completely
monotone in r^2. I verified the spectral representation numerically on a 4-layer (eps = 3, 8, 0.5, 3) stack against a direct
finite-difference solution of the k-space Green function (agreement 1e-12 relative at k = 0, 0.1, 0.5, 2; `diel.py`). This
supersedes the Poisson argument (it is a sum of squares, the same S_m structure), covers the very devices of Sec. 6, and
removes dielectric images from the list of possible causes (the remaining ones are lateral inhomogeneity, finite gate screening,
disorder, fluctuations, and the status of the lattice theorem). The "Limits" paragraph and the L3 interpretation ("evidence for
one of those") need correcting; the limitations item "Theorem 1 is for ideal grounded metals and a homogeneous dielectric"
should be relaxed.

### M4. L5 is not a prediction of this note; L3 cannot fail and does not test Theorem 1

* L5 (reservoir clamp at gamma/R, condensate slope 1/gamma) is the textbook Wouters-Carusotto/threshold behaviour; its pass or
  fail says nothing about Theorem 1 or about any gate this paper tested, yet the table header is "Prediction (from this note)" and
  the Decision rule makes L1 and L5 "the first experiments". The two live in different samples by the paper's own regime paragraph.
  Also "slope 1/gamma" is an absolute density slope that requires an absolute calibration of both P and n.
* L3: "A non-hexagonal pattern ... is not a refutation; a hexagonal pattern is the null result". Neither outcome can falsify
  anything, and a triangular lattice is the ground state of essentially every repulsive 2D monotone interaction, so hexagonal
  order does not discriminate the CM kernel from any alternative. The Sec. 6 opening ("measurements that can fail") is not met by
  L3, L4 or L6.

### M5. "exactly where q > 1" (Fig. 4c caption) and the D-e threshold

Five step sizes were tested: q = 0.29, 0.59, 0.73 succeed, 1.17, 2.93 fail. That brackets 1 between 0.73 and 1.17 (a factor
1.6); "exactly" is not shown. Also the implicit stage is a *linear diagonal* decay solved by fixed point, so D-e is a unit test of
a known contraction condition, not evidence about the module on a nonlinear stiff stage; the text is mostly honest about this
but the abstract's "solver stack tested" is generous.

---------------------------------------------------------------------------------------------------------------------------

## MINOR

1. D-d failure explanation. The box says "the gated state relaxes more slowly". The linearised slowest decay rates about the
   author's own gated states are 2.13e-3 (V0=0.25), 1.81e-3 (0.5), 1.42e-3 (1.0) versus 2.39e-3 ungated: 10-40 % slower. The
   dominant reason is that the registered horizon was calibrated on a 1e-3 perturbation while the gated state is O(1) away from the
   uniform start (residual at t=4000 of 3.9e-4 = e^{-1.42e-3*4000} ~ 3.4e-3 times an O(0.1) amplitude). And V0=0 failed at 1.6e-7
   vs 1e-7 for the same reason (noise 1e-3 x e^{-9.6} ~ 7e-8 x O(2)): predictable from the prereg's own numbers before the run.
2. D-a (above threshold) starts at the closed-form state plus 1e-3 noise, so it checks the steady state and its linear stability,
   not the basin of attraction. Only "below" starts away from the answer. Say so in the table.
3. Table, D-a: "within ... of the closed form" mixes relative (n, n_R) and absolute (omega) tolerances without saying so.
4. Table row D-d (iii): the three shifts are medians over the t=4000 states (not yet stationary; they differ from the t=16000
   values by 5e-7 to 5e-5). Immaterial, but "0.0488, 0.0876, 0.1422" are t=4000 numbers while the discussion mixes both.
5. Fig. 4b title "all modes stable": a Re lambda = 0 Goldstone point is plotted. Legend says "CVODE Jacobian"; it is a central
   difference Jacobian of the right-hand side, not CVODE's. Fig. 2 (b) plots S/2(1-e^{-sd^2}) under the label "measure
   mu(s) >= 0" (it is a rescaled S(s)); (c) y-axis "U(r) d/2" and label "h = 4d" overlaps the curve; the cover figure does not say
   V0, t or what is interpolated. Fig. 3 (a): 8x8 data drawn as smooth bicubic images (disclosed in the caption), line-cut
   abscissae are cell-centred (0.5...7.5) while the gate is centred on node 4 (the minimum appears at 4.5).
6. "Cost" paragraph: "A Krylov or banded implicit solver is the obvious requirement": with a spectral Laplacian the Jacobian
   is dense, so banded does not apply; matrix-free Krylov or an exponential/split treatment of the linear kinetic term is meant.
7. Reproducibility: `Cargo.toml` depends on `/home/xavkal/xdev/rusty-SUNDIALS-c3/...` absolute paths; the text says "tag v11.6.0"
   while the prereg says tree 996aaf0706e1 / commit 5db8041. Give the single identifier. The D-g JSON never existed (A4);
   only three log lines; fine, but say "3 of 10 seeds" in the abstract paragraph that lists D-g.
8. Citations: only [1] is cited in the text; OpenAI2026, CohnKumar2007, WoutersCarusotto2007, Qi2026 and Hindmarsh2005 appear
   only in the bibliography, and "Qi et al." in Sec. 3 is uncited. I could not verify Qi et al., Nature 654, 629 (2026) or the
   OpenAI "family 090" item; the other three are correct. Sec. 1 cites "the brief that prompted it", a private document.
9. Model parameters (g_R/g = 25, gamma_R/gamma = 2000, i.e. a reservoir 2000x faster than the condensate) are chosen for
   stiffness and stability, as the prereg discloses; real polariton/exciton reservoirs are typically slower than the condensate.
   Sec. 3's "the model one would write for short-lived excitons or polaritons" should add "with reservoir parameters chosen for
   solver stiffness". L5's "clamped at gamma/R" is correct for the model; a real long-lived reservoir is not clamped this way.
10. "Kagome or stripe ground states ... must come from something the model leaves out" is conditional on an AI-generated,
    unrefereed lattice theorem (the paper says so two sentences later; the hedge should be in the same sentence).
11. L1's "fail if the slope is independent of D within 10 % over D/d in [3,20]" is a rule on the *slope*; the single-gate device
    is predicted to have the ungated slope exactly (U~(0) = 4 pi d as D -> infinity); that null control is worth stating.

---------------------------------------------------------------------------------------------------------------------------

## What I checked and found correct (so the author need not redo it)

**Theorem 1 and the algebra.**
* Images: grounded planes z = +h1, z = -h2, period P = 2(h1+h2), +charge at z0 + Pn and -charge at 2h1 - z0 + Pn. I verified by
  hand that V vanishes on both planes (second plane: 2h1 - z0 - P = -2h2 - z0). Correct, including the paper's formula.
* Poisson summation formula quoted: correct (`sum_n e^{-s(c+Pn)^2} = sqrt(pi/s) P^{-1} sum_m e^{-pi^2 m^2/(P^2 s)} cos(2 pi m c/P)`).
* `S_m = 2 - cos 2a - cos 2b - 2cos(b-a) + 2cos(a+b) = 2(1-cos(b-a))(1+cos(a+b))` is correct. Equivalent, and clearer, form:
  `S_m = 2(sin a - sin b)^2` (direct/image difference gives `2 sin(alpha u) sin(alpha u0)` per pair). `S_0 = 0` by neutrality.
* Independent numerics (my own image generator from the Dirichlet construction, N=300-400 periods; 8 geometries asymmetric,
  3 with a layer within 0.01-0.3 of a gate, h from 0.1 to 5): U(r) from direct image sum equals the Laplace integral of the
  Poisson measure to 6 digits at the test point; S(s) from the direct sum equals the Poisson form (relative 1e-9 to 1e-3 where S
  is not 1e-20-small; larger relative differences only where S underflows); S_mode = S_Poisson to 1e-15; minimum S >= 0 over
  s in [1e-4, 1e4]. No negative value.
* Single-gate and gate-free limits are pointwise limits of CM functions, hence CM: correct, and their finite limits exist.
* "Cannot be engineered to break" is correctly bounded in the Consequences paragraph for ideal grounded metals and a
  homogeneous dielectric; but see M3 (the bound is too tight on the dielectric side) and note it does not cover floating gates
  (not stated) or finite gate screening (stated).

**Eq. (u0).** Gauss's law: sheets -sigma at z_e, +sigma at z_h between grounded plates; fields E_out = x, E_mid = x - 4 pi sigma,
potential drop zero gives `x = 4 pi sigma d/D`; field energy per area `W = 2 pi sigma^2 d (1 - d/D)`, i.e. `U~(0) = 4 pi d (1-d/D)`
(e^2/eps = 1). Independent numerical integration of the image sum over five geometries (h1, h2 from 0.15 to 4, d from 0.1 to 0.5):
agreement to 4e-4 to 6e-4 relative (cutoff-limited), independent of the layer position as the formula says. It is a textbook
capacitor result (and `D -> infinity` gives the familiar ungated `4 pi d`); describing it as "not new" is correct. The uniaxial
rescaling remark (U~(0) = 4 pi d/eps_z (1-d/D)) is consistent.

**Numbers against the run records.** Recomputed from the `.jsonl`, `.json`, logs:
* D-a above (10 seeds): relative n error 1.24e-12, n_R 5.9e-14, |omega - 0.5| 4.8e-13, std(n) <= 6.1e-7 (gate 1e-5);
  below: max|psi| 1.59e-11, n_R relative 5.2e-16. Match the abstract/table.
* D-b: Jacobian eigenvalues vs my own finite-difference model (independently written rhs): Hungarian-matched max difference
  1.2e-7 (limited by my own delta = 1e-6 differences); largest real part 1.4e-10 (Rust) / 5.6e-13 (mine); next -2.38e-3 (so
  "2.4e-3" is right). Table values 2.7e-9, 1.4e-10 reproduced from the files. See B1.3 for the sorting issue.
* D-c: norm 1.55e-11, energy 4.06e-10, 6464 steps: match.
* D-d at t=4000: budget max 2.5e-15 / 8.0e-9 / 1.0e-7 / 5.0e-7 for V0 = 0, 0.25, 0.5, 1; residual max 1.63e-7 / 1.12e-5 /
  7.64e-5 / 3.93e-4 (paper: 5.0e-7, 3.9e-4, 1.6e-7: match). Median omega - 0.5: 0.04878, 0.08762, 0.14217 (paper 0.0488, 0.0876,
  0.1422). Centre/corner densities 7.07/11.08, 4.58/11.92, 1.49/13.06; max current 7.6e-3, 1.3e-2, 1.2e-2: match. Ratios to V0
  0.195, 0.175, 0.142 ("0.20, 0.18, 0.14"): match.
* Exploratory t=16000 (seed 1): residual 3.3e-10 / 6.0e-8 / 1.04e-8 / 8.7e-9, budget 0 / 2.4e-14 / 1.1e-13 / 6.9e-13: match;
  rtol variants 7.63e-5 at 1e-8 and 1e-12 (steps 104388 vs 422469): the residual is not integration error. Note the V0=0.25
  continuation passes by a factor 1.7 only (6.0e-8 vs 1e-7).
* D-e: ok at h = 0.005, 0.01, 0.0125; error "failed to converge at stage 1" at 0.02, 0.05; trajectory difference 7.34e-6
  (limit 1e-3). 0.017071 = 1/(200 (1 - 1/sqrt2)): correct.
* D-f: errors 1.62e-5, 3.86e-6, 9.47e-7, ratios 4.20, 4.07: correct.
* D-g: n = 219.99992, n_R = 0.05, omega = 8.85, budget 0.524: check by hand: n_R = gamma/(2R) = 0.05 and
  P = gamma_R n_R + R n n_R gives n = 220, budget (gamma n + 0.. ) mismatch (32-21)/21 = 0.524. Correct.
* Cost claims (A2, A3: 43 ms/step at 768, 1.4 s per t = 20 at 192; ratio ~88 ~ "two orders") consistent with the per-run
  `seconds` fields (194-507 s at 8x8).
* Model identities used in the text: n = P/gamma - gamma_R/R, P_th = gamma gamma_R/R = 20, budget identity from the sum of the
  two equations: correct.

**Labelling.** D-d (iii) is labelled "hypothesis" in the prereg and in the table; the exploratory continuation is in a separate
`failbox`, marked "Exploratory ... (not gates, one seed each)", and the table's registered column says **fail**. Good practice.
The abstract states clearly that no data are used, no exciton BEC claim, no Hugging Face data or GNN, and the text states "not
SUNDIALS' ARKode" and that the model is not that of the Qi et al. experiment. I found no overclaim on those items beyond the
points above. The regime paragraph of Sec. 6 (the driven model does not apply to long-lived interlayer excitons) is right and
should also be said next to L4/L5 in the table, since L4 is listed with "pump fixed above condensation threshold" without
saying which sample.

---------------------------------------------------------------------------------------------------------------------------

## Suggested minimal repair list (in order)

1. Correct the A4 sentence in the abstract and Sec. 3; add the D-b sorted-criterion disclosure and the invalid exploratory runs;
   restore or drop the reference to `run_log_attempt1.txt`.
2. Rewrite L1: mean-field regime statement, the lattice-limit table (or a sentence), drop "D-independent offset", give the
   series-dielectric formula.
3. Replace Theorem 1's dielectric limit by the Sturm-Liouville remark (M3) and correct the L3 interpretation accordingly.
4. Re-state L4 as what it is (box-average) or drop the numerical claim; add the L = 8, 16, 32 table as the evidence that the
   shift is size-dependent; note that A3's "same sigma/L" is not equivalent.
5. Relabel L5 as a textbook control, not a prediction of this note; relabel L3 as non-discriminating.
