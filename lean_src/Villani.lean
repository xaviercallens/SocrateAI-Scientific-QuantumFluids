/-
  Villani.lean -- a foundation for formalizing Cédric Villani's work, offered as a tribute.

  * `card_sq_ge` -- **Ollivier and Villani, "A curved Brunn-Minkowski inequality on the discrete
    hypercube", arXiv:1011.4779, Theorem 1, the K = 0 case.** For nonempty A, B in the Hamming cube
    {0,1}^N with midpoint set M, `#A * #B ≤ (#M)^2`. FULLY PROVED, no `sorry`, by the injection
    A×B ↪ M×M the paper's Section 3 describes: a canonical choice of which half of the differing
    coordinates of a pair (a,b) comes from `a`, together with the complementary choice, is
    recoverable from the resulting pair of midpoints.

  * The full Theorem 1, with the curvature term K = 1/(2N), is NOT attempted: its proof needs
    concentration of measure in the symmetric group (the paper's Lemma 4 and Proposition 5, via a
    quotienting argument), machinery not built here. See
    `docs/designs/ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md` §7 for the open-target list this belongs to.

  * `klDiv_nonincreasing_to_invariant` -- a three-line corollary of Mathlib's own
    `MeasureTheory.klDiv_comp_right_le` (the Data Processing Inequality for a Markov kernel), for a
    measure invariant under that kernel: the modern relative-entropy form of Boltzmann's H-theorem
    for a Markov chain. NOT presented as a contribution -- the mathematical content is entirely
    Mathlib's `klDiv_comp_right_le`. Included because it is the discrete skeleton of the entropy
    methods Villani surveys in "H-theorem and beyond" (Boltzmann's Legacy, EMS 2008), and it connects
    this file to `ZeroSound.lean`'s Fermi-liquid kinetic theory inside one project.

  Not attempted: the continuous collisional Boltzmann H-theorem, hypocoercivity, log-Sobolev and
  Talagrand inequalities, the Lott-Villani-Sturm curvature-dimension condition, and Landau damping
  (linear: see `ZeroSound.lean`; nonlinear: formalized, sorry-free, by J. Bedrossian,
  arXiv:2609.16801, which this file does not duplicate).
-/
import Mathlib

open scoped Classical
open Finset

namespace QuantumFluids.Villani

variable {N : ℕ}

abbrev Cube (N : ℕ) := Fin N → Bool

/-- The coordinates where `a` and `b` differ. -/
def diff (a b : Cube N) : Finset (Fin N) := univ.filter (fun i => a i ≠ b i)

/-- The Hamming distance. -/
def dist (a b : Cube N) : ℕ := (diff a b).card

theorem mem_diff_iff {a b : Cube N} {i : Fin N} : i ∈ diff a b ↔ a i ≠ b i := by
  simp [diff]

/-- The general metric definition of a midpoint (Ollivier-Villani, Section 1.1):
`d(m,a) + d(m,b) = d(a,b)`, and `d(m,a)` within `1` of `d(a,b)/2` (written without division). -/
def IsMidpoint (a b m : Cube N) : Prop :=
  dist m a + dist m b = dist a b ∧ 2 * dist m a ≤ dist a b + 1 ∧ dist a b ≤ 2 * dist m a + 1

/-- The midpoint set of two finite sets `A, B`. -/
noncomputable def midpointSet (A B : Finset (Cube N)) : Finset (Cube N) :=
  univ.filter (fun m => ∃ a ∈ A, ∃ b ∈ B, IsMidpoint a b m)

/-- `crossover c a b` takes `a`'s bit on `c` and `b`'s bit elsewhere: `φ_c(a,b)` in the paper. -/
def crossover (c : Finset (Fin N)) (a b : Cube N) : Cube N :=
  fun i => if i ∈ c then a i else b i

@[simp] theorem crossover_apply_mem {c : Finset (Fin N)} {a b : Cube N} {i : Fin N} (h : i ∈ c) :
    crossover c a b i = a i := if_pos h

@[simp] theorem crossover_apply_not_mem {c : Finset (Fin N)} {a b : Cube N} {i : Fin N}
    (h : i ∉ c) : crossover c a b i = b i := if_neg h

/-- `diff (crossover c a b) a = diff a b \ c`, for ANY `c` (no hypothesis needed). -/
theorem diff_crossover_left (c : Finset (Fin N)) (a b : Cube N) :
    diff (crossover c a b) a = diff a b \ c := by
  ext i
  by_cases hi : i ∈ c
  · have : i ∉ diff a b \ c := by simp [hi]
    simp [mem_diff_iff, crossover_apply_mem hi, this]
  · rw [mem_diff_iff, crossover_apply_not_mem hi, mem_sdiff, mem_diff_iff]
    constructor
    · intro h; exact ⟨Ne.symm h, hi⟩
    · intro h; exact Ne.symm h.1

/-- `diff (crossover c a b) b = c`, given `c ⊆ diff a b`. -/
theorem diff_crossover_right {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) :
    diff (crossover c a b) b = c := by
  ext i
  by_cases hi : i ∈ c
  · have hd : a i ≠ b i := mem_diff_iff.mp (hc hi)
    simp [mem_diff_iff, hi, crossover_apply_mem hi, hd]
  · simp [mem_diff_iff, hi]

theorem dist_crossover_left (c : Finset (Fin N)) (a b : Cube N) :
    dist (crossover c a b) a = (diff a b \ c).card := by rw [dist, diff_crossover_left]

theorem dist_crossover_right {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) :
    dist (crossover c a b) b = c.card := by rw [dist, diff_crossover_right hc]

/-- Any `c ⊆ diff a b` with `c.card` within `1` of `dist a b / 2` gives a genuine midpoint. -/
theorem isMidpoint_crossover {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b)
    (h1 : 2 * c.card ≤ dist a b + 1) (h2 : dist a b ≤ 2 * c.card + 1) :
    IsMidpoint a b (crossover c a b) := by
  have hda : dist (crossover c a b) a = (diff a b \ c).card := dist_crossover_left c a b
  have hdb : dist (crossover c a b) b = c.card := dist_crossover_right hc
  have hsum : (diff a b \ c).card + c.card = dist a b := card_sdiff_add_card_eq_card hc
  have hda' : dist (crossover c a b) a + c.card = dist a b := by rw [hda]; exact hsum
  refine ⟨by rw [hda, hdb]; exact hsum, ?_, ?_⟩ <;> omega

/-! ### A canonical half of a finite subset of `Fin N`

`takeHalf s` is the set of the `s.card / 2` smallest elements of `s`, for the natural order on
`Fin N` -- a function of `s` alone, crucial for the reconstruction argument below. -/

def takeHalf (s : Finset (Fin N)) : Finset (Fin N) :=
  (univ : Finset (Fin (s.card / 2))).image
    (fun i => s.orderEmbOfFin rfl (Fin.castLE (Nat.div_le_self _ 2) i))

theorem takeHalf_subset (s : Finset (Fin N)) : takeHalf s ⊆ s := by
  intro x hx
  simp only [takeHalf, mem_image, mem_univ, true_and] at hx
  obtain ⟨i, hi⟩ := hx
  rw [← hi]
  exact orderEmbOfFin_mem s rfl _

theorem card_takeHalf (s : Finset (Fin N)) : (takeHalf s).card = s.card / 2 := by
  have hinj : Function.Injective
      (fun i : Fin (s.card / 2) => s.orderEmbOfFin (rfl : s.card = s.card)
        (Fin.castLE (Nat.div_le_self _ 2) i)) := by
    intro i j h
    exact Fin.castLE_injective _ ((s.orderEmbOfFin rfl).injective h)
  rw [takeHalf, Finset.card_image_of_injective _ hinj, Finset.card_univ, Fintype.card_fin]

/-! ### The injection, and Theorem 1 at `K = 0` -/

/-- `takeHalf (diff a b)` has size within `1` of `dist a b / 2`, so it qualifies as a crossover. -/
theorem takeHalf_card_bounds (a b : Cube N) :
    2 * (takeHalf (diff a b)).card ≤ dist a b + 1 ∧
    dist a b ≤ 2 * (takeHalf (diff a b)).card + 1 := by
  unfold dist; rw [card_takeHalf]; omega

/-- The pair of midpoints coded by the canonical half `takeHalf (diff a b)` and its complement:
`Φ_{c_r}(a,b) = (φ_{c_r}(a,b), φ_{c̄_r}(a,b))` in the paper's notation. -/
def encode (a b : Cube N) : Cube N × Cube N :=
  (crossover (takeHalf (diff a b)) a b, crossover (diff a b \ takeHalf (diff a b)) a b)

theorem encode_fst_isMidpoint (a b : Cube N) : IsMidpoint a b (encode a b).1 :=
  isMidpoint_crossover (takeHalf_subset _) (takeHalf_card_bounds a b).1 (takeHalf_card_bounds a b).2

theorem encode_snd_isMidpoint (a b : Cube N) : IsMidpoint a b (encode a b).2 := by
  have hc : diff a b \ takeHalf (diff a b) ⊆ diff a b := sdiff_subset
  have hcard : (diff a b \ takeHalf (diff a b)).card + (takeHalf (diff a b)).card
      = (diff a b).card := card_sdiff_add_card_eq_card (takeHalf_subset _)
  have hd : dist a b = (diff a b).card := rfl
  have hb := takeHalf_card_bounds a b
  have h1 : 2 * (diff a b \ takeHalf (diff a b)).card ≤ dist a b + 1 := by omega
  have h2 : dist a b ≤ 2 * (diff a b \ takeHalf (diff a b)).card + 1 := by omega
  exact isMidpoint_crossover hc h1 h2

theorem encode_mem_midpointSet {A B : Finset (Cube N)} {a b : Cube N} (ha : a ∈ A) (hb : b ∈ B) :
    (encode a b).1 ∈ midpointSet A B ∧ (encode a b).2 ∈ midpointSet A B :=
  ⟨mem_filter.mpr ⟨mem_univ _, a, ha, b, hb, encode_fst_isMidpoint a b⟩,
   mem_filter.mpr ⟨mem_univ _, a, ha, b, hb, encode_snd_isMidpoint a b⟩⟩

/-- **Recoverability**: `diff` of the two encoded midpoints equals `diff a b`, for ANY
`c ⊆ diff a b` and its complement, not just the canonical half. This is what makes `encode`
invertible: `r := d(a,b)` is read off as `d(m, m')`. -/
theorem diff_crossover_crossover_compl {c : Finset (Fin N)} {a b : Cube N} (hc : c ⊆ diff a b) :
    diff (crossover c a b) (crossover (diff a b \ c) a b) = diff a b := by
  ext i
  simp only [mem_diff_iff]
  by_cases hic : i ∈ c
  · have hnc : i ∉ diff a b \ c := by simp [hic]
    rw [crossover_apply_mem hic, crossover_apply_not_mem hnc]
  · by_cases hid : i ∈ diff a b
    · have hinc : i ∈ diff a b \ c := mem_sdiff.mpr ⟨hid, hic⟩
      rw [crossover_apply_not_mem hic, crossover_apply_mem hinc]
      exact ne_comm
    · have hinc : i ∉ diff a b \ c := fun h => hid (mem_sdiff.mp h).1
      have heq : a i = b i := by
        by_contra hne; exact hid (mem_diff_iff.mpr hne)
      rw [crossover_apply_not_mem hic, crossover_apply_not_mem hinc]
      exact iff_of_false (fun h => h rfl) (fun h => h heq)

/-- **`encode` is injective on pairs**: this is Theorem 1's Φ, and the whole content of the
K = 0 case. From `encode a b = encode a' b'`, both sides give `diff a b = diff m m' = diff a' b'`
(previous lemma), so `c := takeHalf (diff a b)` is the SAME finset used to build both encoded
pairs; reading off `a, b, a', b'` at each coordinate `i` by whether `i ∈ c`, `i ∈ diff a b \ c`,
or neither, gives `a = a'` and `b = b'` in every case. -/
theorem encode_injective {a b a' b' : Cube N} (h : encode a b = encode a' b') :
    a = a' ∧ b = b' := by
  simp only [encode, Prod.mk.injEq] at h
  obtain ⟨hm, hm'⟩ := h
  have hD : diff a b = diff a' b' := by
    have h1 := diff_crossover_crossover_compl (a := a) (b := b) (takeHalf_subset (diff a b))
    have h2 := diff_crossover_crossover_compl (a := a') (b := b') (takeHalf_subset (diff a' b'))
    rw [hm, hm'] at h1
    rw [← h1]; exact h2
  rw [← hD] at hm hm'
  have key : ∀ i : Fin N, a i = a' i ∧ b i = b' i := by
    intro i
    by_cases hic : i ∈ takeHalf (diff a b)
    · have e1 : a i = a' i := by
        have hcf := congrFun hm i
        rwa [crossover_apply_mem hic, crossover_apply_mem hic] at hcf
      have hnc : i ∉ diff a b \ takeHalf (diff a b) := by simp [hic]
      have e2 : b i = b' i := by
        have hcf := congrFun hm' i
        rwa [crossover_apply_not_mem hnc, crossover_apply_not_mem hnc] at hcf
      exact ⟨e1, e2⟩
    · by_cases hid : i ∈ diff a b
      · have hinc : i ∈ diff a b \ takeHalf (diff a b) := mem_sdiff.mpr ⟨hid, hic⟩
        have e1 : a i = a' i := by
          have hcf := congrFun hm' i
          rwa [crossover_apply_mem hinc, crossover_apply_mem hinc] at hcf
        have e2 : b i = b' i := by
          have hcf := congrFun hm i
          rwa [crossover_apply_not_mem hic, crossover_apply_not_mem hic] at hcf
        exact ⟨e1, e2⟩
      · have heq : a i = b i := by by_contra hne; exact hid (mem_diff_iff.mpr hne)
        have hid' : i ∉ diff a' b' := hD ▸ hid
        have heq' : a' i = b' i := by by_contra hne; exact hid' (mem_diff_iff.mpr hne)
        have ebb : b i = b' i := by
          have hcf := congrFun hm i
          rwa [crossover_apply_not_mem hic, crossover_apply_not_mem hic] at hcf
        exact ⟨heq.trans (ebb.trans heq'.symm), ebb⟩
  exact ⟨funext fun i => (key i).1, funext fun i => (key i).2⟩

/-- **Ollivier-Villani, Theorem 1, the `K = 0` case.** For nonempty `A, B` in the Hamming cube,
with `M` their midpoint set, `#A * #B ≤ (#M)²`. Proved via the injection
`(a, b) ↦ encode a b` from `A ×ˢ B` into `M ×ˢ M`. -/
theorem card_sq_ge (A B : Finset (Cube N)) :
    A.card * B.card ≤ (midpointSet A B).card * (midpointSet A B).card := by
  have hinj : Set.InjOn (fun p : Cube N × Cube N => encode p.1 p.2) (A ×ˢ B : Finset _) := by
    intro p _ q _ hpq
    obtain ⟨h1, h2⟩ := encode_injective hpq
    exact Prod.ext h1 h2
  have hmap : ∀ p ∈ (A ×ˢ B : Finset (Cube N × Cube N)),
      (fun p : Cube N × Cube N => encode p.1 p.2) p ∈ midpointSet A B ×ˢ midpointSet A B := by
    intro p hp
    obtain ⟨ha, hb⟩ := mem_product.mp hp
    exact mem_product.mpr (encode_mem_midpointSet ha hb)
  have := Finset.card_le_card_of_injOn _ hmap hinj
  rwa [card_product, card_product] at this

/-! ### A discrete H-theorem, from Mathlib's own Data Processing Inequality
(Flattened into this same namespace, not a sub-namespace `EntropyMethods`: `scripts/regen_axiom_audit.py`
only reads a file's FIRST `namespace` line and prefixes every theorem with it, the same class of
limitation as the LeanGraph #print-axioms bug found earlier in this project -- worked around here
rather than fixed, since fixing the script is out of scope for this file.) -/

open MeasureTheory ProbabilityTheory InformationTheory

variable {𝓧 : Type*} {m𝓧 : MeasurableSpace 𝓧}

/-- **A Markov chain's relative entropy to an invariant measure is nonincreasing.** The modern
relative-entropy form of Boltzmann's H-theorem for a Markov kernel, three lines from Mathlib's
`klDiv_comp_right_le`: apply the Data Processing Inequality to `μ` and the invariant `ν`, using
`κ ∘ₘ ν = ν` to keep the reference measure fixed. Not a contribution; see the file header. -/
theorem klDiv_nonincreasing_to_invariant (κ : Kernel 𝓧 𝓧) [IsMarkovKernel κ]
    (μ ν : Measure 𝓧) [IsFiniteMeasure μ] [IsFiniteMeasure ν] (hν : κ ∘ₘ ν = ν) :
    klDiv (κ ∘ₘ μ) ν ≤ klDiv μ ν := by
  calc klDiv (κ ∘ₘ μ) ν = klDiv (κ ∘ₘ μ) (κ ∘ₘ ν) := by rw [hν]
    _ ≤ klDiv μ ν := klDiv_comp_right_le μ ν κ

end QuantumFluids.Villani

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.Villani.mem_diff_iff
#print axioms QuantumFluids.Villani.diff_crossover_left
#print axioms QuantumFluids.Villani.diff_crossover_right
#print axioms QuantumFluids.Villani.dist_crossover_left
#print axioms QuantumFluids.Villani.dist_crossover_right
#print axioms QuantumFluids.Villani.isMidpoint_crossover
#print axioms QuantumFluids.Villani.takeHalf_subset
#print axioms QuantumFluids.Villani.card_takeHalf
#print axioms QuantumFluids.Villani.takeHalf_card_bounds
#print axioms QuantumFluids.Villani.encode_fst_isMidpoint
#print axioms QuantumFluids.Villani.encode_snd_isMidpoint
#print axioms QuantumFluids.Villani.encode_mem_midpointSet
#print axioms QuantumFluids.Villani.diff_crossover_crossover_compl
#print axioms QuantumFluids.Villani.encode_injective
#print axioms QuantumFluids.Villani.card_sq_ge
#print axioms QuantumFluids.Villani.klDiv_nonincreasing_to_invariant
