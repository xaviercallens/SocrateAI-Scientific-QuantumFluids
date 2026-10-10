/-
  Ch02_Galerkin.lean -- NEW Lean written for Chapter 2 of the book "Quantum Fluids in Lean 4".
  It is NOT part of the QuantumFluids library.  Everything below is stated for the Galerkin-projected
  Gross-Pitaevskii nonlinearity `nl` of `QuantumFluids.GPGalerkin` (the definition is copied verbatim so that this
  file compiles on its own, against Mathlib only).

  (1) The exact plane wave.  A single occupied mode `k0` with amplitude `a₀ exp(-i Ω t)`, `Ω = ω_{k0} + g |a₀|²`,
      solves the Galerkin system `i ∂ₜ ψ_k = ω_k ψ_k + g · nl ψ k` on every finite mode set containing `k0`.
      This is the mathematical statement behind the engine's known answer K4 (a numerical test of the same
      statement is in the chapter; the theorem says nothing about any program).
  (2) Momentum.  For every additive map `p : G →+ ℝ` (on `G = ℤ²`: a component of the wave vector) the rate
      `Σ_k p(k) · 2 Im(conj ψ_k · G_k)` of the `p`-weighted occupation vanishes.  This is the algebraic core of
      momentum conservation, in the same form as `GPGalerkin.mass_rate_zero`; the proof uses the resonance condition
      `k1 + k3 = k + k2` and the additivity of `p`, nothing else.
  (3) The hypothesis is not decoration: on a periodic grid `ℤ_N × ℤ_N` every additive map to ℝ is zero
      (`no_momentum_on_torus`), so the theorem has no content for a scheme whose triads wrap around.
-/
import Mathlib

set_option linter.deprecated false           -- `if_pos`/`if_true` aliases: harmless in this file
set_option linter.unusedSectionVars false    -- the helper lemmas about four-fold sums do not use the group structure

namespace QuantumFluids.Ch02Galerkin

open Finset

variable {G : Type*} [AddCommGroup G] [DecidableEq G]

/-- Projected cubic nonlinearity on the retained set `Λ` (verbatim from `QuantumFluids.GPGalerkin.nl`). -/
noncomputable def nl (Λ : Finset G) (ψ : G → ℂ) (k : G) : ℂ :=
  ∑ k1 ∈ Λ, ∑ k2 ∈ Λ, ∑ k3 ∈ Λ,
    if k1 + k3 = k + k2 then ψ k1 * (starRingEnd ℂ) (ψ k2) * ψ k3 else 0

/-! ## 1. The exact plane wave -/

/-- The amplitude of a plane wave at time `t`: `a₀ * exp(-i ω t)`. -/
noncomputable def planeWave (a₀ : ℂ) (ω t : ℝ) : ℂ :=
  a₀ * Complex.exp (-(Complex.I * ω) * t)

/-- The modulus of a plane wave does not depend on time. -/
theorem norm_planeWave (a₀ : ℂ) (ω t : ℝ) : ‖planeWave a₀ ω t‖ = ‖a₀‖ := by
  unfold planeWave
  rw [norm_mul, Complex.norm_exp]
  simp

/-- `a(t) = a₀ exp(-i ω t)` satisfies `a' = -i ω a`. -/
theorem planeWave_hasDerivAt (a₀ : ℂ) (ω t : ℝ) :
    HasDerivAt (planeWave a₀ ω) (-(Complex.I * ω) * planeWave a₀ ω t) t := by
  have h1 : HasDerivAt (fun s : ℝ => -(Complex.I * ω) * (s : ℂ)) (-(Complex.I * ω)) t := by
    simpa using (Complex.ofRealCLM.hasDerivAt (x := t)).const_mul (-(Complex.I * ω))
  have h2 := (h1.cexp).const_mul a₀
  refine h2.congr_deriv ?_
  unfold planeWave
  ring

