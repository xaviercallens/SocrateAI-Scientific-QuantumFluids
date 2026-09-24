# Does topology causally influence physics? Thought experiments, the physical argument, and what is proved

Stream opened 2026-09-25 on the owner's question, in the owner's order: thought experiments first, then
the physical argument, then the mathematics. Companion to `PGPE_BKT_RESULTS.md` (round 1) and
`PGPE_R2_PREREG.md` (round 2, the empirical test of the last link). Lean modules:
`TopologicalProtection.lean`, `ScaleResolvedWinding.lean`, `ContinuumWinding.lean`.

## 0. What "cause" means here

Interventionist sense (Woodward; Pearl): X causes Y if an intervention on X, everything else held
fixed, changes Y. The obstacle: topology is not a free variable but a function of the microstate,
`W = W(ψ)`. So the question splits in two:

1. **Dependence.** At fixed `(E, N, P, T)`, do the observables still depend on `W`?
2. **Stability.** Is `W` conserved well enough that an intervention on it leaves a trace? An integer
   that fluctuated freely would be a descriptor, not a cause.

## 1. Thought experiments

**A. The rotating ring (persistent current).** Give a superfluid ring one turn of phase (`w = 1`) and
stop stirring. The current persists for hours in He-II and for tens of seconds in BEC rings. No
thermodynamic variable remembers the intervention; only the integer does. *Topology acts as memory.*

**B. The small-pair trap.** A vortex and an antivortex a distance `a` apart. A loop around one sees
`w = ±1`; any loop of size `R ≫ a` enclosing both sees `0`. From far away the pair is a phonon. *The
causal variable is not "the number of vortices" but the winding seen at scale `R`, `W(R)`* -- what a
persistent-homology reading of the phase tracks. BKT is where `W(R)` stops vanishing at large `R`.
This also explains round 1's T1 part 2 failure: `Q` counts pairs at every scale, grid noise included.

**C. Aharonov–Bohm.** The electron never enters the flux and its fringes move (Tonomura 1986). Here
the topology of space is not the cause but the *channel* through which a cause acts at a distance. Two
roles to keep apart.

**D. Laughlin's cylinder.** Threading one flux quantum adiabatically returns the Hamiltonian to itself,
so an integer number of electrons has been pumped: `σ_xy ∈ ℤ · e²/h`. Topology fixes an integer that
disorder cannot move -- the same `σ`-plane as `QHFricke.lean`.

**E. The two boxes (round 2, Part I, running).** Same `E, N, P`; one box gets four free vortex pairs,
the other the same energy as phonons. Pre-registered: the thermometer reads the same; the condensate is
lower by ≥ 0.15 in the vortex box.

## 2. The physical argument: four links

1. **Integrality.** `ψ` single-valued ⇒ `∮∇θ = 2π w`.
2. **Continuity ⇒ conservation.** An integer-valued continuous function is constant. The only exit is
   `ψ = 0` on the loop: a core crosses it -- Anderson's phase slip (RMP 38, 298 (1966)).
3. **Barrier.** Passing through `ψ = 0` costs energy; the slip rate goes as `exp(−ΔE/T)`; protection is
   exponential.
4. **Coupling.** The integer enters the observables linearly (`Γ = wκ`, the current); free vortices
   scramble the phase and `g₁` decays exponentially.

The deep point: Noether charges come from a *symmetry* of the Hamiltonian; topological charges come
from the *connectivity* of configuration space (`π₁(U(1)) = ℤ`) and are conserved by continuity alone,
whatever the Hamiltonian. That is why they survive disorder (Hall quantization at `10⁻¹⁰` in dirty
samples). Topology does not push; it *partitions* the state space into sectors the dynamics cannot
connect continuously. The conserved label then is a cause in the interventionist sense.

## 3. What is proved (Lean 4, Mathlib pinned, standard axioms, Comparator both kernels)

