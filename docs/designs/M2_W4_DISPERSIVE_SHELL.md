# M2 / W4 — the dispersive (quantum-pressure) shell regulator

> ## ✅ AUDIT OUTCOME — 2026-08-14 (owner)
>
> **APPROVED.** Implementation unblocked. Rulings on §7's open items, recorded in
> `LEDGER.md`'s design-memo audit register:
>
> - **O1 — record BOTH** `Ω_sum` and `Ω_max`, fitting β against each.
>   **This overrides §6/§7's own recommendation (use the sum)** and is the stronger
>   ruling: it settles empirically whether the two definitions yield different β.
>   §6's protocol is amended accordingly.
> - **O2 — accept** the complexification, labelled as a deformation. **O3 — sweep `D`
>   directly**, report `ξ` only if `c` is non-circularly definable. **O4 — accept the
>   BEC/GPE scope**; no roton, and M1's Δ/Q_m have no counterpart here.
>   **O5 — build here**, offer upstream later.
>
> *The body below is preserved unedited as the artifact that was audited.*

---

> ## ⚠ ERRATUM E1 — 2026-08-14, post-audit: §6's O5 trap was stated wrongly
>
> **This corrects a pre-registered protocol item and therefore needs the owner's
> notice, not merely a silent edit.** It was found before any W4 experiment was run.
>
> §6 states the O5 falsification trap as:
>
> > *"at `ν = D = 0` with real initial data, the model must exhibit finite-time
> > blow-up (Katz–Pavlović 2005). If it does not, the implementation is wrong."*
>
> **That trap can never fire, and demanding it would condemn a correct
> implementation.** With `N+1` shells the nonlinearity conserves `E = ½Σ|aₙ|²`
> exactly (CLAIM-004), so `|aₙ|² ≤ Σₘ|aₘ|² = 2E` for every shell and every time,
> giving the uniform bounds
>
> ```
>     |aₙ(t)|  ≤  √(2E)              Ω(t)  ≤  ½ k_N² · 2E  =  k_N² E
> ```
>
> A **truncated** inviscid dyadic model is therefore globally bounded and cannot
> blow up in finite time. Katz–Pavlović (2005) is a theorem about the **infinite**
> system, where energy reaches arbitrarily high shells; truncation is precisely
> what removes that possibility.
>
> **Corrected statement**, which restores MechanicaFluidorum's original and correct
> formulation (`OP2_LITE_CANDIDATES.md` §3, "O5 (Euler test)") that §6 mis-transcribed:
>
> > **O5 falsification trap (corrected).** Re-run the sweep at `ν = 0`. The trap is
> > about the *exponent*, not about a single trajectory: if the dispersive regulator
> > alone yields `β = 0` at `ν = 0` — i.e. `sup_t Ω` bounded **uniformly in `N`** as
> > `N → ∞` — treat the result as presumptively wrong, since it would amount to
> > proving regularity for the inviscid dyadic model, where finite-time blow-up is a
> > published theorem. A *finite* `sup_t Ω` at any *fixed* `N` is expected and
> > carries no information; only its growth rate with `N` does.
>
> Nothing built so far depends on the incorrect form: no W4 experiment has been run,
> and the code and Positive Control #1 are unaffected. The weak unit test that
> encoded the same confusion (`test_divergence_guard_trips_on_blowup`, which accepted
> either outcome and so asserted nothing) is replaced by tests asserting the bounds
> above, which are the real, checkable content.

---

**Status when authored: Tier C, AWAITING HUMAN AUDIT.** Nothing here may be implemented,
cited, or measured until this memo is marked AUDITED in `LEDGER.md`. This document is that
audit's *input*. Follows the house pattern of MechanicaFluidorum
`docs/designs/OP2_LITE_CANDIDATES.md` (design memo → audit → code; E-1).
**Date:** 2026-08-14. **Supersedes:** the "import the instrument from MechanicaFluidorum"
framing of `EXPRESSION_MEMO_E1.md` §4, corrected 2026-08-14 (see LL-9).

