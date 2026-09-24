# CLAIM LEDGER: SocrateAI-Scientific-QuantumFluids

**Purpose:** Track all empirical/theoretical claims made in this stream. Every claim must have:
1. A clear statement
2. Evidentiary tier (A=citation-verified, B=unit-testable, C=narrative/speculation)
3. Status (PENDING, VERIFIED, DISPUTED, RETRACTED)
4. Source references (LITERATURE_LEDGER.md entry or unit test ID)
5. Date filed and last-updated timestamp

---

## Template entry

```
[CLAIM-001] [TIER-A] [PENDING]
Statement: "The Landau two-parameter form (c, Δ) fits the Godfrin et al. 2021 
           dispersion data to within ±5% on phonon branch."
Source: LITERATURE_LEDGER.md#Godfrin2021, test:dispersion_fit::test_landau_fit
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Blocking M1 definition-of-done.
```

---

## Current claims

```
[CLAIM-001] [TIER-C] [VERIFIED]
Statement: "Fitting the roton branch (Landau parabolic form) to a hand-digitized
           version of Fig. 5 (Godfrin & Krotscheck 2022, [LIT-001], representing
           Godfrin et al. 2021 [LIT-002] data) recovers Delta = 0.7306 +/- 0.0040 meV
           and Q_m = 1.9192 +/- 0.0044 Angstrom^-1, within 1.9% and 0.3% of the
           literature values respectively."
Source: M1_REPORT.md, data/derived/godfrin_2021_fit_results.json,
        test:test_dispersion_fit.py::test_roton_fit_recovers_known_delta_and_qm
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Tier C (digitized fallback data, not raw instrument data — see
       M1_DATA_ACCESS_STRATEGY.md). Validates landau_model.fit_roton_branch
       against real published curve shape, not just synthetic round-trip data.
```

```
[CLAIM-002] [TIER-C] [VERIFIED]
Statement: "The phonon-branch fit (linear form) applied to the same digitized
           Fig. 5 data does NOT recover the literature sound velocity
           c = 1.568 meV*Angstrom (238 m/s); fitted c = 1.10-1.15 meV*Angstrom
           across phonon_q_max in [0.2, 0.6], a stable ~27% deficit."
Source: M1_REPORT.md ("Why the roton fit succeeds and the phonon fit does not")
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Attributed to near-origin visual-reading precision limits of hand
       digitization, not a defect in fit_phonon_branch (which the roton-branch
       success and synthetic recovery tests both support). Filed as a genuine
       negative finding — no adjustment was made to force agreement. Awaiting
       M1-DATA-001 (raw/reduced instrument data) to re-test on Tier-B data.
```

```
[CLAIM-003] [TIER-B] [VERIFIED]
Statement: "Fitting the Landau phonon (linear) and roton (parabolic) forms
           to Godfrin et al. (2021)'s own published dispersion-curve table
           ([LIT-002], arXiv:2012.09067 ancillary file DispersionP0allRange.txt)
           recovers c = 1.5716 +/- 0.0003 meV*Angstrom (0.24% from literature,
           window Q<0.05 Angstrom^-1) and Delta = 0.7442 +/- 0.0005 meV
           (0.04% from literature, window |Q-1.9|<0.2 Angstrom^-1) -- both
           within the M1 tolerance (c +/-5%, Delta +/-10%; PLAN.md)."
Source: M1_REPORT.md Part 1, data/derived/godfrin_2021_ancillary_fit_results.json,
        data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt.meta,
        test:test_godfrin_ancillary.py (10 tests)
Filed: 2026-08-14
Updated: 2026-08-14 (reference values CORRECTED -- see below)
Notes: Tier B — author-published, exact tabulated data, not raw ILL numor
       (M1-DATA-001 still open) but a legitimate substitute for M1's stated
       objective. Supersedes CLAIM-002 (Tier-C phonon-fit failure) for
       practical purposes; CLAIM-002's root-cause diagnosis was confirmed
       correct by this result's fit-window sensitivity scan. M1 milestone
       objective (PLAN.md) met.

CORRECTION 2026-08-14 (LL-10): the agreement percentages originally filed here
       were computed against reference values that were partly invented —
       recalled from memory and misattributed to Cowley-Woods (1971) and
       Glyde et al. (1998), neither of which reports the Landau triple.
       RECOMPUTED against six correctly-attributed determinations from
       Godfrin et al. 2021 Table IV (all natively in meV):

         reference        c %diff   Delta %diff   within tolerance
         godfrin_2021      0.198%       0.329%    yes
         woods_1977        0.198%       0.221%    yes
         stirling          0.198%       0.329%    yes
         andersen          0.198%       0.167%    yes
         gibbs_1999        0.198%       0.221%    yes
         pearce_2001       0.198%       0.032%    yes

       The CONCLUSION is unchanged and is now better supported (six
       independent references rather than one invented number). The fitted
       values themselves never changed; only what they were compared against.

CAVEAT, newly recorded: Godfrin et al.'s own P=0 Delta_R is taken from
       Stirling as an energy-calibration input, so this stream's fit —
       which extracts Delta from THEIR published curve — is partly
       circular with respect to Stirling's value. What the fit
       legitimately demonstrates is that the pipeline RECOVERS the
       parameter encoded in the curve, not that the curve's absolute
       energy scale is independently correct.
```

```
[CLAIM-004] [TIER-B] [VERIFIED]
Statement: "At D = 0 with real initial data, the complexified dyadic shell model
           (adapters: w4_shell_model.shell_dynamics + .integrate) reproduces
           MechanicaFluidorum's independently-written reference implementation
           (exploration/dyadic_cascade.py) EXACTLY -- relative difference
           0.00e+00 on all 9 tested configurations (N=8, nu in {0.1, 0.01,
           0.001}, profiles P1/P2/P3), for both sup_Omega and E_final, across
           ~2.4e6 RK4 steps."
Source: exploration/positive_control_1.py, output archived at
        exploration/positive_control_1.out; Positive Control #1 of
        docs/designs/M2_W4_DISPERSIVE_SHELL.md section 6.
Filed: 2026-08-14
Updated: 2026-08-14
Notes: This is the audited memo's own pre-registered positive control, and it
       confirms three things at once: (i) the conjugated complexification really
       does reduce exactly to the real Katz-Pavlovic model, (ii) the reals really
       are an exactly invariant subspace -- which is what keeps the O5
       Katz-Pavlovic falsification trap applicable, and (iii) this stream's
       integrator implements the same scheme as the reference.

       The agreement is EXACT, not merely within round-off, and the reason was
       checked rather than assumed: k_n = 2^n are exact powers of two, so scaling
       by them shifts the IEEE754 exponent without touching the mantissa. The two
       implementations associate their products differently ((k*a)*a vs k*(a*a)),
       which for a generic k differs at ~1e-14 but for a power of two is
       bit-identical (measured: 0.0 vs 1.42e-14). A shell model with spacing
       lambda != 2 would NOT reproduce exactly and this control would need a
       tolerance -- recorded so the exactness is not mistaken for a general
       property.

       Comparison uses the MAX enstrophy convention because that is what
       MechanicaFluidorum's _simulate actually computes (see
       docs/DEFECT_REPORT_MF_ENSTROPHY.md). Having both conventions available
       -- audit ruling O1 -- is what made a like-for-like comparison possible.
```

```
[CLAIM-005] [TIER-B] [VERIFIED]
Statement: "sup_t Omega does not converge in the horizon T for a purely dispersive
           regulator (nu = 0, D > 0) in the complexified dyadic shell model. At
           N=4, profile P3, D=0.02, it climbs monotonically from 30.7 at T=1 to
           105.8 at T=64 and is still climbing, against an energy-conservation
           ceiling k_N^2 * E = 160.0. The viscous comparison (nu=0.02, D=0) is
           stable at 10.1035 from T=2 through T=64."
Source: docs/designs/M2_W4_DISPERSIVE_SHELL.md OPEN ITEM O7;
        exploration/w4_first_comparison.out (invalidation section)
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Mechanism: dispersion is energy-neutral by construction, so at nu = 0 the
       system has no attractor and the enstrophy keeps finding new maxima,
       bounded only by k_N^2 * E -- a property of the TRUNCATION, not the
       dispersion. Dissipation is what makes sup_t Omega converge.

       This BLOCKS the primary W4 experiment as specified in the audited memo,
       which fits beta from sup_t Omega for all regulators. beta_nu is a model
       property; beta_D is a property of the chosen horizon. See O7 for four
       options and a recommendation.

       Under the memo's own section 6 framing this counts as "a real and useful
       negative" and a successful outcome, not a failure -- arguably a sharper
       statement about dispersive-vs-dissipative regularization than the beta
       comparison would have been.

       LIMITS: demonstrated non-convergence by T=64 at N=4 with the mechanism
       clear. NOT demonstrated that it never converges at any horizon, nor that
       this holds for every profile and D.

PRECISION ERRATUM (2026-08-14, Fable review): "does not converge in T" is
       corrected to: sup_{t<=T} Omega is monotone and bounded (by k_N^2 E),
       hence convergent in principle; on all tested horizons it remains
       horizon-dependent, and its empirical limit is ceiling-scale, so the
       observable DEGENERATES to the trivial energy bound rather than
       diverging. Conclusions unchanged; wording corrected for exactness.
```

```
[CLAIM-R1] [RETRACTED] -- never filed as a claim, recorded here so it cannot resurface
Statement (WITHDRAWN): "beta_nu = -0.91 and beta_D = -0.63 with disjoint 95%
           confidence intervals, i.e. dissipative and dispersive regularization
           give distinguishable peak-enstrophy exponents."
Reason for retraction: invalid. The beta_D value was an artifact of the T=1.0
       horizon (CLAIM-005). Every quality signal looked good -- r^2 > 0.96, tight
       CIs, zero exclusions, and dt-refinement passing at 0.00% on all 12 points --
       because the pre-registered protocol tested convergence in the TIMESTEP and
       nothing tested convergence in the HORIZON. See LL-11.
Filed: 2026-08-14 (as a retraction; the result was never promoted to a claim)
```