| Link | Theorem | Module |
|---|---|---|
| 1 | `loop_sum_eq_mul` | `VortexWinding` (earlier) |
| 2 stability | `loop_sum_stable`, `loop_sum_stable_of_small`: a perturbation that pushes no edge through the branch point leaves `w` unchanged | `TopologicalProtection` |
| 2 conservation | `loop_sum_const_of_no_slip`: continuous phases, no edge step at `π` on `[t₀, t₁]` ⇒ `w(t₁) = w(t₀)` (IVT on an integer-valued sum) | " |
| 2 contrapositive | `slip_of_winding_change`: a change of `w` forces a step at `π` at some intermediate time | " |
| 2 Kelvin | `circulation_conserved` | " |
| 3 mountain pass | `mountain_pass`: on the XY ring any winding-changing evolution passes `E ≥ −(n−2)J` | " |
| 3 barrier > 0 | `barrier_pos`: from the twisted `w = 1` state the barrier is `≥ 2J − 2π²J/n > 0` for `n ≥ 10` (false at `n = 9`: negative control) | " |
| B scale | `stokes`: boundary sum = Σ plaquette windings (no interior edge at `π`); `dipole_invisible`; `single_core_visible`; `W(R)` = net charge inside `R` | `ScaleResolvedWinding` |
| Rome | `discrete_eq_degree`: for a continuous closed loop of angles, the path lift through `ℝ → ℝ/2πℤ` gives an integer degree `w`, and Heine–Cantor a threshold `n₀` beyond which the sampled principal-branch loop sum is exactly `2πw` for any representatives | `ContinuumWinding` |
| Rome, detector | `detector_correct`: `arg` of a nowhere-vanishing closed loop of field values ⇒ the detector returns `2πw` for all `n ≥ n₀` | " |
| 4 coupling | **empirical** -- round 2 Part I | `PGPE_R2_PREREG.md` |

Counts: 13 + 6 + 9 = 28 theorems in the three new modules; 12 negative controls fail as required.
Comparator: all three modules accepted by both kernels (2026-09-25).

## 4. What is not proved, said plainly

* **The argument principle.** That the degree along a loop counts the zeros of `ψ` inside it. The pinned
  Mathlib has no argument principle for general continuous maps; `stokes` is the discrete substitute.
* **Grid spacing vs `n₀`.** `detector_correct` gives existence of a threshold; a quantitative one needs
  a modulus of continuity of `ψ` (a bound on `|∇θ|` away from cores, i.e. on `ξ/Δx`).
* **The minimal `w = 1` state.** `barrier_pos` uses the uniformly twisted state; that it minimises the
  energy in its sector is not proved.
* **Link 4.** The coupling of the integer to condensate and coherence is physics, tested in round 2.

## 5. Transfer to astrophysics (owner's rule, 2026-09-25)

**Transferable, at the level where it is proved:** the chain integrality → conservation by continuity →
barrier → scale additivity (W(R) = net charge) → continuum limit. It holds for ANY U(1) phase field
(axion, Peccei–Quinn, U(1) cosmic strings), because conservation comes from π₁(U(1)) = ℤ, not from the
Hamiltonian. And the method: a causal measurement needs an equally arbitrary control arm (same energy
surplus, different form); without a matched pair, "topology influences" is a descriptor again.

**Not transferable:** link 4. The coupling integer → observables is empirical, measured here with three
bases; a V/P result in the Bose gas says nothing about the coupling in cosmology. An astrophysical
claim needs a matched intervention inside the astrophysical model itself.

**Recommendation:** quantum fluids as the laboratory of the *method* (matched pair, effect per unit
energy, proved chain) — justified; exporting the physical coupling — not.

## 6. Literature status

None of the physics is new: Anderson (1966) for phase slips; Langer–Fisher (1967) for the ring barrier;
Kosterlitz–Thouless for the scale-resolved picture; Laughlin (1981); Tonomura (1986). What is new to
this project is the machine-checked chain and its explicit gaps. No novelty is claimed.
