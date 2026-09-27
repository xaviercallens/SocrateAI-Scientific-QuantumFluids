# Retractions, 2026-09-20 — the literature check

The literature check that `DUAL_SCALE_PROPOSAL.md` §6 listed as *"pending and blocking any external
novelty claim"* was run on 2026-09-20. **It went against this programme on both counts.** This file
records what is withdrawn, against what reference, and what survives.

Epistemic status of the references: the two decisive papers were verified independently of the search
— exact titles, authors and journal references confirmed by direct fetch, and the *Fibonacci
turbulence* abstract confirms the "families of quadratic conservation laws" in its own words. The
equation-level quotations below come from the literature check's account of reading those PDFs and
**have not been read line-by-line here**; a human spot-check of the two 2021 papers is the one
outstanding verification, and nothing in this file depends on an equation number.

---

## R1 — The "second invariant" (CLAIM-023) is a **rediscovery**

**Withdrawn:** any suggestion that the Hamiltonian / second-harmonic-generation structure of the
complexified dyadic shell model, or its cubic invariant, is new.

| reference | what it already contains |
|---|---|
| **Vladimirova, Shavit, Falkovich, "Fibonacci turbulence", Phys. Rev. X 11, 021063 (2021)**, arXiv:2101.10418 | the three-wave Hamiltonian, a local **cubic** Hamiltonian, the **graded** U(1) phase symmetry, and quadratic invariants the authors themselves call *"generalizations of the Manley–Rowe invariants for three-wave interactions"*. Its abstract states the "families of quadratic conservation laws defined by the Fibonacci numbers". |
| **Vladimirova, Shavit, Belan, Falkovich, "Second harmonic generation as a minimal model of turbulence", Phys. Rev. E 104, 014129 (2021)**, arXiv:2103.15468 | **the title is the framing offered here as an insight.** The two-mode case of our chain, with the cubic monomial `conj(v)²v'` in the Hamiltonian and the Manley–Rowe invariant. |
| **L'vov, Podivilov, Procaccia, Europhys. Lett. 46, 609 (1999)**, arXiv:chao-dyn/9804036 | the Sabra shell model is canonically Hamiltonian under `a_n = v_n/ε^{n/2}` — **the exact analogue of our `w_n = 2^{-n/2}v_n`** — and they already note that the Hamiltonian is not the energy. |
| **Ditlevsen, Phys. Rev. E 62, 484 (2000)**, arXiv:chao-dyn/9811004 | the same package independently: graded phases, cubic invariant, Hamiltonian structure after rescaling. |
| **Armstrong, Bloembergen, Ducuing, Pershan, Phys. Rev. 127, 1918 (1962)** | `Re(a₁²a₂*)` as a constant of motion — since 1962. |
| **Biferale, Annu. Rev. Fluid Mech. 35, 441 (2003)**, p. 442 | Liouville (phase-space volume preservation) is stated there as a **design criterion** for shell models, not an observation. So CLAIM-011 "Liouville is a corollary" restates a textbook desideratum. |

**Worse than neutral.** On the dyadic lattice `2^a + 2^b = 2^c` forces `a = b`, so the Manley–Rowe
family **collapses to a single invariant**, where the Fibonacci lattice carries two — which is why
those models exhibit dual cascades and ours cannot. The dyadic case therefore has **less** structure
than the published family, not more. If anything defensible remains it is a remark about the
degenerate special case, stated as a special case of Vladimirova–Shavit–Falkovich.

**What is untouched:** the Lean proofs are correct mathematics and the machine-checking is real. They
formalize known results. `H ≡ 0` on real data, and the `σ`-rule bookkeeping, remain correct statements.

## R2 — The dual length (CLAIM-024) is not novel in content, and its bound is **weaker than the known one**

**Withdrawn:** any suggestion that `ℓ(k) = ε²/(ħ²c²k³)` or its floor constitutes a new result.

1. **It is a repackaging.** `k·ℓ = (ε/ħck)²`, and `ℓ = χ(0)/(k χ(k))` with `χ` the static density
   response; also `ℓ = v_L(k)²/(c²k)` with `v_L = ε/ħk` the Landau-velocity function. The "bound" is
   `x + 1/x ≥ 2`, i.e. AM–GM, which §1 already said — but §1 presented the *shape* as the point.