---

## 0. What changed since E1 §4 was written

E1 §4 proposed running "the Stage-1 exponent instrument (dyadic lab from
MechanicaFluidorum, already calibrated)" on three regulators. A scoped search
(2026-08-14) established that **no such instrument exists**, in either sibling repo. What
exists in MechanicaFluidorum is:

- `exploration/dyadic_cascade.py` — a real, working **Tier C** RK4 integrator for the
  truncated viscous dyadic (Katz–Pavlović / Desnyansky–Novikov) model. No regulator
  abstraction; the viscous term is hardcoded.
- `docs/designs/OP2_LITE_CANDIDATES.md` — a **pre-registered exponent protocol** with no
  implementation ("No code is written"). Its `β = −2/3` is a pre-registered *threshold*,
  **not a measured control value**; E1 §4 mis-cited it as measured.

So M2 must **build** the harness. This memo designs the physics content (§1–§5); the
harness protocol (§6) is written to be *compatible with* OP2_LITE §3 so that, if
MechanicaFluidorum later implements its own, the two produce comparable numbers.

---

## 1. A structural obstruction, and why E1's "two-field candidate" was not optional

E1 §4 offered, parenthetically, "candidate: a phase/amplitude two-field shell system." That
understates the situation. **A real-amplitude shell model cannot host a dispersive regulator
at all.**

The model is `da_n/dt = B_n(a) − ν k_n² a_n` with `a_n ∈ ℝ`. Consider any linear regulator
`−c(k_n) a_n` with `c` real. Its contribution to the energy is

```
d/dt (½ Σ aₙ²)  ⊃  − Σ c(kₙ) aₙ²
```

which is `≤ 0` if `c ≥ 0` (dissipation) and `≥ 0` if `c ≤ 0` (forcing). **There is no real
linear regulator that is energy-neutral**, and energy-neutrality is precisely what
distinguishes dispersion from dissipation. The obstruction is a property of the model class,
not a shortage of ingenuity: dispersion is *phase rotation*, and a real amplitude has no
phase to rotate.

Consequence: W4 requires enlarging the state space. This is a **change of model**, not a
change of regulator, and it must be audited as such.

---

## 2. Resolution — a complexification that is not the obvious one

### 2a. The obvious complexification fails

Take `a_n ∈ ℂ` and keep the formula unchanged,
`B_n = k_{n−1} a_{n−1}² − k_n a_n a_{n+1}`. Then `E = ½ Σ |a_n|²` is **not** conserved.
Measured over 200 random complex states, `N=10`:

```
max |dE/dt| = 8.7e+03      median |dE/dt| = 7.9e+02
```

This is not a small violation to be absorbed; the naive complexification is a different,
non-conservative system.

### 2b. The conjugated complexification works

Place a single conjugation on the outgoing term:

```
        Bₙ(a)  =  k_{n−1} a_{n−1}²  −  kₙ · conj(aₙ) · a_{n+1}
```

Proof sketch (the cancellation is exact, not asymptotic). With
`dE/dt = Σ Re(conj(aₙ) Bₙ)`, the incoming term gives `Σ_m k_m Re(a_m² conj(a_{m+1}))` after
re-indexing `m = n−1`; the outgoing term gives `−Σ_n k_n Re((conj(aₙ))² a_{n+1})`, and since
`Re(z) = Re(z̄)`, `Re((conj(aₙ))² a_{n+1}) = Re(aₙ² conj(a_{n+1}))`. The two sums are
term-by-term identical and cancel.

**Verified numerically before being written here** (LL-7 discipline; scratch script, to be
promoted to a Tier B test on audit), 200 random complex states, `N=10`:

| Claim | Measured | Expected |
|---|---|---|
| `B_conj` conserves `½Σ\|aₙ\|²` | `max \|dE/dt\| = 1.8e−12` | round-off |
| `B_conj = B_real` on real data | `max abs diff = 0.000e+00` | **exact** |
| `Im(B_conj)` on real data | `max \|Im\| = 0.000e+00` | **exact** |