/-- On a single occupied mode the Galerkin nonlinearity is `|a|² a`, and it vanishes on every other mode. -/
theorem nl_single (Λ : Finset G) (k0 : G) (hk0 : k0 ∈ Λ) (a : ℂ) (k : G) :
    nl Λ (fun x => if x = k0 then a else 0) k = if k = k0 then a * (starRingEnd ℂ) a * a else 0 := by
  unfold nl
  rw [Finset.sum_eq_single k0]
  · rw [Finset.sum_eq_single k0]
    · rw [Finset.sum_eq_single k0]
      · by_cases h : k = k0
        · simp [h]
        · have h' : ¬ (k0 + k0 = k + k0) := fun h'' => h (add_right_cancel h''.symm)
          simp [h, h']
      · intro b _ hb; simp [hb]
      · intro h; exact absurd hk0 h
    · intro b _ hb; simp [hb]
    · intro h; exact absurd hk0 h
  · intro b _ hb; simp [hb]
  · intro h; exact absurd hk0 h

/-- The plane-wave state: amplitude `planeWave a₀ Ω t` on the mode `k0`, zero elsewhere. -/
noncomputable def planeState (k0 : G) (a₀ : ℂ) (Ω t : ℝ) : G → ℂ :=
  fun x => if x = k0 then planeWave a₀ Ω t else 0

/-- The vector field of the Galerkin system `i ∂ₜ ψ_k = ω_k ψ_k + g · nl ψ k`, solved for `∂ₜ ψ_k`. -/
noncomputable def galerkinField (Λ : Finset G) (ω : G → ℝ) (g : ℝ) (ψ : G → ℂ) (k : G) : ℂ :=
  -Complex.I * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)

/-- **The exact plane wave solves the Galerkin Gross-Pitaevskii system**, on every finite mode set that
contains the occupied mode, for every dispersion `ω`, coupling `g`, amplitude `a₀` and time `t`:
each component `ψ_k(t)` has the time derivative that the vector field prescribes. -/
theorem planeState_solves_galerkin (Λ : Finset G) (k0 : G) (hk0 : k0 ∈ Λ) (ω : G → ℝ) (g : ℝ)
    (a₀ : ℂ) (k : G) (t : ℝ) :
    HasDerivAt (fun s : ℝ => planeState k0 a₀ (ω k0 + g * ‖a₀‖ ^ 2) s k)
      (galerkinField Λ ω g (planeState k0 a₀ (ω k0 + g * ‖a₀‖ ^ 2) t) k) t := by
  by_cases hk : k = k0
  · subst hk
    have hnl : nl Λ (planeState k a₀ (ω k + g * ‖a₀‖ ^ 2) t) k
        = ((‖a₀‖ ^ 2 : ℝ) : ℂ) * planeWave a₀ (ω k + g * ‖a₀‖ ^ 2) t := by
      unfold planeState
      rw [nl_single Λ k hk0]
      simp only [if_true]
      have hn := norm_planeWave a₀ (ω k + g * ‖a₀‖ ^ 2) t
      have : planeWave a₀ (ω k + g * ‖a₀‖ ^ 2) t * (starRingEnd ℂ) (planeWave a₀ (ω k + g * ‖a₀‖ ^ 2) t)
          = ((‖a₀‖ ^ 2 : ℝ) : ℂ) := by
        rw [Complex.mul_conj, Complex.normSq_eq_norm_sq, hn]
      rw [this]
    have hd := planeWave_hasDerivAt a₀ (ω k + g * ‖a₀‖ ^ 2) t
    simp only [planeState, galerkinField, if_true, hnl]
    convert hd using 1
    push_cast
    ring
  · have hz : (fun s : ℝ => planeState k0 a₀ (ω k0 + g * ‖a₀‖ ^ 2) s k) = fun _ => 0 := by
      funext s; simp [planeState, hk]
    have hnl : nl Λ (planeState k0 a₀ (ω k0 + g * ‖a₀‖ ^ 2) t) k = 0 := by
      unfold planeState
      rw [nl_single Λ k0 hk0]
      simp [hk]
    rw [hz]
    have : galerkinField Λ ω g (planeState k0 a₀ (ω k0 + g * ‖a₀‖ ^ 2) t) k = 0 := by
      simp [galerkinField, hnl, planeState, hk]
    rw [this]
    exact hasDerivAt_const t (0 : ℂ)

/-! ## 2. Momentum -/

/-- The summand of the four-fold resonant sum `conj ψ_a · ψ_b · conj ψ_c · ψ_d`, restricted to `b + d = a + c`. -/
noncomputable def F (ψ : G → ℂ) (a b c d : G) : ℂ :=
  if b + d = a + c then (starRingEnd ℂ) (ψ a) * (ψ b * (starRingEnd ℂ) (ψ c) * ψ d) else 0