```
[CLAIM-006] [TIER-B] [VERIFIED]
Statement: "Every observable of the form 'how large does Omega become' so far tested
           inherits a horizon dependence on the DISPERSIVE side and none on the
           viscous side. Five candidates failed: sup_t Omega (10.35% horizon
           drift), time-averaged Omega (49.99%), max_t dOmega/dt (19.31%),
           Omega-at-first-peak (horizon-stable but non-monotonic in the swept
           parameter), and max_{t<=T*} Omega (beta drifts 40%, -1.062 to -1.496,
           as T* goes 1.5 to 4.0). The viscous regulator passes every check for
           every candidate tried."
Source: exploration/observable_convergence.out,
        exploration/windowed_sup_check.out,
        exploration/w4_first_comparison.out (both annotated invalidations),
        docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Common root, identified: a purely dispersive regulator has NO ATTRACTOR.
       Dissipation removes energy so the viscous system settles and "how large
       does Omega get" has a converged answer; dispersion is energy-neutral by
       construction (memo section 3) so the conservative system keeps exploring,
       measured at 66% of the k_N^2 E ceiling at T=64 and still climbing.

       This is a structural consequence of comparing a system WITH an attractor
       against one WITHOUT, not a run of bad luck in choosing observables. It is
       evidence bearing on whether peak-enstrophy is the right framing for W4 at
       all -- option (c) in the 2026-08-14 decision, not selected at the time,
       when the evidence was three failures rather than five with a known
       mechanism.

       NOT a claim that no suitable observable exists -- only that none of the
       five tried works, and that the reason they fail is now understood rather
       than incidental.

UPDATE 2026-08-14, round 2 -- TIMESCALE observables also fail, and reveal a
       THIRD failure class that reframes the problem. t_peak PASSES the full
       battery on the viscous side but on the dispersive side is non-monotonic
       with r^2 = 0.24 / 0.10 -- no power-law relationship at all, so there is
       no exponent there to measure. t_cross(theta) REVERSES the asymmetry: it
       is well-behaved for the DISPERSIVE regulator and UNDEFINED for the
       VISCOUS one, because under strong damping the cascade never reaches
       4 x Omega(0) and there is no crossing time.

       That reversal matters. Every earlier failure was on the dispersive side,
       which invited "the dispersive case is awkward, keep looking". It is not.
       The two regulators DO NOT SHARE A COMMON DOMAIN on which one observable
       is well-posed: amplitude observables are convergent for the viscous
       regulator and horizon-divergent for the dispersive one; threshold
       observables are defined for the dispersive one and undefined for the
       viscous one. The dynamics differ in KIND -- attractor vs no attractor --
       not in degree.

       Seven candidates now, three distinct failure classes: horizon
       divergence, parameter discontinuity, domain non-overlap.

REFRAMING + NOVELTY VERDICT (2026-08-15, retrieval complete): the phenomenon
       is thermalization toward ABSOLUTE EQUILIBRIUM of a Galerkin-truncated
       conservative system -- established for truncated Euler ([LIT-012],
       [LIT-013]), truncated GPE/NLS ([LIT-014]-[LIT-016]), and, decisively
       for novelty, for SHELL MODELS themselves ([LIT-017]-[LIT-020];
       closest: Thalabard-Turkington 2016, "relaxation ... towards Gibbs
       equilibrium in an inviscid shell model of 3D turbulence"). No prior
       thermalization study of the KP/DN dyadic model specifically was found
       (that literature centres on blowup/regularity), so this claim is a
       RE-EXPRESSION confirming known behaviour in a dyadic variant --
       recorded per Rule E-X, novelty withdrawn.
```

```
[CLAIM-007] [TIER-A] [VERIFIED]
Statement: "The conjugated complexified dyadic shell nonlinearity
           B_n(v) = k_{n-1} v_{n-1}^2 - k_n conj(v_n) v_{n+1}
           conserves the energy pairing EXACTLY under the truncation boundary
           condition v_{N+1} = 0: sum_{n<=N} Re(conj(v_n) * B_n(v)) = 0.
           Additionally, the reals are an invariant subspace: real data has
           Im(B_n(v)) = 0."
Source: lean_src/QuantumFluidsShell.lean --
        theorem shellBc_energy_conservation, theorem shellBc_real,
        with supporting re_conj_sq_mul and sum_re_conj_mul_shellBc.
        Kernel-checked against Mathlib rev 6d605ae1 (the SAME revision
        MechanicaFluidorum pins), toolchain leanprover/lean4:v4.33.0-rc2.
Filed: 2026-08-14
Updated: 2026-08-14
Notes: TIER A. Closes audit ruling O2, which accepted the complexification as
       a labelled deformation "carrying no Tier A backing until it has its own
       Lean development". W4's model now has formal backing for its single
       load-bearing algebraic claim.

       Axiom footprint verified on all four theorems:
         [propext, Classical.choice, Quot.sound]
       and nothing else -- in particular no sorryAx.

       Deliberately mirrors MechanicaFluidorum's real-model development
       (shellB / sum_mul_shellB / shellB_energy_conservation) so the two can be
       compared line for line, and is checked against the same pinned Mathlib.

       The proof turns on one identity, re_conj_sq_mul:
         Re(conj(a) * conj(a) * b) = Re(conj(b) * a * a)
       -- both sides are the real part of a conjugate pair. That is the formal
       content of the hand-derivation in memo section 2b, and the reason the
       SINGLE conjugation placement works where the unconjugated version fails.

       SCOPE: this is an algebraic identity about the nonlinearity. It says
       nothing about boundedness, blow-up, or any observable -- those remain
       Tier B or open. In particular it does NOT give Tier A status to
       anything in the W4 measurement programme.

       Gate 2 of scripts/verify.sh now BUILDS and axiom-audits Lean rather
       than grepping for import lines; a text check cannot distinguish a proved
       theorem from one containing sorry. The gate was negative-controlled by
       inserting a sorry and confirming sorryAx appears in the certificate.
```

```
[CLAIM-008] [TIER-B] [VERIFIED]
Statement: "All three of EXPRESSION_MEMO_E1 section 4's regulators are
           energy-conserving -- truncation exactly (v_{N+1}=0 kills the
           telescoping outflux), dispersive exactly (-iDk^2 a is energy-neutral),
           and bounce only for special seams. None dissipates. The sup_t Omega
           obstruction of CLAIM-005 therefore applies to the ENTIRE experiment,
           not only its dispersive arm. Measured for the truncation control
           (nu = D = 0, profile P3): sup_t Omega still climbing at T=32, at 99.2%
           of the k_N^2 E ceiling, at every N in {4,5,6}."
Source: M2_REPORT.md section 6a; lean_src/QuantumFluidsShell.lean
        (sum_re_conj_mul_shellBc gives the outflux form the argument rests on);
        tests/test_shell_dynamics.py seam section.
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Why this was not visible earlier: the comparisons in M2_REPORT sections
       2-3 used a VISCOUS regulator as one arm, and it passed every check. But
       viscosity is NOT one of E1 section 4's three regulators -- it was
       introduced by this stream as a dimensionally-matched stand-in for D. It
       is the only dissipative element in the study, which is exactly why it was
       the only well-behaved arm. The apparent "one side works, one doesn't"
       pattern was an artifact of that substitution.
```

```
[CLAIM-009] [TIER-B] [VERIFIED]
Statement: "For the truncation control at nu = D = 0, sup_t Omega saturates at the
           energy-conservation ceiling k_N^2 E, so beta measured against
           alpha' = 4^-N converges to -1 EXACTLY -- the trivial bound restated.
           Measured across horizons T = 2,4,8,16,32: beta = -0.948, -0.990,
           -1.002, -1.003, -1.002."
Source: M2_REPORT.md section 6a.
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Consequence: even at a FIXED horizon the truncation control is measuring
       sup Omega <= k_N^2 E and carries no dynamical information. A control that
       returns the trivial bound cannot serve as a baseline for detecting whether
       another regulator's beta differs.

       Note this is a different number from OP2_LITE section 3's pre-registered
       beta = -2/3 "no effect" threshold. No conflict is claimed: their protocol
       runs at nu > 0, i.e. WITH dissipation and hence with an attractor, which is
       a different regime from the nu = 0 case measured here.
```

```
[CLAIM-010] [TIER-B] [VERIFIED]
Statement: "A boundary seam conserves energy in the complexified dyadic model IFF
           Re(conj(v_N)^2 * v_{N+1}) = 0. On REAL data this reduces to
           v_N^2 * v_{N+1}, so truncation (v_{N+1} = 0) is the ONLY conserving
           boundary condition and a reflective seam v_{N+1} = v_{N-1} leaks. In
           the COMPLEXIFIED model a conserving seam exists: v_{N+1} = i*mu*v_N^2
           gives conj(v_N)^2 * (i mu v_N^2) = i mu |v_N|^4, purely imaginary,
           so the pairing is exactly zero."
Source: derived from lean_src/QuantumFluidsShell.lean's sum_re_conj_mul_shellBc,
        which gives the energy pairing as -k_N * Re(conj(v_N)^2 * v_{N+1});
        pinned by tests/test_shell_dynamics.py seam section.
Filed: 2026-08-14
Updated: 2026-08-14
Notes: Resolves the question memo section 5 left open about W2. The condition is
       exactly orthogonality of v_{N+1} to v_N^2 under the real inner product
       Re(conj(x) y).

       Two consequences. (i) A naive real reflective seam would measure BROKEN
       CONSERVATION rather than the bounce -- the failure OP2_LITE flags for its
       Candidate A. (ii) The complexification, adopted solely for the dispersive
       regulator, unexpectedly also ENABLES a conserving bounce seam with no real
       analogue.

       But W2 is caught either way: a conserving seam inherits the CLAIM-008
       obstruction, and a non-conserving one measures an artifact.

       This is a case where the Lean formalisation did work beyond certifying a
       known result -- it converted an open design question ("does a bounce
       conserve energy?") into a precise, checkable condition.
```

```
[CLAIM-011] [TIER-A] [VERIFIED]
Statement: "The conjugated complexified dyadic model preserves phase-space volume
           (Liouville property), while the REAL Katz-Pavlovic model does not.
           Formalised core (kernel-checked, Lean): the shell-diagonal derivative
           blocks have zero R-trace -- rtrace_conj_mul (v |-> conj(v)*w has zero
           trace for every w), rtrace_mul_I (multiplication by a purely imaginary
           constant has zero trace), shell_divergence_zero (their sum), with
           rtrace_mulRight (trace of mult-by-c is 2*Re c) as the sanity anchor.
           Numerically: full-field divergence 4e-9 (complexified, with and
           without dispersion) vs. -sum k_n a_{n+1} for the real model,
           verified against the analytic formula to 4 decimals."
Source: lean_src/QuantumFluidsShell.lean (Liouville section; axiom footprint
        [propext, Classical.choice, Quot.sound] on all four lemmas);
        M2_REPORT.md section 6b(ii) (numeric verification record).
Filed: 2026-08-15
Updated: 2026-08-15
Notes: TIER SPLIT, stated exactly: Tier A covers the trace identities; the
       assembly "these maps ARE the diagonal blocks of the flow derivative"
       is by inspection of shellBc and is the numerically verified Tier-B
       part. Fourth dividend of the conjugation (after invariant subspace,
       conserving seam, and the free bit-for-bit positive control).

       Consequence: volume preservation on the compact energy sphere gives
       Poincare recurrence and licenses the statistical-equilibrium
       description of CLAIM-012. Interpretive remark (flagged as such): the
       real KP model's non-Liouville, volume-contracting character is
       consistent with its blowup-oriented literature; the complexification
       moves it into the Liouville family where the shell-model
       statistical-equilibrium literature ([LIT-017]-[LIT-020]) operates.
```

