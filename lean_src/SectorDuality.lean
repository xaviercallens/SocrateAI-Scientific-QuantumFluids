/-
  SectorDuality.lean -- the finite-cyclic-group counterpart of `CompactBoson`'s duality-as-reindexing
  statement: on a Z_N sector group, the duality *is* Mathlib's own discrete Fourier transform
  (`ZMod.dft`), and its defining property -- Fourier inversion, `ZMod.dft_dft` -- is exactly Savit's
  "duality is a Fourier/Poisson-resummation transform on the group of sectors" (Rev. Mod. Phys. 52,
  453, 1980) and Gaiotto-Kapustin-Seiberg-Willett's "the S-operation is a discrete Fourier transform
  ... via Poincaré duality between H^{q+1}(M,G) and H^{d-q-1}(M,Ĝ)" (arXiv:1412.5148), in the simplest
  nontrivial case G = Ĝ = Z_N. Nothing here is a new theorem of Fourier analysis -- `ZMod.dft_dft` is
  Mathlib's (David Loeffler's); what is new is stating three of its corollaries in the vocabulary the
  2026-09-26 literature review (`LITERATURE_REVIEW_SECTOR_LEAD.md`) asked for:

  * `sectorDuality_bijective`   : the duality is a bijection of sector-weighted data (a `LinearEquiv`
                                  is in particular an `Equiv` -- the same fact `CompactBoson.swap`
                                  states for Z, now for the finite cyclic case).
  * `sectorDuality_sq_ne_id`    : for N ≥ 2 the duality squared is NOT the identity on sector-weighted
                                  data -- Aasen-Mong-Fendley's "duality is not a symmetry in the
                                  traditional sense" (arXiv:1601.07185) and Shao's "away from the
                                  critical point Kramers-Wannier 'duality' is... a map from the
                                  high-temperature phase to the low-temperature phase" (TASI lectures,
                                  arXiv:2308.00747), read off `ZMod.dft_dft`'s own N•(reflection) shape.
  * `kramersWannier_gauging_sq` : the N = 2 (Ising / Kramers-Wannier) case of `ZMod.dft_dft`, spelled
                                  out: gauging a Z_2 sector symmetry twice returns TWICE the original
                                  weighting -- Choi-Córdova-Hsin-Lam-Shao's and Gaiotto-Kapustin-
                                  Seiberg-Willett's "gauging a non-anomalous Z_2 twice gives back the
                                  original theory" (up to the decoupled factor |G| = 2 the finite-sum
                                  identity actually produces).

  What this module does NOT claim: no anomaly-inflow / SPT-obstruction argument (Choi et al.'s and
  Hayashi-Tanizaki's actual theorems, which need cohomology this file does not touch) and no statement
  about which physical fixed points are forced to be transitions -- that is the criterion of
  `duality_sector.tex`'s addendum, stated in prose there and NOT reduced to the algebra below. This
  file is the algebraic backbone the addendum cites (Savit's "duality = Fourier transform on the sector
  group"), not the anomaly argument itself.
-/
import Mathlib

namespace QuantumFluids.SectorDuality

open ZMod

/-- **The duality is a bijection of Z_N-sector-weighted data**, for any `N ≠ 0`: `ZMod.dft` is a
`LinearEquiv`, hence in particular an `Equiv`. The finite-cyclic-group counterpart of
`CompactBoson.swap` (there, the reindexing of the Z² winding lattice was `Equiv.prodComm`; here, the
reindexing of Z_N-indexed sector data is Mathlib's own discrete Fourier transform). -/
theorem sectorDuality_bijective (N : ℕ) [NeZero N] :
    Function.Bijective (ZMod.dft (N := N) (E := ℂ) : (ZMod N → ℂ) → (ZMod N → ℂ)) :=
  (ZMod.dft (N := N) (E := ℂ)).toEquiv.bijective

/-- **The duality squared is not the identity**, for `N ≥ 2`: by Fourier inversion (`ZMod.dft_dft`),
`𝓕(𝓕 Φ) = N • Φ(-·)`, and evaluating on the indicator of `0` shows this differs from `Φ` itself unless
`N = 1`. A duality is a bijection of the sector lattice, not (in general) an order-two symmetry of it. -/
theorem sectorDuality_sq_ne_id (N : ℕ) [NeZero N] (hN : 2 ≤ N) :
    (ZMod.dft (N := N) (E := ℂ)) ∘ (ZMod.dft (N := N) (E := ℂ)) ≠ id := by
  intro h
  set Φ : ZMod N → ℂ := fun j => if j = 0 then 1 else 0 with hΦ
  have hcomp : (ZMod.dft (N := N) (E := ℂ)) ((ZMod.dft (N := N) (E := ℂ)) Φ) = Φ := by
    have := congrFun h Φ
    simpa [Function.comp] using this
  have hdd : (ZMod.dft (N := N) (E := ℂ)) ((ZMod.dft (N := N) (E := ℂ)) Φ)
      = fun j => (N : ℂ) • Φ (-j) := ZMod.dft_dft Φ
  rw [hdd] at hcomp
  have h0 := congrFun hcomp 0
  simp only [hΦ, neg_zero, if_pos rfl, smul_eq_mul, mul_one] at h0
  have hN1 : (N : ℂ) ≠ 1 := by
    intro heq
    have : N = 1 := by exact_mod_cast heq
    omega
  exact hN1 h0

/-- **Kramers–Wannier: gauging the Z₂ sector symmetry twice returns twice the original weighting.**
The `N = 2` case of Fourier inversion: since `-j = j` for every `j : ZMod 2`, `ZMod.dft_dft` reads
`𝓕(𝓕 Φ) = 2 • Φ`, exactly "gauging a non-anomalous Z₂ symmetry twice gives back the original theory"
(up to the decoupled factor of `|Z₂| = 2` that the finite-sum identity produces; this is a normalisation
fact of summing over the two-element group, not extra physics). -/
theorem kramersWannier_gauging_sq (Φ : ZMod 2 → ℂ) :
    (ZMod.dft (N := 2) (E := ℂ)) ((ZMod.dft (N := 2) (E := ℂ)) Φ) = (2 : ℂ) • Φ := by
  have hdd : (ZMod.dft (N := 2) (E := ℂ)) ((ZMod.dft (N := 2) (E := ℂ)) Φ)
      = fun j => (2 : ℂ) • Φ (-j) := ZMod.dft_dft Φ
  have hneg : ∀ j : ZMod 2, (-j : ZMod 2) = j := by decide
  rw [hdd]
  funext j
  rw [hneg j]
  rfl

end QuantumFluids.SectorDuality

-- BEGIN axiom audit (generated by scripts/regen_axiom_audit.py -- do not edit by hand)
#print axioms QuantumFluids.SectorDuality.sectorDuality_bijective
#print axioms QuantumFluids.SectorDuality.sectorDuality_sq_ne_id
#print axioms QuantumFluids.SectorDuality.kramersWannier_gauging_sq