/-- Four-fold sum over the retained set. -/
noncomputable def S4 (Λ : Finset G) (f : G → G → G → G → ℂ) : ℂ :=
  ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ c ∈ Λ, ∑ d ∈ Λ, f a b c d

theorem S4_congr (Λ : Finset G) {f g : G → G → G → G → ℂ} (h : ∀ a b c d, f a b c d = g a b c d) :
    S4 Λ f = S4 Λ g := by
  unfold S4
  exact Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun b _ =>
    Finset.sum_congr rfl (fun c _ => Finset.sum_congr rfl (fun d _ => h a b c d))))

theorem S4_add (Λ : Finset G) (f g : G → G → G → G → ℂ) :
    S4 Λ (fun a b c d => f a b c d + g a b c d) = S4 Λ f + S4 Λ g := by
  unfold S4
  simp only [Finset.sum_add_distrib]

theorem S4_conj (Λ : Finset G) (f : G → G → G → G → ℂ) :
    (starRingEnd ℂ) (S4 Λ f) = S4 Λ (fun a b c d => (starRingEnd ℂ) (f a b c d)) := by
  unfold S4
  simp only [map_sum]

theorem S4_swap_ac (Λ : Finset G) (f : G → G → G → G → ℂ) :
    S4 Λ f = S4 Λ (fun a b c d => f c b a d) := by
  unfold S4
  calc ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ c ∈ Λ, ∑ d ∈ Λ, f a b c d
      = ∑ a ∈ Λ, ∑ c ∈ Λ, ∑ b ∈ Λ, ∑ d ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun a _ => Finset.sum_comm)
    _ = ∑ c ∈ Λ, ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ d ∈ Λ, f a b c d := Finset.sum_comm
    _ = ∑ c ∈ Λ, ∑ b ∈ Λ, ∑ a ∈ Λ, ∑ d ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun c _ => Finset.sum_comm)

theorem S4_swap_bd (Λ : Finset G) (f : G → G → G → G → ℂ) :
    S4 Λ f = S4 Λ (fun a b c d => f a d c b) := by
  unfold S4
  calc ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ c ∈ Λ, ∑ d ∈ Λ, f a b c d
      = ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ d ∈ Λ, ∑ c ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun b _ => Finset.sum_comm))
    _ = ∑ a ∈ Λ, ∑ d ∈ Λ, ∑ b ∈ Λ, ∑ c ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun a _ => Finset.sum_comm)
    _ = ∑ a ∈ Λ, ∑ d ∈ Λ, ∑ c ∈ Λ, ∑ b ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun d _ => Finset.sum_comm))

theorem S4_swap_pairs (Λ : Finset G) (f : G → G → G → G → ℂ) :
    S4 Λ f = S4 Λ (fun a b c d => f b a d c) := by
  unfold S4
  calc ∑ a ∈ Λ, ∑ b ∈ Λ, ∑ c ∈ Λ, ∑ d ∈ Λ, f a b c d
      = ∑ b ∈ Λ, ∑ a ∈ Λ, ∑ c ∈ Λ, ∑ d ∈ Λ, f a b c d := Finset.sum_comm
    _ = ∑ b ∈ Λ, ∑ a ∈ Λ, ∑ d ∈ Λ, ∑ c ∈ Λ, f a b c d :=
        Finset.sum_congr rfl (fun b _ => Finset.sum_congr rfl (fun a _ => Finset.sum_comm))

theorem F_swap_ac (ψ : G → ℂ) (a b c d : G) : F ψ c b a d = F ψ a b c d := by
  unfold F
  rw [add_comm c a]
  split_ifs
  · ring
  · rfl

theorem F_swap_bd (ψ : G → ℂ) (a b c d : G) : F ψ a d c b = F ψ a b c d := by
  unfold F
  rw [add_comm d b]
  split_ifs
  · ring
  · rfl