```
[CLAIM-012] [TIER-B] [VERIFIED]
Statement: "Time-averaged enstrophy of the conservative complexified model is
           consistent with microcanonical equipartition on the energy sphere,
           <Omega_sum>_eq = E(4^{N+1}-1)/(3(N+1)) = 42.625 at N=4, E=0.625:
           measured second-half means 37.8 (88.6%, truncation), 46.2 (108.3%,
           D=0.02), 31.1 (73.0%, D=0.1 -- still relaxing). First-quarter means
           differ 4x across regulators (32.3 / 65.5 / 17.6) while late-time
           means converge: the regulator's signature is in the TRANSIENT."
Source: M2_REPORT.md section 6b(iii) (runs of 2026-08-14, complex-phase
        initial data, single trajectories).
Filed: 2026-08-15
Updated: 2026-08-15 -- *** QUANTITATIVE CONTENT WITHDRAWN, see below ***

*** WITHDRAWAL 2026-08-15 (ensemble check, exploration/equipartition_ensemble.out) ***
       The reported percentages (88.6% / 108.3% / 73.0%) are single-trajectory
       draws from very wide distributions. Fixed-D ensemble CV of the
       time-averaged Omega is 25.5% (D=0) and 84.0% (D=0.02) -- comparable to
       or worse than tau's, so time-averaging did NOT rescue the observable as
       hypothesised. At D=0.02 four realisations span 6.0-57.1; the single
       trajectory behind the claim reported 46.2, the four-realisation mean is
       23.8.

       SURVIVES WEAKLY: at D=0 the ensemble mean is 85.5% of prediction with
       SEM ~12.7% (n=4) -- consistent with equipartition within ~1.1 sigma.
       A weak consistency statement, not quantitative agreement.

       ALSO WITHDRAWN: the "first-quarter means differ 4x while late-time means
       converge" observation, and with it the inference that the regulator's
       signature is in the transient. At CV 25-84% a 4x difference between
       single-trajectory quarter-means is not distinguishable from noise.

       UNAFFECTED: the equipartition FORMULA itself,
       <Omega_sum>_eq = E(4^{N+1}-1)/(3(N+1)), which is analytic.

Notes: LIMITS, stated in advance of any use: five shells, single trajectories,
       +/-20-30% expected fluctuation scale; unknown additional invariants
       would shift the prediction (open question); the D=0.1 run had not
       equilibrated by its horizon (itself evidence of slower relaxation --
       the round-3 hypothesis, and the direct analogue of the "dispersive
       bottleneck delaying thermalization" of [LIT-016]).

       Also resolves the 'mean' observable's battery failure retroactively:
       it was relaxing toward equilibrium, not misbehaving.
```

```
[CLAIM-013] [TIER-B] [VERIFIED]
Statement: "In the conservative complexified dyadic model at N=4, stronger dispersion
           delays thermalization, ORDINALLY and without exception: the time tau_f to
           reach a ceiling-relative enstrophy level f*k_N^2*E increases with D, and at
           sufficiently large D the level is never reached within T=32 at all. Censoring
           is perfectly ordered -- it always strikes the largest D first and strikes more
           often at the harder level -- with NO inversion at any D, level, or enstrophy
           convention. Censored (D, level) pairs: [sum] f=1/8: D=0.2; [sum] f=1/4:
           D=0.2, 0.15; [max] f=1/8: D=0.2, 0.15; [max] f=1/4: D=0.2, 0.15, 0.1."
Source: exploration/run_battery_round3.out (run + post-run analysis of 2026-08-15),
        pre-registered in docs/designs/M2_OBSERVABLE_VALIDATION_BATTERY.md
        ("Round 3" + "AMENDED SCOPE AND CENSORING RULE").
Filed: 2026-08-15
Updated: 2026-08-15 -- *** RETRACTED, see below ***

*** RETRACTION 2026-08-15 (ensemble check) ***
       WITHDRAWN. The censoring pattern was measured with exactly ONE
       trajectory per configuration. An ensemble check at fixed D
       (exploration/ensemble_scatter.out; identical |a_n| and energy, phases
       varied) shows tau scatter of 72-105% of the mean, and -- decisively --
       at D=0.05 THREE OF SIX realisations were censored while three attained
       (tau = 1.008, 1.044, 2.663). Attainment there is close to a coin flip.
       "Perfectly ordered censoring with no inversion" is therefore an
       artifact of single-sampling, not an established property. The
       DIRECTION of the effect may well be real -- the D >= 0.15 censoring
       is an 8x gap against ~40% scatter -- but it is NOT established at the
       strength claimed, and no ordinal claim is made pending an ensemble
       measurement (n ~ 40-100 per D for 5% precision).

Notes: ORDINAL ONLY. No exponent is claimed -- see CLAIM-R3 for the withdrawn
       quantitative fit. The censoring pattern is reported as a first-class
       result per owner ruling 2 (2026-08-15) precisely because non-attainment
       correlates with the hypothesised effect.

       This is the model's analogue of the "dispersive bottleneck delaying
       thermalization" established for the truncated GPE by Krstulovic-Brachet
       ([LIT-016]) -- a re-expression in the dyadic setting, not a new
       phenomenon, per Rule E-X.

       Direction agrees with the independent Option C evidence (dispersion
       suppresses peak enstrophy, sign consistent at both viscous floors,
       docs/designs/C_NU_FLOOR_CROSSCHECK.md). Two methodologically different
       routes, same direction.

       LIMITS: single grid (N=4; B5' deferred, not waived), single trajectory
       per configuration, T=32, f=1/2 unattainable and dropped pre-run.
```

```
[CLAIM-R3] [RETRACTED] -- never promoted; recorded so it cannot resurface
Statement (WITHDRAWN): "beta for tau_f vs D is +0.97 (f=1/8) / +1.33 (f=1/4) [sum],
           +0.69 / +0.65 [max]."
Reason: FAILS its own pre-registered battery. B2 monotonicity fails for [sum]
       f=1/8; B3' across f fails (|dbeta| = 0.36 >> 0.05); r^2 = 0.66/0.72 [sum];
       windowed slopes disagree by ~50x ([sum] f=1/8: +2.210 large-D half vs
       +0.042 small-D half).

       DIAGNOSIS, and it is arithmetic rather than speculation: the baseline is
       NONZERO -- tau(D=0) = 0.993 (f=1/8), 1.499 (f=1/4). Since tau(D) tends to
       tau(0) != 0 as D -> 0, log(tau) vs log(D) MUST flatten to slope zero at
       small D whatever the physics. A pure power law tau ~ D^beta forces
       tau(0) = 0 and is therefore the WRONG MODEL; the observed window
       signature is exactly its fingerprint.

       The natural form is tau(D) = tau_0 + c*D^alpha, whose EXCESS DELAY
       tau(D) - tau_0 could carry a clean exponent. Fitting that on this data
       would be post-hoc and is NOT done; it requires its own pre-registration.
Filed: 2026-08-15 (as a retraction; never promoted to a claim)
```

```
[CLAIM-014] [TIER-B] [VERIFIED]
Statement: "Single-trajectory measurement of tau in this chaotic model carries a
           fixed-D ensemble spread of 72-105% of the mean (CV 23-49%), measured
           across phase realisations with identical |a_n| and identical energy at
           N=4, f=1/8, T=24. At D=0.05, three of six realisations failed to attain
           the level while three attained it (tau = 1.008, 1.044, 2.663). A 5%
           measurement of the mean requires n ~ 22-97 realisations per D."
Source: exploration/ensemble_scatter.py, output exploration/ensemble_scatter.out.
Filed: 2026-08-15
Updated: 2026-08-15
Notes: THIS IS THE METHODOLOGICAL FINDING OF THE M3 RELAUNCH, and it retracts
       work rather than adding to it. Every tau in rounds 3 and 4, and every
       sup_t Omega in Option C, came from a SINGLE trajectory. All of those
       quantitative and ordinal results are therefore noise-dominated and
       unestablished (CLAIM-R3, CLAIM-013 retracted; C's sign-consistency
       likewise unestablished).

       WHY THE BATTERY MISSED IT: all six criteria test DETERMINISTIC
       reproducibility -- same trajectory at finer discretisation, or a
       neighbouring parameter on the same trajectory family. NONE tests
       STATISTICAL reproducibility across trajectories drawn from the same
       physical ensemble. In a chaotic system that is the binding constraint,
       and it was absent from the battery by construction. A seventh criterion
       (B8, ensemble reproducibility) is the correct fix.

       UNIFIED EXPLANATION: rather than seven observables failing for six
       distinct reasons, the parameter-discontinuity, own-parameter-drift,
       non-monotonicity and B3' failures are all consistent with this ONE
       cause. The horizon-divergence failures are separate and remain real --
       those concern the k_N^2 E ceiling, not sampling.

       UNAFFECTED: everything analytic or deterministic -- CLAIM-004 (bit-exact
       positive control), CLAIM-010/011 (seam algebra, Liouville, Lean),
       CLAIM-005/008/009 (ceiling/degeneracy, which are about T-behaviour not
       sampling), and all M1 results (deterministic fits to published data).
       The damage is confined to the W4 measurement programme.
```

```
[CLAIM-015] [TIER-B] [VERIFIED]
Statement: "From Godfrin et al. 2021's all-pressure dispersion table (7 pressures,
           per-point uncertainties), weighted parabolic fits over |Q-1.9|<=0.2 give
           Delta(P) = 0.7438, 0.7413, 0.7386, 0.7338, 0.7199, 0.6963, 0.6185 meV
           and Q_m(P) = 1.9085, 1.9131, 1.9177, 1.9267, 1.9517, 1.9909, 2.1147 A^-1
           at P = 0, 0.51, 1.02, 2.01, 5.01, 10.01, 24.08 bar (all +/- <= 0.0007).
           Neither is a power law in P (windowed slopes disagree; r^2 ~ 0.75). The
           low-P regime is LINEAR: Delta at -0.67%/bar, Q_m at +0.475%/bar, constant
           across three independent points."
Source: exploration/pressure_scaling.py, output exploration/pressure_scaling.out;
        data/external/godfrin_2021_arxiv_ancillary/DispersionAllPressures.txt(.meta).
Filed: 2026-08-15
Updated: 2026-08-15
Notes: DETERMINISTIC (weighted least squares on published data) -- immune to the
       single-trajectory problem of CLAIM-014. P=0 cross-checks M1's CLAIM-003 to
       0.05% (0.7438 vs 0.7442).

       Role for the theory (THEORY_MEMO section 4): a CONSTRAINT on the form of any
       T-dual coupling law tested against these parameters -- it cannot be a pure
       power law in pressure, and must be stated in the physical variable (density,
       not P). It is NOT a measurement of the CR-1 exponent s. Density is not in the
       file; converting requires a separately sourced equation of state.
```

