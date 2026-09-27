# Pre-registration: a projected Gross–Pitaevskii (classical-field) solver, its known answers, and the BKT gate

Direction 2 of `paper/wasserstein_slack.pdf` §6.2, which stopped at "this project has no finite-temperature
solver". This document opens that gate the only honest way: build the solver, validate it against known
answers that have nothing to do with BKT, cross-check its integrator against an independent one
(rusty-SUNDIALS, the owner's pure-Rust CVODE), and only then look at the transition. Committed before the
solver is written. Changes after this commit are dated amendments.

## 0. What is being built, and why these tools

**Model.** The projected Gross–Pitaevskii equation (PGPE) on a 2D periodic box, in units ħ = m = 1,
healing length and sound speed set by `g` and the mean density:

    i ∂ₜψ = P[ −½∇²ψ + g|ψ|²ψ ],      P = projector onto |k| ≤ k_cut  (sharp cutoff in Fourier space).

This is the classical-field method of Simula–Blakie (PRL 96, 020404, 2006) and Foster–Blakie–Davis
(PRA 81, 023623, 2010) for exactly this question: a PGPE trajectory started from a random high-energy
state thermalises (the field is ergodic) and samples the microcanonical ensemble of the coherent region;
temperature and chemical potential are *measured* from the trajectory, not imposed.

**Integrator.** Fourier pseudo-spectral, with the linear part `−½k²` treated exactly by an integrating
factor and the nonlinear part by RK4 (IF-RK4 / "ETD-RK4", the scheme LeanFlow's `RustDyadicSolver`
already uses for the shell model, `crates/leanflow-solver/src/lib.rs`), dealiased by the projector itself
(the cutoff `k_cut ≤ (2/3)·k_max` makes the cubic term alias-free).

**Independent integrator (the cross-check).** The same ODE system — the `2·N_modes` real components of
the projected Fourier amplitudes — integrated by **rusty-SUNDIALS** CVODE (Adams–Moulton, non-stiff,
adaptive order and step; `crates/rusty-sundials-py`, `CvodeSolver(method="adams")`) from the same initial
state to the same time, on a small grid. The two integrators share only the right-hand side function.
This is the *use* of the solver capability asked for: not speed, but a second, independently written,
adaptive integrator whose error control is not ours.

**What is NOT built.** A stochastic (SPGPE) reservoir; a trap; 3D; a Rust port of the PGPE step (a
LeanFlow "complex scalar field" engine is the natural follow-up PR and is recorded as such, not done here).

## 1. Known answers (controls) — all must pass before any thermal run is looked at

| # | Statement | Criterion |
|---|---|---|
| K1 | **Norm** `N = Σ|c_k|²` conserved by IF-RK4 over the full run | relative drift `≤ 1e-8` at `dt = 0.005` (report the drift; it is the time-stepping error of a symplectic-like scheme, not exactly zero) |
| K2 | **Energy** `E = Σ ½k²|c_k|² + (g/2)∫|ψ|⁴` conserved | relative drift `≤ 1e-6`; drift must scale as `dt⁴` between `dt` and `dt/2` (ratio `16 ± 3`) |
| K3 | **Momentum** `P = Σ k|c_k|²` conserved | `≤ 1e-10` absolute (exact for the projected scheme up to roundoff, because the projector and the cubic term commute with translations) |
| K4 | **Exact solution**: a single plane wave `ψ = √n₀ e^{i(k·x − ωt)}`, `ω = ½k² + g n₀`, reproduced | phase error `≤ 1e-9` after `t = 10` |
| K5 | **Bogoliubov dispersion**: a small perturbation on a uniform state oscillates at `ω² = ½k²(½k² + 2 g n₀)` | frequency from the FFT of the mode amplitude within `0.5 %` for three `k` values, amplitude `1e-3 √n₀` |
| K6 | **Cross-check**: IF-RK4 vs rusty-SUNDIALS Adams on a `16×16` grid from the same random initial state to `t = 5` | `max_k |c_k^{RK4} − c_k^{CVODE}| ≤ 10·(rtol·‖c‖)` with `rtol = 1e-8`; **and** the two disagree by more than that if one of them is deliberately run with `rtol = 1e-3` (negative control: the comparison can fail) |
| K7 | **Thermalisation / equipartition**: after the transient, the high-`k` modes of the coherent region satisfy the classical equipartition `⟨|c_k|²⟩ (½k² − μ + 2 g n) ≈ k_B T` with one `(T, μ)` pair; the temperature from a fit over `k ∈ [0.6, 1.0] k_cut` agrees with the temperature from `[0.4, 0.6] k_cut` | agreement within `10 %`; this is the classical-field analogue of a thermometer reading the same on two scales |

Stop rule: any K failing is a bug or a wrong scheme; no thermal ensemble is analysed until K1–K7 pass.

## 2. The thermal sweep and the BKT gate (pre-registered observables)

Box `L = 64 ξ₀` (`ξ₀` the healing length at the mean density `n₀ = 1`), grid `128²`, `k_cut = 2/3 k_max`
(so about 5 800 modes in the coherent region), `g n₀ = 1`. Twelve total energies `E/N` spanning the
range from a nearly pure condensate to a nearly incoherent gas, three seeds each; each trajectory
`t ∈ [0, 1500]` at `dt = 0.01` (the compute budget of this machine: about 6 min per trajectory, 36
trajectories on 8 cores), samples every `Δt = 10` after `t = 500` (transient discarded; the K7 thermometer
must be stationary over the sampling window, checked by comparing the two halves of the window to within
5 %).

Observables per sample:

* `T`, `μ` from K7's equipartition fit; the condensate fraction `|c₀|²/N`;
* the **first-order correlation** `g₁(r) = ⟨ψ*(0)ψ(r)⟩/n` along the axes (azimuthal average);
* the **vortex count** `N_v` and the **pair-unbinding statistic**: vortices located by the phase-winding
  detector proved correct in `lean_src/VortexWinding.lean` (`quantumfluids` package, winding of the
  principal phase around each plaquette); a vortex is *paired* if its nearest opposite-sign neighbour is
  closer than `ξ_T = 1/√(gn)`·(pre-set factor 3) and no same-sign vortex is closer — the fraction of
  unpaired vortices `f_free`;
* the **superfluid fraction** `n_s/n` from the momentum-space current correlators of the classical
  field, `J = Im(ψ*∇ψ)`, split into longitudinal and transverse parts: in linear response
  `⟨|J_L(k)|²⟩ → n T` and `⟨|J_T(k)|²⟩ → n_n T` as `k → 0`, so `n_s/n = 1 − lim_{k→0} ⟨|J_T|²⟩/⟨|J_L|²⟩`,
  taken from the smallest three `|k|` shells. This is the standard classical-field estimator (used by
  Foster–Blakie–Davis and by Prokof'ev–Svistunov's classical-field studies); the primary text of
  Foster–Blakie–Davis is paywalled and was **not** read, so the estimator is cited as standard, not by
  their equation number.

Predictions:

| # | Statement | Criterion |
|---|---|---|
| B1 | `g₁(r)` decays **algebraically** at low `T` (fit `r^{−η}` with `η < 1/4`) and **exponentially** at high `T` (fit `e^{−r/ℓ}` with `ℓ < L/4`), with a crossover at some `T_×` | reported; the two regimes must both be seen within the sweep, else the sweep is too narrow and is widened *before* any transition value is read (that widening is an amendment) |
| B2 | `f_free` rises from `≈ 0` to `> 0.5` across the same `T_×` (within one energy step) | PASS/FAIL |
| B3 | **Nelson–Kosterlitz universal jump**: at the transition `n_s λ_T² = 4` (`λ_T² = 2π/T` in these units). The crossing of `n_s(T)·λ_T²` with `4` gives `T_BKT`; prediction: `T_BKT` lies within one energy step of `T_×` from B1/B2 | PASS/FAIL |
| B4 | **Prokof'ev–Ruebenacker–Svistunov**: `n λ_T² = ln(ξ/ g̃)` with `ξ = 380 ± 3`, `g̃ = g` (m = ħ = 1), i.e. `n λ_T² = ln(380)` at the transition. With `n` the coherent-region density, prediction: the measured `n λ²_T` at `T_BKT` lies within `20 %` of `ln(380/g)` | PASS/FAIL, **reported with the caveat** that the classical field with a cutoff is not the quantum gas; a 20 % agreement is the level Foster–Blakie–Davis-type comparisons reach, and a failure here is a statement about the cutoff dependence, to be quantified by repeating one energy at `k_cut = 0.5 k_max` (pre-set) |
| B5 | Finite-size: repeating the transition energy at `L = 32 ξ₀` shifts `T_BKT` by less than one energy step | reported |

Kill: if B1 shows only one regime after widening once, or if K7's thermometer is not stationary at any
energy, the sweep is reported as "no equilibrium classical-field ensemble reached" and no BKT number is
quoted. A B4 failure is *not* a kill; it is the measured cutoff dependence, reported.

## 3. What would count as leverage of the three solver repositories, honestly

* **rusty-SUNDIALS** — used (K6) as the independent integrator. If the Python binding cannot be built on
  this machine (pyo3 0.20 against Python 3.13 is a known incompatibility), the cross-check is done with
  `scipy.integrate.solve_ivp(method="DOP853")` instead and this is written down as such; a PR adding a
  numpy-array RHS path to `rusty-sundials-py` (its current callback converts Python lists on every RHS
  call, prohibitive above a few thousand unknowns) is the concrete improvement to propose.
* **LeanFlow (DualScale solver)** — the IF-RK4 step is the same scheme as its `step_etd_rk4`; the
  follow-up PR is a `ComplexField2D` engine (rustfft, cutoff projector, the K1–K5 tests as Rust tests).
  Not done in this round.
* **QuantumFluids' own Lean** — `VortexWinding.lean` is the correctness proof of the vortex detector used
  for B2; nothing new is claimed for it.

## 4. Not in this round

No Lean for the PGPE (a Hamiltonian ODE on a finite mode set is `GPGalerkin.lean`'s object; its
invariants K1–K3 are theorems there for the *unprojected* Galerkin truncation and the projector does
not change them — the equality of the two is a one-line remark, not a new theorem). No SPGPE. No 3D.
No claim about helium films: the Bishop–Reppy jump is the same universal number, but the data class
here is a weakly interacting Bose gas.

## Amendment A1 (2026-09-22, after the first control run, before any thermal run)

Three of the seven known answers failed on the first run, two through my own errors, one through a
measurement bug; none through the physics, and all three are exactly what the controls are for.

1. **K3 (momentum) FAILED, drift 8.5 (1 % of `P`)** — because §0 said the cutoff `k_cut ≤ (2/3) k_max`
   "makes the cubic term alias-free". That is the dealiasing rule for a *quadratic* nonlinearity; for the
   cubic term `|ψ|²ψ` the alias-free condition is `k_cut ≤ k_max/2`. The aliased scheme is not
   translation-invariant and K3 saw it. Corrected: `k_cut = k_max/2` everywhere (about 3 200 modes on the
   `128²` sweep grid, not 5 800). K1 (norm, `4×10⁻¹⁰`) and K4 (plane wave, `7×10⁻¹⁰`) had passed
   regardless — a reminder that norm and one exact solution do not test translation invariance.
2. **K5 (Bogoliubov) FAILED by factors 5, 2.5, 1.2** — the measured frequency was `μ ± ω` with `μ = g n₀ = 1`:
   the mode amplitude `c_k(t)` carries the condensate's global phase `e^{−iμt}`. Fixed by measuring
   `c_k · c₀*/|c₀|` (the condensate frame). Criterion unchanged (`0.5 %`).
3. **K2 (energy) FAILED only on the `dt⁴` ratio**: drift `2×10⁻⁹` at `dt = 0.005` (well inside `10⁻⁶`)
   but ratio `23` instead of `16 ± 3`, because at that level the drift is roundoff accumulated over 4 000
   steps, not truncation error. The scaling test is moved to `dt = 0.02` vs `0.04`, where the drift is
   far above roundoff; the `≤ 10⁻⁶` at `dt = 0.005` criterion stays.

K6 passed with the pre-registered **fallback** (`scipy` DOP853): `rusty-sundials-py` does not build on
this machine — it is not a member of the Cargo workspace (maturin refuses), and once added it fails to
compile against its pinned `pyo3 0.20` with the current Rust toolchain (three errors, recorded in the
results file). Both are concrete upstream fixes to propose; K6's independent-integrator content
(agreement `3.5×10⁻⁷` against a tolerance `2.6×10⁻⁵`, and disagreement `0.086` when the reference is run
loose) stands with DOP853. K7 passed (`4.7 %`).

## Amendment A2 (2026-09-24, before any thermal run): the duality and topology observables, and three gate verdicts

Written after the quick dry run was *launched* but before its output or any full-sweep output was read.
It adds observables; it changes no K or B criterion.

### A2.1 Gate verdicts on the external feedback ("the duality has a legitimate physical home")

The feedback listed four places where a modular duality is exact with a physical fixed point: quantum Hall
(Γ₀(2) on σ = σ_xy + iσ_xx), Seiberg–Witten (Γ(2) on the u-plane), the 2D XY/BKT transition (R ↔ α′/R,
"the self-dual radius, measured in films and cold atoms") and K3 mirror symmetry (Fricke W_N as the
Dolgachev–Nikulin mirror involution on Γ₀(N)+N). Checked before building on any of them:

1. **K3 mirror** — correct; already read and recorded (Dolgachev alg-geom/9502005 Thm 7.1, `Fricke.lean`,
   CLAIM-035). It is a theorem about lattice-polarised K3 moduli. Nothing in this repository is a K3
   surface; the verdict "same involution, without the group" stands for helium.
2. **BKT is NOT at the self-dual radius.** For the compact boson `S = (K/2)∫(∇θ)²` the unit spin-wave
   operator `e^{iθ}` has scaling dimension `Δ_e = 1/(4πK)` and the unit vortex `Δ_m = πK`; T-duality
   (José–Kadanoff–Kirkpatrick–Nelson, PRB 16, 1217 (1977), DOI verified) exchanges them, `Δ_e Δ_m = 1/4`.
   Self-dual point: `Δ_e = Δ_m = 1/2`, i.e. `η = 2Δ_e = 1`, `K = 1/(2π)`. BKT point: the vortex becomes
   marginal, `Δ_m = 2`, i.e. `K = 2/π`, `η = 1/4` — four times the self-dual stiffness (twice the radius).
   What films (Bishop–Reppy) and cold atoms measure is the Nelson–Kosterlitz jump `n_s λ_T² = 4` (PRL 39,
   1201 (1977), DOI verified) ⇔ `η = 1/4`; the self-dual point `η = 1` lies inside the vortex-relevant
   (normal) region and is not a fixed point of the XY transition. The duality is exact; its fixed point
   is not the physical one here. This is tested below (D3), not assumed.
3. **Quantum Hall: Γ₀(2) yes, Fricke no.** Lütken–Ross (PRB 45, 11837 (1992), DOI verified; review
   arXiv:1008.5257) take Γ_H = Aut Γ₀(2) generated by `T: σ ↦ σ+1`, `D = ST²S: σ ↦ σ/(1−2σ)` and the
   antiholomorphic `J`. The critical point `σ⊗ = (1+i)/2` is the elliptic point of `M = (1,−1;2,−1) ∈ Γ₀(2)`;
   the 3→4 plateau transition at 13 mK gives `ρ_H = 0.282 ± 0.002` against `7/25` (Li et al., PRL 102,
   216801 (2009) — Lütken–Ross cite it as 216811, a typo; the Crossref DOI is 10.1103/PhysRevLett.102.216801).
   The Fricke involution `W₂: σ ↦ −1/(2σ)` normalises Γ₀(2) and maps `σ⊗` to `σ⊗ − 1` (same Γ₀(2)-orbit),
   **but it sends every plateau `p/q` (q odd) to `−q/(2p)`, an even-denominator point that is never a
   plateau** (checked for |p| ≤ 40, q < 40 odd; the general statement is to be proved in Lean, `QHFricke.lean`).
   So `W₂` is not a symmetry of the Hall phase diagram: it swaps the two cusps of X₀(2) and only one of them
   carries plateaux. The feedback's "keeps the duality" is right for Γ₀(2); it is not right for the Fricke
   element that `Fricke.lean` is about.
4. **Seiberg–Witten** — a theorem about N=2 SU(2) gauge theory; no instrument here; not pursued.
5. **Literature gate on the TDA side:** persistent homology locating the XY BKT transition from spin
   configurations is published (Cole–Loges–Shiu arXiv:2009.14231; Sale–Giansiracusa–Lucini arXiv:2109.10960;
   PH on 2D Bose-gas dynamics: Spitz et al. arXiv:2001.02616). T1 below is therefore an *instrument* in the
   closed loop, not a claim of novelty.

### A2.2 Added observables and predictions (PASS/FAIL, fixed now)

Per sample, the W₁-optimal perfect matching of the +1 to the −1 vortices on the torus (the 1-Wasserstein
transport between the two signed point clouds; `observables.dipole_matching`), its mean edge `ℓ_d`, the
same for 4 charge-shuffled copies of the same positions `ℓ_null`, and `Q = ℓ_d/ℓ_null`. No length is
pre-set (unlike B2's 3 ξ). With `η` from B1's algebraic fit, `n_s` from B3's estimator, `λ_T² = 2π/T`, `n = 1`:

| # | Statement | Criterion |
|---|---|---|
| C-T1 | control: 50 dipoles of separation 1 at random positions in L = 64 give `Q < 0.2`; 100 independent random charges give `Q ∈ [0.85, 1.15]` | must pass before T1 is read |
| D1 | spin-wave duality relation `η · n_s λ_T² = 1` on every energy in the algebraic regime with `n_s λ_T² > 4` | seed-mean within `[0.75, 1.33]` at each such energy |
| D2 | at `T_BKT` (linear interpolation of the `n_s λ_T² = 4` crossing), the interpolated `η` | `0.25 ± 0.08` |
| D3 | the self-dual point is not the transition: at the last energy where the algebraic fit beats the exponential one, `η < 0.5` (the self-dual value is `1`) | PASS/FAIL |
| T1 | topology ↔ stiffness closed loop: `Q ≤ 0.5` at the lowest energy with `⟨N_v⟩ ≥ 4`; `Q ≥ 0.8` at the highest energy; the largest seed-mean rise of `Q` between consecutive energies lies within one energy step of `T_BKT` from B3 | three parts, each PASS/FAIL |

D1 fails for finite-size or cutoff reasons as readily as for physical ones; a D1 failure is reported with
the B5 finite-size run, not explained away.

## Amendment A3 (2026-09-24, DATA-TRIGGERED: written after reading the first 6 of 36 full-sweep trajectories)

This amendment is not blind: it was written after seeing `e = 0.60` (seed 11), `e = 0.90` (seeds 11–13) and
`e = 1.20` (seeds 11–12). It changes no B/D/T threshold. It adds an admission criterion, because those six
trajectories show that K7's thermometer is not a sufficient equilibrium test.

**What was seen.** (i) At `e = 0.90` two seeds give `n_s/n = −3.0` and `−3.2` with condensate fraction
0.18–0.23, while the third seed at the same energy gives `n_s/n = 0.57`, condensate 0.62. The transverse
current correlator at the smallest shell is `⟨|J_T|²⟩ ≈ 7 n T A`, i.e. `n_n ≈ 7 n` — impossible in
equilibrium. Those two runs carry ≈ 10–12 vortices with `Q = 0.67` (largely unbound) at `T = 0.44`, while
`e = 1.20` (`T = 0.77`) carries ≈ 90 vortices with `Q = 0.22` (bound): a non-monotonic `Q(T)`. Reading:
free vortices left by the random initial state have not annihilated by `t = 1500` (the Hamiltonian PGPE
has no damping beyond its own thermal cloud, which is thin at low energy); the third seed is visibly still
losing them (`⟨N_v⟩` 9.4 → 6.3 between the two halves of its window). (ii) At `e = 0.60`, `⟨|J_L|²⟩` at the
smallest shells is `2.1 n T A`: the lowest-k phonons are not at the temperature of the high-k modes.
(iii) K7 passed on all six (halves within 5 %): it fits `[0.4, 1.0] k_cut` and is blind to both.

**Admission criterion (the classical longitudinal sum rule).** In classical equilibrium the f-sum rule
`χ_L = n/m` and the classical fluctuation–dissipation relation give `⟨|J_L(k)|²⟩ = n T A` for every `k`
(`A = L²`); and `0 ≤ n_n ≤ n` bounds `⟨|J_T(k)|²⟩ ≤ n T A`. A trajectory is admitted to the B/D/T
analysis only if, averaged over the three smallest shells,
`R_L = ⟨|J_L|²⟩/(nTA) ∈ [0.8, 1.25]` **and** `R_T = ⟨|J_T|²⟩/(nTA) ≤ 1.1`.
Non-admitted trajectories are reported (they are the finding that the thermometer can pass while the
topology has not relaxed) and are re-run for longer (`t_end = 4000`, same seed, final state saved),
up to one extension; an energy with no admitted seed after the extension is reported as "not equilibrated"
and excluded, and the B/D/T criteria are evaluated on the admitted energies only, with the exclusions
listed. The prereg's compute estimate (6 min per trajectory) was wrong by a factor ≈ 15 (measured
14.6 ms per step at 128² single-process; ≈ 95 min per trajectory with 8 in parallel on a shared desktop).

## Amendment A4 (2026-09-24, POST HOC: after all 36 t = 1500 trajectories) — A3's premise was wrong

A3 called `⟨|J_L(k)|²⟩ = n T A` an exact classical sum rule. **It is not, for a classical field.** It holds
for classical *particles*, and for the field in its ordered (hydrodynamic) regime, where the current
fluctuations are phase fluctuations with `⟨|φ_k|²⟩ = T/(n_s k² A)`. In the incoherent regime, a
Rayleigh–Jeans field with occupations `n_k = T/(ε_k + b)` has
`⟨|J_L(q)|²⟩ = Σ_k ((k + q/2)·q̂)² n_k n_{k+q}`, which is below `n T A` whenever `b = 2gn − μ` is not small
next to the kinetic energies inside the cutoff. Evaluated with each trajectory's own fitted `(T, b)` on
the same projected mode set, this ideal-field value reproduces the measured `R_L` within 5 % at
`e = 2.4 … 3.2` (0.611/0.566, 0.536/0.563, 0.454/0.466, 0.318/0.320). So A3's lower bound `R_L ≥ 0.8`
excludes the normal phase for a reason that is false. A3's two other signals survive, because no
equilibrium regime produces them: `R_L > 1` by a margin (hydrodynamic → 1; ideal field < 1), and
`R_T > R_L` (`n_n > n`).

**A4 admission:** `R_L ≤ 1.25` and `R_T ≤ 1.1 R_L`. This is a post-hoc correction made after all data were
seen; the verdicts are reported under **both** A3-as-written and A4, and any criterion whose verdict
differs between them is flagged. The one-time extension to `t = 4000` is run for trajectories failing
A4 (`e = 0.60` × 3 on `R_L`; `e = 0.90` seeds 11, 12 on `R_T`). A3-as-written would also extend every
trajectory at `e ≥ 2.0`; that is not run, because their failure is the regime, not the relaxation
(their thermometers are stationary and the ideal-field value accounts for their `R_L`).

## Amendment A2 (2026-09-26): the rusty-sundials-py build is fixed, upstream

Both concrete fixes §3 proposed for `rusty-sundials-py` are made, on the upstream repository, not here:
added to `[workspace] members` (so `cargo build --workspace` and CI cover it), and — the actual root cause,
simpler than guessed — its three `E0603` errors were a stale import path (`cvode::solver::Cvode`,
`cvode::constants::{Method, Task}`, private modules) instead of the crate-root re-export
(`cvode::{Cvode, Method, Task}`); **not** a `pyo3 0.20`-versus-current-Rust-toolchain incompatibility as
§3 conjectured. `pyo3 0.20.3` compiles cleanly against the current toolchain once the import path is right.
Built with `maturin develop --release` into this project's own `.venv` and verified numerically correct
(a scalar decay ODE through the real CVODE Adams integrator from Python, `err ≈ 2.4×10⁻⁶` against the
closed form) — not merely "imports without error". PR:
[rusty-SUNDIALS#55](https://github.com/xaviercallens/rusty-SUNDIALS/pull/55) (open, not yet merged).

**Not fixed, and not attempted here**: the numpy-array RHS path. The `.solve()` callback still round-trips
every internal CVODE step through the GIL and a Python-list conversion; re-running K6's own 16×16-grid
comparison end to end with the now-working binding was started and killed after several CPU-minutes with
no result, to avoid contending with a concurrent `L=128` PGPE run for the machine's 8 cores — this is the
same "prohibitive above a few thousand unknowns" limitation §3 already named, now observed directly rather
than only inferred. K6's own pass (scipy fallback, `3.5×10⁻⁷` agreement) is unaffected and is not re-run.