theorem F_conj (ψ : G → ℂ) (a b c d : G) : (starRingEnd ℂ) (F ψ a b c d) = F ψ b a d c := by
  unfold F
  by_cases h : b + d = a + c
  · have h' : a + c = b + d := h.symm
    rw [if_pos h, if_pos h']
    simp only [map_mul, Complex.conj_conj]
    ring
  · have h' : ¬ (a + c = b + d) := fun e => h e.symm
    rw [if_neg h, if_neg h']
    simp

/-- The `p`-weighted pairing `Σ_k p(k) conj(ψ_k) N_k` as a four-fold sum. -/
theorem weighted_pairing_eq_S4 (Λ : Finset G) (ψ : G → ℂ) (p : G → ℝ) :
    ∑ k ∈ Λ, (p k : ℂ) * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k)
      = S4 Λ (fun a b c d => (p a : ℂ) * F ψ a b c d) := by
  unfold S4 nl F
  refine Finset.sum_congr rfl (fun a _ => ?_)
  simp only [Finset.mul_sum, mul_ite, mul_zero]

/-- **The `p`-weighted pairing is real, for every additive `p`.** -/
theorem weighted_pairing_real (Λ : Finset G) (ψ : G → ℂ) (p : G →+ ℝ) :
    (∑ k ∈ Λ, (p k : ℂ) * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k)).im = 0 := by
  rw [weighted_pairing_eq_S4]
  set SA := S4 Λ (fun a b c d => (p a : ℂ) * F ψ a b c d) with hSA
  set SB := S4 Λ (fun a b c d => (p b : ℂ) * F ψ a b c d) with hSB
  set SC := S4 Λ (fun a b c d => (p c : ℂ) * F ψ a b c d) with hSC
  set SD := S4 Λ (fun a b c d => (p d : ℂ) * F ψ a b c d) with hSD
  -- symmetry a <-> c and b <-> d
  have hAC : SA = SC := by
    rw [hSA, S4_swap_ac]
    exact S4_congr Λ (fun a b c d => by simp only [F_swap_ac])
  have hBD : SB = SD := by
    rw [hSB, S4_swap_bd]
    exact S4_congr Λ (fun a b c d => by simp only [F_swap_bd])
  -- additivity and the resonance condition: (p a + p c) = (p b + p d) whenever b + d = a + c
  have hsum : SA + SC = SB + SD := by
    rw [hSA, hSC, hSB, hSD, ← S4_add, ← S4_add]
    refine S4_congr Λ (fun a b c d => ?_)
    by_cases h : b + d = a + c
    · have hp : p b + p d = p a + p c := by rw [← map_add, ← map_add, h]
      have hp' : (p b : ℂ) + (p d : ℂ) = (p a : ℂ) + (p c : ℂ) := by exact_mod_cast hp
      calc (p a : ℂ) * F ψ a b c d + (p c : ℂ) * F ψ a b c d
          = ((p a : ℂ) + (p c : ℂ)) * F ψ a b c d := by ring
        _ = ((p b : ℂ) + (p d : ℂ)) * F ψ a b c d := by rw [hp']
        _ = (p b : ℂ) * F ψ a b c d + (p d : ℂ) * F ψ a b c d := by ring
    · simp [F, h]
  have hAB : SA = SB := by
    rw [← hAC, ← hBD] at hsum
    linear_combination (1 / 2 : ℂ) * hsum
  -- complex conjugation exchanges (a, b, c, d) with (b, a, d, c)
  have hconj : (starRingEnd ℂ) SA = SB := by
    rw [hSA, S4_conj, hSB, S4_swap_pairs]
    refine S4_congr Λ (fun a b c d => ?_)
    rw [map_mul, Complex.conj_ofReal, F_conj]
  have hreal : (starRingEnd ℂ) SA = SA := by rw [hconj, hAB]
  exact Complex.conj_eq_iff_im.mp hreal

/-- **Momentum-rate identity.**  For every finite mode set `Λ` in an additive group `G`, every state `ψ`, every
real dispersion `ω`, real coupling `g` and every additive map `p : G →+ ℝ` (a component of the wave vector when
`G = ℤ²`), with `G_k = ω_k ψ_k + g N_k`:  `Σ_{k ∈ Λ} p(k) Im(conj ψ_k · G_k) = 0`.
Since `d/dt |ψ_k|² = 2 Im(conj ψ_k · G_k)` for `i ∂ₜ ψ_k = G_k`, this is `d/dt Σ p(k)|ψ_k|² = 0`.
Compare `GPGalerkin.mass_rate_zero` (the case of the constant weight, which is not additive). -/
theorem momentum_rate_zero (Λ : Finset G) (ψ : G → ℂ) (ω : G → ℝ) (g : ℝ) (p : G →+ ℝ) :
    ∑ k ∈ Λ, p k * ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im = 0 := by
  have h1 : ∀ k, p k * ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im
      = g * ((p k : ℂ) * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k)).im := by
    intro k
    have h2 : (starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)
        = ((ω k * Complex.normSq (ψ k) : ℝ) : ℂ) + (g : ℂ) * ((starRingEnd ℂ) (ψ k) * nl Λ ψ k) := by
      push_cast
      rw [Complex.normSq_eq_conj_mul_self]
      ring
    rw [h2]
    simp [Complex.mul_im]
    ring
  simp_rw [h1]
  rw [← Finset.mul_sum, ← Complex.im_sum, weighted_pairing_real, mul_zero]

