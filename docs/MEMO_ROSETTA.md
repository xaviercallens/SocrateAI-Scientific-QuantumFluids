# MEMO ROSETTA: The Dual-Scale Principles Across Domains — Living Catalog

**Status:** living document; one row per domain; governed by Rule E-X.

**Rule E-X (Express before extend):** a domain enters this table only as the *re-expression of an established theorem* in the common language (Tier A/B by inheritance, citation verified), and may only afterwards host an extension (Tier C, labeled). A row violating this order is deleted, not fixed.

---

## The Four Atomic Principles

The dual-scale hypothesis, atomized into four testable principles:

- **P1** **Self-dual bound:** conserved product ⇒ scale floor at √C  
  Lean: `Mathesis.Duality.sqrt_le_max_of_le_mul`

- **P2** **Sym² lock:** macroscopic modes are products of microscopic modes; no independent macro degree of freedom  
  Lean: `sym2_recurrence` (TBD)

- **P3** **Discrete pins continuous:** a continuous quantity equals (a power of) the inverse of a discrete invariant  
  Lean: `resonance_law` family (TBD)

- **P4** **Bounce:** contraction below the self-dual scale reflects into dilation  
  Lean: `Reff_bounce` (TBD)

---

## The Catalog

### Finite Fourier Analysis

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Finite Fourier analysis** | Donoho–Stark: `∣supp x∣ · ∣supp x̂∣ ≥ N`; Tao (2005, N prime): `∣supp x∣ + ∣supp x̂∣ ≥ N+1` | P1; P1+P3 (prime hardening) | Consequence proved (`support_balance`, lean_src/Duality.lean); full DS = TARGET T-DS; Tao row `[LL-6 pending]` | First dual-scale theorem outside fluids; the prime refinement is the thesis "arithmetic hardens duality" already in print | Library check for `ZMod.dft`+Plancherel; discharge T-DS |

**Notes:**
- Donoho–Stark is Tier A (Donoho & Stark, 1989, *SIAM Review*).
- Tao refinement (Tao, 2005, *"An introduction to measure theory"*, or *"Additive Combinatorics"*) shows that on primes, the bound hardens: the sum of support sizes has a strictly larger floor than just √N.
- Status: the abstract theorem is kernel-proved; discharging the hypothesis (that the product is indeed ≥ N) is TARGET T-DS.

---

### 2D Ising Model

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **2D Ising duality** | Kramers–Wannier duality `sinh(2K)·sinh(2K*) = 1`; self-dual point = critical point; K_c = log(1+√2)/2 | P1, A.5 fixed point | **Kernel-proved**: `kramers_wannier_self_dual` (lean_src/Duality.lean L98) | The critical temperature of a real phase transition located *purely by self-duality* — the stat-mech twin of √α′ | T-KW2 (involution packaging); Tier B finite-lattice identities to go to exact-arithmetic harness |

**Notes:**
- Kramers–Wannier (1941, *Phys. Rev.*) is Tier A.
- The self-dual fixed point uniquely determines the critical coupling; this is the closest statistical-mechanics analogue to the quantum-fluid roton-gap scale.
- Conceptual bridge: just as roton gap Δ × length scale ξ = α' (conserved), the Ising coupling K and its dual K* obey sinh(2K)·sinh(2K*) = 1, pinning the self-dual point.

---

