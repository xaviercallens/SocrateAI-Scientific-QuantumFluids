# Expériences de pensée for the dual-scale programme, run in a quantum fluid

**Date:** 2026-09-19. **Why a quantum fluid:** it is the one fluid where the small scale is not an assumption. Circulation is quantized
(κ = h/m), the healing length ξ is fixed by ħ, m, c, and the excitation spectrum is *measured* (our Godfrin table). A thought experiment there
can end in a number or a theorem instead of an opinion. Each one below states **what was imagined, what it forced, how it was checked, and its tier**.
Tier A = Lean-checked here, B = measured/exact check here, C = heuristic. Negative outcomes are kept.

---

## GE-1. Riding the graded phase (the "riding a light beam" move)  →  a second invariant  [A/B, CLAIM-023]

**Imagine** an observer who co-rotates with each shell at its own rate: shell `n` is viewed in a frame turning at `2ⁿθ`. In the *real* Katz–Pavlović
model the amplitudes have no phase, so this observer does not exist. In the complexified (quantum-like) model it does, and the equations look the same to
every such observer: `v_n → e^{i2ⁿθ}v_n` is a symmetry (`v_{n-1}²` and `conj(v_n)v_{n+1}` both carry charge `2ⁿ`).

**Forced consequence.** A continuous symmetry of a Hamiltonian system has a Noether charge. The charge of the graded phase is `Σ2ⁿ|w_n|²`, which is the conserved
energy `Σ|v_n|²` if `w_n = 2^{-n/2}v_n`. In those variables the model *is* Hamiltonian, a chain of second-harmonic generators (two quanta of shell n fuse into one
of shell n+1), and the Hamiltonian itself must be a second invariant:

```
H = Σ_n 2^{-n} [ D k_n² |v_n|² + k_n Im(conj(v_n)² v_{n+1}) ]  (+ ½ μ k_N 2^{-N}|v_N|⁴ for the conserving seam v_{N+1} = iμ v_N²)
```

**Checks.** Exact polynomial identity `dH/dt ≡ 0` for general `k_n`, `D`, `μ` (sympy, N = 3, 5; wrong-weight control fails). Lean:
`lean_src/ShellHamiltonian.lean` (`hamiltonian_rate_zero`, D = 0 part, standard axioms; control without the factor 2 fails). Nullspace search: see
`exploration/second_invariant/results.json`.

**What it explains.** (i) Liouville (CLAIM-011) is a corollary: Hamiltonian flows preserve volume. (ii) Energy conservation (CLAIM-007) is the Manley–Rowe relation.
(iii) On real data `H ≡ 0` (`T_real`): the real model lives on the zero level set and has no access to the structure. This is the precise sense in which
"the quantum nature makes it easier": the phase is what carries the second conservation law.

**What it does not give.** `H` is cubic and sign-indefinite. For `D > 0` and `k_n = 2ⁿ` it bounds `D Σ k_n|v_n|² ≤ H + (2E)^{3/2}`, uniformly in the cutoff N
(an H^{1/2}-type norm), **not** the enstrophy `Σk_n²|v_n|²`. One power of k is lost to the Manley–Rowe weight `2^{-n}`. So the pre-registered question Q1
("Ω + positive quartic") is answered *no in that span*; the structure that exists is weaker and different. Novelty not claimed; literature check pending.