/-- The same identity on the lattice `ℤ × ℤ` (the group in which the wave vectors of the engine live, as long as no triple
wraps around), with `p(k) = k₁`, the first component of the integer wave vector. -/
theorem momentum_rate_zero_lattice (Λ : Finset (ℤ × ℤ)) (ψ : ℤ × ℤ → ℂ) (ω : ℤ × ℤ → ℝ) (g : ℝ) :
    ∑ k ∈ Λ, (k.1 : ℝ) * ((starRingEnd ℂ) (ψ k) * ((ω k : ℂ) * ψ k + (g : ℂ) * nl Λ ψ k)).im = 0 := by
  have h := momentum_rate_zero Λ ψ ω g ((Int.castAddHom ℝ).comp (AddMonoidHom.fst ℤ ℤ))
  simpa using h

/-! ## 3. The hypothesis cannot be dropped: no momentum on a torus -/

/-- An additive map to the reals kills every torsion element. -/
theorem additive_map_vanishes_on_torsion {H : Type*} [AddCommGroup H] (p : H →+ ℝ) (x : H) (n : ℕ)
    (hn : n ≠ 0) (hx : n • x = 0) : p x = 0 := by
  have h : (n : ℝ) * p x = 0 := by
    have := congrArg p hx
    simpa [map_nsmul, nsmul_eq_mul] using this
  rcases mul_eq_zero.mp h with h0 | h0
  · exact absurd (by exact_mod_cast h0) hn
  · exact h0

/-- On the periodic grid `ℤ_N × ℤ_N` every additive map to the reals is zero: there is no additive "momentum"
for a scheme whose mode sums are taken modulo `N`. -/
theorem no_momentum_on_torus (N : ℕ) [NeZero N] (p : (ZMod N × ZMod N) →+ ℝ) (x : ZMod N × ZMod N) :
    p x = 0 := by
  refine additive_map_vanishes_on_torsion p x N (NeZero.ne N) ?_
  ext <;> simp [nsmul_eq_mul]

/-- In particular the wave number itself is not an additive function on `ℤ_N`: no additive `p` takes the value `1` at `1`. -/
theorem no_additive_wavenumber (N : ℕ) [NeZero N] : ¬ ∃ p : ZMod N →+ ℝ, p 1 = 1 := by
  rintro ⟨p, hp⟩
  have h : p 1 = 0 := additive_map_vanishes_on_torsion p 1 N (NeZero.ne N) (by simp [nsmul_eq_mul])
  rw [hp] at h
  exact one_ne_zero h

end QuantumFluids.Ch02Galerkin

#print axioms QuantumFluids.Ch02Galerkin.norm_planeWave
#print axioms QuantumFluids.Ch02Galerkin.planeWave_hasDerivAt
#print axioms QuantumFluids.Ch02Galerkin.nl_single
#print axioms QuantumFluids.Ch02Galerkin.planeState_solves_galerkin
#print axioms QuantumFluids.Ch02Galerkin.weighted_pairing_real
#print axioms QuantumFluids.Ch02Galerkin.momentum_rate_zero
#print axioms QuantumFluids.Ch02Galerkin.additive_map_vanishes_on_torsion
#print axioms QuantumFluids.Ch02Galerkin.momentum_rate_zero_lattice
#print axioms QuantumFluids.Ch02Galerkin.no_momentum_on_torus
#print axioms QuantumFluids.Ch02Galerkin.no_additive_wavenumber