### 2c. Three consequences the auditor should weigh

**(i) The real model is an exactly invariant subspace.** Real initial data stays real under
`B_conj` (verified exactly, above). Therefore every solution of the real dyadic model —
including the finite-time blow-up solutions of **Katz–Pavlović (2005)** for the inviscid
case — is still a solution of the complexified model. The O5 falsification trap of OP2_LITE
§3 survives the change of model. This is the single strongest argument for *this*
complexification over switching to an off-the-shelf complex shell model (Sabra/GOY), which
would forfeit it.

**(ii) The Lean theorems do not transfer.** MechanicaFluidorum's `shellB_energy_conservation`
and `DyadicShellHypothesisU` (`lean_src/DyadicShell_Statements.lean`) are statements about
the **real** model. They say nothing about `B_conj`. Any formal claim about W4 needs its own
Lean development; until then W4 carries **no Tier A backing** and must not borrow the real
model's.

**(iii) The complexification is not unique, and this is a modeling choice.** Other
conjugation placements also conserve `Σ|aₙ|²` and also reduce to the real model. Nothing in
the physics selects `B_conj` uniquely — it is chosen here for the invariant-subspace property
of (i). **It must be reported as a deformation with a stated motivation, never as "the"
complexification.**

---

## 3. The W4 regulator: dissipation and dispersion differ by a 90° rotation

With complex amplitudes, viscosity and quantum pressure become the same term with the
coefficient rotated in the complex plane:

```
   viscous          daₙ/dt ⊃ − ν kₙ² aₙ        ν real        → dissipative
   quantum press.   daₙ/dt ⊃ − i D kₙ² aₙ      D real        → dispersive
```

Verified (200 random states): the viscous term drives `dE/dt` strictly negative
(`−3.7e+05` at the extreme); the quantum-pressure term is energy-neutral to
`max |dE/dt| = 2.7e−11`.

**Why this specific form, and why it makes the experiment clean.** In Madelung variables the
GPE quantum pressure is `Q = −(ℏ²/2m)·∇²√ρ/√ρ`, entering the *phase* equation. In Fourier
space `∇² → −k²`, so at shell `n` the quantum pressure contributes a phase rotation at rate
`D kₙ²` with `D = ℏ/2m`. It is amplitude-independent — a pure dispersion, exactly the
free-particle branch.

The payoff for W4 is that the dissipative and dispersive regulators have **identical
`k`-dependence** and differ *only* in the phase of the coefficient. The experiment therefore
isolates "dispersive vs dissipative" without confounding it with "different spectral
slope" — which the alternatives (hyperviscosity, truncation) cannot do.

**Healing length.** The crossover between the phonon branch (`ω ≈ ck`) and the free branch
(`ω ≈ Dk²`) sits at `ck = Dk²`, i.e. `ξ = D/c`, recovering E1 §2's healing scale.

**Common sweep axis.** For the three regulators to be comparable, each needs a regularization
*length*, squared, as its `α′`:

| Regulator | Regularization length | `α′` |
|---|---|---|
| Truncation | cutoff `k_N⁻¹` | `4^{−N}` (matches OP2_LITE §3) |
| Bounce (W2) | seam scale | seam location, `k⁻²` (see §5 — undesigned) |
| Dispersive (W4) | healing length `ξ = D/c` | `ξ²` |

Without this the three β's are not on a common axis and the comparison is meaningless.
**Auditor: this correspondence is a proposal, not a derivation** — in particular `c` for the
shell model is not yet defined (see §7, open item O3).

---

## 4. An honest limit: this is a BEC experiment, not a helium experiment

**The quantum-pressure regulator produces Bogoliubov dispersion, which has no roton.**

```
ω(k) = √( c²k²  +  (D k²)² )       — monotonic, no minimum
```

Superfluid ⁴He — the system M1 actually measured, and the system E1 §2 builds its dictionary
on — has a **phonon–maxon–roton** spectrum with a pronounced minimum at `Q ≈ 1.9 Å⁻¹`. That
minimum is a strong-correlation effect absent from GPE at any parameter value.