```
[CLAIM-016] [TIER-A] [VERIFIED]
Statement: "In the complexified dyadic model with k_N != 0, the energy pairing
           over shells 0..N vanishes IFF Re(conj(v_N)^2 * v_{N+1}) = 0 -- i.e. a
           boundary seam conserves energy iff its value is orthogonal to v_N^2 under
           Re(conj x * y). Both directions kernel-checked (seam_conserves_iff).
           Corollaries, also kernel-checked: truncation conserves
           (seam_zero_conserves); the GPE-like family v_{N+1} = i*mu*v_N^2 conserves
           (seam_gpe_conserves)."
Source: lean_src/QuantumFluidsShell.lean, axiom footprint
        [propext, Classical.choice, Quot.sound] on all three; eleven theorems total.
Filed: 2026-08-15
Updated: 2026-08-15
Notes: This is the theorem that says what a T-dual "bounce" CAN be. Upgrades
       CLAIM-010 (which established the <= direction and the family numerically) to
       a full characterisation at Tier A.

       Combined with the numerical mirror test (exploration, 2026-08-15: every seam
       reading a NEIGHBOURING shell -- v_{N-1}, its conjugate, negation, i-rotation
       -- leaks at |dE/dt| ~ 1e2-1e3), the consequence for P4 is: an energy-
       conserving T-dual bounce cannot be a spatial reflection about the self-dual
       scale; it must be LOCAL PHASE ROTATION at the cutoff, GPE-like. That mirror
       test is [C-num]; the theorem it rests on is [A].

       This is the stream's principal theoretical output and the first retrofit
       item for Mathesis (THEORY_MEMO section 6, item 1).
```

```
[CLAIM-017] [TIER-B] [RETRACTED -- R4]
Statement (WITHDRAWN): "SOCRATES/Mensura's FINDINGS section 4 exponent -0.672
           (nu=0, t_max=12) is a fixed-horizon transient; re-running at longer
           horizons will drive beta monotonically toward -1, because a
           conservative truncated cascade relaxes to absolute equilibrium."
Filed: 2026-08-15
Retracted: 2026-08 (same turn it was tested -- it was never shipped as standing)
Source of refutation: exploration/socrates_horizon_test.py(.out) -- THEIR protocol
           re-run verbatim (N=30, nu=0, cfl=0.05, 9 alphas over 8 decades) at
           t_max in {6,12,24,48}.
Result: beta = -0.6721 at EVERY horizon. Drift over an 8x range: -0.0001.
           4-seed control at t_max=12: spread 0.0006. Their published -0.672
           reproduces exactly and is robust on both challenged axes.

WHY THE PREDICTION WAS WRONG (this is the retained content):
  - Absolute-equilibrium/thermalization arguments require a LIOUVILLE flow.
    This stream itself proved the REAL Katz-Pavlovic flow is volume-CONTRACTING
    (div = -sum k_n a_{n+1} != 0, CLAIM-011). Only the COMPLEXIFIED model is
    Liouville -- and that is the model in which beta -> -1 was measured. The
    transfer to their real-amplitude model was invalid on this stream's own
    theorem.
  - Similarly, CLAIM-014's CV 23-49% came from randomising PHASES. A real
    amplitude has no phase to randomise (the same structural fact as the M2
    obstruction proposition). Their seed spread is 0.0006, not 30%, for exactly
    that reason.

LESSON (LL-15): a result must be transferred with its HYPOTHESES, not just its
conclusion. Both transferred conclusions were true in this stream and false
next door, and this stream had already proven the discriminating property.
```

```
[CLAIM-018] [TIER-B] [VERIFIED]
Statement: "SOCRATES/Mensura's sup-enstrophy readout is sampling-limited, not a
           supremum: ShellResult.max_enstrophy maxes over RECORDED SAMPLES while
           sample_times = linspace(0, t_max, n_samples) with n_samples fixed at
           2000, so the sampling interval scales with the horizon. At alpha'=1e-6
           the reported value FALLS 11425.5 -> 11425.5 -> 10950.9 -> 9885.8
           (-13.5%) as t_max goes 12 -> 48 -> 200 -> 800, which is impossible for
           a supremum over a nested growing window. Energy drift is 1.34e-7
           throughout, so the integrator is sound and only the readout is not.
           Their PUBLISHED section-4 exponent is NOT affected: varying only
           n_samples (2000 vs 200000) across all nine alpha' moves the worst peak
           by 0.051% and beta by 0.0000."
Source: exploration/socrates_why_stable.py(.out),
        exploration/socrates_sampled_max_defect.py(.out).
Filed: 2026-08
Notes: Found as a by-product of testing CLAIM-017, which refuted itself. Same
       defect CLASS as DEFECT_REPORT_MF_ENSTROPHY (a measurement instrument
       silently reporting something other than the named observable), and the
       same class this stream's own observable.py guards with SAMPLING_TOL.
       Latent, not live: it bites when the horizon grows or the peak sharpens.
       Fix available in their code: retain a running max of the per-step
       current_enstrophy already computed at shell.py:183 for the ceiling test.
       Reported in socrates-project docs/QUANTUMFLUIDS_RETROFIT.md section R1.
```

```
[CLAIM-019] [TIER-B] [VERIFIED]
Statement: "Applying the LL-15 rule to the MechanicaFluidorum note BEFORE sending it,
           both exported conclusions were tested in MF's own code (nu=0, N=12, P3,
           exploration/mf_transfer_check.py). They SPLIT:

           (a) THERMALIZATION/DEGENERACY TRANSFERS. sup_t Omega reaches 51.7%, 95.0%,
               99.6%, 99.90% of the ceiling k_N^2 E at T = 2, 8, 32, 64 (energy drift
               <= 2.7e-13). By T=64 the observable is a readout of the truncation.

           (b) SINGLE-TRAJECTORY NOISE DOES NOT TRANSFER. 10 realisations at identical
               energy, amplitudes perturbed 10%, T=8: CV 0.15%, spread 0.53% -- two
               orders of magnitude below the complexified model's CV 23-49%.

           The discriminating feature for (a) is the wavenumber profile: MF's k_n = 2^n
           is UNBOUNDED so the cutoff shell dominates, whereas SOCRATES/Mensura's dual
           cap k_eff = min(k, 1/(alpha' k)) makes trans-cutoff shells SOFT -- which is
           why the same claim failed there (CLAIM-017) and holds here. The
           discriminating feature for (b) is phase freedom, absent in both real models.

           Instrument contrast: MF's _simulate accumulates sup_om at EVERY STEP, so MF
           does NOT have the sampled-max defect found in Mensura (CLAIM-018)."
Source: exploration/mf_transfer_check.py, output .out
Filed: 2026-08
Notes: This is LL-15 applied prospectively rather than learned retrospectively. The
       cost was one script; it caught a false claim before it left the stream and
       upgraded a true one from analogy to measurement.

       Consequence for Mensura, recorded in their retrofit doc: their T-dual cap
       PROTECTS against the sup-Omega degeneracy that plain truncation suffers. That
       is a positive result for their design, found while checking a claim against it.
```

---

## Design-memo audit register

Per E-1 (definition first, audit before code) and the house pattern inherited from
MechanicaFluidorum `PLAN.md` §6: **authorship never unblocks a track — only audit does.**
A design memo listed here as PENDING AUDIT may not be implemented, cited, or measured.

| Memo | Date authored | Status | Blocks |
|---|---|---|---|
| `docs/designs/M2_W4_DISPERSIVE_SHELL.md` | 2026-08-14 | ✅ **AUDITED 2026-08-14** (owner) | — unblocked |
| `docs/designs/DS_QF_PRIME_COLD_ATOM.md` | 2026-09-20 | ❌ **NOT RUN, by decision 2026-09-20** — outcome dimensionally forced (RETRACTIONS R2); only data route is digitising Steinhauer et al. PRL 88, 120407 Fig. 3(b), whose 3 points above k* carry a systematic the authors neglected | — |
| `docs/designs/TDA_DUAL_SCALE_COMBINED.md` | 2026-09-20 | ❌ **WITHDRAWN 2026-09-20** before any run — both halves fell independently (CLAIM-T3; RETRACTIONS R2) | — |
| `docs/designs/TDA_VORTEX_FLOOR.md` | 2026-09-20 | ⏳ **PENDING AUDIT** — pre-registration only; workstream T (GUDHI persistent homology of vortex configurations), data section deliberately empty | T1–T5 measurements |
| `docs/designs/DUAL_SCALE_QUANTUM_FLUID.md` | 2026-09-20 | ⏳ **PENDING AUDIT** — pre-registration only; results section empty by construction | DS-QF measurement (M1–M5) |
| `docs/designs/DUAL_SCALE_SECOND_INVARIANT.md` | 2026-09-19 | ✅ **AUDITED 2026-09-19** (owner: "I approve it", as written; addendum A1 registered before any run) | — unblocked |
| W2 (bounce regulator) | not authored | — | W2 only; W4 proceeds without it |

**M2 memo — auditor's rulings (owner, 2026-08-14):**

- **O1 — RULED: record BOTH.** Every run computes and reports both
  `Ω_sum = ½Σₙkₙ²|aₙ|²` and `Ω_max = maxₙ ½kₙ²|aₙ|²`, and β is fitted against each.
  *This overrides the memo's own recommendation (use the sum) and is the stronger
  ruling:* it settles empirically whether the two definitions actually yield different β,
  rather than assuming they do or don't, and preserves comparability with
  MechanicaFluidorum's existing CSVs at no meaningful cost.
- **O2 — RULED: accept** the conjugated complexification, explicitly labelled as a
  deformation with a stated motivation (the invariant-subspace property), and carrying no
  Tier A backing until it has its own Lean development.
- **O3 — RULED: sweep `D` directly.** `ξ = D/c` is reported only if `c` can be defined
  non-circularly for the shell model; otherwise omitted.
- **O4 — RULED: accept the BEC/GPE scope.** W4 is a Bogoliubov-regime experiment with no
  roton. It must not be reported as modeling ⁴He's excitation spectrum, and M1's fitted
  Δ, Q_m have no counterpart in it.
- **O5 — RULED:** harness built in QuantumFluids, offered upstream later if generally useful.

**Post-audit items on the M2 memo** (both found before any W4 experiment was run):

- **ERRATUM E1 — §6's O5 falsification trap was stated wrongly.** It demanded that the
  truncated inviscid model exhibit finite-time blow-up. It cannot: energy conservation
  gives `|aₙ| ≤ √(2E)` and `Ω ≤ k_N²E`, so a *truncated* model is globally bounded —
  Katz–Pavlović is a theorem about the *infinite* system. As stated the trap could never
  fire and would have condemned a correct implementation. Corrected to
  MechanicaFluidorum's original formulation: the trap is about the **exponent**
  (`β = 0` at `ν = 0` is presumptively wrong), not a single trajectory.
  *Status: corrected in the memo as a dated erratum; bounds now unit-tested.*
- **O6 (new, needs ruling) — the three regulators do not share one α′ axis.** `α′` is a
  length²; `ν` and `D` are diffusivities (length²/time). The conversion differs by
  regulator (`η² ~ ν^{3/2}` needing `ε`; `ξ² = D²/c²` needing `c`) and neither quantity
  is defined for this model. **Does not block the primary experiment:** `ν` and `D`
  share dimensions *with each other*, so `β_ν` vs `β_D` at matched diffusivity is
  dimensionally airtight and is precisely the memo §3 design. Comparison against the
  truncation control is secondary and blocked. *Recommendation: adopt `β_D` vs `β_ν` as
  the primary readout; rule separately on whether the truncation comparison is needed.*

**Cross-stream defect (arising from O1):** the MechanicaFluidorum sum-vs-max inconsistency is
written up as a portable, standalone report at `docs/DEFECT_REPORT_MF_ENSTROPHY.md` for the
owner to route to that stream's own audit. **This stream does not modify another stream's
code or data.**

---

## Claim status history

