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

---

## Design-memo audit register

Per E-1 (definition first, audit before code) and the house pattern inherited from
MechanicaFluidorum `PLAN.md` §6: **authorship never unblocks a track — only audit does.**
A design memo listed here as PENDING AUDIT may not be implemented, cited, or measured.

| Memo | Date authored | Status | Blocks |
|---|---|---|---|
| `docs/designs/M2_W4_DISPERSIVE_SHELL.md` | 2026-08-14 | ✅ **AUDITED 2026-08-14** (owner) | — unblocked |
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

---

## Governance notes

- Claims start PENDING on filing.
- Tier-A claims require successful literature retrieval + citation in LITERATURE_LEDGER.md.
- Tier-B claims require passing unit test (referenced in LEDGER entry).
- Tier-C claims are narrative only; no verification required, but must be explicitly labeled (docs/narrative/).
- Disputes are recorded in LEDGER and logged with rationale.
- Retractions are never deleted; status changed to RETRACTED with explanation.