So: **M1's fitted `Δ` and `Q_m` have no counterpart in W4 as designed.** W4 tests a
dispersively-regularized cascade in the *GPE/weakly-interacting-BEC* sense. It does not, and
must not be reported as if it does, model ⁴He's excitation spectrum.

This is not a defect to be engineered away — it is the honest scope of the construction, and
stating it is required by E1's own quarantine discipline. Two live options for the auditor:

- **Accept the scope.** W4 is a BEC-regime experiment; E1 §2's ⁴He material stands as
  Tier A physics expression and is simply not what W4 probes. *(Recommended — see §7.)*
- **Extend the dispersion.** A roton minimum can be put in by hand via a `k`-dependent
  coefficient, but that is fitting a curve, not deriving a regulator, and it would forfeit
  the clean "same `k²`, rotated 90°" comparison of §3. Not recommended without a separate
  memo.

---

## 5. W2 (the bounce regulator) is NOT designed in this memo

For completeness and to prevent the same fiction recurring: **no reflective-seam regulator
exists anywhere, and none is designed here.**

What is known: T-duality `R ↔ α′/R` maps `k ↔ 1/(α′k)`, self-dual at `k = 1/√α′`. With
`α′ = 4^{−N}` this puts the self-dual scale exactly at `k_N` — the truncation scale, which is
a satisfying consistency check on the `α′` correspondence of §3.

What is **not** known, and must be settled before W2 is implemented: whether any reflecting
boundary condition at the seam (e.g. `a_{N+1} = a_{N−1}`) preserves `Σ|aₙ|²`. The dyadic
nonlinearity's energy cancellation is a telescoping identity that depends on the boundary
convention `a_{N+1} = 0`; changing that convention **will** break the telescoping unless the
replacement is constructed to preserve it. A W2 that silently leaks or creates energy would
produce a β difference caused by broken conservation rather than by the bounce — the exact
failure mode OP2_LITE flags for its Candidate A.

**Recommendation: W2 gets its own design memo, and W4 does not wait for it.** The
three-regulator comparison of E1 §4 can be run as two-then-three (truncation + W4 first,
W2 added when designed) without invalidating anything.

---

## 6. Pre-registered protocol (fixed before any run)

Written to be comparable with OP2_LITE §3; deviations are flagged.

- **Exponent definition:** `β` from `sup_t Ω ∝ α′^β`.
- **⚠ Ω is ambiguous in the reference implementation — auditor must rule.** See §7, O1.
- **Fit window:** largest contiguous `α′` range in which all configurations completed
  without tripping the magnitude guard. Fixed before the run; no post-hoc trimming.
- **Inclusion criterion:** a configuration enters the fit only if it reaches the full horizon
  at two successive `dt` refinements with `sup Ω` agreeing to within 1%. Exclusions reported
  **with their count**, never silently dropped.
- **Positive control #1 (free, and unusually strong):** at `D = 0` with real initial data,
  the complexified model must reproduce `exploration/dyadic_cascade.py`'s numbers **bit-for-bit
  up to integrator round-off**, because §2b showed the reduction is exact. An implementation
  failing this is miswired. *This control exists only because of the invariant-subspace
  property — it is the practical dividend of choosing `B_conj`.*
- **Positive control #2 (instrument validation, per OP2_LITE):** a known-bounded regime must
  read as bounded. An instrument never shown to register a known-bounded case cannot be
  believed when it reports boundedness.
- **O5 falsification trap:** at `ν = D = 0` with real initial data, the model must exhibit
  finite-time blow-up (Katz–Pavlović 2005). If it does not, the **implementation** is wrong.
  *Note the trap's precise scope:* it validates the integrator, not the dispersion claim,
  because `D > 0` breaks the reality-invariance and leaves the regime KP covers.