| Claim ID | Status → | Date | Notes |
|---|---|---|---|
| CLAIM-001 | PENDING → VERIFIED | 2026-08-14 | Roton branch fit, digitized Fig. 5 |
| CLAIM-002 | PENDING → VERIFIED | 2026-08-14 | Confirmed negative finding: phonon branch fit fails on digitized data; root cause documented in M1_REPORT.md |
| CLAIM-003 | PENDING → VERIFIED | 2026-08-14 | Both c and Delta recovered within tolerance on Tier-B author-published data; CLAIM-002's diagnosis confirmed correct |
| CLAIM-004 | PENDING → VERIFIED | 2026-08-14 | M2 Positive Control #1 PASS at 0.00e+00 across 2.4e6 RK4 steps; complexification validated against MechanicaFluidorum's reference |
| CLAIM-003 | VERIFIED → VERIFIED (references corrected) | 2026-08-14 | Reference values had been misattributed (LL-10); recomputed against 6 correct determinations, conclusion unchanged and better supported |
| CLAIM-005 | PENDING → VERIFIED | 2026-08-14 | sup_t Omega does not converge in T for a purely dispersive regulator; blocks the primary W4 experiment as specified (O7) |
| CLAIM-R1 | — → RETRACTED | 2026-08-14 | Never promoted to a claim. beta_D vs beta_nu comparison invalid: horizon artifact (LL-11) |
| CLAIM-R2 | — → RETRACTED | 2026-08-14 | Never promoted. Re-run on first-peak also invalid: non-monotonic in the sweep, conventions disagreed, N-check used the retracted observable |
| CLAIM-006 | PENDING → VERIFIED | 2026-08-14 | Five observables fail on the dispersive side with a common root: no attractor. Bears on whether peak-enstrophy is the right framing |
| CLAIM-007 | PENDING → VERIFIED | 2026-08-14 | TIER A: complexified nonlinearity's exact energy conservation, kernel-checked in Lean. Closes audit ruling O2 |
| CLAIM-008 | PENDING → VERIFIED | 2026-08-14 | All three E1 §4 regulators are conservative; the obstruction is experiment-wide, not dispersive-only |
| CLAIM-009 | PENDING → VERIFIED | 2026-08-14 | Truncation control's β converges to the trivial energy bound −1, carrying no dynamical information |
| CLAIM-010 | PENDING → VERIFIED | 2026-08-14 | Seam conserves iff Re(conj(v_N)²·v_{N+1})=0; resolves the W2 question left open by memo §5 |
| CLAIM-006 | VERIFIED → VERIFIED (reframed) | 2026-08-15 | Novelty withdrawn: phenomenon identified as absolute-equilibrium thermalization, established incl. for shell models ([LIT-017]–[LIT-020]); re-expression per Rule E-X |
| CLAIM-011 | PENDING → VERIFIED | 2026-08-15 | TIER A core: Liouville property of the complexification, kernel-checked trace identities; real KP is non-Liouville |
| CLAIM-012 | VERIFIED → **QUANTITATIVE CONTENT WITHDRAWN** | 2026-08-15 | Ensemble CV 25–84%; percentages were single-trajectory draws. Weak D=0 consistency survives; "signature in the transient" withdrawn |
| CLAIM-013 | VERIFIED → **RETRACTED** | 2026-08-15 | Ensemble check: single-trajectory artifact. At D=0.05, 3/6 realisations censored, 3 attained. Ordering not established |
| CLAIM-T3 | PENDING → **HYPOTHESIS REFUTED** | 2026-09-20 | TDA-DS refuted on our own 2D GPE run at xi/dx = 8 (1024^2, L = 128 xi, 200 planted vortices; written because a survey found NO public dilute-BEC data with xi/dx >= 5, best 2.26). At t = 20: F = 0.280 xi (dt 0.01) and 0.375 xi (dt 0.005), inside the matched Poisson band (p05-p95 0.09-0.78) and far below xi; f_< = 0.081 / 0.071 lies ABOVE the null's 95th percentile (0.040-0.042), so vortices sit CLOSER than random, the opposite of a floor. Reason: opposite-sign vortices attract and annihilate, a process passing continuously through separations below xi, so a snapshot contains pairs in mid-approach; quantization constrains circulation, not distance. The hypothesis was physically naive. CAVEATS: count (3%) and mean separation (2%) converged in dt, but F moves 34% (extreme statistic of a chaotic system) so the refutation rests on the verdict being identical at both timesteps; energy drift 2.4% FAILS the solver's own strict control and is disclosed not relaxed; C-RES fails at 29%. ERRATUM: first script mislabelled t=15 as t=20. CONSEQUENCE: the two-probe correlation CDS (TDA_DUAL_SCALE_COMBINED.md) is WITHDRAWN, its Fourier half being dimensionally forced (RETRACTIONS R2) and its real-space half having no floor to measure. |
| CLAIM-T2 | PENDING → **PARTIAL (split verdict)** | 2026-09-20 | Workstream T second run, threshold-free topological line tracing (cube adjacency, no tunable parameter), same dataset. Tracing validated: 0 ambiguous cubes out of 46762 pierced; 175 lines vs the 67 the proximity method reported, which was merging lines. FLOOR SUPPORTS THE HYPOTHESIS: F = 0.943 xi (the minimum separation between distinct vortex lines sits essentially AT the healing length), 6.1x above the random-shift null p95 of 0.156. f_< REFUTES IT AS WRITTEN: 0.402 in data vs 0.381 in the null, indistinguishable, which is one of the two refutation conditions fixed in memo section 3; pre-registered prediction T2 (f_< < 0.1) is WRONG. Both distributions put ~40% of edges below xi but the data's stop at 0.943 xi while the null's continue to 0.105 -- f_< at one threshold is a poor discriminator, which does not rescue T2. LIMIT: xi = 1.5 dx so F = 1.41 dx, only 2x the 0.707 dx geometric minimum the face lattice permits. TDA-DS partially supported, NOT established; a dataset with xi/dx >~ 5 is still required. |
| CLAIM-T1 | PENDING → **NOT ESTABLISHED (confounded)** | 2026-09-20 | Workstream T first real-data run (Zenodo 5510351, 256^3 generalised-GP, 46581 vortex points). Line-graph floor F = 1.491 xi with f_< = 0 against a random-shift null F = 0.101 looked like a strong confirmation of TDA-DS, but a link-radius sweep (not in the original design) shows F tracks the segmentation threshold: F/threshold stays in 1.00-1.24 across a 4x sweep while F itself ranges 0.667-2.749 xi (132%). The floor is the parameter, not the physics. The null comparison is separately invalid (data segmented, null not re-segmented). Root cause is the caveat recorded in memo section 6 BEFORE the run: xi = 1.5 dx leaves no room between a proximity threshold and xi. TDA-DS neither confirmed nor refuted; nothing from this run is citable. Valid future run needs xi/dx >~ 5 or threshold-free topological line tracing. |
| CLAIM-025 | PENDING → VERIFIED, **with a retraction of its claimed significance** | 2026-09-20 | TIER A: `SigmaRule.lean`, 6 theorems, standard axioms, negative control (sigma=2 claimed to control enstrophy) rejected. On k_n = 2^n the graded weight eats one dyadic power, so omega_n = D k_n^2 (quantum pressure) controls D*sum k_n|v_n|^2 while omega_n = D k_n^3 controls D*sum k_n^2|v_n|^2 = 2*D*Omega: `enstrophy_le_sigma_three` gives 2*D*Omega <= H + sqrt(S)*S with H, S conserved, i.e. uniform in the cutoff N. **RETRACTION OF SIGNIFICANCE**: an earlier assessment in this session called the sigma-rule 'the one result that could matter to something unsolved', pointing at MechanicaFluidorum's O5. Working the bound out shows the constant is 1/D, so it diverges as D -> 0 -- exactly the failure MF's own Q1 adjudication cited when discarding the smooth filter ('bounds explode, proving absolutely nothing'), and Q2 retired that work package. That verdict applies here and is not contested. Value is ILLUSTRATIVE (it exhibits cutoff-uniform-at-fixed-regulator-strength in a fully machine-checked model), NOT progress on O5, and must not be sent to MF as such. No conflict with Katz-Pavlovic: D>0 leaves the reals and H's cubic part vanishes on real data. |
| CLAIM-031 | — → CONFIRMED NULL, second independent search | 2026-09-22 | Widened data search for CLAIM-030's V2 gap (2D He-3 Landau parameters) and general quantum-fluid datasets, per docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md Sec. 12. He-3 2D: arXiv:2206.06039 read directly, confirmed no F0s/F0a table; Boronat et al. arXiv:cond-mat/0307493 gives m*/m(density) by QMC but not F0s/F0a; Casey/Nyeki/Saunders/Hallock papers with the numbers are paywalled, no open mirror found. Three unexploited leads recorded: Godfrin et al., J. Low Temp. Phys. 158, 147 (2010) (same team/substrate as the Nature 2012 paper, likely the real source), and two OSTI PhD theses (Dann 2000, Casey 2001) whose abstracts mention inferring Landau parameters -- OSTI access failed this session, values UNVERIFIED. Structural caveat recorded: Casey/Nyeki/Saunders' system (Royal Holloway, HD-bilayer substrate) and Godfrin's (Grenoble, He-4-monolayer substrate) are DIFFERENT systems; transferring parameters between them needs explicit justification. SECOND independent null result -- raises confidence the gap is real. Datasets: HuggingFace near-100% false-positive rate for this domain (vortex/BEC/helium/condensate/ superfluid searches all irrelevant or zero results) -- confirmed useless. Zenodo: PolancoData (already used) still the best field-snapshot dataset; one new find, Kwon & Shin, Zenodo 10.5281/zenodo.20068724 (2026), processed observables for BEC vortex shedding past an obstacle, NOT raw fields -- noted for future cross-validation, not a replacement. Two questions left genuinely UNVERIFIED (not 'not found'): a machine-readable He-4 S(Q,omega) dataset beyond Godfrin PRB 103,104516's own ancillaries; any 2D dilute-BEC data beating xi/dx=2.26 since 2026-09-20. Session's WebSearch budget (200/200) exhausted before these two could be checked; not answered, not faked as answered. No code written; V1/V2 remain stopped as in CLAIM-030. |
| CLAIM-032 (erratum) | VERIFIED → VERIFIED with one certificate re-scoped | 2026-09-22 | Found while re-computing the seven pairs for the Wasserstein-stability round (`docs/designs/WASSERSTEIN_STABILITY_PREREG.md` A3): the phase-space pair's W1 certificate in `CLOSED_LOOP_RESULTS.md` and in `paper/closed_loop.pdf` Table 3 (`n, m = 5, 5`, `W1 = 0.06320251512622`) was computed on FIVE points per side, whereas the full H0 diagrams of the raw f_S1/f_S2 arrays have 2150 and 1623 finite bars, so the pre-registered top-30 truncation should have had 30 points per side. Same class of defect as the S1 corruption of the same round (a point list altered between workflow stages), on the one pair not independently recomputed then. The diagrams stage was correct: the bottleneck distance on the full raw diagrams is 0.0325030850643 = the published d_B = 0.0325, and eps = 0.2878 is reproduced. The 5x5 certificate is valid for the 5 points it was given; the published number is NOT the l^inf top-30 W1 of the phase-space diagrams. The correct top-30 value is computed in the new round's results file (`linf_top30_W1` for P1) and reported in the new paper. Published PDF (v1.8.1, DOI 10.5281/zenodo.22895282) is not silently changed; the erratum is stated in the new paper and will be carried in the next Zenodo version's notes. |
| CLAIM-038 | — → VERIFIED IN PART (pre-registered; one amendment wrong and corrected post hoc) | 2026-09-24 | PGPE classical-field BKT gate + duality + topology closed loop, `docs/designs/PGPE_BKT_RESULTS.md`. 36 runs (128², L=64ξ, k_cut=k_max/2) + 7 extensions to t=4000. PASS under both admissions: B3 (n_sλ² crosses 4 at T_BKT≈0.718, between e=0.9 and 1.2), D1 (η·n_sλ²=1.047, 1.072), D2 (η=0.313 at the jump — Nelson–Kosterlitz, not the self-dual η=1), T1 parts 1 and 3 (W1 dipole matching Q=0.23 bound, rises where n_s collapses). FAIL: B2 (3ξ pairing statistic saturates at high vortex density), B4 (nλ²=8.76 vs ln380=5.94, cutoff dependence NOT quantified), T1 part 2 (Q saturates ≈0.53, not 0.8). A3-vs-A4 FLIPS: B1 and D3 PASS under A3, FAIL under A4 (g1 fit window [2,16] reaches noise at e≥2.2). NOT RUN: B5. PROCESS: A3 (data-triggered) called ⟨|J_L|²⟩=nTA an exact classical sum rule — false for an incoherent classical field (ideal Rayleigh–Jeans value reproduces measured R_L within 5% at e=2.4–3.2); A4 corrected it post hoc and both are reported. OBSERVATION (post hoc, n=2): at e=0.90, same thermometer T, runs with ~10 unbound quench vortices (Q=0.67) had condensate 0.18–0.23 and η≈0.5; after the vortices bound/annihilated (Q=0.22) condensate 0.62–0.64, η≈0.11 — the K7 thermometer is blind to the topology that sets the observables. NO NOVEL PHYSICS (known BKT phenomenology reproduced with own solver). |
| CLAIM-037 | — → VERIFIED (gate verdicts + group theory) | 2026-09-24 | Gate on an external 'exact dualities' feedback (PGPE_BKT_PREREG.md A2.1): (i) BKT is NOT at the self-dual radius (self-dual η=1, K=1/2π; BKT η=1/4, K=2/π); (ii) Γ₀(2) acts on the Hall conductivity plane (Lütken–Ross PRB 45 11837) but the Fricke involution W₂ is NOT a Hall symmetry. `lean_src/QHFricke.lean`, 6 theorems, standard axioms, Comparator accepted (both kernels), 3 negative controls fail: M=(1,−1;2,−1)∈Γ₀(2), M²=−1, M fixes (1+i)/2; Γ₀(2) preserves the odd-denominator class; W₂((1+i)/2)=(1+i)/2−1 (fixes the critical orbit on Γ₀(2)\H); W₂ sends every plateau p/q (q odd) to a point equal to no odd-denominator fraction. Also: PH detecting XY BKT is published (arXiv:2009.14231, 2109.10960). Citation note: Lütken–Ross arXiv:1008.5257 cite Li et al. as PRL 102, 216811; Crossref DOI is 10.1103/PhysRevLett.102.216801. Library 187 theorems / 22 modules. |
| CLAIM-036 | — → PUBLISHED | 2026-09-22 | v1.9.0 published on Zenodo, DOI 10.5281/zenodo.22904619 (new version of 22895282, concept 10.5281/zenodo.22855581), archive + 5 PDFs incl. `paper/wasserstein_slack.pdf` (CLAIM-034) and the erratum to `closed_loop.pdf` (CLAIM-032 erratum) stated in the record notes; GitHub release v1.9.0. Library 181 theorems / 21 modules (CLAIM-035 `Fricke`). |
| CLAIM-035 | — → VERIFIED (group theory, honestly scoped) | 2026-09-22 | `lean_src/Fricke.lean`, 12 theorems, standard axiom footprint (one needs only propext+Quot.sound), Comparator accepted by both kernels (3 min 40 s), 3 negative controls (wrong sign of W², conjugate with +c', wrong fixed point) fail to compile. Content, as GROUP THEORY only: the integer Fricke matrix W=(0,-1;n,0) satisfies W²=-n·1; for every A in Mathlib's `Gamma0 n` there is an explicit B in `Gamma0 n` with W·A = B·W (`fricke_normalizes`, via `conj` and `det_conj`), and A↦B is an involution (`conj_conj`) -- the facts that make Γ₀(n)⁺ a group with Γ₀(n) of index 2 (Dolgachev alg-geom/9502005 Thm 7.1's group); the Möbius action of W on the imaginary axis is i·y ↦ i/(n·y) (`fricke_on_axis`); with n = 1/ks² this is literally `DualLength`'s k ↦ ks²/k (`axis_eq_dual`), leaves `ell ks` invariant (`ell_axis_invariant`) and fixes 1/√n = ks (`axis_fixed_iff`). NOT proved, NOT claimed: anything about K3 surfaces, lattice polarisation, period maps, mirror symmetry, or helium. This is the Lean behind the gate verdict of `paper/wasserstein_slack.pdf` §6.3 ("the same involution without the group"): it proves what W does to Γ₀(n) and what its shadow does to a wavenumber, and nothing connects the two. Library: 181 theorems / 21 modules. |
| CLAIM-034 | — → VERIFIED (a negative result, pre-registered) | 2026-09-22 | Skraba–Turner cellular Wasserstein stability (arXiv:2006.16824 v7, Thm 4.6) on the seven closed-loop pairs, `docs/designs/WASSERSTEIN_STABILITY_PREREG.md` (committed before code; A1: my hand W_2 on the toy was wrong, sqrt(37/8) not 5/2, caught by control C2; A2: reduced dual LP verified against the full matrix, top-200 scope by size rule; A3: P1 raw arrays + the CLAIM-032 erratum), results `WASSERSTEIN_STABILITY_RESULTS.md`, paper `paper/wasserstein_slack.pdf`. Controls C1–C4 exact (C3: exact known answer on real data, slack 9 and 3). The bound holds on all 7 pairs, p=1,2 (as it must) and is VACUOUS on all 7: V_1 = 139–3200, V_2 = 18–65 (bound / trivial triangle-inequality bound); slack S_1 = 493–19300. P2, P3 PASS (resolution pairs vacuous at p=1 and p=2 → the kill written in closed_loop.pdf §7.1 is executed), P4 FAIL (I predicted the phase-space pair informative; V_1 = 139), P6, P7 PASS. Mechanism measured: V_1 = (cells per bar)·(mean cell change / mean bar length), cells/bar 400–3200, mean |Δρ| 0.25–0.5 n0 (dense perturbation); V_2/√V_1 = 0.94–1.56 on all 7; exploratory p-sweep: min_p V_p ∈ [2.1, 4.0], never < 1. 28 degree-level W_p certificates (primal + dual potentials, independent checker): 22 at ≤1e-15, 6 at the solver's 1e-7 tolerance reported with a rigorous shifted-potential gap ≤ 1.5e-4. NOT done: Lean for Thm 4.6; finite-temperature run (direction 2 stopped at gate); Fricke/K3 (direction 3: Dolgachev alg-geom/9502005 read in full, Thm 7.1/7.6 — DualLength's k ↦ ks²/k is the imaginary-axis restriction of the Fricke involution WITHOUT the group Γ₀(n): shadow, not instance; no claim for helium). |
| CLAIM-033 | — → PUBLISHED | 2026-09-22 | v1.8.1 published on Zenodo, DOI 10.5281/zenodo.22895282 (concept 10.5281/zenodo.22855581), carrying `paper/closed_loop.pdf` (CLAIM-032) and `paper/villani_tribute.pdf` (CLAIM-029), archive tag v1.8.1, GitHub release v1.8.1. Correction made BEFORE publishing, caught in the final review pass: the draft's Sec. 7.1 attributed a bound `W_p <= ||f-g||_p` to Cohen-Steiner-Edelsbrunner-Harer-Mileyko, FoCM 10:127 (2010). That paper's bound keeps the SUP norm on the right-hand side with a fractional exponent (`W_p <= C^{1/p} ||f-g||_inf^{1-k/p}`, statement as reproduced in Skraba-Turner Thm 3.2); the cellular `l_p`-norm bound is Skraba-Turner, arXiv:2006.16824 (v7, 2025), Thm 4.6, verified from the PDF (norm over ALL cells of the complex; part (ii) per-degree over cells of dimensions k, k+1; l_p ground metric in the plane, diagonal at distance 2^{(1-p)/p}|b-a|). Sec. 7.1 rewritten with the correct attribution and a gate that names both conventions. Tags v1.7.0 and v1.8.0 point at pre-correction trees and are NOT released (a forced tag move was refused by the sandbox; a new tag was cleaner than a moved one). |
| CLAIM-032 | — → PARTIAL (13 PASS, 1 not attempted), amended after a pipeline-transmission bug was found and fixed | 2026-09-22 | `docs/designs/CLOSED_LOOP_RESULTS.md` against the pre-registered `docs/designs/CLOSED_LOOP_PREREG.md` (controls C1-C3 exact, C4 satisfied via amendment A1). Predictions P1 (d_B<=eps) and P2 (CSEH sandwich) each PASS on all 7 pairs (R1, R2, R3, T1, T2, S1, phase-space P1). P3/P4 (reported, not pass/fail): eps for R1/R2/R3 = 2.09/2.20/2.39 n0, 8-10x the 0.25 n0 threshold; P4 fraction = 100% for all three, i.e. the CSEH bound holds but is vacuous at this resolution gap (2*eps exceeds the full persistence range), consistent with D1's threshold-detector failure in `KINETIC_TDA_RESULTS.md`. **P5, the centerpiece: all 7 Wasserstein-1 duality certificates hold** (exact primal assignment via `linear_sum_assignment` vs LP dual potentials via `linprog`), relative primal/dual agreement <=2e-16, dual-feasibility violation <=1.1e-16 on every pair, C3's broken potentials correctly rejected by an independent checker -- first independently-certified (not library-trusted) W1 computation in this project. P6 (Lean verification of P5/C3): NOT ATTEMPTED this round, no Lean file written or touched for this loop. **P6 done, same day, after the S1 correction above:** `lean_src/WassersteinCertificate.lean` (8 theorems, standard axiom footprint, 0 sorry) proves finite LP weak duality (`weak_duality`) and the resulting certificate (`certificate`) IN GENERAL, for any finite cost matrix and any finite index types -- the reusable content behind all seven Python certificates, not just the one instantiated in Lean. Instantiated exactly on C1's toy example (the augmented 6x6 cost matrix, the matching a<->a', b<->b', c,c'->diagonal, and the exact rational potentials phi=(0,1/2,3/2), psi=(0,-1/2,1/4), the same ones pre-registered by hand): `toy_certificate` proves the matching optimal, `toy_cost_eq` proves the cost is exactly 7/4. Negative control: the broken C3 potential (psi_c'=1/2) is proved INFEASIBLE (`broken_infeasible`), so it certifies nothing; two further negative controls (wrong claimed cost; strict instead of non-strict inequality in the certificate statement) fail to compile. NOT attempted: re-verifying the seven real 60x60 float certificates inside the Lean kernel -- the general theorem covers them in principle, their specific numbers are not re-checked by the kernel. Library now 169 theorems / 20 modules. Score with P6 included: 14 PASS out of 14 applicable lines, zero not-attempted, zero unavailable. **Post-hoc correction, same day:** the workflow's first synthesis pass correctly caught and reported an inconsistency for pair S1 (P1/P2 marked N/D rather than guessed) instead of trusting a corrupted diagram silently, but did not trace it to the source; independent verification (owner-directed, not the workflow) found the corruption was confined to the point-list handed from the diagrams stage to the certificate stage (10 points at birth=0 for one side, 1 point for the other) -- the diagrams stage's own summary statistics (eps=1.4848, d_B=0.4406, 505/788 finite bars) were already correct and were confirmed exactly by hand-recomputation, and S1's certificate was recomputed (W1_primal=W1_lp=10.800256297166865, `exploration/tda/loop_certificate_S1.py` rewritten) with the same proven-correct code used for the other six pairs. Nothing softened into a pass without verification; the one remaining gap (P6) is recorded as a gap, not a result. |
| CLAIM-030 | — → STOPPED at the literature gate, before any code | 2026-09-22 | V1/V2 of `docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` (Pomeranchuk=Penrose in 2D; certified Arb enclosures of He-3 zero sound). Gate ran per the doc's own Sec. 5, before any Lean/Arb code. V1: the thermodynamic Pomeranchuk criterion F0s > -1 is standard (Pomeranchuk 1958, Baym-Pethick, via secondary sources), but its equivalence to a DYNAMICAL (Penrose-type, no growing root of the linearized kinetic equation) criterion is NOT an established theorem for the target case. Closest match, Kolomeitsev-Voskresensky, Eur. Phys. J. A 52, 362 (2016), arXiv:1610.09748, does derive dynamical stability explicitly (undamped f0>0, damped -1<f0<=0, growing f0<-1) but for a 3D scalar-interaction nuclear-matter model, not named Penrose, and not the 2D case this project targets. Formalizing V1 as scoped needs an ORIGINAL 2D dynamical derivation, out of this project's stated discipline (formalize existing results, do not generate new physics). STOPPED on the doc's own criterion. V2: bulk 3D He-3 Landau parameters (F0s~9.3, F1s~5.4 at SVP; ~88-94 near melting) found only via SECONDARY citations of Greywall, Phys. Rev. B 27, 2747 (1983) -- paywalled, NOT verified against the primary table, so a 40-digit certified enclosure on it would certify the wrong number if the secondary citation is wrong. The 2D monolayer case (Godfrin et al., Nature 483, 576, 2012, the actual measured system) has NO numeric F0s(density) values found at all -- Nature paywalled, companion papers (Casey/Nyeki/Saunders) gave no usable table within budget. STOPPED on the doc's own criterion (2D Landau parameters not available with uncertainties). No Lean or Arb code written for V1/V2. Reopen only if: someone with institutional access verifies Greywall's table and finds 2D density-dependent values; or a published 2D dynamical stability analysis is found. No contact with Villani or Godfrin from this (hold already in force). |
| CLAIM-029 | PENDING → VERIFIED (a tribute, honestly scoped) | 2026-09-22 | Villani.lean, a foundation for formalizing Cedric Villani's work. Literature survey (13 PDFs: his two 2025/2026 solo papers arXiv:2501.00925, arXiv:2608.14904; Mouhot-Villani 0904.2760; hypocoercivity math/0609050; Lott-Villani math/0412127, math/0506481; Ollivier-Villani 1011.4779; H-theorem and beyond) plus a Mathlib inventory (found: klDiv + klDiv_comp_right_le = Data Processing Inequality for Markov kernels, already proven; NOT found: Wasserstein, logSobolev, Talagrand, Bakry, Otto, Boltzmann, Fisher information, hypocoercivity -- confirmed via grep of the project's OWN pinned Mathlib checkout, not a different one). TIER A (16 thms, standard axioms, 3 negative controls rejected): `card_sq_ge` = Ollivier-Villani arXiv:1011.4779 Theorem 1 at K=0 (#A*#B <= (#M)^2 for the midpoint set of nonempty A,B in the Hamming cube), FULLY PROVED via the crossover-coding injection A x B into M x M the paper's Sec. 3 describes (read from the PDF directly, not guessed) -- own math verified by hand before writing Lean, no discrepancy; plus `klDiv_nonincreasing_to_invariant`, a 3-line corollary of Mathlib's own `klDiv_comp_right_le`, explicitly NOT claimed as a contribution. NOT attempted and said so in the file: the full Theorem 1 with curvature K=1/(2N) (needs concentration of measure in S_n, the paper's Lemma 4/Prop 5); continuous Boltzmann H-theorem, hypocoercivity, log-Sobolev/Talagrand, Lott-Villani-Sturm curvature-dimension; Landau damping (linear: ZeroSound.lean; nonlinear: Bedrossian arXiv:2609.16801, not duplicated). Library now 161 theorems / 19 modules. SIDE FINDING: a fourth bug in scripts/make_comparator_challenges.py (fixed, tests added tests/test_comparator_challenge_generator.py) -- sorry_proof searched for ':=' across the WHOLE item including the docstring, so a docstring using ':=' as informal math notation (e.g. "`r := d(a,b)`") truncated the real theorem statement; and is_thm/decl_name only stripped `/--...-/` docstrings, not `/-!...-/` section headers, so a section comment containing the bare word "theorem" in prose was misclassified as an unlisted theorem and silently dropped -- this ALSO affected DualLength, MadelungNSE, QuantumFluidsShell and RipsFloor's challenge files (their solutions were unaffected; only auto-generated challenge documentation was being silently dropped). Comparator: all five affected modules (DualLength, MadelungNSE, QuantumFluidsShell, RipsFloor, Villani) accepted by both the Lean kernel and nanoda. |
| CLAIM-028 | PENDING → VERIFIED IN PART, REFUTED IN PART | 2026-09-21 | Kinetic benchmark + zero sound + TDA instruments. PRE-REGISTERED: `docs/designs/KINETIC_TDA_PREREG.md` committed b274fdb before any code; amendments A1 (before code), A2, A3 (A3 before any D3 data) dee61eb. RESULTS `docs/designs/KINETIC_TDA_RESULTS.md`: 25 criteria, 14 met, 11 not. VERIFIED: certified Landau root (Arb interval Newton) k=0.5: 1.4156618886045364 - 0.1533594669096048 i, radius < 3e-40, wrong-gamma ball rejected; solver matches it to 0.14% (k=0.5), 0.36% (k=0.4), discriminates wavenumbers by 57%; ballistic echo vs closed form 2e-9; free-streaming recurrence exact; two-stream root 0.225844 confirmed by independent quadrature (D = 8e-15) and by post-hoc small-seed run (0.04%). TIER A: `ZeroSound` (6 thms: undamped zero sound iff F > 0 in 3D and 2D, explicit 2D root) and `PhaseMixing` (3 thms), standard axioms, 4 negative controls rejected; PhaseMixing is SUBSUMED by Bedrossian arXiv:2609.16801 (nonlinear Landau damping in Lean 4) and claims nothing. D0 duality control exact on GP data (985 pairs, diff 0; same-construction 985 vs 1772). REFUTED: D1 density-only vortex detection by prominence (precision 0.871, recall 0.433; criteria 0.95/0.90); D3 phase-space hole counting (29 vs 1; depths 0.84 vs 0.17 for equivalent holes). Common mechanism: H0 persistence is depth to the connecting saddle and both feature types share a valley; by D0, H1 cannot help. FAILED through my own design: K1 rounding criterion (truncated literature values), D3 growth-rate measurement (seed 1e-3 leaves no linear phase), K3 field-on control threshold. FAILED, physics I did not apply: field-on recurrence (36.5 vs 33.51) and echo time (16.40 vs 15.0, converged). UNEXPLAINED: mass drift 6.7e-10 vs threshold 1e-10. ERRATUM: my proposal said nonlinear Landau damping in Lean was out of reach; it had been posted six days earlier. NO NOVEL PHYSICS. Paper draft `paper/kinetic_known_answers.tex`, NOT published. Kinetic repo: PR #1 (person-named agents removed, retractions) awaiting owner. |
| CLAIM-027 | PENDING → VERIFIED (a CONFIRMATION, not a finding) | 2026-09-21 | TIER A + exact symbolic: Godfrin et al. PRB 103, 104516 Eq. (22), the phonon specific-heat series. Independent sympy derivation (`exploration/godfrin/derive_cv_series.py`): all 7 printed inverse-series coefficients (alpha_1 general, incl. eta) and all 6 printed closed forms A, C, D, E, K, L match symbolically; T^4 term vanishes. Lean: `PhononSeries` (9 thms; reversion mod e^8 and DOS mod e^9 in any CommRing with a nilpotent; linear_combination certificates of 40-202 terms GENERATED by `exploration/godfrin/gen_phonon_series_lean.py` and checked by the kernel) and `PhononSpecificHeat` (14 thms; B6, B8, B10; zeta(6), zeta(8), zeta(10); thermal Bose integral at every order; capstone `phonon_specific_heat`). Standard axioms. Negative controls, 4 of 4 rejected: eta -12->-11, D 15120->15121, K 9->8, L 55->54. PROCESS LAPSE: NOT pre-registered (E-1 not followed); derivation was run before the checks were written down. A symbolic match admits no tuning so the result stands, but the lapse is recorded; an earlier draft of the design memo wrongly described the checks as pre-registered with stated priors and was corrected before commit. NOT PROVED: DOS brackets reach the capstone by inspection (no coeff-extraction lemma); term-by-term integration not stated as one theorem; asymptotic validity for the measured dispersion is not a provable statement. The EARLIER check of this series (numbers from printed formulas) tested arithmetic only -- LL-15. Also noted: alpha_2 printed in A^-2 in sec. VI vs A^2 in sec. II (dimensionally A^2). arXiv has v1 only (16 Dec 2020, pre-acceptance); PRB version of record NOT read (paywalled); no erratum on APS page or Crossref. Godfrin contact remains ON HOLD (`docs/FOR_GODFRIN.md` sec. 0). |
| CLAIM-026 | PENDING → VERIFIED | 2026-09-20 | TIER A: `MadelungNSE.lean`, 2 theorems, standard axioms, negative control (wrong scale factor) rejected. Imports `NavierStokes.ProblemStatement` from openai/NavierStokesAndEuler @ 8937a8f (Apache-2.0, the MF-audited commit) -- possible only after the 2026-09-19 migration put both trees on Lean 4.34.0-rc2 / Mathlib 85e3a25. `divergence_pressureGradient`: the divergence of THEIR pressureGradient is the scalar Laplacian (div grad = Laplacian), which their tree does not contain since pressure enters their residual only as a gradient. `divergence_madelungVelocity`: div u = (hbar/m) Laplacian S for the Madelung velocity. SCOPE: kinematics only, no dynamics, no GPE, nothing touching their blow-up theorems. Twice-differentiability of the phase is a hypothesis and fails on a vortex line. |
| CLAIM-023 | VERIFIED → **VERIFIED AS MATHEMATICS, NOVELTY RETRACTED (rediscovery)** | 2026-09-20 | Literature check ran and went against it. The Hamiltonian/SHG structure, the graded phase symmetry, the cubic invariant and Manley-Rowe are all published: Vladimirova-Shavit-Falkovich PRX 11, 021063 (2021); Vladimirova-Shavit-Belan-Falkovich PRE 104, 014129 (2021) -- whose TITLE is the framing offered here as an insight; L'vov-Podivilov-Procaccia EPL 46, 609 (1999), where Sabra is canonically Hamiltonian under a_n = v_n/eps^(n/2), the exact analogue of our w_n = 2^(-n/2) v_n; Ditlevsen PRE 62, 484 (2000); ABDP Phys. Rev. 127, 1918 (1962) for Re(a1^2 a2*). Liouville is a textbook DESIGN CRITERION (Biferale, Annu. Rev. Fluid Mech. 35, 441 (2003), p.442), so CLAIM-011's 'Liouville is a corollary' restates a desideratum. WORSE THAN NEUTRAL: on the dyadic lattice 2^a+2^b=2^c forces a=b, so the Manley-Rowe family collapses to ONE invariant where Fibonacci carries two -- the dyadic case has LESS structure. Lean proofs remain correct mathematics. See RETRACTIONS.md R1. |
| CLAIM-024 | VERIFIED → **VERIFIED AS MATHEMATICS AND MEASUREMENT, SIGNIFICANCE RETRACTED** | 2026-09-20 | (1) l = chi(0)/(k chi(k)) = (eps/hbar c k)^2/k, a repackaging; the bound is AM-GM. (2) The KNOWN structure-factor bound is STRONGER: Onsager's inequality with the sum-rule constant gives S(k) <= hbar k/(2mc), LINEAR in k (Wreszinski & da Silva, J. Phys. A 38, 6293 (2005), arXiv:cond-mat/0411640; Stringari arXiv:cond-mat/9311024). Ours is strictly weaker for k < k*/2 and vacuous beyond 2k*. (3) DIMENSIONALLY FORCED: Bogoliubov has one length and one velocity, so ANY such length with an interior minimum must have it at k ~ 1/xi with value ~ xi; 'l_min = sqrt2 xi at k*' carries no information beyond 'the crossover is at xi'. (4) Since l = v_L^2/(c^2 k), ANY fluid with a roton violates the floor, so the He-4 result confirms that He-4 has a roton. (5) PROSE ERROR corrected: Bijl-Feynman is an inequality, not an equality (the Lean was already correct, taking eps^2 <= (...)^2 as a hypothesis). (6) The Pythagorean form is standard (Dalfovo-Giorgini-Pitaevskii-Stringari RMP 71, 463 (1999) eq. 70-71). eps^2/k^3 as a named diagnostic was NOT FOUND, but per (3) that is not evidence of a finding. See RETRACTIONS.md R2. |
| CLAIM-024-orig | PENDING → VERIFIED (see the retraction row above) | 2026-09-20 | TIER A (Lean) + TIER B (measured): DUAL-SCALE HYPOTHESIS FOR QUANTUM FLUIDS, STATED AND REFUTED FOR He-II. Dual length l(k) := eps(k)^2/(hbar^2 c^2 k^3). Lean `DualLength.lean`, 7 theorems, footprint [propext, Classical.choice, Quot.sound], negative control (bound 3/ks) rejected: for Bogoliubov eps^2 = (hc k)^2 + (hc k^2/ks)^2, l = 1/k + k/ks^2 exactly (the R + alpha'/R form), invariant under k -> ks^2/k, l >= 2/ks = hbar/(mc) = sqrt2 xi with equality iff k = ks; falsification lemma: measured l < 2/ks implies the dispersion is not Bogoliubov at that k. MEASURED on Godfrin P=0 full range (1726 pts, k in [0.002,3.600] A^-1), controls M4/M5 PASS (0.9998, 1.0000, duality err 2.2e-5; phonon -> endpoint): He-II has NO interior minimum in range, l_min/(sqrt2 xi) = 0.0316 at the 3.6 edge, l(roton)/(sqrt2 xi) = 0.0474 (21x below), duality error 132%. Pressure trend (7-pressure table, amended scope A2, control C2 PASS): 0.0473 at 0 bar -> 0.0197 at 24.08 bar, ratio 0.417, shortfall 21x -> 51x. All four pre-registered predictions P1-P4 confirmed. NOT CLAIMED: novelty of the physics (roton below Bogoliubov is textbook); any statement beyond k = 3.6 A^-1 (a minimum must exist there); M2/M3 at P > 0 (out of range) |
| CLAIM-023 | PENDING → VERIFIED | 2026-09-19 | TIER A + exact symbolic: SECOND INVARIANT of the complexified truncated shell model. Under w_n = 2^(-n/2) v_n the model is a Hamiltonian SHG chain; H = sum_n 2^-n [omega_n |v_n|^2 + k_n Im(conj(v_n)^2 v_(n+1))] (+ mu k_N 2^-N |v_N|^4/2 for the GPE seam) is conserved. Lean `ShellHamiltonian.lean`, 7 theorems, standard axioms, negative control (weights without the factor 2) rejected; exact polynomial identity dH/dt = 0 for general k_n, omega_n, mu (sympy N=3,4,5; wrong-weight control fails); nullspace search completed 2026-09-20 at N=4,5,6 (all seams, D=0 and 0.3, two sample sizes): WITHOUT cubics dim 2 = span{mass, mass^2} so the pre-registered kill criterion FIRES (no Omega coefficient, i.e. no invariant of the form 'Omega + positive quartic'); WITH cubics dim 3 = span{mass, mass^2, H}, nothing further hides in the span (1.9e-13), gap 1.5e-3. Controls: GP energy in nullspace 2.2e-15 (PASS), leaking seam expels mass distance 1.0 (PASS). Pre-registered N=8,10 NOT attempted: the first run was killed by its own 50-min budget (a bookkeeping stop, not a finding, LL-18; cause was a 1.25 GB monomial cache, since removed). Consequences: Liouville (CLAIM-011) is a corollary of Hamiltonian structure; energy conservation (CLAIM-007) is Manley-Rowe; H = 0 identically on real data, so the real KP model cannot see it. Uniform-in-cutoff bound `dispersive_norm_le`: a regulator of order k^sigma controls the norm of order k^(sigma-1); quantum pressure (sigma=2) controls sum k|v|^2, NOT enstrophy. PREDICTION ERROR RECORDED: addendum A1 predicted nullspace dim 1/2, measured 2/3 -- the trivial quartic mass^2 was forgotten. NOT PROVED in Lean: the dispersive/GPE-seam parts of conservation (exact-symbolic only), the chain-rule step to d/dt along a solution. Novelty NOT claimed: literature check on complex dyadic / SHG-chain models pending |
| CLAIM-022 | PENDING → VERIFIED | 2026-09-19 | TIER A (algebraic core) + TIER B (numeric mirror): `GPGalerkin.lean`, 7 theorems, footprint [propext, Classical.choice, Quot.sound]. For EVERY finite truncation Λ of an additive group (Z^3 included): Q = Σ conj(ψ_k)N_k = Σ_q |A_q|² (real, ≥ 0, the defocusing sign); mass rate Σ Im(conj ψ_k G_k) = 0; polarised Hamiltonian gradient identity Σ_q 2Re(conj A_q dA_q[δ]) = 4 Re Σ conj(δ_k) N_k; energy rate along δ = -iG vanishes algebraically; kinetic ≤ E when g ≥ 0. NOT PROVED: the chain-rule step identifying these first variations with d/dt along a solution; existence/dynamics; any Navier–Stokes comparison (prose only). Numeric mirror (random ψ, 3x3 lattice): gradient identity 131.75213201 = 131.75213201, matches finite-difference dQ; energy rate along flow 1.7e-14; negative controls (nonlinearity without the conjugate): Q complex, mass rate 843, energy rate 18.15 |
| CLAIM-021 | PENDING → VERIFIED | 2026-09-19 | TIER B (measured): Landau critical velocity from the Godfrin P=0 table (1727 pts): v_L = min eps(Q)/(hbar Q) = 57.9 m/s at Q=1.966 A^-1, i.e. Ma_L = 0.243 vs c = 238.3 m/s. Caveats: uniform flow past a defect, vortex nucleation is typically lower, He-II is two-fluid. Not a claim about the OpenAI blow-up itself |
| CLAIM-020 | PENDING → VERIFIED | 2026-09-19 | TIER A: Madelung split `MadelungSplit.lean`, 5 theorems, footprint [propext, Classical.choice, Quot.sound], negative control rejected (perturbed identity gives errors). |grad psi|^2 = |grad a|^2 + a^2 |grad S|^2 for psi = a e^{iS} differentiable at x; NOTHING about dynamics or vortex cores (where the hypothesis fails) |
| CLAIM-019 | PENDING → VERIFIED | 2026-08 | LL-15 applied prospectively to MF: thermalization degeneracy TRANSFERS (99.9% of ceiling by T=64), single-trajectory noise DOES NOT (CV 0.15%) |
| CLAIM-018 | PENDING → VERIFIED | 2026-08 | Mensura's sup-enstrophy is a sampled max; "sup" falls 13.5% as the window grows; their published beta unaffected (0.051%) |
| CLAIM-017 | PENDING → **RETRACTED** | 2026-08 | Predicted their -0.672 was a horizon transient; tested in their code, beta stable to 4 decimals across 8x horizons. Retracted same turn |
| CLAIM-016 | PENDING → VERIFIED | 2026-08-15 | TIER A: seam characterisation both directions; the T-dual bounce must be local phase rotation, not spatial reflection |
| CLAIM-015 | PENDING → VERIFIED | 2026-08-15 | Delta(P), Q_m(P) from 7-pressure published data: linear at low P (−0.67%/bar, +0.475%/bar), not power-law; constrains CR-1's form |
| CLAIM-014 | PENDING → VERIFIED | 2026-08-15 | Single-trajectory measurement is noise-dominated (CV 23–49%); battery tested deterministic, never statistical, reproducibility |
| CLAIM-R3 | — → RETRACTED | 2026-08-15 | β for τ_f vs D fails its own battery; nonzero baseline makes a pure power law the wrong model |

---

## Governance notes

- Claims start PENDING on filing.
- Tier-A claims require successful literature retrieval + citation in LITERATURE_LEDGER.md.
- Tier-B claims require passing unit test (referenced in LEDGER entry).
- Tier-C claims are narrative only; no verification required, but must be explicitly labeled (docs/narrative/).
- Disputes are recorded in LEDGER and logged with rationale.
- Retractions are never deleted; status changed to RETRACTED with explanation.
