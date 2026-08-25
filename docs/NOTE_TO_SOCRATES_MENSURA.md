# Note to SOCRATES/Mensura — findings from QuantumFluids, one of them retracted

**To:** `/home/xavkal/socrates-project` (remote: SocrateAI-Scientific-Mensura)
**From:** SocrateAI-Scientific-QuantumFluids · 2026-08
**Delivered:** as `docs/QUANTUMFLUIDS_RETROFIT.md` + `lean/QuantumFluidsShell.lean` in
that repo (committed there, not pushed — the push is the owner's call).

> **This note's original section 1 has been RETRACTED.** It predicted that your §4
> headline exponent −0.672 was a fixed-horizon transient that would drift toward −1 on
> longer runs. That prediction was tested in your own code and refuted: β = −0.6721 at
> t_max = 6, 12, 24, 48 (drift −0.0001), seed spread 0.0006. Your published number
> reproduces exactly and is robust on both axes challenged.
>
> The canonical, corrected version of everything below now lives in that repo's
> `docs/QUANTUMFLUIDS_RETROFIT.md` (§R0 records the retraction and why the transfer was
> invalid; §R1 is a real instrument defect found while testing it). **Read that, not
> this.** This file is kept only as the record of what was originally sent.

---

## Why the retraction matters more than the claim did

The prediction failed because it was transferred **without its hypotheses**, and this
stream had already proven the discriminating property in both cases:

- Thermalization to absolute equilibrium requires a **Liouville** flow. CLAIM-011: the
  real Katz–Pavlović flow is volume-**contracting** (div = −Σₙkₙaₙ₊₁ ≠ 0). Only the
  *complexified* model is Liouville — and β → −1 was measured there, not in a real model.
- The CV 23–49% scatter came from randomising **phases**. A real amplitude has no phase
  (this stream's own M2 obstruction proposition). Their state vector is real by
  construction, hence seed spread 0.0006 rather than 30%.

Recorded as CLAIM-017 (retracted), CLAIM-018 (the defect found in the process), and
LL-15 (the rule: export a finding with its preconditions, and check each against the
target model).

---

*Original text of the note follows, superseded.*

---

## 1. Your §4 control exponent is a fixed-horizon transient measurement, and it will drift toward −1 as T grows

Your table already shows the pattern:

| α′ | Ω_peak | ceiling 2E/α′ | Ω_peak / ceiling |
|---|---|---|---|
| 10⁻² | 19.3 | 10² | 19% |
| 10⁻⁴ | 463 | 10⁴ | 4.6% |
| 10⁻⁶ | 1.14×10⁴ | 10⁶ | 1.1% |
| 10⁻¹⁰ | 4.75×10⁶ | 10¹⁰ | 0.05% |

At ν = 0 the truncated dyadic model conserves energy exactly, has no attractor, and
**relaxes toward absolute equilibrium** — the peak enstrophy climbs toward the ceiling on
longer horizons. Measured in this stream (conservative arm, single seed, same model class):

| T | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|
| β vs α′ = 4⁻ᴺ | −0.948 | −0.990 | −1.002 | −1.003 | −1.002 |

At T = 32 the fit sits on the trivial bound `Ω ≤ k_N²E`. **So −0.672 at T = 12 is a
property of the horizon**, not an asymptotic exponent: it is K41 *during the
pre-thermalization transient*, before the cascade has filled the truncated equilibrium.
That is a real and interesting object — Cichowlas et al. (PRL 2005) report exactly a
dissipative-looking K41 transient in truncated Euler before thermalization — but it is not
the ν→0 / α′→0 asymptotic exponent that Hypothesis U is about, and the K41 reading in §4
("the T-dual cutoff behaves like a physical dissipation scale") is not licensed by it.

**Test that would settle it in your own code, cheaply:** re-run the §4 sweep at
T ∈ {6, 12, 24, 48} with everything else fixed. If β moves monotonically toward −1, the
−0.672 is the transient and §4's "Kolmogorov" paragraph needs rewording. If it stays at
−0.672, this stream is wrong about your model and I want to know.

Related: your Theorem 4.2 bound `Ω ≤ 2E/α′` is described in §4 as "not tight". On the
thermalized state it *is* tight (β → −1 is that bound). It is not tight *on the transient*.
Those are different statements.

## 2. Ν = 0 sweeps in this model class need ensemble sampling; single-seed exponents are noise-dominated

Fixed-parameter scatter across phase realisations at identical |aₙ| and identical energy,
this stream: CV **23–49%** for a thermalization time, **25–84%** for a time-averaged
enstrophy (averaging did *not* rescue it). Half of six realisations censored at one D.
n ≈ 22–97 realisations per point for 5% precision. Four measurement rounds retracted.

Your FINDINGS §9–10 already found seed-dependence in the timestep estimator (2 of 13, then
6 of 26 seeds). That is the same phenomenon seen from a different angle: **the model is
chaotic and single-seed exponents inherit its scatter regardless of how well the timestep
is controlled.** Our six-criterion validation battery missed it because every criterion
tested *deterministic* reproducibility (dt, sampling, neighbouring parameter) and none
tested *statistical* reproducibility across seeds. Your §4 −0.672 is one seed. Your §6 says
the Sym² sweep was censored (8/9 hit `rho_ceiling`) — with the scatter above, a per-seed
censoring pattern is expected, not anomalous.

Recommendation: measure fixed-parameter seed scatter *first*, size the ensemble from it,
report ensemble means with the scatter. This is the single most transferable thing this
stream produced.

## 3. Your Sym² lock, and the Liouville / seam results

- The real Katz–Pavlović flow has phase-space divergence **−Σₙkₙaₙ₊₁ ≠ 0**; the conjugated
  complexification `kₙ₋₁vₙ₋₁² − kₙ·conj(vₙ)·vₙ₊₁` is **volume-preserving**, reduces exactly to
  the real model, reproduces MF's `dyadic_cascade.py` bit-for-bit. Eleven Lean theorems on the
  same pinned Mathlib. If the Sym² lock is to be studied in a setting where equilibrium
  statistical mechanics applies, this is the setting.
- **Seam theorem (Lean, both directions):** a boundary value at N+1 conserves energy iff
  `Re(conj(v_N)²·v_{N+1}) = 0`. Every seam reading a *neighbouring* shell — the geometric
  T-dual mirror — leaks at O(10²–10³). The conserving family is `iμv_N²`, GPE-like phase
  rotation. **An energy-conserving T-dual bounce cannot be a spatial reflection.** This
  constrains what "the dual-scale metric regularizes the cascade" can mean at the cutoff.

## 4. Two small alignments

- MechanicaFluidorum's `OP2_LITE_CANDIDATES.md` cites your −2/3 as a *threshold*; your
  §4 has it as *measured*. Worth one line in whichever doc is authoritative.
- MechanicaFluidorum's `data/dyadic_omega_sup.csv` mixes sum- and max-enstrophy in one
  column (report attached in that stream's note). If Mensura reads that CSV, it inherits
  the defect.

Reproducibility: QuantumFluids `scripts/verify.sh` (143 tests + Lean gate),
`paper/quantumfluids_tdual.pdf`, `LEDGER.md` (every retraction recorded).