- **Pre-registered skepticism.** If W4 reports `β ≈ 0` (bounded) from dispersion alone at
  `ν = 0`, that is a claim of dispersive regularization of a model with a published blow-up
  theorem in its real subspace. It is **not** excluded by KP (see above), but it is
  extraordinary, and is pre-registered here as *requiring* independent replication at a
  second integrator and a second complexification before it may be reported as a finding.
- **Kill criterion:** if `β_W4` and `β_truncation` agree within fit uncertainty across the
  whole tested range, the cutoff *mechanism* is irrelevant at this observable. Per E1 §4 that
  is a **real and useful negative**, and is a successful outcome of the experiment, not a
  failure of it.

---

## 7. Open items requiring the auditor's ruling

**O1 — Which Ω? (blocking; also a defect report to MechanicaFluidorum.)**
`exploration/dyadic_cascade.py` is internally inconsistent about its own headline observable.
Its docstring and its `enstrophy()` helper (line 133) define `Ω = ½ Σₙ kₙ²aₙ²` (a **sum**),
but the `sup_Omega` actually written to `data/dyadic_omega_sup.csv` is computed in
`_simulate` (lines 160–163, 201–207) as a **max over shells**, `maxₙ ½kₙ²aₙ²`. Demonstrated
on that repo's own profile P2 at `N=8`, where every shell contributes equally:

```
enstrophy() helper (sum form) : 4.5
_simulate inner loop (max form): 0.5        ratio 9.0 = N+1
```

The two are not related by a fixed constant in general — the ratio depends on how energy is
distributed across shells, which itself varies with the regularization parameter, so the two
definitions can in principle yield **different β**, not merely an offset in `log`-space.
(Demonstrated: the observables differ. *Not* demonstrated: that β differs numerically in
MechanicaFluidorum's actual sweep — that would require re-running it, which is that repo's
call, not this one's.)

W4 cannot pick one silently. Options: **(a)** sum, matching the stated definition and the
standard meaning of enstrophy *(recommended)*; **(b)** max, matching what the reference
implementation actually computed, for numerical comparability with existing CSVs;
**(c)** record both. **This should also be reported to MechanicaFluidorum as a defect** —
it is that repo's data, and this memo does not modify another stream's code.

**O2 — Is the change of model acceptable?** W4 requires complexifying the dyadic model
(§1–§2). This forfeits the existing Lean backing (§2c-ii) and introduces a non-unique
modeling choice (§2c-iii), in exchange for the only construction in which "dispersive" is
even definable. *Recommendation: accept, with the deformation explicitly labelled.*

**O3 — What is `c` for the shell model?** §3's healing length `ξ = D/c` needs a sound speed.
The dyadic model has no pressure and no linear wave branch, so `c` is not intrinsic to it.
Either define `c` operationally (e.g. from the nonlinear transfer rate at the largest shell)
or re-parameterize the sweep directly in `D` and drop `ξ`. *Recommendation: sweep `D`
directly; report `ξ` only if `c` can be defined non-circularly.*

**O4 — Scope: BEC or ⁴He?** §4. *Recommendation: accept the BEC scope; do not bolt on a
roton.*

**O5 — Harness location.** Owner has provisionally chosen "build in QuantumFluids, offer
upstream later" (PLAN.md decision 2c). Nothing in this memo depends on that choice.

---

## 8. What this document does not do

No code is written; nothing here may be implemented before audit. The verification in §2b/§3
is a **scratch script** run to prevent this memo from asserting unchecked mathematics — it
is not a repository test, and must be promoted to a Tier B harness (with negative controls,
per LL-2) as the *first* implementation step after audit, not retrofitted afterwards.

No claim is made that `B_conj` **is** the quantum-fluid dyadic model. It is a deformation
chosen for one specific property (§2c-i). No claim is made that dispersion regularizes the
cascade — that is the question W4 exists to ask, and §6 pre-registers the answer's
acceptance criteria in both directions.

W2 is not designed (§5). The Lean development is not attempted (§2c-ii). No Tier A or Tier B
claim is created by this document.