**Dual-scale reading.** A dispersive regulator of order `k^σ` controls the norm of order `k^{σ-1}` uniformly in the cutoff. To control enstrophy one needs `σ = 3`,
not the quantum-pressure `σ = 2`. That is a design rule for regulators, stated so it can be tested (P-d' below).

## GE-2. Running the OpenAI forcing in He-II  →  the blow-up exits at one quantum of circulation  [C, with one B number]

**Imagine** OpenAI's collapsing core (radial Re = O(1), so `ℓ ~ √(ντ)`, `u ~ √(ν/τ)`) driven in superfluid helium, with the only available kinematic scale
`ν → ħ/m = κ/2π = 1.59×10⁻⁸ m²/s`. **Forced consequence:** `u` reaches the measured Landau velocity `v_L = 57.9 m/s` (CLAIM-021) when
`ℓ* = ν/v_L = 2.7 Å` and `τ* = ν/v_L² = 4.7 ps`, and the circulation of a Re = O(1) core of that size is `2πν = κ`: **exactly one quantum**.
The classical blow-up therefore leaves its domain of validity at the scale where the fluid can no longer subdivide circulation, and where roton emission starts.
Tier C: `ν_eff = ħ/m` is an assumption (order-unity factor unknown), He-II is two-fluid, and OpenAI's `τ^{∓h}` corrections are ignored.
Testable form: GP simulation of a forced collapsing core; prediction: core stops contracting at a few ξ with Γ = κ, energy goes to sound.

## GE-3. Two observers, one dispersion  →  Bogoliubov is a dual-scale form  [A, instance only]

**Imagine** one observer who only has phonons (rulers made of sound, `ω = ck`) and one who only has particles (`ω = ħk²/2m`). They disagree about every
length except one. **Forced consequence:** `ω² = c²k² + c²k⁴/k*² = (c²k³/k*)·(k/k* + k*/k)` with `k* = 2mc/ħ = √2/ξ`: the `R + α'/R` shape, self-dual at `k*`,
so `ω² ≥ 2c²k³/k*`. Lean: `Duality.lean`, `bogoliubov_dual_form`, `bogoliubov_selfdual_bound`. It is AM–GM on two branches, a Rosetta row, not a finding.
**Negative check on real helium [B]:** with measured ε(k), `ε²/k³` has *no interior minimum* up to 3.6 Å⁻¹ (k* would be 3.0 Å⁻¹): ⁴He is not a Bogoliubov gas
(roton, plateau), so the clean duality is a property of the weakly interacting model, not of the liquid. The measured curve crosses the free-particle parabola at 1.44 Å⁻¹.

## GE-4. The smallest vortex ring (Feynman's roton picture)  →  fails quantitatively  [C, negative]

**Imagine** shrinking a quantized ring until its self-velocity equals `v_L`. Classical formula with core 1 Å gives `R = 4.1 Å`, impulse `p/ħ = 7.2 Å⁻¹`,
against the roton's 1.92 Å⁻¹. Off by ~4×. The classical ring formula is outside its validity at R ~ core; the picture stays qualitative. Kept as a negative.

## GE-5. The elevator: can a local observer detect the cutoff?  [open, proposed]

**Imagine** an observer confined to shells `n ≤ n₀ ≪ N` of the truncated Hamiltonian chain. By GE-1 they can measure `E` and `H` fluxes through their boundary.
Question: is there any local measurement that distinguishes "truncated at N with conserving seam" from "infinite chain", before information returns from N?
In the Hamiltonian chain signals travel up the cascade in finite time (`Σ 1/k_n|v_n|` converges for KP-type scaling), so the answer should be *yes, after a finite
echo time*, and that echo time is a cutoff-dependent observable that is **deterministic in the ensemble mean** only. This re-poses the failed M3 measurement
as an echo-time measurement with two conserved fluxes to normalise by. Needs its own pre-registration; ensemble only (B8).

---

## Proposed next steps
1. **P-d'** (Lean): the uniform-in-N bound `D Σ k_n|v_n|² ≤ H + (2E)^{3/2}` for `k_n = 2ⁿ`.
2. **σ-rule.** Conservation part DONE exactly (sympy, N = 4): for an **arbitrary real dispersion** `ω_n`, `H = Σ2^{-n}ω_n|v_n|² + Σ2^{-n}k_n Im(conj(v_n)²v_{n+1})` is conserved.
   So with `ω_n = D k_n³` and `k_n = 2ⁿ`, `H` controls `Σk_n²|v_n|²`, i.e. Ω, uniformly in N: `2DΩ ≤ H + (2E)^{3/2}` (bound not yet in Lean). If it survives audit this is the
   first regulator in this stream with a cutoff-uniform enstrophy bound; it must then pass the O5 trap discussion (it regularizes the *complexified* model at H ≠ 0 levels;
   on real data the dispersive term breaks reality, so no contradiction with Katz–Pavlović blow-up is implied, to be argued carefully).
3. Literature check for the SHG-chain / Hamiltonian structure of complex dyadic models before any novelty language.
4. GE-5 pre-registration.