### Quantum Fluids (GPE, superfluid ⁴He, BEC)

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Quantum fluids: dual-scale regularization** | Quantized circulation; vortex cores pinned at healing length ξ ~ ℏ/√(mα'); quantum-pressure regulator; ξ→0 limit open | P2, P3, P4; sibling of MechanicaFluidorum Hyp. U | Expression memo **E1** filed (docs/EXPRESSION_MEMO_E1.md); all citations `[LL-6 pending]` (LITERATURE_LEDGER.md); M0 blocking | "Nature already implements a topological cascade cutoff" becomes citable (in He II, not water); Hyp. U gains a named sibling with experimental grounding | E1 §5 literature retrieval (M0); W4 experiment design and execution (M1–M3) |

**Notes:**
- QuantumFluids instantiates P2 (hydrodynamic modes as products of phonon×roton) and P3 (healing length pinned by circulation quantum).
- Roton gap Δ and length scale ξ satisfy ξ ~ √(α'/Δ), exemplifying the P1 bound.
- The program does NOT claim to resolve ξ→0; that limit remains open (MechanicaFluidorum obstruction O5).

---

### Quantum Hall Metrology

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Hall conductance metrology** | σ_xy = ν·e²/h pinned by a Chern integer ν to ~10⁻¹⁰ accuracy; defines the ohm (NIST standard) | P3 (topological pinning) | Established, experimentally verified (NIST, BIPM); citation TBD `[LL-6 pending]` | The resonance law running as *industrial metrology* — P3's strongest existing instance; a continuous (conductance) pinned by a topological integer (Chern class) | One related-work paragraph in outreach; no formalization planned |

**Notes:**
- Quantum Hall effect (von Klitzing, 1980, *Phys. Rev. Lett.* 45:494) is Tier A.
- Integer Quantum Hall Plateaus obey σ_xy = (e²/h)·(Chern integer), making it the most precise continuous-to-discrete pinning in metrology.

---

### Discrete Geometry

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Discrete Gauss–Bonnet** | Descartes/discrete Gauss–Bonnet: Σ(angular defects) = 2πχ, where χ is the Euler characteristic | P3 (combinatorial) | Lean-able now (pure combinatorics, integer invariant); `[LL-6 pending]` for a modern citation | A ten-line kernel proof that a continuous total (sum of angles) is pinned by a topological integer (Euler characteristic); pedagogical anchor for P3 | Add to Mathesis backlog (low priority, high pedagogical value) |

**Notes:**
- Descartes (1639 manuscript); rigorous in Chern–Simons (1974) and discrete curvature literature (Stillwell, Cartwright).
- Directly exemplifies P3: the continuous sum of angular defects equals an integer × 2π.

---

### Analytic Number Theory (⚠️ Change Request CR-1)

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Dirichlet class number formula** | L(1, χ_d) ~ c·h(d)/√\|d\|, where h(d) is the class number and χ_d is a character | P3 — **with exponent 1/2** | Established (Dirichlet, 1839); `[LL-6 pending]` for the precision statement | **A correction to the programme (CR-1):** where nature realizes P3 arithmetically, the pinning goes as 1/√\|disc\|, not 1/\|disc\|. This may force a choice in the coupling-mass exponent (see CR-1 below). | Apéry–Fermi instance (K3 arithmetic); decision awaits MEMO-K3 §5.2 |

**Notes:**
- The class number h is pinned *inversely as the square root* of the discriminant, not its reciprocal. This is the exponent correction that CR-1 raises.

---

### String T-Duality

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **T-duality: R ↔ α′/R** | Under T-duality, strings at radius R are indistinguishable from strings at radius α′/R; spectrum invariant (Giveon–Porrati–Rabinovici, *Eq. 2.2.11*, VERIFIED in MechanicaFluidorum report) | P1, P4 (motivation) | Already in the programme, correctly quarantined (MechanicaFluidorum §4.1) | Unchanged; no re-expression planned | None (already integrated) |

**Notes:**
- T-duality is the primary motivation for studying P1 and P4 in string theory.
- The programme does not attempt to extend this result.

---

### Operations Research (EOQ)

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Wilson Economic Order Quantity** | Optimal lot Q* is self-dual between ordering cost (D·K/Q) and holding cost (h·Q/2); both are equal at optimum; total cost = 2√(D·K·h/2) | P1 (additive twin, A.4) | **Kernel-proved**: `eoq_lower_bound` (lean_src/Duality.lean L60) | A century of industrial practice (Wilson, 1934) as an instance of the same lemma — the "universality" claim made concrete and unpretentious | None (done); cite in outreach materials |

**Notes:**
- Wilson's EOQ is taught in every supply-chain management course.
- The self-dual structure (ordering cost = holding cost at optimum) mirrors the quantum-fluid structure (phonon energy = roton energy at scale √α').

---

### K3 Arithmetic (Apéry Constants)

| Field | Established result | Principle(s) | Status | What expression gains | Action |
|---|---|---|---|---|---|
| **Apéry operator / ζ(3) family** | Apéry operator = Picard–Fuchs operator of the Beukers–Peters family; symbol self-reciprocal; z₁·z₂ = 1 (MEMO-K3, VERIFIED + ELEMENTARY) | P1's involution on a discriminant locus; P2 via Doran | Filed (MEMO-K3, separate repo) | The T-involution and the Sym² lock co-occur on the ζ(3) family; arithmetic instance of dual-scale locking | MEMO-K3 §5 actions (Doran scope check first); Peters 1986 retrieval (`[LL-6 pending]`) |

**Notes:**
- Apéry (1978, *Astérisque*) is Tier A.
- The Apéry–Fermi transcendental lattice is a named, measured discrete structure whose discriminant couples to the ζ(3) constant.
- This is the **primary candidate for testing CR-1's √|disc| refinement** once Peters 1986 is retrieved.

---

## Rejected Instances

These were proposed and rejected. Recording them prevents re-proposal.

| Candidate | Reason for rejection |
|---|---|
| Loop-quantum-cosmology bounce | Conjectural physics cannot evidence a conjectural principle; P4 must be instantiated by theorems or measurements only. LQC remains speculative. |
| AdS/CFT "holography" | Already quarantined by the programme (MechanicaFluidorum §4.1); no rigorously constructed correspondence exists here. Cannot be used as evidence. |
| Finance power laws / "market self-duality" | No conserved product, no theorem; pattern-matching risk maximal. Rejected as over-extrapolation. |

---

## CR-1: Change Request to Mathesis — the √|disc| refinement

### Observation

The catalog's strongest arithmetic instance of P3 (Dirichlet class number formula) pins the continuous quantity with **exponent 1/2** in the discriminant:

$$h(d) \sim \frac{c}{\sqrt{|d|}}$$

However, the programme's `couplingMass F = 1/|disc F|` uses **exponent 1**.

### Proposal

Add, without deleting:

```lean
def couplingMassSqrt (F : NumberField) : ℝ :=
  1 / Real.sqrt |(F.disc : ℝ)|
```

with the same theorem suite (positivity, ≤ 1, resonance law in the form `m² · |disc| = 1`, quantization).

Both laws are trivially consistent; the **choice between them is empirical/structural** and must be decided by an instance. The first candidate is the **Apéry–Fermi transcendental lattice** (once Peters 1986 is retrieved — MEMO-K3 §5.2).

### Implementation

Until the choice is decided, papers state the coupling law as:

$$m = |disc|^{-s}, \quad s \in \{1/2, 1\}$$

with **s explicitly open as a structural exponent**. This is what it looks like for a general principle to accept correction from its instances—the catalog's first concrete payoff.

### Timeline

- Retrieve Peters 1986 (MEMO-K3 §5.2, target 2026-09-30)
- Compute discriminant of Apéry–Fermi lattice
- Measure which exponent (1/2 or 1) fits the constant
- File decision in Mathesis repo with justification

---

## Standing Process

1. **New rows require:** established theorem + verified citation + principle tag(s) + gain statement
2. **Extensions** live in a row's Action column as Tier C; they never appear in the Status column
3. **Axiom certificates:** every kernel-proved Status entry links a `#print axioms` line from the Lean proof
4. **Review cadence:** the catalog is re-audited whenever a row's Action completes; stale `[LL-6 pending]` items older than one quarter trigger escalation (Rule E-1)

---

## Cross-References

- **Duality.lean** (lean_src/): Core theorems (P1, A.4, A.5, Kramers–Wannier)
- **EXPRESSION_MEMO_E1.md**: QuantumFluids expression (P2, P3, P4 in physics language)
- **LITERATURE_LEDGER.md**: Citation inventory for all Tier A rows
- **LL.md**: Lessons learned, including LL-6 (pending literature from E1)
- **PLAN.md**: Milestones M0–M4 (M0 unlocks all `[LL-6 pending]` items)
- **MEMO-K3** (separate repo): Apéry operator and K3 arithmetic

---

**Last updated:** 2026-08-14  
**Governed by:** Rule E-X (express before extend)  
**Next review:** Upon completion of M0 literature retrieval or CR-1 decision