2. **The known structure-factor bound is stronger.** Onsager's inequality, with the explicit constant
   from the f-sum and compressibility sum rules, gives **`S(k) ≤ ħk/(2mc)`** — *linear* in `k`:
   - **Wreszinski & da Silva, J. Phys. A 38, 6293 (2005)**, arXiv:cond-mat/0411640 (Onsager's
     inequality; attribution via Price, Phys. Rev. 94, 257 (1954));
   - **Stringari, arXiv:cond-mat/9311024** (sum-rule form; the same argument yields Bogoliubov's
     1/q theorem).
   Our `S ≤ √(k/2k*)` is **strictly weaker for `k < k*/2`** and **vacuous beyond `2k*`**. It is
   non-trivially tighter only in the narrow window `k*/2 < k < 2k*`.
3. **The result is dimensionally forced.** Bogoliubov theory contains exactly one length (`ξ`) and one
   velocity (`c`). *Any* length built from `ε, c, m, ħ, k` that has an interior minimum must have it at
   `k ∼ 1/ξ` with value `∼ ξ`. So "`ℓ_min = √2 ξ` at `k* = √2/ξ`" **carries no information beyond
   "the crossover is at ξ"**. This is the deepest objection: the theorem could not have come out
   otherwise.
4. **The ⁴He "refutation" is structural, not empirical.** Since `ℓ = v_L²/(c²k)`, **any** fluid with a
   roton (`v_L ≪ c` at finite `k`) violates `ℓ ≥ ħ/(mc)`. Measuring 21–51× confirms ⁴He has a roton.
5. **Prose error, now corrected.** `DUAL_SCALE_PROPOSAL.md` §2 wrote "under Feynman's relation … the
   bound is **exactly** `S(k) ≤ √(k/2k*)`". Bijl–Feynman is an **inequality**,
   `ε(k) ≤ ħ²k²/(2mS(k))`. The Lean is sound — `not_bogoliubov_of_structure_factor` correctly takes
   `epsSq ≤ (…)²` as a hypothesis — but the prose implied an equality. Sharper rigorous bounds exist:
   **Boronat, Casulleras, Dalfovo, Moroni, Stringari, Phys. Rev. B 52, 1236 (1995)**.
6. **The "Pythagorean" form is standard**: `Dalfovo, Giorgini, Pitaevskii, Stringari, Rev. Mod. Phys.
   71, 463 (1999)`, eq. (70)–(71). Only the word is ours.

**Not found in the literature:** `ε²/k³` used as a named diagnostic, and the `k ↦ k*²/k` self-duality
of the Bogoliubov dispersion. But per (3) that absence is not evidence of a finding — it is what one
expects of a quantity nobody needed to name. One unverified lead remains
(DOI 10.1007/s40509-026-00409-7, snippet only, paywalled).

## R3 — Also corrected this day (external review of the v1.1.0 tag)

- **`lean_src/.lake` was committed as a symlink to a local disk**, breaking every clone. `.gitignore`
  had `lean_src/.lake/` *with a trailing slash*, which matches a directory but not a symlink. Untracked
  and the pattern fixed.
- **Reported theorem counts were wrong.** 76 theorems existed where 65 carried a `#print axioms` line,
  so 11 were never axiom-audited and every published count conflated "theorems" with "theorems
  carrying an audit line". The external review spotted one instance (`DualLength`: 13 vs 12); checking
  all files showed it was five files. Root cause — a hand-maintained audit list — is fixed by
  `scripts/regen_axiom_audit.py`, which regenerates the blocks and has a `--check` mode. All 76 now
  audited; all clean.

---

## What survives

**No novel scientific contribution survives in the dual-scale programme.** Stated plainly because the
alternative is to keep the framing and quietly drop the novelty, which would be worse.

What remains real:

1. **The formalization.** 76 machine-checked theorems, Comparator-verified against two independent
   kernels. They are correct proofs of results that are known (R1) or dimensionally forced (R2). Value:
   verification infrastructure and a worked example of formalizing fluid-dynamics structure — not discovery.
2. **The measurements.** The ⁴He numbers (21× → 51×) are correct measurements, correctly controlled.
   They confirm textbook physics.
3. **The methodology record.** Controls that voided runs, a confound caught by a threshold sweep,
   registered predictions recorded as wrong, a timeout logged as a bookkeeping stop. This is the part
   that held up, and the literature check is its final instance: the programme's own gate fired against
   the programme.
4. **One possible small item**, subject to its own check: the *degenerate/dyadic* case is not in print
   as such, and the collapse of the Manley–Rowe family to a single invariant is a concrete structural
   difference from the Fibonacci family. It would be a remark within Vladimirova–Shavit–Falkovich's
   framework, not a result of its own.

**Consequence for the paper and releases:** the paper must be rewritten to cite these references and
to present its content as formalization of known structure. The `v1.0.0`/`v1.1.0` release notes already
say "no novelty is claimed" throughout, so they are not false — but they are now superseded by named
references, which is stronger and belongs in the record.
